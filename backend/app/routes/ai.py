# AI Agent routes
from flask import Blueprint, request, jsonify
from app import db
from app.models import Agent, Game
from app.services.ai_agent import AIAgent
import json

bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# Initialize AI agent (can be shared or per-request)
ai_agent = AIAgent("GameAgent")


@bp.route('/play/<int:game_id>', methods=['POST'])
def ai_play(game_id):
    """AI makes a move in the game"""
    
    game = Game.query.get_or_404(game_id)
    
    if game.status != 'playing':
        return jsonify({'error': 'Game not in progress'}), 400
    
    # Parse game state
    try:
        state = json.loads(game.state) if isinstance(game.state, str) else game.state
    except:
        state = {}
    
    # Get AI to decide move
    try:
        # Use AI to decide
        move = ai_agent.decide_move(game.game_type, {
            'state': state,
            'current_player': game.current_turn,
            'game_type': game.game_type
        })
        
        # For now, if AI returns a valid move, make it
        # In production, parse the move and apply it
        
        return jsonify({
            'ai_move': move,
            'game_state': state
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/prompt/<game_type>', methods=['GET'])
def test_prompt(game_type):
    """Test AI prompt for a game type"""
    
    # Get sample state for testing
    if game_type == 'rps':
        state = {'round': 1, 'player1_move': 'rock'}
    elif game_type == 'tictactoe':
        state = {'board': [None] * 9, 'current_player': 'X'}
    else:
        state = {}
    
    prompt = ai_agent.get_prompt(game_type, state)
    
    return jsonify({
        'game_type': game_type,
        'sample_state': state,
        'prompt': prompt
    })


@bp.route('/play', methods=['POST'])
def ai_make_move():
    """Direct AI move - give game state, get move"""
    
    data = request.get_json()
    
    game_type = data.get('game_type')
    game_state = data.get('state')
    api_key = data.get('api_key')  # Optional custom API key
    
    if not game_type or not game_state:
        return jsonify({'error': 'game_type and state required'}), 400
    
    # Create agent with optional API key
    agent = AIAgent("TempAgent", api_key)
    
    try:
        move = agent.decide_move(game_type, game_state)
        
        return jsonify({
            'move': move,
            'game_type': game_type
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
