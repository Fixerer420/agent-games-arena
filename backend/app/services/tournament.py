# Tournament System
# Single elimination bracket tournament

import random
from collections import defaultdict

class Tournament:
    """Run tournaments between bots"""
    
    def __init__(self, bot_ids, game_type='rps', num_games_per_match=5):
        self.bot_ids = bot_ids
        self.game_type = game_type
        self.num_games = num_games_per_match
        self.rounds = []
        self.winners = {}
        self.matches = []
    
    def run(self, battle_func):
        """Run the tournament
        
        battle_func(bot1_id, bot2_id) -> {'agent1': wins, 'agent2': wins, 'draw': draws}
        """
        bots = list(self.bot_ids)
        random.shuffle(bots)
        round_num = 1
        
        while len(bots) > 1:
            round_matches = []
            next_round = []
            
            # Pair up bots
            for i in range(0, len(bots), 2):
                if i + 1 < len(bots):
                    bot1 = bots[i]
                    bot2 = bots[i + 1]
                    
                    # Run match
                    result = battle_func(bot1, bot2)
                    winner = bot1 if result['agent1'] > result['agent2'] else bot2
                    
                    round_matches.append({
                        'bot1': bot1,
                        'bot2': bot2,
                        'score': f"{result['agent1']}-{result['draw']}-{result['agent2']}",
                        'winner': winner
                    })
                    
                    next_round.append(winner)
                    self.winners[winner] = self.winners.get(winner, 0) + 1
                else:
                    # Bye - automatically advance
                    next_round.append(bots[i])
            
            self.rounds.append({
                'round': round_num,
                'matches': round_matches
            })
            
            bots = next_round
            round_num += 1
        
        self.champion = bots[0] if bots else None
        return self.get_results()
    
    def get_results(self):
        """Get tournament results"""
        return {
            'champion': self.champion,
            'rounds': self.rounds,
            'total_wins': self.winners,
            'num_bots': len(self.bot_ids),
            'num_rounds': len(self.rounds)
        }


def run_tournament_bracket(bot_ids, battle_func, game_type='rps'):
    """Quick tournament runner"""
    t = Tournament(bot_ids, game_type)
    return t.run(battle_func)


if __name__ == '__main__':
    # Test
    def mock_battle(bot1, bot2):
        return {
            'agent1': random.randint(2, 5),
            'agent2': random.randint(2, 5),
            'draw': random.randint(0, 2)
        }
    
    bots = ['smart', 'random', 'cyclic', 'counter', 'mirror', 'defensive', 'aggressive', 'gambler']
    result = run_tournament_bracket(bots, mock_battle)
    print(f"Champion: {result['champion']}")
    print(f"Rounds: {result['num_rounds']}")
