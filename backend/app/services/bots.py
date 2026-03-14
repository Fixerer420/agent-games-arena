# Advanced AI Bots for Rock Paper Scissors
import random
import json


class Bot:
    """Base bot class"""
    def __init__(self, name):
        self.name = name
    
    def get_move(self, game_type, state):
        return random.choice(['rock', 'paper', 'scissors'])


class RandomBot(Bot):
    """Pure random - unpredictable but weak"""
    def __init__(self):
        super().__init__("RandomBot")


class RockBot(Bot):
    """Always plays rock"""
    def __init__(self):
        super().__init__("RockBot")
    
    def get_move(self, game_type, state):
        return 'rock'


class PaperBot(Bot):
    """Always plays paper"""
    def __init__(self):
        super().__init__("PaperBot")
    
    def get_move(self, game_type, state):
        return 'paper'


class ScissorsBot(Bot):
    """Always plays scissors"""
    def __init__(self):
        super().__init__("ScissorsBot")
    
    def get_move(self, game_type, state):
        return 'scissors'


class CyclicBot(Bot):
    """Cycles through rock -> paper -> scissors"""
    def __init__(self):
        super().__init__("CyclicBot")
        self.moves = ['rock', 'paper', 'scissors']
        self.index = 0
    
    def get_move(self, game_type, state):
        move = self.moves[self.index]
        self.index = (self.index + 1) % 3
        return move


class CounterBot(Bot):
    """Remembers what opponent played last and counters"""
    def __init__(self):
        super().__init__("CounterBot")
        self.last_opponent_move = None
        self.beats = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
    
    def get_move(self, game_type, state):
        if self.last_opponent_move:
            # Counter what they played
            return self.beats[self.last_opponent_move]
        
        # First move is random
        move = random.choice(['rock', 'paper', 'scissors'])
        if state and 'history' in state:
            # Get opponent's last move from history
            for h in reversed(state.get('history', [])):
                if 'opponent_move' in h:
                    self.last_opponent_move = h['opponent_move']
                    return self.beats[self.last_opponent_move]
        
        return move
    
    def update(self, my_move, opponent_move):
        self.last_opponent_move = opponent_move


class DefensiveBot(Bot):
    """Plays what beats the most common opponent move"""
    def __init__(self):
        super().__init__("DefensiveBot")
        self.opponent_moves = []
        self.beats = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
    
    def get_move(self, game_type, state):
        if len(self.opponent_moves) < 3:
            return random.choice(['rock', 'paper', 'scissors'])
        
        # Find most common
        most_common = max(set(self.opponent_moves), key=self.opponent_moves.count)
        return self.beats[most_common]
    
    def update(self, my_move, opponent_move):
        self.opponent_moves.append(opponent_move)


class AggressiveBot(Bot):
    """Tries to win, switches after loss"""
    def __init__(self):
        super().__init__("AggressiveBot")
        self.last_result = None
        self.wins = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    
    def get_move(self, game_type, state):
        if self.last_result == 'loss':
            # Switch it up after loss
            return random.choice(['rock', 'paper', 'scissors'])
        
        # Default to random
        return random.choice(['rock', 'paper', 'scissors'])
    
    def update(self, my_move, opponent_move):
        if self.wins.get(my_move) == opponent_move:
            self.last_result = 'win'
        elif my_move == opponent_move:
            self.last_result = 'draw'
        else:
            self.last_result = 'loss'


class MirrorBot(Bot):
    """Copies what opponent played last time"""
    def __init__(self):
        super().__init__("MirrorBot")
        self.last_opponent_move = None
    
    def get_move(self, game_type, state):
        if self.last_opponent_move:
            return self.last_opponent_move
        return random.choice(['rock', 'paper', 'scissors'])
    
    def update(self, my_move, opponent_move):
        self.last_opponent_move = opponent_move


class SmartBot(Bot):
    """Uses probability based on history"""
    def __init__(self):
        super().__init__("SmartBot")
        self.history = []
        self.beats = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
    
    def get_move(self, game_type, state):
        if len(self.history) < 5:
            return random.choice(['rock', 'paper', 'scissors'])
        
        # Analyze patterns
        opponent_moves = [h[1] for h in self.history[-10:]]
        
        # Find most common
        if opponent_moves:
            most_common = max(set(opponent_moves), key=opponent_moves.count)
            return self.beats[most_common]
        
        return random.choice(['rock', 'paper', 'scissors'])
    
    def update(self, my_move, opponent_move):
        self.history.append((my_move, opponent_move))


class GamblerBot(Bot):
    """Risky - sometimes makes unexpected moves"""
    def __init__(self):
        super().__init__("GamblerBot")
        self.beats = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
    
    def get_move(self, game_type, state):
        # 20% chance of random move
        if random.random() < 0.2:
            return random.choice(['rock', 'paper', 'scissors'])
        
        # 80% chance of rock
        return 'rock'


# Bot registry
BOTS = {
    'random': RandomBot(),
    'rock': RockBot(),
    'paper': PaperBot(),
    'scissors': ScissorsBot(),
    'cyclic': CyclicBot(),
    'counter': CounterBot(),
    'defensive': DefensiveBot(),
    'aggressive': AggressiveBot(),
    'mirror': MirrorBot(),
    'smart': SmartBot(),
    'gambler': GamblerBot(),
    'rulebot': RandomBot(),  # Alias
}
