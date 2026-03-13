# AI vs Human Game Route
# Simplified: Human plays directly against AI

from flask import Blueprint, request, jsonify
from app.services.rule_agent import RuleBasedAgent

bp = Blueprint('ai_game', __name__, url_prefix='/api/ai-game')

# Default rule-based AI
ai_agent = RuleBasedAgent("RuleBot")


@bp.route('/start', methods=['POST'])
def start_ai_game():
    """Start a game against AI - returns game state"""
    
    data = request.get_json()
    game_type = data.get('game_type', 'rps')
    
    # Initial state
    if game_type == 'rps':
        state = {'round': 1, 'moves': [], 'player_move': None, 'ai_move': None}
    elif game_type == 'tictactoe':
        state = {'board': [None] * 9, 'current_player': 'human'}
    else:
        state = {}
    
    return jsonify({
        'game_type': game_type,
        'state': state,
        'player': 'human',
        'ai': 'RuleBot'
    })


@bp.route('/move', methods=['POST'])
def make_ai_move():
    """Human makes move, AI responds"""
    
    data = request.get_json()
    game_type = data.get('game_type')
    state = data.get('state', {})
    human_move = data.get('move')
    
    if not game_type or human_move is None:
        return jsonify({'error': 'game_type and move required'}), 400
    
    # Update state with human move
    if game_type == 'rps':
        state['player_move'] = human_move
        
        # Get AI move
        ai_state = {'round': state.get('round', 1), 'player1_move': human_move}
        ai_move = ai_agent.decide_move('rps', ai_state)
        state['ai_move'] = ai_move
        state['round'] += 1
        
        # Determine winner
        winners = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
        if human_move == ai_move:
            state['result'] = 'draw'
        elif winners.get(human_move) == ai_move:
            state['result'] = 'win'
        else:
            state['result'] = 'lose'
            
    elif game_type == 'tictactoe':
        board = state.get('board', [None] * 9)
        board[int(human_move)] = 'X'
        
        # Check if X won
        if check_tictactoe_winner(board, 'X'):
            state['board'] = board
            state['result'] = 'win'
            return jsonify({'state': state, 'ai_move': None, 'game_over': True})
        
        # AI move
        ai_state = {'board': board, 'current_player': 2}
        ai_move = ai_agent.decide_move('tictactoe', ai_state)
        
        if ai_move:
            board[int(ai_move)] = 'O'
            state['board'] = board
            
            if check_tictactoe_winner(board, 'O'):
                state['result'] = 'lose'
                return jsonify({'state': state, 'ai_move': ai_move, 'game_over': True})
        
        state['board'] = board
        state['ai_move'] = ai_move
    else:
        # Generic AI response
        ai_move = ai_agent.decide_move(game_type, state)
        state['ai_move'] = ai_move
    
    return jsonify({'state': state, 'ai_move': ai_move, 'game_over': False})


def check_tictactoe_winner(board, symbol):
    """Check if symbol won"""
    lines = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
    for line in lines:
        if all(board[i] == symbol for i in line):
            return True
    return False
