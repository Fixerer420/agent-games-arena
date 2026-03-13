# Rule-Based AI routes
from flask import Blueprint, request, jsonify
from app.services.rule_agent import RuleBasedAgent

bp = Blueprint('rule', __name__, url_prefix='/api/rule')

# Default rule-based agent
rule_agent = RuleBasedAgent("RuleBot")


@bp.route('/play', methods=['POST'])
def rule_play():
    """Rule-based AI move - instant, no external calls"""
    
    data = request.get_json()
    
    game_type = data.get('game_type')
    game_state = data.get('state')
    
    if not game_type or not game_state:
        return jsonify({'error': 'game_type and state required'}), 400
    
    try:
        move = rule_agent.decide_move(game_type, game_state)
        
        return jsonify({
            'move': move,
            'game_type': game_type,
            'agent': 'RuleBot'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
