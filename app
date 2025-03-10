from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    return f'Nome: {nome}, Email: {email}, Telefone: {telefone}'

if __name__ == '__main__':
    app.run(debug=True)
