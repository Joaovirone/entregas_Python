from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "supersegredo"

# Config do banco (PostgreSQL container)
DATABASE_URL = "postgresql+psycopg2://admin:admin@db:5432/entregas_db"

engine = create_engine(DATABASE_URL)

# ============================================
# === LOGIN ==================================
# ============================================
@app.route('/login', methods=['GET', 'POST'])
def login_porteiro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with engine.connect() as conn:
            user = conn.execute(
                text('SELECT * FROM porteiros WHERE username = :username'),
                {'username': username}
            ).fetchone()

        if user and check_password_hash(user.senha_hash, password):
            session['user'] = user.username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('painel_porteiro'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')

    return render_template('login.html')


# ============================================
# === REGISTRO ===============================
# ============================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        senha_hash = generate_password_hash(password)

        try:
            with engine.connect() as conn:
                conn.execute(text('''
                    INSERT INTO porteiros (username, email, senha_hash)
                    VALUES (:username, :email, :senha_hash)
                '''), {'username': username, 'email': email, 'senha_hash': senha_hash})
                conn.commit()

            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect(url_for('login_porteiro'))

        except Exception as e:
            flash(f'Erro: usuário ou email já cadastrados. ({str(e)})', 'danger')

    return render_template('register.html')


# ============================================
# === ESQUECI A SENHA ========================
# ============================================
@app.route('/forgot', methods=['GET', 'POST'])
def forgot_pass():
    if request.method == 'POST':
        email = request.form['email']
        flash(f'Instruções enviadas para o email: {email}', 'info')
        return redirect(url_for('login_porteiro'))
    return render_template('forgot.html')


# ============================================
# === PAINEL (APÓS LOGIN) ====================
# ============================================
@app.route('/porteiro/')
def painel_porteiro():
    if 'user' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login_porteiro'))

    with engine.connect() as conn:
        entregas = conn.execute(text("""
            SELECT nome_entregador, morador, apartamento, bloco, data_hora, foto_url 
            FROM entregas ORDER BY id DESC
        """)).fetchall()

    return render_template('porteiro.html', entregas=entregas)


# ============================================
# === LOGOUT ================================
# ============================================
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('login_porteiro'))


# ============================================
# === ROTA PRINCIPAL ========================
# ============================================
@app.route('/')
def index():
    return redirect(url_for('login_porteiro'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
