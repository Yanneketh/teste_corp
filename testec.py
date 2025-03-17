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
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

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

# Rota para listar todos os celulares
@app.route("/celulares", methods=["GET"])
def get_celulares():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT ns, modelo, responsavel FROM CADASTRO")
            celulares = cursor.fetchall()
            if not celulares:
                return jsonify({"message": "Nenhum celular encontrado"}), 404
            return jsonify(celulares), 200
    except mysql.connector.Error as e:
        return jsonify({"error": f"Erro ao conectar ao banco de dados: {e}"}), 500

# Rota para adicionar um celular
@app.route("/celulares", methods=["POST"])
def add_celular():
    try:
        data = request.json
        ns = data.get("ns")
        modelo = data.get("modelo")
        responsavel = data.get("responsavel")

        if not ns or not modelo or not responsavel:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM CADASTRO WHERE ns = %s", (ns,))
            if cursor.fetchone():
                return jsonify({"error": "Número de série já cadastrado."}), 409
            cursor.execute("INSERT INTO CADASTRO (ns, modelo, responsavel) VALUES (%s, %s, %s)", (ns, modelo, responsavel))
            conn.commit()
            return jsonify({"message": "Celular cadastrado com sucesso"}), 201
    except mysql.connector.Error as e:
        return jsonify({"error": f"Erro ao conectar ao banco de dados: {e}"}), 500

# Rota para editar um celular
@app.route("/celulares/<ns>", methods=["PUT"])
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
        return jsonify({"error": f"Erro ao conectar ao banco de dados: {e}"}), 500

# Rota para excluir um celular
@app.route("/celulares/<ns>", methods=["DELETE"])
def delete_celular(ns):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM CADASTRO WHERE ns = %s", (ns,))
            conn.commit()
            if cursor.rowcount > 0:
                return jsonify({"message": "Celular removido com sucesso"}), 200
            return jsonify({"message": "Celular não encontrado"}), 404
    except mysql.connector.Error as e:
        return jsonify({"error": f"Erro ao conectar ao banco de dados: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)