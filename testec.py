from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import mysql.connector
import os
import re
from contextlib import contextmanager

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

# Função para conectar ao MySQL utilizando contexto
@contextmanager
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "inventario")
    )
    try:
        yield conn
    finally:
        conn.close()

# Função para validar o IMEI
def validar_imei(imei):
    return bool(re.match(r'^\d{15}$', imei))  # Verifica se o IMEI tem 15 dígitos numéricos

# Rota GET para o caminho raiz
@app.route("/", methods=["GET"])
def home():
    return "Bem-vindo ao inventário de celulares!"

# Rota GET para obter a lista de celulares
@app.route("/celulares", methods=["GET"])
def get_celulares():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM celulares")
            celulares = cursor.fetchall()
            response = make_response(jsonify(celulares))
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
    except mysql.connector.Error as e:
        return jsonify({"error": f"Erro ao conectar ao banco de dados: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota POST para adicionar um novo celular
@app.route("/celulares", methods=["POST"])
def add_celular():
    try:
        data = request.json
        imei = data.get("imei")
        modelo = data.get("modelo")
        marca = data.get("marca")
        
        # Validação dos dados de entrada
        if not imei or not modelo or not marca:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400
        if not validar_imei(imei):
            return jsonify({"error": "IMEI inválido. Deve ter 15 dígitos."}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO celulares (imei, modelo, marca) VALUES (%s, %s, %s)", (imei, modelo, marca))
            conn.commit()
            response = make_response(jsonify({"message": "Celular cadastrado com sucesso"}), 201)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
    except mysql.connector.Error as e:
        return jsonify({"error": f"Erro ao conectar ao banco de dados: {str(e)}"}), 