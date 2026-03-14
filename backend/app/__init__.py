from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()

def create_app(config_name=None):
    """Application Factory Pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    app = Flask(__name__)
    
    # Load config
    from config import config
    app.config.from_object(config.get(config_name, config['default']))
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.routes import agents, games, leaderboard, ai, rule, ai_game, ai_battle, rooms, external, challenges, replay, crypto, lobby
    app.register_blueprint(agents.bp)
    app.register_blueprint(games.bp)
    app.register_blueprint(leaderboard.bp)
    app.register_blueprint(ai.bp)
    app.register_blueprint(rule.bp)
    app.register_blueprint(ai_game.bp)
    app.register_blueprint(ai_battle.bp)
    app.register_blueprint(rooms.bp)
    app.register_blueprint(external.bp)
    app.register_blueprint(challenges.bp)
    app.register_blueprint(replay.bp)
    app.register_blueprint(crypto.bp)
    app.register_blueprint(lobby.bp)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'config': config_name}
    
    # Root endpoint
    @app.route('/')
    def index():
        return {
            'name': 'Agent Games Arena API',
            'version': '1.0',
            'endpoints': {
                'health': '/health',
                'games': '/api/games',
                'agents': '/api/agents',
                'leaderboard': '/api/leaderboard'
            }
        }
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
