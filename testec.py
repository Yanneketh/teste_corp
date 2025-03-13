from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import mysql.connector
import os
import re
from contextlib import contextmanager
<<<<<<< Updated upstream
from functools import wraps
import time
=======

# Verificar as variáveis de ambiente com valores padrão
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "2020")
DB_NAME = os.getenv("DB_NAME", "corporativos")

print("DB_HOST:", DB_HOST)
print("DB_USER:", DB_USER)
print("DB_PASSWORD:", DB_PASSWORD)
print("DB_NAME:", DB_NAME)
>>>>>>> Stashed changes

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Função para logar variáveis de ambiente
def log_env_variables():
    print("DB_HOST:", os.getenv("DB_HOST", "localhost"))
    print("DB_USER:", os.getenv("DB_USER", "root"))
    print("DB_PASSWORD:", os.getenv("DB_PASSWORD", "2020"))
    print("DB_NAME:", os.getenv("DB_NAME", "corporativos"))

# Decorador para tentar reconectar ao banco de dados
def retry_on_failure(max_retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except mysql.connector.Error as e:
                    print(f"Erro ao conectar ao banco de dados: {e}")
                    retries += 1
                    time.sleep(delay)
            return jsonify({"error": "Erro ao conectar ao banco de dados após várias tentativas"}), 500
        return wrapper
    return decorator

# Função para conectar ao MySQL utilizando contexto
@contextmanager
def get_db_connection():
    log_env_variables()
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

# Função para validar o IMEI
def validar_imei(imei):
    return bool(re.match(r'^\d{15}$', imei))

# Rota raiz
@app.route("/", methods=["GET"])
def home():
    return "Bem-vindo ao inventário de celulares!"

# Rota de verificação de saúde
@app.route("/health", methods=["GET"])
def health_check():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return jsonify({"status": "Conectado ao banco de dados"}), 200
    except mysql.connector.Error as e:
        return jsonify({"status": "Erro ao conectar ao banco de dados"}), 500

# Rota de status com HTML
@app.route("/status", methods=["GET"])
def status():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            status = "Conectado ao banco de dados"
    except mysql.connector.Error as e:
        status = "Erro ao conectar ao banco de dados"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Status da Conexão</title>
    </head>
    <body>
        <h1>Status da Conexão com o Banco de Dados</h1>
        <p>{status}</p>
    </body>
    </html>
    """
    return render_template_string(html)

# GET: Lista de celulares
@app.route("/celulares", methods=["GET"])
@retry_on_failure()
def get_celulares():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM celulares")
            celulares = cursor.fetchall()
<<<<<<< Updated upstream
            if not celulares:
                return jsonify({"message": "Nenhum celular encontrado"}), 404
            return jsonify(celulares), 200
=======
            response = make_response(jsonify(celulares))
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
>>>>>>> Stashed changes
    except mysql.connector.Error as e:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

# POST: Adicionar celular
@app.route("/celulares", methods=["POST"])
@retry_on_failure()
def add_celular():
    try:
        data = request.json
        imei = data.get("imei")
        modelo = data.get("modelo")
        marca = data.get("marca")
        
        if not imei or not modelo or not marca:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400
        if not validar_imei(imei):
            return jsonify({"error": "IMEI inválido. Deve ter 15 dígitos."}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM celulares WHERE imei = %s", (imei,))
            if cursor.fetchone():
                return jsonify({"error": "IMEI já cadastrado."}), 409
            cursor.execute("INSERT INTO celulares (imei, modelo, marca) VALUES (%s, %s, %s)", (imei, modelo, marca))
            conn.commit()
            return jsonify({"message": "Celular cadastrado com sucesso"}), 201
    except mysql.connector.Error as e:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

<<<<<<< Updated upstream
# PUT: Atualizar celular
@app.route("/celulares/<ns>", methods=["PUT"])
@retry_on_failure()
def update_celular(ns):
    try:
        data = request.json
        modelo = data.get("modelo")
        responsavel = data.get("responsavel")

        if not modelo or not responsavel:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE CADASTRO SET modelo = %s, responsavel = %s WHERE ns = %s", (modelo, responsavel, ns))
            conn.commit()
            if cursor.rowcount > 0:
                return jsonify({"message": "Celular atualizado com sucesso"}), 200
            return jsonify({"message": "Celular não encontrado"}), 404
    except mysql.connector.Error as e:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

# DELETE: Remover celular
@app.route("/celulares/<ns>", methods=["DELETE"])
@retry_on_failure()
=======
# Rota DELETE para remover um celular pelo número de série (ns)
@app.route("/CADASTRO/<ns>", methods=["DELETE"])
>>>>>>> Stashed changes
def delete_celular(ns):
    try:
        # Validação do número de série
        if not validar_ns(ns):
            return jsonify({"error": "Número de série inválido. Deve ser numérico."}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM CADASTRO WHERE ns = %s", (ns,))
            conn.commit()
            if cursor.rowcount > 0:
                return jsonify({"message": "Celular removido com sucesso"}), 200
            return jsonify({"message": "Celular não encontrado"}), 404
    except mysql.connector.Error as e:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

