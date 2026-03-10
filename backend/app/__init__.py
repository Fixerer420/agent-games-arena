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
    from app.routes import agents, games, leaderboard, ai
    app.register_blueprint(agents.bp)
    app.register_blueprint(games.bp)
    app.register_blueprint(leaderboard.bp)
    app.register_blueprint(ai.bp)
    
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
