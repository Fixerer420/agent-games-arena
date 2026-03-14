# LLM Battle Arena - Backend API
# Player matchmaking + game lobby system

from flask import Blueprint, request, jsonify
from app import db
from app.models import Agent, Game
import uuid
import time
import random

bp = Blueprint('lobby', __name__, url_prefix='/api/lobby')

# In-memory lobby state
LOBBY = {
    'waiting': [],  # Players waiting for match
    'active': {}     # Active games: {game_id: {player1, player2, game_type, state}}
}


@bp.route('/join', methods=['POST'])
def join_lobby():
    """Player joins lobby with their LLM choice"""
    data = request.get_json()
    
    player_id = str(uuid.uuid4())[:8]
    llm_choice = data.get('llm', 'llama3.2')
    player_name = data.get('name', f'Player_{player_id}')
    
    player = {
        'id': player_id,
        'name': player_name,
        'llm': llm_choice,
        'joined_at': time.time()
    }
    
    # Check for existing match
    if LOBBY['waiting']:
        # Match with waiting player
        opponent = LOBBY['waiting'].pop(0)
        game_id = str(uuid.uuid4())[:8]
        
        game = {
            'id': game_id,
            'player1': opponent,
            'player2': player,
            'game_type': None,  # Not chosen yet
            'state': 'waiting_for_game',
            'created_at': time.time()
        }
        
        LOBBY['active'][game_id] = game
        
        return jsonify({
            'status': 'matched',
            'game_id': game_id,
            'opponent': opponent,
            'message': f'Matched with {opponent["name"]}! Choose a game.'
        })
    else:
        # Add to waiting list
        LOBBY['waiting'].append(player)
        
        return jsonify({
            'status': 'waiting',
            'message': 'Waiting for opponent...',
            'position': len(LOBBY['waiting'])
        })


@bp.route('/leave', methods=['POST'])
def leave_lobby():
    """Player leaves lobby"""
    data = request.get_json()
    player_id = data.get('player_id')
    
    # Remove from waiting
    LOBBY['waiting'] = [p for p in LOBBY['waiting'] if p['id'] != player_id]
    
    return jsonify({'status': 'left'})


@bp.route('/status', methods=['GET'])
def lobby_status():
    """Get lobby status"""
    return jsonify({
        'waiting': len(LOBBY['waiting']),
        'players': [{'name': p['name'], 'llm': p['llm']} for p in LOBBY['waiting']],
        'active_games': len(LOBBY['active'])
    })


@bp.route('/game/<game_id>', methods=['GET'])
def get_game(game_id):
    """Get game state"""
    game = LOBBY['active'].get(game_id)
    
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    return jsonify({
        'id': game['id'],
        'player1': game['player1'],
        'player2': game['player2'],
        'game_type': game['game_type'],
        'state': game['state'],
        'current_turn': game.get('current_turn', 1)
    })


@bp.route('/game/<game_id>/choose', methods=['POST'])
def choose_game(game_id):
    """Choose game type for the match"""
    game = LOBBY['active'].get(game_id)
    
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    if game['state'] != 'waiting_for_game':
        return jsonify({'error': 'Game already started'}), 400
    
    data = request.get_json()
    game_type = data.get('game_type', 'rps')
    
    game['game_type'] = game_type
    game['state'] = 'playing'
    game['current_turn'] = 1
    
    return jsonify({
        'status': 'started',
        'game_type': game_type,
        'message': f'Game {game_type} started!'
    })


@bp.route('/game/<game_id>/move', methods=['POST'])
def make_move(game_id):
    """Make a move in the game"""
    game = LOBBY['active'].get(game_id)
    
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.get_json()
    player_id = data.get('player_id')
    move = data.get('move')
    
    # Track moves
    if 'moves' not in game:
        game['moves'] = []
    
    game['moves'].append({
        'player_id': player_id,
        'move': move,
        'turn': game.get('current_turn', 1)
    })
    
    # Simple RPS logic
    if game['game_type'] == 'rps':
        if len(game['moves']) >= 2:
            move1 = game['moves'][0]['move']
            move2 = game['moves'][1]['move']
            
            winner = determine_rps_winner(move1, move2)
            
            game['state'] = 'finished'
            game['winner'] = winner
            
            return jsonify({
                'status': 'finished',
                'move1': move1,
                'move2': move2,
                'winner': winner
            })
    
    game['current_turn'] = game.get('current_turn', 1) + 1
    
    return jsonify({
        'status': 'waiting',
        'message': 'Waiting for opponent move...'
    })


def determine_rps_winner(move1, move2):
    if move1 == move2:
        return 'draw'
    elif (move1 == 'rock' and move2 == 'scissors') or \
         (move1 == 'paper' and move2 == 'rock') or \
         (move1 == 'scissors' and move2 == 'paper'):
        return 'player1'
    else:
        return 'player2'


@bp.route('/tournament', methods=['POST'])
def create_tournament():
    """Create a tournament"""
    data = request.get_json()
    
    tournament_id = str(uuid.uuid4())[:8]
    
    # Get players from lobby or specified list
    players = data.get('players', [])
    
    if len(players) < 2:
        # Get from waiting lobby
        players = LOBBY['waiting'][:8]
    
    if len(players) < 2:
        return jsonify({'error': 'Need at least 2 players'}), 400
    
    # Create bracket
    random.shuffle(players)
    rounds = []
    round_num = 1
    
    while len(players) > 1:
        round_matches = []
        next_round = []
        
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                p1, p2 = players[i], players[i + 1]
                round_matches.append({
                    'player1': p1['name'],
                    'player2': p2['name'],
                    'winner': None
                })
                next_round.append(p1)  # Placeholder
            else:
                next_round.append(players[i])  # Bye
        
        rounds.append({'round': round_num, 'matches': round_matches})
        players = next_round
        round_num += 1
    
    tournament = {
        'id': tournament_id,
        'players': data.get('players', []),
        'rounds': rounds,
        'champion': None,
        'state': 'ready'
    }
    
    return jsonify({
        'tournament_id': tournament_id,
        'rounds': rounds,
        'total_players': len(players)
    })


@bp.route('/tournament/<tournament_id>', methods=['GET'])
def get_tournament(tournament_id):
    """Get tournament status"""
    # This would normally fetch from DB
    return jsonify({
        'tournament_id': tournament_id,
        'status': 'Not implemented - use tournament.html'
    })
