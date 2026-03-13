# External Agent API
# Allows outside agents to connect and play

from flask import Blueprint, request, jsonify
from app import db
import uuid

bp = Blueprint('external', __name__, url_prefix='/api/external')


@bp.route('/register', methods=['POST'])
def register_agent():
    """Register an external agent with custom LLM endpoint"""
    data = request.get_json()
    
    name = data.get('name', 'ExternalAgent')
    endpoint = data.get('endpoint')  # Their LLM endpoint
    api_key = data.get('api_key', '')
    model = data.get('model', 'default')
    
    agent_id = str(uuid.uuid4())
    
    # Store in a simple dict (could be DB)
    if not hasattr(bp, 'external_agents'):
        bp.external_agents = {}
    
    bp.external_agents[agent_id] = {
        'id': agent_id,
        'name': name,
        'endpoint': endpoint,
        'api_key': api_key,
        'model': model,
        'games_played': 0,
        'games_won': 0
    }
    
    return jsonify({
        'agent_id': agent_id,
        'name': name,
        'message': 'Agent registered! Use agent_id to join games.'
    }), 201


@bp.route('/agents', methods=['GET'])
def list_external_agents():
    """List registered external agents"""
    agents = getattr(bp, 'external_agents', {})
    return jsonify([{
        'id': v['id'],
        'name': v['name'],
        'games_played': v['games_played'],
        'games_won': v['games_won']
    } for v in agents.values()])


@bp.route('/agent/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get external agent info"""
    agents = getattr(bp, 'external_agents', {})
    agent = agents.get(agent_id)
    
    if not agent:
        return jsonify({'error': 'Agent not found'}), 404
    
    return jsonify({
        'id': agent['id'],
        'name': agent['name'],
        'games_played': agent['games_played'],
        'games_won': agent['games_won'],
        'win_rate': round(agent['games_won'] / max(1, agent['games_played']), 2)
    })


@bp.route('/agent/<agent_id>/play', methods=['POST'])
def external_agent_play():
    """Get move from external agent"""
    data = request.get_json()
    agent_id = data.get('agent_id')
    game_type = data.get('game_type', 'rps')
    state = data.get('state', {})
    
    agents = getattr(bp, 'external_agents', {})
    agent = agents.get(agent_id)
    
    if not agent:
        return jsonify({'error': 'Agent not found'}), 404
    
    # Call their endpoint
    if agent['endpoint']:
        try:
            import requests
            response = requests.post(
                agent['endpoint'],
                headers={'Authorization': f"Bearer {agent['api_key']}"},
                json={
                    'game_type': game_type,
                    'state': state,
                    'model': agent['model']
                },
                timeout=30
            )
            if response.status_code == 200:
                move = response.json().get('move', 'rock')
            else:
                move = 'rock'  # Fallback
        except:
            move = 'rock'  # Fallback
    else:
        move = 'rock'  # Default
    
    # Update stats
    agent['games_played'] += 1
    
    return jsonify({
        'agent_id': agent_id,
        'agent_name': agent['name'],
        'move': move
    })


@bp.route('/agent/<agent_id>/result', methods=['POST'])
def report_result(agent_id):
    """Report game result to update agent stats"""
    data = request.get_json()
    won = data.get('won', False)
    
    agents = getattr(bp, 'external_agents', {})
    agent = agents.get(agent_id)
    
    if not agent:
        return jsonify({'error': 'Agent not found'}), 404
    
    if won:
        agent['games_won'] += 1
    
    return jsonify({
        'agent_id': agent_id,
        'games_played': agent['games_played'],
        'games_won': agent['games_won']
    })
