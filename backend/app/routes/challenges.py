# Challenge System
# Challenge specific bots/players

from flask import Blueprint, request, jsonify
from app import db
import uuid
import secrets
from datetime import datetime, timedelta

bp = Blueprint('challenges', __name__, url_prefix='/api/challenges')


# In-memory challenge storage
challenges = {}


@bp.route('', methods=['GET'])
def list_challenges():
    """List active challenges"""
    active = [c for c in challenges.values() if c['status'] == 'pending']
    return jsonify(active)


@bp.route('', methods=['POST'])
def create_challenge():
    """Create a challenge"""
    data = request.get_json()
    
    challenger = data.get('challenger', 'Anonymous')
    game_type = data.get('game_type', 'rps')
    bet = data.get('bet', 0)  # Optional wager
    
    challenge_id = secrets.token_hex(4)
    
    challenges[challenge_id] = {
        'id': challenge_id,
        'challenger': challenger,
        'game_type': game_type,
        'bet': bet,
        'status': 'pending',
        'created_at': datetime.utcnow().isoformat(),
        'challenger_wins': 0,
        'challenger_losses': 0
    }
    
    return jsonify({
        'id': challenge_id,
        'challenger': challenger,
        'game_type': game_type,
        'bet': bet,
        'status': 'pending',
        'message': 'Challenge created! Share the ID.'
    }), 201


@bp.route('/<challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    """Get challenge details"""
    challenge = challenges.get(challenge_id)
    
    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404
    
    return jsonify(challenge)


@bp.route('/<challenge_id>/accept', methods=['POST'])
def accept_challenge(challenge_id):
    """Accept a challenge"""
    data = request.get_json()
    responder = data.get('responder', 'Challenger')
    
    challenge = challenges.get(challenge_id)
    
    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404
    
    if challenge['status'] != 'pending':
        return jsonify({'error': 'Challenge already accepted'}), 400
    
    challenge['responder'] = responder
    challenge['status'] = 'accepted'
    challenge['responder_wins'] = 0
    challenge['responder_losses'] = 0
    
    return jsonify({
        'id': challenge_id,
        'status': 'accepted',
        'responder': responder,
        'message': 'Challenge accepted! Game on!'
    })


@bp.route('/<challenge_id>/result', methods=['POST'])
def report_challenge_result(challenge_id):
    """Report result of a challenge game"""
    data = request.get_json()
    winner = data.get('winner')  # 'challenger' or 'responder'
    
    challenge = challenges.get(challenge_id)
    
    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404
    
    if winner == 'challenger':
        challenge['challenger_wins'] += 1
    elif winner == 'responder':
        challenge['responder_wins'] += 1
    
    return jsonify({
        'challenger_wins': challenge['challenger_wins'],
        'responder_wins': challenge['responder_wins']
    })


@bp.route('/<challenge_id>', methods=['DELETE'])
def delete_challenge(challenge_id):
    """Delete/cancel a challenge"""
    if challenge_id in challenges:
        del challenges[challenge_id]
        return jsonify({'message': 'Challenge deleted'})
    return jsonify({'error': 'Challenge not found'}), 404
