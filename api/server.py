from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import sqlite3
import random
import os

app = Flask(__name__)
CORS(app)

# КОНФИГУРАЦИЯ С ВАШИМИ ДАННЫМИ
ADMIN_IDS = [6359121076]  # Ваш ID админа
BOT_TOKEN = "8133300846:AAFGk1qpvJR0OglStD6J4LbW3BIDU6EZGJU"

class BananaDatabase:
    def __init__(self, db_path='banana_casino.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_tables()
    
    def init_tables(self):
        c = self.conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (user_id INTEGER PRIMARY KEY,
                     username TEXT,
                     first_name TEXT,
                     bananas INTEGER DEFAULT 1000,
                     total_earned INTEGER DEFAULT 0,
                     total_wagered INTEGER DEFAULT 0,
                     games_played INTEGER DEFAULT 0,
                     level INTEGER DEFAULT 1,
                     daily_streak INTEGER DEFAULT 0,
                     last_daily TEXT,
                     registration_date TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER,
                     type TEXT,
                     amount INTEGER,
                     details TEXT,
                     timestamp TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS transfers
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     from_user_id INTEGER,
                     to_user_id INTEGER,
                     amount INTEGER,
                     timestamp TEXT)''')
        
        self.conn.commit()
    
    def get_user(self, user_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        return dict(result) if result else None
    
    def create_user(self, user_id, username="", first_name=""):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute('''INSERT OR IGNORE INTO users 
                    (user_id, username, first_name, bananas, registration_date) 
                    VALUES (?, ?, ?, ?, ?)''',
                 (user_id, username, first_name, 1000, now))
        self.conn.commit()
        return self.get_user(user_id)
    
    def get_balance(self, user_id):
        user = self.get_user(user_id) or self.create_user(user_id)
        return user['bananas']
    
    def update_balance(self, user_id, amount, transaction_type="", details=""):
        user = self.get_user(user_id) or self.create_user(user_id)
        new_balance = user['bananas'] + amount
        
        c = self.conn.cursor()
        c.execute("UPDATE users SET bananas = ? WHERE user_id = ?", (new_balance, user_id))
        
        c.execute('''INSERT INTO transactions 
                    (user_id, type, amount, details, timestamp) 
                    VALUES (?, ?, ?, ?, ?)''',
                 (user_id, transaction_type, amount, details, datetime.now().isoformat()))
        
        self.conn.commit()
        return new_balance
    
    def transfer_bananas(self, from_user_id, to_user_id, amount):
        fee_percent = 5
        fee = max(1, amount * fee_percent // 100)
        total_deduct = amount + fee
        
        from_balance = self.get_balance(from_user_id)
        if from_balance < total_deduct:
            return False, "Недостаточно бананов"
        
        self.update_balance(from_user_id, -total_deduct, "transfer_out", f"Перевод пользователю {to_user_id}")
        self.update_balance(to_user_id, amount, "transfer_in", f"Перевод от пользователя {from_user_id}")
        
        c = self.conn.cursor()
        c.execute('''INSERT INTO transfers 
                    (from_user_id, to_user_id, amount, timestamp) 
                    VALUES (?, ?, ?, ?)''',
                 (from_user_id, to_user_id, amount, datetime.now().isoformat()))
        
        self.conn.commit()
        return True, f"Перевод выполнен! Комиссия: {fee}🍌"
    
    def admin_add_bananas(self, admin_id, target_user_id, amount, reason=""):
        if amount <= 0:
            return False, "Сумма должна быть положительной"
        
        new_balance = self.update_balance(target_user_id, amount, "admin_add", reason)
        return True, f"Выдано {amount}🍌 пользователю {target_user_id}"

db = BananaDatabase()

@app.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

@app.route('/api/user/<int:user_id>')
def get_user(user_id):
    user = db.get_user(user_id) or db.create_user(user_id)
    return jsonify(user)

@app.route('/api/user/<int:user_id>/is-admin')
def check_admin(user_id):
    return jsonify({'is_admin': user_id in ADMIN_IDS})

@app.route('/api/transfer', methods=['POST'])
def transfer_bananas():
    data = request.json
    from_user_id = data.get('from_user_id')
    to_user_id = data.get('to_user_id')
    amount = data.get('amount')
    
    success, message = db.transfer_bananas(from_user_id, to_user_id, amount)
    return jsonify({'success': success, 'message': message})

@app.route('/api/admin/add-bananas', methods=['POST'])
def admin_add_bananas():
    data = request.json
    admin_id = data.get('admin_id')
    target_user_id = data.get('target_user_id')
    amount = data.get('amount')
    reason = data.get('reason', '')
    
    if admin_id not in ADMIN_IDS:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    success, message = db.admin_add_bananas(admin_id, target_user_id, amount, reason)
    return jsonify({'success': success, 'message': message})

@app.route('/api/game/slots', methods=['POST'])
def play_slots():
    data = request.json
    user_id = data.get('user_id')
    bet_amount = data.get('bet_amount', 10)
    
    balance = db.get_balance(user_id)
    if balance < bet_amount:
        return jsonify({'success': False, 'message': 'Недостаточно бананов'})
    
    symbols = ['🍌', '🎰', '💰', '🏆', '🎯', '⭐']
    result = [random.choice(symbols) for _ in range(3)]
    
    if result[0] == result[1] == result[2]:
        win_amount = bet_amount * 10
        result_type = 'jackpot'
    elif result[0] == result[1] or result[1] == result[2]:
        win_amount = bet_amount * 3
        result_type = 'win'
    else:
        win_amount = 0
        result_type = 'loss'
    
    if win_amount > 0:
        db.update_balance(user_id, win_amount - bet_amount, 'game_win', 'Слоты')
    else:
        db.update_balance(user_id, -bet_amount, 'game_loss', 'Слоты')
    
    return jsonify({
        'success': True,
        'result': result,
        'win_amount': win_amount,
        'result_type': result_type,
        'new_balance': db.get_balance(user_id)
    })

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('public', path)

if __name__ == '__main__':
    if not os.path.exists('public'):
        os.makedirs('public')
    app.run(host='0.0.0.0', port=5000, debug=True)
    
