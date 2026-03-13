# Crypto/Betting System
# Dogechain integration for bets and rewards

from flask import Blueprint, request, jsonify
import hashlib
import time

bp = Blueprint('crypto', __name__, url_prefix='/api/crypto')

# In-memory wallet storage (for demo - would need DB in production)
wallets = {}
bets = {}


@bp.route('/wallet/<address>', methods=['GET'])
def get_wallet(address):
    """Get wallet info"""
    wallet = wallets.get(address.lower())
    
    if not wallet:
        # Create new wallet
        wallet = {
            'address': address.lower(),
            'balance': 1000,  # Free starting credits
            'total_won': 0,
            'total_lost': 0,
            'transactions': []
        }
        wallets[address.lower()] = wallet
    
    return jsonify(wallet)


@bp.route('/wallet/<address>/transactions', methods=['GET'])
def get_transactions(address):
    """Get wallet transactions"""
    wallet = wallets.get(address.lower())
    
    if not wallet:
        return jsonify({'transactions': []})
    
    return jsonify(wallet['transactions'][-20:])


@bp.route('/bet', methods=['POST'])
def place_bet():
    """Place a bet on a game"""
    data = request.get_json()
    
    address = data.get('address', '').lower()
    amount = data.get('amount', 10)
    game_type = data.get('game_type', 'rps')
    bet_on = data.get('bet_on')  # 'win', 'lose', 'draw'
    match_id = data.get('match_id')
    
    if not address or amount <= 0:
        return jsonify({'error': 'Invalid address or amount'}), 400
    
    wallet = wallets.get(address)
    if not wallet or wallet['balance'] < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Deduct from balance
    wallet['balance'] -= amount
    
    # Create bet
    bet_id = hashlib.sha256(f"{address}{time.time()}".encode()).hexdigest()[:8]
    
    bets[bet_id] = {
        'id': bet_id,
        'address': address,
        'amount': amount,
        'game_type': game_type,
        'bet_on': bet_on,
        'match_id': match_id,
        'status': 'pending',
        'created_at': time.time()
    }
    
    # Record transaction
    wallet['transactions'].append({
        'type': 'bet',
        'amount': amount,
        'bet_id': bet_id,
        'timestamp': time.time()
    })
    
    return jsonify({
        'bet_id': bet_id,
        'amount': amount,
        'balance': wallet['balance'],
        'message': 'Bet placed!'
    }), 201


@bp.route('/bet/<bet_id>/resolve', methods=['POST'])
def resolve_bet(bet_id):
    """Resolve a bet (win/lose)"""
    data = request.get_json()
    result = data.get('result')  # 'win', 'lose', 'draw'
    
    bet = bets.get(bet_id)
    if not bet:
        return jsonify({'error': 'Bet not found'}), 404
    
    if bet['status'] != 'pending':
        return jsonify({'error': 'Bet already resolved'}), 400
    
    wallet = wallets.get(bet['address'])
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    # Check if bettor won
    won = False
    if (bet['bet_on'] == 'win' and result == 'win') or \
       (bet['bet_on'] == 'lose' and result == 'lose') or \
       (bet['bet_on'] == 'draw' and result == 'draw'):
        won = True
    
    if won:
        # Double the bet
        winnings = bet['amount'] * 2
        wallet['balance'] += winnings
        wallet['total_won'] += winnings
        bet['status'] = 'won'
        
        wallet['transactions'].append({
            'type': 'win',
            'amount': winnings,
            'bet_id': bet_id,
            'timestamp': time.time()
        })
    else:
        wallet['total_lost'] += bet['amount']
        bet['status'] = 'lost'
    
    return jsonify({
        'bet_id': bet_id,
        'status': bet['status'],
        'won': won,
        'balance': wallet['balance']
    })


@bp.route('/leaderboard', methods=['GET'])
def get_crypto_leaderboard():
    """Get richest wallets"""
    sorted_wallets = sorted(wallets.values(), key=lambda x: x['balance'], reverse=True)
    
    return jsonify([{
        'address': w['address'][:8] + '...' + w['address'][-4:],
        'balance': w['balance'],
        'total_won': w['total_won'],
        'total_lost': w['total_lost']
    } for w in sorted_wallets[:10]])


@bp.route('/faucet', methods=['POST'])
def get_free_coins():
    """Get free test coins"""
    data = request.get_json()
    address = data.get('address', '').lower()
    
    if not address:
        return jsonify({'error': 'Address required'}), 400
    
    wallet = wallets.get(address)
    if not wallet:
        wallet = {
            'address': address,
            'balance': 1000,
            'total_won': 0,
            'total_lost': 0,
            'transactions': []
        }
        wallets[address] = wallet
    
    # Give free coins every 24 hours (simplified)
    last_faucet = wallet.get('last_faucet', 0)
    if time.time() - last_faucet < 86400:  # 24 hours
        return jsonify({'error': 'Faucet only available every 24 hours'}), 400
    
    wallet['balance'] += 100
    wallet['last_faucet'] = time.time()
    
    wallet['transactions'].append({
        'type': 'faucet',
        'amount': 100,
        'timestamp': time.time()
    })
    
    return jsonify({
        'balance': wallet['balance'],
        'message': 'Got 100 free coins!'
    })
