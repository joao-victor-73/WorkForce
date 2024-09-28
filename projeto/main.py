from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy  # pip install flask-SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:darc147@localhost/workforce'
print('Banco de dados CONECTADO')

db = SQLAlchemy(app)  # Instanciando a aplicação para o SQLAlchemy


@app.route('/lista')
def lista_funcionario():
    return render_template('lista.html')


@app.route('/cadastro')
def cadastro_funcionario():
    return render_template('cadastro.html')


@app.route('/criando')
def criando():
    # Requisitando as informações do fórmulario:
    nome = request.form['nome_func']
    email = request.form['email']
    tel1 = request.form['tel1']
    tel2 = request.form['tel2']
    data_nascimento = request.form['birthdate']
    salario = request.form['salary']


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
