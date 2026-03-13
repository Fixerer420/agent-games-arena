# Room/Lobby System
# Players can create rooms, invite others, and play together

from flask import Blueprint, request, jsonify
from app import db
import uuid
import secrets

bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')


@bp.route('', methods=['GET'])
def get_rooms():
    """Get all active rooms"""
    from app.models import Room
    rooms = Room.query.filter_by(status='waiting').all()
    return jsonify([{
        'id': r.id,
        'name': r.name,
        'player1': r.player1_name,
        'status': r.status,
        'game_type': r.game_type
    } for r in rooms])


@bp.route('', methods=['POST'])
def create_room():
    """Create a new room"""
    from app.models import Room
    
    data = request.get_json()
    name = data.get('name', 'Game Room')
    player_name = data.get('player_name', 'Player')
    game_type = data.get('game_type', 'rps')
    
    room = Room(
        id=str(uuid.uuid4())[:8],
        name=name,
        player1_name=player_name,
        game_type=game_type,
        status='waiting',
        room_code=secrets.token_hex(4)
    )
    
    db.session.add(room)
    db.session.commit()
    
    return jsonify({
        'id': room.id,
        'name': room.name,
        'player1': room.player1_name,
        'player2': None,
        'status': room.status,
        'game_type': room.game_type,
        'room_code': room.room_code
    }), 201


@bp.route('/<room_id>', methods=['GET'])
def get_room(room_id):
    """Get room details"""
    from app.models import Room
    
    room = Room.query.get_or_404(room_id)
    return jsonify({
        'id': room.id,
        'name': room.name,
        'player1': room.player1_name,
        'player2': room.player2_name,
        'status': room.status,
        'game_type': room.game_type,
        'room_code': room.room_code
    })


@bp.route('/<room_id>/join', methods=['POST'])
def join_room(room_id):
    """Join a room"""
    from app.models import Room
    
    data = request.get_json()
    player_name = data.get('player_name', 'Player')
    
    room = Room.query.get_or_404(room_id)
    
    if room.player2_name:
        return jsonify({'error': 'Room is full'}), 400
    
    room.player2_name = player_name
    room.status = 'ready'
    db.session.commit()
    
    return jsonify({
        'id': room.id,
        'name': room.name,
        'player1': room.player1_name,
        'player2': room.player2_name,
        'status': room.status,
        'game_type': room.game_type
    })


@bp.route('/<room_id>/leave', methods=['POST'])
def leave_room(room_id):
    """Leave a room"""
    from app.models import Room
    
    room = Room.query.get_or_404(room_id)
    room.status = 'closed'
    db.session.commit()
    
    return jsonify({'message': 'Left room'})


@bp.route('/code/<room_code>', methods=['GET'])
def get_room_by_code(room_code):
    """Find room by code"""
    from app.models import Room
    
    room = Room.query.filter_by(room_code=room_code, status='waiting').first()
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    
    return jsonify({
        'id': room.id,
        'name': room.name,
        'player1': room.player1_name,
        'status': room.status,
        'game_type': room.game_type
    })


@bp.route('/<room_id>/add-bot', methods=['POST'])
def add_bot_to_room(room_id):
    """Add an AI bot to a room"""
    from app.models import Room
    
    data = request.get_json()
    bot_type = data.get('bot_type', 'rulebot')  # rulebot, random, llm
    
    room = Room.query.get_or_404(room_id)
    
    if room.player2_name:
        return jsonify({'error': 'Room is full'}), 400
    
    # Add bot as player 2
    bot_names = {
        'rulebot': '🤖 RuleBot',
        'random': '🎲 RandomBot',
        'rock': '🪨 RockBot',
        'paper': '📄 PaperBot',
        'scissors': '✂️ ScissorsBot',
        'llm': '🧠 LLM Agent',
    }
    
    room.player2_name = bot_names.get(bot_type, '🤖 Bot')
    room.bot_type = bot_type
    room.status = 'ready'
    db.session.commit()
    
    return jsonify({
        'id': room.id,
        'player2': room.player2_name,
        'status': room.status,
        'bot_type': bot_type
    })


@bp.route('/<room_id>/play', methods=['POST'])
def play_room_turn(room_id):
    """Play a turn in a room game"""
    from app.models import Room
    from app.services.rule_agent import RuleBasedAgent
    
    data = request.get_json()
    player_move = data.get('move')
    
    room = Room.query.get_or_404(room_id)
    
    if not room.player2_name:
        return jsonify({'error': 'Waiting for opponent'}), 400
    
    # Get opponent move (bot or human)
    bot_type = getattr(room, 'bot_type', None)
    opponent_move = None
    
    if bot_type:
        # Bot opponent
        bot = RuleBasedAgent("Bot")
        state = {'round': getattr(room, 'round', 1)}
        if room.player1_move:
            state['player1_move'] = room.player1_move
        opponent_move = bot.decide_move(room.game_type, state)
    else:
        # Human opponent - they already played
        opponent_move = room.player2_move
    
    # Determine winner
    result = None
    winners = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    
    if player_move and opponent_move:
        if player_move == opponent_move:
            result = 'draw'
        elif winners.get(player_move) == opponent_move:
            result = 'win'
        else:
            result = 'lose'
    
    # Update room
    room.player1_move = player_move
    room.player2_move = opponent_move
    room.round = getattr(room, 'round', 1) + 1
    room.result = result
    
    db.session.commit()
    
    return jsonify({
        'player_move': player_move,
        'opponent_move': opponent_move,
        'result': result,
        'round': room.round,
        'is_bot': bool(bot_type)
    })
    
    if result:
        room.status = 'finished'
    
    db.session.commit()
    
    return jsonify({
        'player_move': player_move,
        'bot_move': bot_move,
        'result': result,
        'round': room.round,
        'status': room.status
    })


@bp.route('/<room_id>/messages', methods=['GET'])
def get_messages(room_id):
    """Get chat messages for a room"""
    from app.models import Room, RoomMessage
    
    room = Room.query.get_or_404(room_id)
    messages = RoomMessage.query.filter_by(room_id=room_id).order_by(RoomMessage.created_at).limit(50).all()
    
    return jsonify([{
        'id': m.id,
        'player': m.player_name,
        'message': m.message,
        'created_at': m.created_at.isoformat() if m.created_at else None
    } for m in messages])


@bp.route('/<room_id>/messages', methods=['POST'])
def add_message(room_id):
    """Add a chat message to a room"""
    from app.models import Room, RoomMessage
    
    data = request.get_json()
    player_name = data.get('player_name', 'Player')
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message required'}), 400
    
    msg = RoomMessage(
        room_id=room_id,
        player_name=player_name,
        message=message[:500]  # Limit message length
    )
    
    db.session.add(msg)
    db.session.commit()
    
    return jsonify({
        'id': msg.id,
        'player': msg.player_name,
        'message': msg.message,
        'created_at': msg.created_at.isoformat() if msg.created_at else None
    }), 201


@bp.route('/match', methods=['POST'])
def matchmake():
    """Find a random opponent or create a waiting entry"""
    from app.models import Room
    
    data = request.get_json()
    player_name = data.get('player_name', 'Player')
    game_type = data.get('game_type', 'rps')
    
    # Find a waiting room with same game type
    waiting_room = Room.query.filter_by(
        status='waiting',
        game_type=game_type
    ).first()
    
    if waiting_room:
        # Join existing room
        waiting_room.player2_name = player_name
        waiting_room.status = 'ready'
        db.session.commit()
        
        return jsonify({
            'found': True,
            'room': {
                'id': waiting_room.id,
                'name': waiting_room.name,
                'player1': waiting_room.player1_name,
                'player2': waiting_room.player2_name,
                'room_code': waiting_room.room_code,
                'game_type': waiting_room.game_type,
                'status': waiting_room.status
            }
        })
    
    # Create new waiting room
    room = Room(
        id=str(uuid.uuid4())[:8],
        name=f"{player_name} seeking game",
        player1_name=player_name,
        game_type=game_type,
        status='waiting',
        room_code=secrets.token_hex(4)
    )
    
    db.session.add(room)
    db.session.commit()
    
    return jsonify({
        'found': False,
        'room_id': room.id,
        'message': 'Looking for opponent...'
    })


@bp.route('/match/bot-join', methods=['POST'])
def bot_join_match():
    """AI bot joins matchmaking queue"""
    from app.models import Room
    
    data = request.get_json()
    bot_type = data.get('bot_type', 'rulebot')
    game_type = data.get('game_type', 'rps')
    
    bot_names = {
        'rulebot': '🤖 RuleBot',
        'random': '🎲 RandomBot',
        'rock': '🪨 RockBot',
        'paper': '📄 PaperBot',
        'scissors': '✂️ ScissorsBot',
        'llm': '🧠 LLM Agent',
    }
    
    # Find a waiting room
    waiting_room = Room.query.filter_by(
        status='waiting',
        game_type=game_type
    ).first()
    
    if waiting_room:
        waiting_room.player2_name = bot_names.get(bot_type, '🤖 Bot')
        waiting_room.bot_type = bot_type
        waiting_room.status = 'ready'
        db.session.commit()
        
        return jsonify({
            'found': True,
            'room': {
                'id': waiting_room.id,
                'name': waiting_room.name,
                'player1': waiting_room.player1_name,
                'player2': waiting_room.player2_name,
                'room_code': waiting_room.room_code,
                'game_type': waiting_room.game_type,
                'status': waiting_room.status,
                'bot_type': waiting_room.bot_type
            }
        })
    
    # Create waiting room with bot as player 1
    room = Room(
        id=str(uuid.uuid4())[:8],
        name=f"{bot_names.get(bot_type, '🤖 Bot')} seeking game",
        player1_name=bot_names.get(bot_type, '🤖 Bot'),
        bot_type=bot_type,
        game_type=game_type,
        status='waiting',
        room_code=secrets.token_hex(4)
    )
    
    db.session.add(room)
    db.session.commit()
    
    return jsonify({
        'found': False,
        'room_id': room.id,
        'message': 'Bot waiting for player...'
    })


@bp.route('/<room_id>/bot-chat', methods=['POST'])
def bot_chat(room_id):
    """Get bot chat message"""
    from app.models import Room
    import random
    
    room = Room.query.get_or_404(room_id)
    
    if not room.bot_type:
        return jsonify({'message': None})
    
    # Bot messages to encourage playing
    messages = [
        "Hey! Want to play? 🎮",
        "Ready when you are!",
        "Let's go! 🚀",
        "Waiting for you! ⏰",
        "My bots are tough! Want to try? 😈",
        "GG! Play again?",
        "You almost got me! Rematch?",
    ]
    
    bot_name = room.player1_name if room.bot_type else room.player2_name
    
    return jsonify({
        'bot_name': bot_name,
        'message': random.choice(messages)
    })


@bp.route('/stats', methods=['GET'])
def get_stats():
    """Get arena stats"""
    from app.models import Room, Agent
    
    total_rooms = Room.query.count()
    active_rooms = Room.query.filter_by(status='waiting').count()
    total_agents = Agent.query.count()
    
    return jsonify({
        'total_rooms': total_rooms,
        'active_rooms': active_rooms,
        'total_agents': total_agents
    })


@bp.route('/<room_id>/play-connect4', methods=['POST'])
def play_connect4(room_id):
    """Play Connect 4 move"""
    from app.models import Room
    
    data = request.get_json()
    col = data.get('column')  # 0-6
    
    room = Room.query.get_or_404(room_id)
    
    if not room.player2_name:
        return jsonify({'error': 'Waiting for opponent'}), 400
    
    if room.game_type != 'connect4':
        return jsonify({'error': 'Not a Connect 4 room'}), 400
    
    # Get current board
    board = getattr(room, 'board', None)
    if not board:
        board = [[None]*7 for _ in range(6)]
    else:
        import json
        board = json.loads(board)
    
    # Drop piece in column
    if col < 0 or col > 6:
        return jsonify({'error': 'Invalid column'}), 400
    
    # Find lowest empty row
    row = -1
    for r in range(5, -1, -1):
        if board[r][col] is None:
            row = r
            break
    
    if row == -1:
        return jsonify({'error': 'Column full'}), 400
    
    # Place piece
    player = getattr(room, 'round', 1) % 2 + 1
    board[row][col] = 'X' if player == 1 else 'O'
    
    # Check winner
    winner = check_connect4_winner(board, 'X' if player == 1 else 'O')
    
    # Save board
    room.board = json.dumps(board)
    room.round = getattr(room, round, 1) + 1
    
    if winner:
        room.status = 'finished'
        room.result = 'win' if player == 1 else 'lose'
    
    db.session.commit()
    
    return jsonify({
        'board': board,
        'column': col,
        'row': row,
        'player': 'X' if player == 1 else 'O',
        'winner': winner,
        'round': room.round
    })


def check_connect4_winner(board, symbol):
    """Check Connect 4 winner"""
    # Horizontal
    for r in range(6):
        for c in range(4):
            if all(board[r][c+i] == symbol for i in range(4)):
                return True
    # Vertical
    for r in range(3):
        for c in range(7):
            if all(board[r+i][c] == symbol for i in range(4)):
                return True
    # Diagonal
    for r in range(3):
        for c in range(4):
            if all(board[r+i][c+i] == symbol for i in range(4)):
                return True
    for r in range(3, 6):
        for c in range(4):
            if all(board[r-i][c+i] == symbol for i in range(4)):
                return True
    return False


@bp.route('/<room_id>/add-external', methods=['POST'])
def add_external_to_room(room_id):
    """Add an external agent to a room"""
    from app.models import Room
    
    data = request.get_json()
    external_agent_id = data.get('external_agent_id')
    
    room = Room.query.get_or_404(room_id)
    
    if room.player2_name:
        return jsonify({'error': 'Room is full'}), 400
    
    # Get external agent info
    from app.routes.external import bp as external_bp
    agents = getattr(external_bp, 'external_agents', {})
    agent = agents.get(external_agent_id)
    
    if not agent:
        return jsonify({'error': 'External agent not found'}), 404
    
    room.player2_name = f"🤖 {agent['name']}"
    room.external_agent_id = external_agent_id
    room.status = 'ready'
    db.session.commit()
    
    return jsonify({
        'id': room.id,
        'player2': room.player2_name,
        'status': room.status
    })
