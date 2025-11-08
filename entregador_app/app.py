import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, text
import requests

app = Flask(__name__)

# Configuração do banco
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "admin123")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "entregas_db")

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

N8N_WEBHOOK_URL = "http://n8n:5678/webhook/entregas"

# Criação da tabela (caso não exista)
with engine.connect() as conn:
    conn.execute(text('''CREATE TABLE IF NOT EXISTS entregas (
        id SERIAL PRIMARY KEY,
        nome_entregador VARCHAR(100),
        morador VARCHAR(100),
        apartamento VARCHAR(20),
        bloco VARCHAR(10),
        data_hora VARCHAR(30),
        foto_url VARCHAR(255)
    )'''))
    conn.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        morador = request.form['morador']
        apartamento = request.form['apartamento']
        bloco = request.form['bloco']
        foto = request.files['foto']

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(f"{timestamp}_{foto.filename}")
        foto_path = os.path.join(UPLOAD_FOLDER, filename)
        foto.save(foto_path)

        foto_url = f"/static/uploads/{filename}"
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

        with engine.connect() as conn:
            conn.execute(text('''INSERT INTO entregas (nome_entregador, morador, apartamento, bloco, data_hora, foto_url)
                                 VALUES (:nome, :morador, :apartamento, :bloco, :data_hora, :foto_url)'''),
                         {"nome": nome, "morador": morador, "apartamento": apartamento, "bloco": bloco, "data_hora": data_hora, "foto_url": foto_url})
            conn.commit()

        try:
            requests.post(N8N_WEBHOOK_URL, json={
                "nome_entregador": nome,
                "morador": morador,
                "apartamento": apartamento,
                "bloco": bloco,
                "data_hora": data_hora,
                "foto_url": foto_url
            })
        except Exception as e:
            print(f"Erro ao enviar para n8n: {e}")

        return redirect(url_for('sucesso'))

    return render_template('index.html')

@app.route('/sucesso')
def sucesso():
    return render_template('sucesso.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
