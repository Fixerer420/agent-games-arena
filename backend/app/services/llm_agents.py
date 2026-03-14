# LLM-powered game agents
# Different personality prompts for each LLM

LLM_CONFIGS = {
    # Quick/cheap models
    'phi': {
        'model': 'phi',
        'description': 'Fast, small model'
    },
    'gemma:2b': {
        'model': 'gemma:2b', 
        'description': 'Google Gemma 2B'
    },
    'llama3.2': {
        'model': 'llama3.2:latest',
        'description': 'Meta Llama 3.2'
    },
    
    # Strategy prompts
    'strategist': {
        'model': 'llama3.2:latest',
        'system_prompt': '''You are a rock-paper-scissors strategist. 
Analyze patterns and try to predict opponent moves.
Think about what would beat their likely next move.
Respond with ONLY one word: rock, paper, or scissors.''',
        'temperature': 0.7
    },
    'randomizer': {
        'model': 'llama3.2:latest', 
        'system_prompt': '''You play rock-paper-scissors completely randomly.
Ignore any patterns, just pick randomly for maximum unpredictability.
Respond with ONLY one word: rock, paper, or scissors.''',
        'temperature': 1.0
    },
    'counter': {
        'model': 'llama3.2:latest',
        'system_prompt': '''You are a rock-paper-scissors counter-player.
Always play what beats whatever you played last time (if you played rock, play paper).
Never repeat the same move twice in a row.
Respond with ONLY one word: rock, paper, or scissors.''',
        'temperature': 0.3
    },
    'psychologist': {
        'model': 'llama3.2:latest',
        'system_prompt': '''You play rock-paper-scissors like a mind reader.
Try to predict what the opponent will play based on human psychology.
People often: play what would beat their last move, or get stuck in patterns.
Try to outsmart them!
Respond with ONLY one word: rock, paper, or scissors.''',
        'temperature': 0.8
    },
    'aggressive': {
        'model': 'llama3.2:latest',
        'system_prompt': '''You are an aggressive rock-paper-scissors player.
Prefer attacking moves. If unsure, lean toward scissors.
Play to win!
Respond with ONLY one word: rock, paper, or scissors.''',
        'temperature': 0.6
    },
    'defensive': {
        'model': 'llama3.2:latest',
        'system_prompt': '''You are a defensive rock-paper-scissors player.
Play it safe! Prefer paper (most common). 
Minimize losses over trying to win big.
Respond with ONLY one word: rock, paper, or scissors.''',
        'temperature': 0.4
    },
    'chaos': {
        'model': 'llama3.2:latest',
        'system_prompt': '''You play rock-paper-scissors CHAOTICALLY!
Make unpredictable choices. Sometimes follow patterns, sometimes break them.
Embrace maximum chaos!
Respond with ONLY one word: rock, paper, or scissors.''',
        'temperature': 1.5
    }
}


def get_llm_response(prompt, config):
    """Get response from LLM using the config"""
    import requests
    import json
    
    port = 11435  # Tunnel port
    
    try:
        response = requests.post(
            f'http://localhost:{port}/api/generate',
            json={
                'model': config.get('model', 'llama3.2:latest'),
                'prompt': prompt,
                'system': config.get('system_prompt', ''),
                'temperature': config.get('temperature', 0.7),
                'stream': False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip().lower()
    
    except Exception as e:
        print(f"LLM error: {e}")
    
    return None


def llm_move(bot_id, game_state):
    """Get LLM to make a move"""
    
    config = LLM_CONFIGS.get(bot_id, LLM_CONFIGS['strategist'])
    
    # Build prompt with game state
    history = game_state.get('history', [])
    prompt = f"Game state: {game_state}\nHistory: {history}\nWhat do you play?"
    
    response = get_llm_response(prompt, config)
    
    # Parse response
    if 'rock' in response:
        return 'rock'
    elif 'paper' in response:
        return 'paper'
    elif 'scissors' in response:
        return 'scissors'
    
    # Fallback
    import random
    return random.choice(['rock', 'paper', 'scissors'])
