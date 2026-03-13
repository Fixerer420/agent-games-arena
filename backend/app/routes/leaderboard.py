from flask import Blueprint, jsonify
from app.models import Agent, Game
from datetime import datetime

bp = Blueprint('leaderboard', __name__, url_prefix='/api/leaderboard')

@bp.route('', methods=['GET'])
def get_overall_leaderboard():
    """Get overall leaderboard (all games)"""
    agents = Agent.query.order_by(Agent.elo.desc()).limit(20).all()
    return jsonify([
        {
            'rank': i + 1,
            **agent.to_dict()
        }
        for i, agent in enumerate(agents)
    ])

@bp.route('/<game_type>', methods=['GET'])
def get_game_leaderboard(game_type):
    """Get leaderboard for specific game type"""
    games = Game.query.filter_by(game_type=game_type, status='finished').all()
    
    # Calculate stats per agent for this game
    agent_stats = {}
    for game in games:
        for agent_id in [game.player1_id, game.player2_id]:
            if agent_id not in agent_stats:
                agent_stats[agent_id] = {'played': 0, 'won': 0, 'drawn': 0}
            agent_stats[agent_id]['played'] += 1
            
            if game.winner_id == agent_id:
                agent_stats[agent_id]['won'] += 1
            elif game.is_draw:
                agent_stats[agent_id]['drawn'] += 1
    
    # Get agent details and sort
    leaderboard = []
    for agent_id, stats in agent_stats.items():
        agent = Agent.query.get(agent_id)
        if agent:
            leaderboard.append({
                'agent': agent.to_dict(),
                'game_stats': stats,
                'win_rate': round(stats['won'] / stats['played'] * 100, 1) if stats['played'] > 0 else 0
            })
    
    leaderboard.sort(key=lambda x: x['game_stats']['won'], reverse=True)
    
    return jsonify([
        {**item, 'rank': i + 1}
        for i, item in enumerate(leaderboard)
    ])


@bp.route('/stats', methods=['GET'])
def get_leaderboard_stats():
    """Get arena statistics"""
    from app.models import Agent, Game
    
    agents = Agent.query.order_by(Agent.elo.desc()).limit(10).all()
    games_today = Game.query.filter(
        Game.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).count()
    
    return jsonify({
        'top_agents': [a.to_dict() for a in agents],
        'games_today': games_today
    })
