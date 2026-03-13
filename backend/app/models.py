from app import db
from datetime import datetime
import uuid
import secrets

class Agent(db.Model):
    __tablename__ = 'agents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(64), unique=True, default=lambda: secrets.token_hex(32))
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Stats
    games_played = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    games_drawn = db.Column(db.Integer, default=0)
    elo = db.Column(db.Integer, default=1000)
    
    # Relationships
    games_as_player1 = db.relationship('Game', foreign_keys='Game.player1_id', backref='player1', lazy='dynamic')
    games_as_player2 = db.relationship('Game', foreign_keys='Game.player2_id', backref='player2', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'stats': {
                'games_played': self.games_played,
                'games_won': self.games_won,
                'games_drawn': self.games_drawn,
                'elo': self.elo,
                'win_rate': round(self.games_won / self.games_played * 100, 1) if self.games_played > 0 else 0
            }
        }


class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    game_type = db.Column(db.String(50), nullable=False)  # rps, tictactoe, etc.
    
    player1_id = db.Column(db.String(36), db.ForeignKey('agents.id'), nullable=False)
    player2_id = db.Column(db.String(36), db.ForeignKey('agents.id'))
    
    # Game state as JSON
    state = db.Column(db.Text, default='{}')
    
    status = db.Column(db.String(20), default='waiting')  # waiting, playing, finished
    winner_id = db.Column(db.String(36), db.ForeignKey('agents.id'))
    is_draw = db.Column(db.Boolean, default=False)
    
    current_turn = db.Column(db.Integer, default=1)  # 1 or 2
    
    moves = db.Column(db.Text, default='[]')  # JSON array of moves
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    finished_at = db.Column(db.DateTime)
    
    winner = db.relationship('Agent', foreign_keys=[winner_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'game_type': self.game_type,
            'player1': self.player1.to_dict() if self.player1 else None,
            'player2': self.player2.to_dict() if self.player2 else None,
            'state': self.state,
            'status': self.status,
            'winner': self.winner.to_dict() if self.winner else None,
            'is_draw': self.is_draw,
            'current_turn': self.current_turn,
            'moves': self.moves,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Room(db.Model):
    """Game room/lobby for multiplayer"""
    __tablename__ = 'rooms'
    
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    room_code = db.Column(db.String(8), unique=True, nullable=False)
    
    # Players
    player1_name = db.Column(db.String(100))
    player2_name = db.Column(db.String(100))
    bot_type = db.Column(db.String(20))  # rulebot, random, llm, etc.
    
    # Game
    game_type = db.Column(db.String(20), default='rps')
    player1_move = db.Column(db.String(20))
    player2_move = db.Column(db.String(20))
    round = db.Column(db.Integer, default=1)
    result = db.Column(db.String(20))  # win, lose, draw
    
    # Status
    status = db.Column(db.String(20), default='waiting')  # waiting, ready, playing, finished
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'room_code': self.room_code,
            'player1': self.player1_name,
            'player2': self.player2_name,
            'game_type': self.game_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class RoomMessage(db.Model):
    """Chat messages in rooms"""
    __tablename__ = 'room_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(8), db.ForeignKey('rooms.id'))
    player_name = db.Column(db.String(100))
    message = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
