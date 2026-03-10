from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    CORS(app)
    db.init_app(app)
    
    from app.routes import agents, games, leaderboard
    app.register_blueprint(agents.bp)
    app.register_blueprint(games.bp)
    app.register_blueprint(leaderboard.bp)
    
    with app.app_context():
        db.create_all()
    
    return app
