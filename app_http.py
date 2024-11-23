from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3
from config import *
from database import init_db, get_humidity_history, get_settings
from utils import verify_password

app = Flask(__name__)
app.secret_key = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1])
    return None

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Проверяем наличие специального флага формы
        if request.form.get('login_attempt') == 'true':
            username = request.form['username']
            password = request.form['password']
            
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, username, password FROM users WHERE username = ?",
                    (username,))
            user = c.fetchone()
            conn.close()
            
            if user and verify_password(user[2], password):
                login_user(User(user[0], user[1]))
                return redirect(url_for('index'))
            flash('Неверный логин или пароль')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def settings():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if request.method == 'POST':
        max_humidity = float(request.form['max_humidity'])
        c.execute("UPDATE settings SET max_humidity = ? WHERE id = 1",
                 (max_humidity,))
        conn.commit()
    
    c.execute("SELECT max_humidity FROM settings WHERE id = 1")
    settings = c.fetchone()
    conn.close()
    
    if request.method == 'POST':
        return redirect(url_for('index'))
    return jsonify({'max_humidity': settings[0]})

@app.route('/api/current_humidity')
@login_required
def current_humidity():
    try:
        # Получаем последнюю запись из истории влажности
        history = get_humidity_history()
        max_humidity = get_settings()
        
        # Возвращаем последнюю запись (если есть)
        if history:
            last_record = history[-1]
            return jsonify({
                'timestamp': last_record['timestamp'],
                'humidity': last_record['humidity'],
                'fan_status': 'ON' if last_record['humidity'] > max_humidity else 'OFF'
            })
        else:
            return jsonify({'humidity': None, 'fan_status': 'OFF'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@app.route('/api/humidity_history')
@login_required
def humidity_history():
    history = get_humidity_history()
    return jsonify(history)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, use_reloader=False)  # use_reloader=False важно при использовании MQTT