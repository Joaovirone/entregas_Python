from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('entregas.db')
    c = conn.cursor()
    c.execute('''
            CREATE TABLE IF NOT EXISTS entregas (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              nome TEXT,
              apartamento TEXT,
              data_hora TEXT
            )
              ''')
    
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        apartamento = request.form['apartamento']
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

        conn = sqlite3.connect('entregas.db')
        c = conn.cursor()
        c.execute('INSERT INTO entregas (nome, apartamento, data_hora) VALUES (?, ?, ?)',
                  (nome, apartamento, data_hora))
        conn.commit()
        conn.close()

    return render_template('index.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)