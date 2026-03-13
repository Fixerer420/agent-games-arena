# Multiple AI Bots with different strategies

import random


class RuleBot:
    """Smart bot - tries to win, counters opponent"""
    name = "RuleBot"
    
    @staticmethod
    def get_move(game_type, state):
        if game_type == "rps":
            return RuleBot.rps_smart(state)
        elif game_type == "tictactoe":
            return RuleBot.tictactoe_smart(state)
        return random.choice(['rock', 'paper', 'scissors']) if game_type == 'rps' else '0'
    
    @staticmethod
    def rps_smart(state: dict) -> str:
        moves = ['rock', 'paper', 'scissors']
        last_round = state.get('round', 1)
        
        # Counter opponent's last move
        if last_round > 1:
            prev = state.get('player1_move')
            if prev == 'rock': return 'paper'
            elif prev == 'paper': return 'scissors'
            elif prev == 'scissors': return 'rock'
        
        return random.choice(moves)
    
    @staticmethod
    def tictactoe_smart(state: dict) -> str:
        board = state.get('board', [None] * 9)
        win_lines = [
            [0,1,2], [3,4,5], [6,7,8],
            [0,3,6], [1,4,7], [2,5,8],
            [0,4,8], [2,4,6]
        ]
        
        # Try to win
        for line in win_lines:
            symbols = [board[i] for i in line]
            if symbols.count('X') == 2 and None in symbols:
                return str([i for i in line if board[i] is None][0])
        
        # Block opponent
        for line in win_lines:
            symbols = [board[i] for i in line]
            if symbols.count('O') == 2 and None in symbols:
                return str([i for i in line if board[i] is None][0])
        
        # Take center
        if board[4] is None:
            return '4'
        
        # Take corners
        for c in [0, 2, 6, 8]:
            if board[c] is None:
                return str(c)
        
        # Any available
        for i in range(9):
            if board[i] is None:
                return str(i)
        return '0'


class RandomBot:
    """Completely random - unpredictable but not smart"""
    name = "RandomBot"
    
    @staticmethod
    def get_move(game_type, state):
        if game_type == "rps":
            return random.choice(['rock', 'paper', 'scissors'])
        elif game_type == "tictactoe":
            board = state.get('board', [None] * 9)
            empty = [i for i in range(9) if board[i] is None]
            return str(random.choice(empty)) if empty else '0'
        return 'rock' if game_type == 'rps' else '0'


class RockBot:
    """Always plays rock - easy to beat"""
    name = "RockBot"
    
    @staticmethod
    def get_move(game_type, state):
        return 'rock'


class PaperBot:
    """Always plays paper"""
    name = "PaperBot"
    
    @staticmethod
    def get_move(game_type, state):
        return 'paper'


class ScissorsBot:
    """Always plays scissors"""
    name = "ScissorsBot"
    
    @staticmethod
    def get_move(game_type, state):
        return 'scissors'


class CyclicBot:
    """Plays in sequence: rock -> paper -> scissors"""
    name = "CyclicBot"
    _counter = 0
    
    @staticmethod
    def get_move(game_type, state):
        if game_type == "rps":
            moves = ['rock', 'paper', 'scissors']
            move = moves[CyclicBot._counter % 3]
            CyclicBot._counter += 1
            return move
        return random.choice(['rock', 'paper', 'scissors'])


class CounterBot:
    """Always counters the most common move"""
    name = "CounterBot"
    _history = {'rock': 0, 'paper': 0, 'scissors': 0}
    
    @staticmethod
    def get_move(game_type, state):
        if game_type == "rps":
            # Track what opponent plays
            last = state.get('player1_move')
            if last:
                CounterBot._history[last] = CounterBot._history.get(last, 0) + 1
            
            # Play what beats the most common
            most_common = max(CounterBot._history, key=CounterBot._history.get)
            if most_common == 'rock': return 'paper'
            if most_common == 'paper': return 'scissors'
            return 'rock'
        return random.choice(['rock', 'paper', 'scissors'])


class DefensiveBot:
    """Prefers draws - plays to not lose"""
    name = "DefensiveBot"
    
    @staticmethod
    def get_move(game_type, state):
        if game_type == "rps":
            # Copy opponent's last move (draw)
            last = state.get('player1_move')
            if last:
                return last
            return 'rock'
        return random.choice(['rock', 'paper', 'scissors']) if game_type == 'rps' else '0'


class AggressiveBot:
    """Tries to win, takes risks"""
    name = "AggressiveBot"
    
    @staticmethod
    def get_move(game_type, state):
        if game_type == "rps":
            # Random but weighted toward winning moves
            return random.choice(['rock', 'rock', 'paper', 'scissors', 'scissors'])
        return random.choice(['rock', 'paper', 'scissors']) if game_type == 'rps' else '0'


# All available bots
BOTS = {
    'rulebot': RuleBot,
    'random': RandomBot,
    'rock': RockBot,
    'paper': PaperBot,
    'scissors': ScissorsBot,
    'cyclic': CyclicBot,
    'counter': CounterBot,
    'defensive': DefensiveBot,
    'aggressive': AggressiveBot,
}


class Connect4Bot:
    """Connect 4 AI - tries to win, blocks opponent"""
    name = "Connect4Bot"
    
    @staticmethod
    def get_move(game_type, state):
        if game_type != "connect4":
            return '0'
        
        board = state.get('board', [[None]*7 for _ in range(6)])
        
        # Try to win
        for col in range(7):
            if can_win(board, col, 'O'):
                return str(col)
        
        # Block opponent
        for col in range(7):
            if can_win(board, col, 'X'):
                return str(col)
        
        # Prefer center
        if board[0][3] is None:
            return '3'
        
        # Random valid
        for col in [2, 4, 1, 5, 0, 6]:
            if board[0][col] is None:
                return str(col)
        
        return '3'


def can_win(board, col, symbol):
    """Check if dropping in column wins"""
    temp = [row[:] for row in board]
    for r in range(5, -1, -1):
        if temp[r][col] is None:
            temp[r][col] = symbol
            if check4(temp, symbol):
                return True
            temp[r][col] = None
    return False


def check4(board, symbol):
    """Check 4 in a row"""
    for r in range(6):
        for c in range(7):
            if c+3 < 7 and all(board[r][c+i] == symbol for i in range(4)): return True
            if r+3 < 6 and all(board[r+i][c] == symbol for i in range(4)): return True
            if r+3 < 6 and c+3 < 7 and all(board[r+i][c+i] == symbol for i in range(4)): return True
            if r-3 >= 0 and c+3 < 7 and all(board[r-i][c+i] == symbol for i in range(4)): return True
    return False


BOTS['connect4'] = Connect4Bot
