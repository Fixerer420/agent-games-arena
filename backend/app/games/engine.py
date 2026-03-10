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


class ConnectFour:
    """Connect Four Game Engine (7x6 board)"""
    
    ROWS = 6
    COLS = 7
    
    @staticmethod
    def validate_move(state, column):
        state = json.loads(state) if isinstance(state, str) else state
        board = state.get('board', [[None] * ConnectFour.COLS for _ in range(ConnectFour.ROWS)])
        if column < 0 or column >= ConnectFour.COLS:
            return False
        # Check if column is full
        if board[0][column] is not None:
            return False
        return True
    
    @staticmethod
    def get_winner(board):
        # Check horizontal
        for row in range(ConnectFour.ROWS):
            for col in range(ConnectFour.COLS - 3):
                if board[row][col] and board[row][col] == board[row][col+1] == board[row][col+2] == board[row][col+3]:
                    return board[row][col]
        
        # Check vertical
        for row in range(ConnectFour.ROWS - 3):
            for col in range(ConnectFour.COLS):
                if board[row][col] and board[row][col] == board[row+1][col] == board[row+2][col] == board[row+3][col]:
                    return board[row][col]
        
        # Check diagonal (down-right)
        for row in range(ConnectFour.ROWS - 3):
            for col in range(ConnectFour.COLS - 3):
                if board[row][col] and board[row][col] == board[row+1][col+1] == board[row+2][col+2] == board[row+3][col+3]:
                    return board[row][col]
        
        # Check diagonal (up-right)
        for row in range(3, ConnectFour.ROWS):
            for col in range(ConnectFour.COLS - 3):
                if board[row][col] and board[row][col] == board[row-1][col+1] == board[row-2][col+2] == board[row-3][col+3]:
                    return board[row][col]
        
        # Check for draw (board full)
        if all(board[0][col] is not None for col in range(ConnectFour.COLS)):
            return 'draw'
        
        return None
    
    @staticmethod
    def get_initial_state():
        return {
            'board': [[None] * ConnectFour.COLS for _ in range(ConnectFour.ROWS)],
            'current_player': 'X',
            'moves': []
        }
    
    @staticmethod
    def make_move(state, player, column):
        state = json.loads(state) if isinstance(state, str) else state
        
        if not ConnectFour.validate_move(json.dumps(state), column):
            return None, "Invalid move"
        
        symbol = 'X' if player == 1 else 'O'
        
        # Check if it's this player's turn
        if state['current_player'] != symbol:
            return None, "Not your turn"
        
        # Find lowest empty row in column
        board = state['board']
        for row in range(ConnectFour.ROWS - 1, -1, -1):
            if board[row][column] is None:
                board[row][column] = symbol
                state['moves'].append({'player': player, 'column': column, 'row': row})
                break
        
        # Check for winner
        winner = ConnectFour.get_winner(board)
        if winner:
            state['winner'] = winner
            state['game_over'] = True
        else:
            # Switch turns
            state['current_player'] = 'O' if symbol == 'X' else 'X'
        
        return state, None


class NumberGuessing:
    """Number Guessing Game - Agent vs Agent (best of 5 rounds)"""
    
    MIN = 1
    MAX = 100
    
    @staticmethod
    def get_initial_state():
        import random
        return {
            'target': random.randint(NumberGuessing.MIN, NumberGuessing.MAX),
            'guesses_p1': [],
            'guesses_p2': [],
            'results_p1': [],  # 'higher', 'lower', 'correct'
            'results_p2': [],
            'current_player': 1,
            'round': 1,
            'max_rounds': 5,
            'score_p1': 0,
            'score_p2': 0
        }
    
    @staticmethod
    def validate_move(state, guess):
        state = json.loads(state) if isinstance(state, str) else state
        try:
            guess = int(guess)
        except:
            return False
        return NumberGuessing.MIN <= guess <= NumberGuessing.MAX
    
    @staticmethod
    def make_move(state, player, guess):
        state = json.loads(state) if isinstance(state, str) else state
        
        if not NumberGuessing.validate_move(state, guess):
            return None, "Invalid move - must be 1-100"
        
        guess = int(guess)
        target = state['target']
        
        # Check if it's this player's turn
        if state['current_player'] != player:
            return None, "Not your turn"
        
        # Record guess
        if player == 1:
            state['guesses_p1'].append(guess)
            if guess == target:
                state['results_p1'].append('correct')
                state['score_p1'] += 1
            elif guess < target:
                state['results_p1'].append('higher')  # Guess was too low
            else:
                state['results_p1'].append('lower')  # Guess was too high
        else:
            state['guesses_p2'].append(guess)
            if guess == target:
                state['results_p2'].append('correct')
                state['score_p2'] += 1
            elif guess < target:
                state['results_p2'].append('higher')
            else:
                state['results_p2'].append('lower')
        
        # Check game end
        total_guesses = len(state['guesses_p1']) + len(state['guesses_p2'])
        if total_guesses >= state['max_rounds'] * 2 or state['score_p1'] > (state['max_rounds'] - state['round']) or state['score_p2'] > (state['max_rounds'] - state['round']):
            state['game_over'] = True
            if state['score_p1'] > state['score_p2']:
                state['winner'] = 1
            elif state['score_p2'] > state['score_p1']:
                state['winner'] = 2
            else:
                state['is_draw'] = True
        else:
            # Switch player
            if state['current_player'] == 1:
                state['current_player'] = 2
            else:
                state['current_player'] = 1
                state['round'] += 1
        
        return state, None


class MemoryGame:
    """Memory/Concentration Game - Find matching pairs"""
    
    PAIRS = 6  # 6 pairs = 12 cards
    
    @staticmethod
    def get_initial_state():
        import random
        # Create pairs of emojis
        emojis = ['🎮', '🎯', '🎨', '🎭', '🎪', '🎬']
        cards = emojis * 2
        random.shuffle(cards)
        
        return {
            'cards': cards,
            'flipped': [],  # Indices of flipped cards
            'matched': [],  # Indices of matched pairs
            'current_player': 1,
            'moves': [],
            'score_p1': 0,
            'score_p2': 0,
            'waiting_second': False,
            'first_card': None
        }
    
    @staticmethod
    def validate_move(state, card_index):
        state = json.loads(state) if isinstance(state, str) else state
        if card_index < 0 or card_index >= len(state['cards']):
            return False
        if card_index in state['flipped'] or card_index in state['matched']:
            return False
        return True
    
    @staticmethod
    def make_move(state, player, card_index):
        state = json.loads(state) if isinstance(state, str) else state
        
        if not MemoryGame.validate_move(state, card_index):
            return None, "Invalid move"
        
        # Flip the card
        state['flipped'].append(card_index)
        state['moves'].append({'player': player, 'card': card_index})
        
        if state.get('waiting_second'):
            # This is the second card flipped
            first_card = state['first_card']
            
            # Check for match
            if state['cards'][first_card] == state['cards'][card_index]:
                # Match!
                state['matched'].extend([first_card, card_index])
                if player == 1:
                    state['score_p1'] += 1
                else:
                    state['score_p2'] += 1
                
                state['waiting_second'] = False
                state['first_card'] = None
                
                # Check if game over
                if len(state['matched']) == len(state['cards']):
                    state['game_over'] = True
                    if state['score_p1'] > state['score_p2']:
                        state['winner'] = 1
                    elif state['score_p2'] > state['score_p1']:
                        state['winner'] = 2
                    else:
                        state['is_draw'] = True
            else:
                # No match - switch turns after delay (handled by frontend)
                state['current_player'] = 2 if player == 1 else 1
                state['waiting_second'] = False
                state['first_card'] = None
                # Flip back (frontend handles timing)
        else:
            # First card flipped
            state['first_card'] = card_index
            state['waiting_second'] = True
        
        return state, None


class Battleship:
    """Battleship Game - Sink the enemy fleet"""
    
    BOARD_SIZE = 10
    SHIPS = [5, 4, 3, 3, 2]  # Ship lengths
    
    @staticmethod
    def get_initial_state():
        import random
        
        def place_ships(board):
            ships = []
            for length in Battleship.SHIPS:
                placed = False
                while not placed:
                    horizontal = random.choice([True, False])
                    if horizontal:
                        row = random.randint(0, Battleship.BOARD_SIZE - 1)
                        col = random.randint(0, Battleship.BOARD_SIZE - length)
                        if all(board[row][col + i] is None for i in range(length)):
                            for i in range(length):
                                board[row][col + i] = 'ship'
                            ships.append({'row': row, 'col': col, 'length': length, 'horizontal': True})
                            placed = True
                    else:
                        row = random.randint(0, Battleship.BOARD_SIZE - length)
                        col = random.randint(0, Battleship.BOARD_SIZE - 1)
                        if all(board[row + i][col] is None for i in range(length)):
                            for i in range(length):
                                board[row + i][col] = 'ship'
                            ships.append({'row': row, 'col': col, 'length': length, 'horizontal': False})
                            placed = True
            return ships
        
        # Create empty boards
        p1_board = [[None] * Battleship.BOARD_SIZE for _ in range(Battleship.BOARD_SIZE)]
        p2_board = [[None] * Battleship.BOARD_SIZE for _ in range(Battleship.BOARD_SIZE)]
        
        p1_ships = place_ships([row[:] for row in p1_board])
        p2_ships = place_ships([row[:] for row in p2_board])
        
        return {
            'p1_board': p1_board,
            'p2_board': p2_board,
            'p1_ships': p1_ships,
            'p2_ships': p2_ships,
            'p1_hits': [[False] * Battleship.BOARD_SIZE for _ in range(Battleship.BOARD_SIZE)],
            'p2_hits': [[False] * Battleship.BOARD_SIZE for _ in range(Battleship.BOARD_SIZE)],
            'current_player': 1,
            'shots_p1': [],
            'shots_p2': [],
            'p1_ships_sunk': [],
            'p2_ships_sunk': [],
            'moves': []
        }
    
    @staticmethod
    def validate_move(state, move_data):
        state = json.loads(state) if isinstance(state, str) else state
        row = move_data.get('row')
        col = move_data.get('col')
        
        if row is None or col is None:
            return False
        if not (0 <= row < Battleship.BOARD_SIZE and 0 <= col < Battleship.BOARD_SIZE):
            return False
        
        # Check if already shot here
        shots = state['shots_p1'] if state['current_player'] == 1 else state['shots_p2']
        if [row, col] in shots:
            return False
        
        return True
    
    @staticmethod
    def make_move(state, player, move_data):
        state = json.loads(state) if isinstance(state, str) else state
        
        if not Battleship.validate_move(state, move_data):
            return None, "Invalid move"
        
        row = move_data['row']
        col = move_data['col']
        
        # Record shot
        if player == 1:
            state['shots_p1'].append([row, col])
        else:
            state['shots_p2'].append([row, col])
        
        state['moves'].append({'player': player, 'row': row, 'col': col})
        
        # Check hit/miss
        target_board = state['p2_board'] if player == 1 else state['p1_board']
        target_hits = state['p1_hits'] if player == 1 else state['p2_hits']
        target_ships = state['p2_ships'] if player == 1 else state['p1_ships']
        sunk_list = state['p2_ships_sunk'] if player == 1 else state['p1_ships_sunk']
        
        if target_board[row][col] == 'ship':
            target_hits[row][col] = True
            state['last_shot_result'] = 'hit'
            
            # Check if ship sunk
            for ship in target_ships:
                ship_hits = []
                if ship['horizontal']:
                    for i in range(ship['length']):
                        if target_hits[ship['row']][ship['col'] + i]:
                            ship_hits.append(True)
                else:
                    for i in range(ship['length']):
                        if target_hits[ship['row'] + i][ship['col']]:
                            ship_hits.append(True)
                
                if len(ship_hits) == ship['length'] and ship not in sunk_list:
                    sunk_list.append(ship)
                    state['last_shot_result'] = f'sunk_{ship["length"]}'
        else:
            state['last_shot_result'] = 'miss'
            # Switch turns on miss
            state['current_player'] = 2 if player == 1 else 1
        
        # Check win condition
        p1_total_hits = sum(sum(row) for row in state['p1_hits'])
        p2_total_hits = sum(sum(row) for row in state['p2_hits'])
        
        total_ship_cells = sum(Battleship.SHIPS)
        
        if p1_total_hits == total_ship_cells:
            state['game_over'] = True
            state['winner'] = 1
        elif p2_total_hits == total_ship_cells:
            state['game_over'] = True
            state['winner'] = 2
        
        return state, None


class Mastermind:
    """Mastermind Code Breaking Game"""
    
    COLORS = ['🔴', '🟡', '🟢', '🔵', '🟣', '🟤']
    CODE_LENGTH = 4
    MAX_GUESSES = 10
    
    @staticmethod
    def get_initial_state():
        import random
        # Generate secret code
        code = [random.choice(Mastermind.COLORS) for _ in range(Mastermind.CODE_LENGTH)]
        
        return {
            'secret_code': code,
            'guesses_p1': [],
            'guesses_p2': [],
            'results_p1': [],
            'results_p2': [],
            'current_player': 1,
            'round': 1,
            'max_rounds': Mastermind.MAX_GUESSES
        }
    
    @staticmethod
    def validate_move(state, guess):
        state = json.loads(state) if isinstance(state, str) else state
        if not isinstance(guess, list) or len(guess) != Mastermind.CODE_LENGTH:
            return False
        for color in guess:
            if color not in Mastermind.COLORS:
                return False
        return True
    
    @staticmethod
    def check_guess(secret, guess):
        """Returns (exact_matches, color_matches)"""
        exact = sum(s == g for s, g in zip(secret, guess))
        
        # Count color matches (not exact positions)
        secret_counts = {}
        guess_counts = {}
        
        for c in secret:
            secret_counts[c] = secret_counts.get(c, 0) + 1
        for c in guess:
            guess_counts[c] = guess_counts.get(c, 0) + 1
        
        color_matches = 0
        for color in guess_counts:
            if color in secret_counts:
                color_matches += min(secret_counts[color], guess_counts[color])
        
        color_matches -= exact  # Remove exact matches
        return exact, color_matches
    
    @staticmethod
    def make_move(state, player, guess):
        state = json.loads(state) if isinstance(state, str) else state
        
        if not Mastermind.validate_move(state, guess):
            return None, "Invalid guess - must be 4 colors"
        
        secret = state['secret_code']
        exact, color_matches = Mastermind.check_guess(secret, guess)
        
        result = {
            'exact': exact,
            'color': color_matches,
            'black': exact,  # Standard Mastermind: black = exact, white = color
            'white': color_matches
        }
        
        if player == 1:
            state['guesses_p1'].append(guess)
            state['results_p1'].append(result)
        else:
            state['guesses_p2'].append(guess)
            state['results_p2'].append(result)
        
        # Check win
        if exact == Mastermind.CODE_LENGTH:
            state['game_over'] = True
            state['winner'] = player
        else:
            # Switch turns
            total_guesses = len(state['guesses_p1']) + len(state['guesses_p2'])
            if total_guesses >= Mastermind.MAX_GUESSES:
                state['game_over'] = True
                # No winner - code remains secret
            else:
                state['current_player'] = 2 if player == 1 else 1
                state['round'] += 1
        
        return state, None


# Game registry
GAMES = {
    'rps': RockPaperScissors,
    'tictactoe': TicTacToe,
    'connect4': ConnectFour,
    'numberguess': NumberGuessing,
    'memory': MemoryGame,
    'battleship': Battleship,
    'mastermind': Mastermind
}

def get_game(game_type):
    return GAMES.get(game_type)
