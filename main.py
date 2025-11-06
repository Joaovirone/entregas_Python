import os
from flask import Flask, render_template, request
import requests
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Caminho absoluto da pasta do projeto (onde está o app.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho para uploads dentro do projeto
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Cria se não existir

# Webhook do n8n
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/entregas"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        cliente = request.form['cliente']
        apartamento = request.form['apartamento']
        bloco = request.form['bloco']
        foto = request.files['foto']

        # Garante nome de arquivo seguro e único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(f"{timestamp}_{foto.filename}")
        foto_path = os.path.join(UPLOAD_FOLDER, filename)
        foto.save(foto_path)

        # URL acessível pelo Flask
        foto_url = f"/static/uploads/{filename}"

        payload = {
            "nome_entregador": nome,
            "cliente": cliente,
            "apartamento": apartamento,
            "bloco": bloco,
            "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "foto_url": foto_url
        }

        try:
            response = requests.post(N8N_WEBHOOK_URL, json=payload)
            if response.status_code == 200:
                return f"✅ Entrega registrada com sucesso!"
            else:
                return f"⚠️ Erro: {response.status_code} - {response.text}"
        except Exception as e:
            return f"❌ Falha ao conectar ao n8n: {e}"

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
