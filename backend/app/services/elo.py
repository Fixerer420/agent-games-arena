# Improved Elo Rating System
# Standard Elo with K-factor

def calculate_elo(player_elo: int, opponent_elo: int, score: float, k: int = 32) -> int:
    """
    Calculate new Elo rating
    
    Args:
        player_elo: Current Elo rating
        opponent_elo: Opponent's Elo rating
        score: 1.0 for win, 0.5 for draw, 0.0 for loss
        k: K-factor (32 for new players, 16 for established)
    
    Returns:
        New Elo rating
    """
    expected_score = 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))
    new_elo = player_elo + k * (score - expected_score)
    return int(new_elo)


def update_elo(winner_elo: int, loser_elo: int, is_draw: bool = False) -> tuple:
    """
    Update Elo for both players after a game
    
    Returns:
        (winner_new_elo, loser_new_elo)
    """
    if is_draw:
        winner_new = calculate_elo(winner_elo, loser_elo, 0.5)
        loser_new = calculate_elo(loser_elo, winner_elo, 0.5)
    else:
        winner_new = calculate_elo(winner_elo, loser_elo, 1.0)
        loser_new = calculate_elo(loser_elo, winner_elo, 0.0)
    
    return winner_new, loser_new


# Example:
if __name__ == "__main__":
    # Test: 1200 vs 1000, win
    w, l = update_elo(1200, 1000, False)
    print(f"1200 vs 1000 (win): winner -> {w}, loser -> {l}")
    
    # Test: 1200 vs 1000, draw
    w, l = update_elo(1200, 1000, True)
    print(f"1200 vs 1000 (draw): winner -> {w}, loser -> {l}")
    
    # Test: 1000 vs 1200, win (upset)
    w, l = update_elo(1000, 1200, False)
    print(f"1000 vs 1200 (win/upset): winner -> {w}, loser -> {l}")
