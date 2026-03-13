# Replay System
# Save and replay games

from flask import Blueprint, request, jsonify

bp = Blueprint('replay', __name__, url_prefix='/api/replay')

# In-memory replay storage
replays = {}
replay_id_counter = 1


@bp.route('', methods=['POST'])
def save_replay():
    """Save a game replay"""
    global replay_id_counter
    
    data = request.get_json()
    
    game_type = data.get('game_type', 'rps')
    moves = data.get('moves', [])  # List of {player, move, result}
    winner = data.get('winner')
    players = data.get('players', ['Player1', 'Player2'])
    
    replay_id = replay_id_counter
    replay_id_counter += 1
    
    replays[replay_id] = {
        'id': replay_id,
        'game_type': game_type,
        'moves': moves,
        'winner': winner,
        'players': players,
        'move_count': len(moves)
    }
    
    return jsonify({
        'id': replay_id,
        'message': 'Replay saved!'
    }), 201


@bp.route('', methods=['GET'])
def list_replays():
    """List all replays"""
    limit = request.args.get('limit', 20, type=int)
    game_type = request.args.get('game_type')
    
    result = list(replays.values())
    
    if game_type:
        result = [r for r in result if r['game_type'] == game_type]
    
    # Sort by ID descending (newest first)
    result = sorted(result, key=lambda x: x['id'], reverse=True)[:limit]
    
    return jsonify([{
        'id': r['id'],
        'game_type': r['game_type'],
        'players': r['players'],
        'winner': r['winner'],
        'move_count': r['move_count']
    } for r in result])


@bp.route('/<int:replay_id>', methods=['GET'])
def get_replay(replay_id):
    """Get full replay"""
    replay = replays.get(replay_id)
    
    if not replay:
        return jsonify({'error': 'Replay not found'}), 404
    
    return jsonify(replay)


@bp.route('/<int:replay_id>/step/<int:step>', methods=['GET'])
def get_replay_step(replay_id, step):
    """Get replay state at specific step"""
    replay = replays.get(replay_id)
    
    if not replay:
        return jsonify({'error': 'Replay not found'}), 404
    
    if step < 0 or step > len(replay['moves']):
        return jsonify({'error': 'Invalid step'}), 400
    
    # Build state up to this step
    state = {
        'game_type': replay['game_type'],
        'players': replay['players'],
        'current_step': step,
        'total_steps': len(replay['moves']),
        'moves': replay['moves'][:step],
        'current_player': replay['players'][step % 2] if step < len(replay['moves']) else None
    }
    
    return jsonify(state)


@bp.route('/<int:replay_id>', methods=['DELETE'])
def delete_replay(replay_id):
    """Delete a replay"""
    if replay_id in replays:
        del replays[replay_id]
        return jsonify({'message': 'Replay deleted'})
    return jsonify({'error': 'Replay not found'}), 404
