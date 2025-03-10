from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import mysql.connector
import os
import re
from contextlib import contextmanager

# Verificar as variáveis de ambiente
print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_PASSWORD:", os.getenv("DB_PASSWORD"))
print("DB_NAME:", os.getenv("DB_NAME"))

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

# Função para conectar ao MySQL utilizando contexto
@contextmanager
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "2020"),
        database=os.getenv("DB_NAME", "corporativos")
    )
    try:
        yield conn
    finally:
        conn.close()

# Função para validar o número de série (ns)
def validar_ns(ns):
    return bool(re.match(r'^\d+$', ns))  # Verifica se o número de série é numérico

# Rota GET para o caminho raiz
@app.route("/", methods=["GET"])
def home():
    return "Bem-vindo ao inventário de celulares!"

# Rota GET para obter a lista de celulares
@app.route("/CADASTRO", methods=["GET"])
def get_celulares():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM CADASTRO")
            celulares = cursor.fetchall()
            response = make_response(jsonify(celulares))
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
    except mysql.connector.Error as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")
        return jsonify({"error": f"Erro ao conectar ao banco de dados: {str(e)}"}), 500
    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"error": str(e)}), 500)

# Rota POST para adicionar um novo celular
@app.route("/CADASTRO", methods=["POST"])
def add_celular():
    try:
        data = request.json
        ns = data.get("ns")
        modelo = data.get("modelo")
        responsavel = data.get("responsavel")
        
        # Validação dos dados de entrada
        if not ns or not modelo or not responsavel:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400
        if not validar_ns(ns):
            return jsonify({"error": "Número de série inválido. Deve ser numérico."}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO CADASTRO (ns, modelo, responsavel) VALUES (%s, %s, %s)", (ns, modelo, responsavel))
            conn.commit()
            response = make_response(jsonify({"message": "Celular cadastrado com sucesso"}), 201)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
    except mysql.connector.Error as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")
        return jsonify({"error": f"Erro ao conectar ao banco de dados: {str(e)}"}), 500
    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Rota DELETE para remover um celular pelo número de série (ns)
@app.route("/CADASTRO/<ns>", methods=["DELETE"])
def delete_celular(ns):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM CADASTRO WHERE ns = %s", (ns,))
            conn.commit()
            if cursor.rowcount > 0:
                response = make_response(jsonify({"message": f"Celular com número de série {ns} removido com sucesso!"}), 200)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
            return jsonify({"message": "Celular não encontrado"}), 404
    except mysql.connector.Error as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")
        return jsonify({"error": f"Erro ao conectar ao banco de dados: {str(e)}"}), 500
    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

