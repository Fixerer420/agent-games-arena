from flask import Blueprint, request, jsonify
from app import db
from app.models import Agent, Game
import json

bp = Blueprint('agents', __name__, url_prefix='/api/agents')

@bp.route('', methods=['GET'])
def list_agents():
    agents = Agent.query.all()
    return jsonify([a.to_dict() for a in agents])

@bp.route('', methods=['POST'])
def create_agent():
    data = request.get_json()
    agent = Agent(
        name=data.get('name'),
        description=data.get('description', '')
    )
    db.session.add(agent)
    db.session.commit()
    return jsonify(agent.to_dict()), 201

@bp.route('/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    return jsonify(agent.to_dict())

@bp.route('/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    db.session.delete(agent)
    db.session.commit()
    return jsonify({'message': 'Agent deleted'})

@bp.route('/<agent_id>/stats', methods=['GET'])
def get_agent_stats(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    return jsonify(agent.to_dict()['stats'])
