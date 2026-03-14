from flask import Blueprint, request, jsonify
from app import db
from app.models import Agent, Game
from app.games.engine import get_game
import json

bp = Blueprint('games', __name__, url_prefix='/api/games')

@bp.route('', methods=['GET'])
def list_games():
    """List available game types"""
    return jsonify([
        {'type': 'rps', 'name': 'Rock Paper Scissors', 'players': 2},
        {'type': 'tictactoe', 'name': 'Tic-Tac-Toe', 'players': 2},
        {'type': 'connect4', 'name': 'Connect Four', 'players': 2},
        {'type': 'numberguess', 'name': 'Number Guessing', 'players': 2},
        {'type': 'memory', 'name': 'Memory Game', 'players': 2},
        {'type': 'battleship', 'name': 'Battleship', 'players': 2},
        {'type': 'mastermind', 'name': 'Mastermind', 'players': 2},
        {'type': 'checkers', 'name': 'Checkers', 'players': 2},
        {'type': 'chess', 'name': 'Chess (5x5)', 'players': 2},
        {'type': 'snake', 'name': 'Snake', 'players': 1},
        {'type': 'pong', 'name': 'Pong', 'players': 2},
        {'type': 'dice', 'name': 'Dice High/Low', 'players': 2}
    ])

@bp.route('/<int:game_id>', methods=['GET'])
def get_game_state(game_id):
    game = Game.query.get_or_404(game_id)
    return jsonify(game.to_dict())

@bp.route('', methods=['POST'])
def create_game():
    """Create a new game"""
    data = request.get_json()
    
    player1_id = data.get('player1_id')
    game_type = data.get('game_type', 'rps')
    
    if not player1_id:
        return jsonify({'error': 'player1_id required'}), 400
    
    player1 = Agent.query.get(player1_id)
    if not player1:
        return jsonify({'error': 'Player 1 not found'}), 404
    
    game_engine = get_game(game_type)
    if not game_engine:
        return jsonify({'error': 'Invalid game type'}), 400
    
    initial_state = game_engine.get_initial_state()
    
    game = Game(
        game_type=game_type,
        player1_id=player1_id,
        player2_id=data.get('player2_id'),
        state=json.dumps(initial_state),
        status='waiting' if not data.get('player2_id') else 'playing'
    )
    
    db.session.add(game)
    db.session.commit()
    
    return jsonify(game.to_dict()), 201

@bp.route('/<int:game_id>/join', methods=['POST'])
def join_game(game_id):
    """Join a waiting game"""
    game = Game.query.get_or_404(game_id)
    
    if game.status != 'waiting':
        return jsonify({'error': 'Game already started'}), 400
    
    data = request.get_json()
    agent_id = data.get('agent_id')
    
    if not agent_id:
        return jsonify({'error': 'agent_id required'}), 400
    
    game.player2_id = agent_id
    game.status = 'playing'
    db.session.commit()
    
    return jsonify(game.to_dict())

@bp.route('/<int:game_id>/play', methods=['POST'])
def make_move(game_id):
    """Make a move in the game"""
    game = Game.query.get_or_404(game_id)
    data = request.get_json()
    
    agent_id = data.get('agent_id')
    move = data.get('move')  # For RPS: rock/paper/scissors, For TTT: position 0-8
    
    if not agent_id or move is None:
        return jsonify({'error': 'agent_id and move required'}), 400
    
    # Verify it's this agent's turn
    if game.current_turn == 1 and agent_id != game.player1_id:
        return jsonify({'error': 'Not your turn'}), 400
    if game.current_turn == 2 and agent_id != game.player2_id:
        return jsonify({'error': 'Not your turn'}), 400
    
    game_engine = get_game(game.game_type)
    if not game_engine:
        return jsonify({'error': 'Invalid game type'}), 400
    
    # Make move
    new_state, error = game_engine.make_move(
        game.state, 
        game.current_turn, 
        move
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    game.state = json.dumps(new_state)
    
    # Check for winner
    if new_state.get('winner') or new_state.get('is_draw'):
        game.status = 'finished'
        game.winner_id = game.player1_id if new_state.get('winner') == 1 else game.player2_id
        game.is_draw = new_state.get('is_draw', False)
        
        # Update stats
        game.player1.games_played += 1
        game.player2.games_played += 1
        
        if game.is_draw:
            game.player1.games_drawn += 1
            game.player2.games_drawn += 1
        else:
            winner = Agent.query.get(game.winner_id)
            loser_id = game.player2_id if winner.id == game.player1_id else game.player1_id
            loser = Agent.query.get(loser_id)
            
            winner.games_won += 1
            # Update ELO (simplified)
            winner.elo += 10
            loser.elo -= 10
    
    # Switch turns
    game.current_turn = 2 if game.current_turn == 1 else 1
    
    db.session.commit()
    
    return jsonify(game.to_dict())

@bp.route('/match', methods=['POST'])
def start_match():
    """Start a match between two agents"""
    data = request.get_json()
    
    player1_id = data.get('player1_id')
    player2_id = data.get('player2_id')
    game_type = data.get('game_type', 'rps')
    
    if not player1_id or not player2_id:
        return jsonify({'error': 'Both player IDs required'}), 400
    
    player1 = Agent.query.get(player1_id)
    player2 = Agent.query.get(player2_id)
    
    if not player1 or not player2:
        return jsonify({'error': 'Player not found'}), 404
    
    game_engine = get_game(game_type)
    initial_state = game_engine.get_initial_state()
    
    game = Game(
        game_type=game_type,
        player1_id=player1_id,
        player2_id=player2_id,
        state=json.dumps(initial_state),
        status='playing'
    )
    
    db.session.add(game)
    db.session.commit()
    
    return jsonify(game.to_dict()), 201


@bp.route('/recent', methods=['GET'])
def recent_games():
    """Get recent games"""
    games = Game.query.order_by(Game.created_at.desc()).limit(20).all()
    return jsonify([g.to_dict() for g in games])
