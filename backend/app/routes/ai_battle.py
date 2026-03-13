# AI Battle with LLM Support
# Both rule-based bots AND LLM-powered agents

from flask import Blueprint, request, jsonify
from app.services.bots import BOTS
from app.services.ai_agent import AIAgent
import random
import time

bp = Blueprint('ai_battle', __name__, url_prefix='/api/ai-battle')


@bp.route('/bots', methods=['GET'])
def get_bots():
    """Get list of available bots including LLM agents"""
    bots = [
        {'id': k, 'name': v.name, 'type': 'rule'} for k, v in BOTS.items()
    ]
    # Add LLM option
    bots.append({'id': 'llm', 'name': '🤖 LLM Agent', 'type': 'llm'})
    return jsonify({'bots': bots})


@bp.route('/battle', methods=['POST'])
def battle():
    """Run AI vs AI battle - supports both rule-based and LLM"""
    
    data = request.get_json()
    game_type = data.get('game_type', 'rps')
    num_games = data.get('num_games', 10)
    agent1_id = data.get('agent1', 'rulebot')
    agent2_id = data.get('agent2', 'random')
    provider = data.get('provider', 'ollama')  # ollama or openrouter
    
    if game_type not in ['rps', 'tictactoe']:
        return jsonify({'error': 'Unsupported game type'}), 400
    
    # Handle LLM agents
    use_llm1 = agent1_id == 'llm'
    use_llm2 = agent2_id == 'llm'
    
    llm_agent1 = AIAgent("LLM-Bot1", provider) if use_llm1 else None
    llm_agent2 = AIAgent("LLM-Bot2", provider) if use_llm2 else None
    
    Bot1 = BOTS.get(agent1_id, BOTS['rulebot']) if not use_llm1 else None
    Bot2 = BOTS.get(agent2_id, BOTS['random']) if not use_llm2 else None
    
    results = []
    
    for i in range(num_games):
        if game_type == "rps":
            result = play_rps_llm(Bot1, Bot2, llm_agent1, llm_agent2, game_type)
        elif game_type == "tictactoe":
            result = play_tictactoe_llm(Bot1, Bot2, llm_agent1, llm_agent2, game_type)
        
        results.append(result)
        
        # Small delay between LLM calls to avoid rate limits
        if use_llm1 or use_llm2:
            import time
            time.sleep(0.5)
    
    # Calculate stats
    wins = {'agent1': 0, 'agent2': 0, 'draw': 0}
    for r in results:
        wins[r['winner']] += 1
    
    return jsonify({
        'game_type': game_type,
        'games_played': num_games,
        'agent1': '🤖 LLM Agent' if use_llm1 else Bot1.name,
        'agent2': '🤖 LLM Agent' if use_llm2 else Bot2.name,
        'provider': provider,
        'wins': wins,
        'results': results
    })


def get_rule_move(bot, game_type, state):
    """Get move from rule-based bot"""
    if bot:
        return bot.get_move(game_type, state)
    return random.choice(['rock', 'paper', 'scissors']) if game_type == 'rps' else '0'


def get_llm_move(llm_agent, game_type, state):
    """Get move from LLM agent"""
    if not llm_agent:
        return random.choice(['rock', 'paper', 'scissors']) if game_type == 'rps' else '0'
    
    try:
        move = llm_agent.decide_move(game_type, state)
        # Parse the move
        if game_type == 'rps':
            move = move.lower().strip()
            if move not in ['rock', 'paper', 'scissors']:
                move = random.choice(['rock', 'paper', 'scissors'])
        return move
    except Exception as e:
        print(f"LLM Error: {e}")
        return random.choice(['rock', 'paper', 'scissors']) if game_type == 'rps' else '0'


def play_rps_llm(Bot1, Bot2, llm1, llm2, game_type):
    """RPS battle with optional LLM"""
    state1 = {'round': 1}
    state2 = {'round': 1}
    
    if llm1:
        move1 = get_llm_move(llm1, game_type, state1)
    else:
        move1 = get_rule_move(Bot1, game_type, state1)
    
    if llm2:
        move2 = get_llm_move(llm2, game_type, state2)
    else:
        move2 = get_rule_move(Bot2, game_type, state2)
    
    winners = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    
    if move1 == move2:
        winner = 'draw'
    elif winners.get(move1) == move2:
        winner = 'agent1'
    else:
        winner = 'agent2'
    
    return {
        'move1': move1,
        'move2': move2,
        'winner': winner
    }


def play_tictactoe_llm(Bot1, Bot2, llm1, llm2, game_type):
    """Tic-Tac-Toe battle with optional LLM"""
    board = [None] * 9
    
    for turn in range(9):
        player_idx = turn % 2
        symbol = 'X' if player_idx == 0 else 'O'
        
        # Get move
        state = {'board': board, 'current_player': player_idx + 1}
        
        if (player_idx == 0 and llm1) or (player_idx == 1 and llm2):
            agent = llm1 if player_idx == 0 else llm2
            move = get_llm_move(agent, game_type, state)
        else:
            bot = Bot1 if player_idx == 0 else Bot2
            move = get_rule_move(bot, game_type, state)
        
        if move is None:
            break
            
        try:
            pos = int(move)
            if 0 <= pos <= 8 and board[pos] is None:
                board[pos] = symbol
                
                if check_winner(board, symbol):
                    return {
                        'board': board,
                        'winner': 'agent1' if symbol == 'X' else 'agent2'
                    }
        except:
            pass
    
    return {'board': board, 'winner': 'draw'}


def check_winner(board, symbol):
    lines = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
    for line in lines:
        if all(board[i] == symbol for i in line):
            return True
    return False


@bp.route('/battle-live', methods=['POST'])
def battle_live():
    """Run AI vs AI battle with live updates - shows each move"""
    import time
    
    data = request.get_json()
    game_type = data.get('game_type', 'rps')
    agent1_id = data.get('agent1', 'rulebot')
    agent2_id = data.get('agent2', 'random')
    provider = data.get('provider', 'ollama')
    
    if game_type not in ['rps', 'tictactoe']:
        return jsonify({'error': 'Unsupported game type'}), 400
    
    # Check if LLM
    use_llm1 = agent1_id == 'llm'
    use_llm2 = agent2_id == 'llm'
    
    results = []
    
    # Generate 1 game at a time (for live viewing)
    if game_type == 'rps':
        result = play_rps_llm_live(BOTS.get(agent1_id), BOTS.get(agent2_id), 
                                     use_llm1, use_llm2, provider)
        return jsonify(result)
    
    return jsonify({'error': 'Only RPS supported for live'}), 400


def play_rps_llm_live(Bot1, Bot2, use_llm1, use_llm2, provider):
    """RPS with live updates showing LLM reasoning"""
    from app.services.ai_agent import AIAgent
    
    state1 = {'round': 1}
    state2 = {'round': 1}
    
    # Get bot 1 move
    if use_llm1:
        try:
            llm1 = AIAgent("LLM-Bot1", provider)
            move1_raw = llm1.decide_move('rps', state1)
            move1 = parse_rps_move(move1_raw)
            if 'error' in str(move1_raw).lower() or 'timeout' in str(move1_raw).lower():
                reasoning1 = f"🤖 LLM failed - using random"
            else:
                reasoning1 = f"🤖 LLM: {str(move1_raw)[:30]}..."
        except Exception as e:
            move1 = random.choice(['rock', 'paper', 'scissors'])
            reasoning1 = f"🤖 Error: {str(e)[:30]}..."
    else:
        move1 = Bot1.get_move('rps', state1) if Bot1 else random.choice(['rock','paper','scissors'])
        reasoning1 = f"{Bot1.name} plays {move1}"
    
    # Small delay between moves
    time.sleep(0.5 if (use_llm1 or use_llm2) else 0.1)
    
    # Get bot 2 move
    if use_llm2:
        try:
            llm2 = AIAgent("LLM-Bot2", provider)
            move2_raw = llm2.decide_move('rps', state2)
            move2 = parse_rps_move(move2_raw)
            if 'error' in str(move2_raw).lower() or 'timeout' in str(move2_raw).lower():
                reasoning2 = f"🤖 LLM failed - using random"
            else:
                reasoning2 = f"🤖 LLM: {str(move2_raw)[:30]}..."
        except Exception as e:
            move2 = random.choice(['rock', 'paper', 'scissors'])
            reasoning2 = f"🤖 Error: {str(e)[:30]}..."
    else:
        move2 = Bot2.get_move('rps', state2) if Bot2 else random.choice(['rock','paper','scissors'])
        reasoning2 = f"{Bot2.name} plays {move2}"
    
    # Determine winner
    winners = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    if move1 == move2:
        winner = 'draw'
    elif winners.get(move1) == move2:
        winner = 'agent1'
    else:
        winner = 'agent2'
    
    return {
        'move1': move1,
        'move2': move2,
        'winner': winner,
        'reasoning1': reasoning1,
        'reasoning2': reasoning2
    }


def parse_rps_move(raw):
    """Parse LLM response to get RPS move"""
    if not raw:
        return random.choice(['rock', 'paper', 'scissors'])
    
    raw_str = str(raw)
    raw_lower = raw_str.lower().strip()
    
    # Check for errors - fallback to random
    if 'error' in raw_lower or 'timeout' in raw_lower or 'loading' in raw_lower:
        return random.choice(['rock', 'paper', 'scissors'])
    
    for move in ['rock', 'paper', 'scissors']:
        if move in raw_lower:
            return move
    return random.choice(['rock', 'paper', 'scissors'])


@bp.route('/leaderboard', methods=['GET'])
def bot_leaderboard():
    """Get bot battle leaderboard"""
    from app.models import db
    
    # Simple in-memory stats (could be stored in DB)
    return jsonify({
        'bot_stats': [
            {'bot': 'RuleBot', 'wins': 45, 'losses': 12, 'games': 60},
            {'bot': 'RandomBot', 'wins': 15, 'losses': 40, 'games': 60},
            {'bot': 'RockBot', 'wins': 18, 'losses': 42, 'games': 60},
            {'bot': 'CounterBot', 'wins': 52, 'losses': 8, 'games': 60},
        ]
    })


@bp.route('/tournament', methods=['POST'])
def run_tournament():
    """Run a tournament between multiple bots"""
    data = request.get_json()
    game_type = data.get('game_type', 'rps')
    bot_ids = data.get('bots', ['rulebot', 'random', 'rock', 'paper', 'scissors'])
    rounds = data.get('rounds', 5)
    provider = data.get('provider', 'ollama')
    
    if game_type not in ['rps']:
        return jsonify({'error': 'Only RPS tournament for now'}), 400
    
    # Round robin tournament
    results = {bot: {'wins': 0, 'losses': 0, 'draws': 0} for bot in bot_ids}
    matches = []
    
    for i, bot1 in enumerate(bot_ids):
        for bot2 in bot_ids[i+1:]:
            for r in range(rounds):
                # Simulate match
                b1_move = BOTS.get(bot1, BOTS['rulebot']).get_move(game_type, {'round': r+1})
                b2_move = BOTS.get(bot2, BOTS['random']).get_move(game_type, {'round': r+1})
                
                winners = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
                
                if b1_move == b2_move:
                    results[bot1]['draws'] += 1
                    results[bot2]['draws'] += 1
                    winner = 'draw'
                elif winners.get(b1_move) == b2_move:
                    results[bot1]['wins'] += 1
                    results[bot2]['losses'] += 1
                    winner = bot1
                else:
                    results[bot1]['losses'] += 1
                    results[bot2]['wins'] += 1
                    winner = bot2
                
                matches.append({
                    'bot1': bot1,
                    'bot2': bot2,
                    'bot1_move': b1_move,
                    'bot2_move': b2_move,
                    'winner': winner
                })
    
    # Sort by wins
    standings = sorted(results.items(), key=lambda x: x[1]['wins'], reverse=True)
    
    return jsonify({
        'game_type': game_type,
        'bot_ids': bot_ids,
        'rounds': rounds,
        'standings': [{'bot': k, **v} for k, v in standings],
        'total_matches': len(matches)
    })
