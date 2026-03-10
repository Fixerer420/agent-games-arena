# Game Engines
# Each game implements: validate_move, get_winner, get_state

class RockPaperScissors:
    """Rock Paper Scissors Game Engine"""
    
    MOVES = ['rock', 'paper', 'scissors']
    WINNERS = {
        'rock': 'scissors',
        'paper': 'rock',
        'scissors': 'paper'
    }
    
    @staticmethod
    def validate_move(move):
        return move.lower() in RockPaperScissors.MOVES
    
    @staticmethod
    def get_winner(move1, move2):
        if move1 == move2:
            return None, True  # Draw
        
        if RockPaperScissors.WINNERS[move1] == move2:
            return 1, False  # Player 1 wins
        return 2, False  # Player 2 wins
    
    @staticmethod
    def get_initial_state():
        return {
            'moves': [],
            'player1_move': None,
            'player2_move': None,
            'round': 1
        }
    
    @staticmethod
    def make_move(state, player, move):
        if not RockPaperScissors.validate_move(move):
            return None, "Invalid move"
        
        state = json.loads(state) if isinstance(state, str) else state
        
        if player == 1 and state.get('player1_move') is None:
            state['player1_move'] = move
        elif player == 2 and state.get('player2_move') is None:
            state['player2_move'] = move
        else:
            return None, "Player already moved this round"
        
        state['moves'].append({'player': player, 'move': move})
        
        # Check if both moved
        if state.get('player1_move') and state.get('player2_move'):
            winner, is_draw = RockPaperScissors.get_winner(
                state['player1_move'], state['player2_move']
            )
            state['winner'] = winner
            state['is_draw'] = is_draw
            state['round_winner'] = winner
            state['round'] += 1
            # Reset for next round
            state['player1_move'] = None
            state['player2_move'] = None
        
        return state, None


class TicTacToe:
    """Tic-Tac-Toe Game Engine"""
    
    WIN_LINES = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
        [0, 4, 8], [2, 4, 6]               # diagonals
    ]
    
    @staticmethod
    def validate_move(state, position):
        state = json.loads(state) if isinstance(state, str) else state
        board = state.get('board', [None] * 9)
        if position < 0 or position > 8:
            return False
        if board[position] is not None:
            return False
        return True
    
    @staticmethod
    def get_winner(board):
        for line in TicTacToe.WIN_LINES:
            if board[line[0]] and board[line[0]] == board[line[1]] == board[line[2]]:
                return board[line[0]]  # 'X' or 'O'
        if None not in board:
            return 'draw'
        return None
    
    @staticmethod
    def get_initial_state():
        return {
            'board': [None] * 9,
            'current_player': 'X',
            'moves': []
        }
    
    @staticmethod
    def make_move(state, player, position):
        state = json.loads(state) if isinstance(state, str) else state
        
        if not TicTacToe.validate_move(json.dumps(state), position):
            return None, "Invalid move"
        
        symbol = 'X' if player == 1 else 'O'
        
        # Check if it's this player's turn
        if state['current_player'] != symbol:
            return None, "Not your turn"
        
        # Make move
        state['board'][position] = symbol
        state['moves'].append({'player': player, 'position': position})
        
        # Check for winner
        winner = TicTacToe.get_winner(state['board'])
        if winner:
            state['winner'] = winner
            state['game_over'] = True
        else:
            # Switch turns
            state['current_player'] = 'O' if symbol == 'X' else 'X'
        
        return state, None


# Game registry
GAMES = {
    'rps': RockPaperScissors,
    'tictactoe': TicTacToe
}

def get_game(game_type):
    return GAMES.get(game_type)
