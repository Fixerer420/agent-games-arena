# Rule-Based AI Agent
# Fast, CPU-only, instant decisions

import random
import json


class RuleBasedAgent:
    """Fast rule-based AI for games - no external calls needed"""
    
    def __init__(self, name: str = "RuleBot"):
        self.name = name
    
    def decide_move(self, game_type: str, state: dict) -> str:
        """Decide move based on game type"""
        
        if game_type == "rps":
            return self.rps_move(state)
        elif game_type == "tictactoe":
            return self.tictactoe_move(state)
        elif game_type == "connect4":
            return self.connect4_move(state)
        elif game_type == "numberguess":
            return self.numberguess_move(state)
        elif game_type == "memory":
            return self.memory_move(state)
        elif game_type == "mastermind":
            return self.mastermind_move(state)
        else:
            return self.random_move(state)
    
    def rps_move(self, state: dict) -> str:
        """Rock Paper Scissors - random but smart"""
        moves = ['rock', 'paper', 'scissors']
        
        # Get opponent's last move if available
        last_round = state.get('round', 1)
        if last_round > 1:
            prev = state.get('player1_move')
            if prev == 'rock':
                return 'paper'  # Counter rock
            elif prev == 'paper':
                return 'scissors'  # Counter paper
            elif prev == 'scissors':
                return 'rock'  # Counter scissors
        
        return random.choice(moves)
    
    def tictactoe_move(self, state: dict) -> str:
        """Tic-Tac-Toe - try to win, block opponent"""
        board = state.get('board', [None] * 9)
        
        # Check for winning move
        win_lines = [
            [0,1,2], [3,4,5], [6,7,8],  # rows
            [0,3,6], [1,4,7], [2,5,8],      # cols
            [0,4,8], [2,4,6]                # diagonals
        ]
        
        current = state.get('current_player', 1)
        my_symbol = 'X' if current == 1 else 'O'
        opp_symbol = 'O' if current == 1 else 'X'
        
        # 1. Try to win
        for line in win_lines:
            symbols = [board[i] for i in line]
            if symbols.count(my_symbol) == 2 and None in symbols:
                return str([i for i in line if board[i] is None][0])
        
        # 2. Block opponent win
        for line in win_lines:
            symbols = [board[i] for i in line]
            if symbols.count(opp_symbol) == 2 and None in symbols:
                return str([i for i in line if board[i] is None][0])
        
        # 3. Take center
        if board[4] is None:
            return '4'
        
        # 4. Take corners
        corners = [0, 2, 6, 8]
        available = [c for c in corners if board[c] is None]
        if available:
            return str(random.choice(available))
        
        # 5. Random available
        available = [i for i in range(9) if board[i] is None]
        return str(random.choice(available)) if available else '0'
    
    def connect4_move(self, state: dict) -> str:
        """Connect Four - basic strategy"""
        board = state.get('board', [])
        if not board:
            return '3'  # Start center
        
        current = state.get('current_player', 1)
        
        # Simple: try to win, block, then random
        available_cols = [c for c in range(7) if board[0][c] is None]
        
        if available_cols:
            return str(random.choice(available_cols))
        
        return '0'
    
    def numberguess_move(self, state: dict) -> str:
        """Number Guessing - binary search"""
        guesses_p1 = state.get('guesses_p1', [])
        
        if not guesses_p1:
            return '50'  # Start middle
        
        # Simple: guess around previous
        last = guesses_p1[-1] if guesses_p1 else 50
        result = state.get('results_p1', [])
        
        if result:
            if 'higher' in result[-1]:
                return str(min(100, last + 10))
            elif 'lower' in result[-1]:
                return str(max(1, last - 10))
        
        return str(random.randint(1, 100))
    
    def memory_move(self, state: dict) -> str:
        """Memory - just return first available"""
        cards = state.get('cards', [])
        flipped = state.get('flipped', [])
        
        if len(flipped) == 0:
            return '0'
        
        return str(len(cards) - 1)  # Just pick something
    
    def mastermind_move(self, state: dict) -> str:
        """Mastermind - random for now"""
        colors = ['🔴', '🟡', '🟢', '🔵', '🟣', '🟤']
        return ' '.join(random.sample(colors, 4))
    
    def random_move(self, state: dict) -> str:
        """Fallback random move"""
        return str(random.randint(0, 8))


# Default instance
rule_agent = RuleBasedAgent("RuleBot")
