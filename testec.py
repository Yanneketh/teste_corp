from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from contextlib import contextmanager

# Configurações do banco de dados
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "2020")
DB_NAME = os.getenv("DB_NAME", "corporativos")

app = Flask(__name__)
CORS(app)  # Configuração simplificada do CORS

# Função para conectar ao MySQL
@contextmanager
def get_db_connection():
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    try:
        yield conn
    finally:
        conn.close()

@app.route('/')
def home():
    return "API do Inventário de Celulares está online"

@app.route('/celulares', methods=['GET', 'OPTIONS'])  # Adicione OPTIONS aqui
def listar_celulares():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM CADASTRO")
            resultados = cursor.fetchall()
            return jsonify(resultados), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _build_cors_preflight_response():
    response = jsonify({"message": "Preflight request accepted"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)