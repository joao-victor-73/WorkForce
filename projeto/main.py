from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy  # pip install flask-SQLAlchemy


app = Flask(__name__)
app.secret_key = 'random_key'

# Fazendo a conexão com o banco de dados através do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:darc147@localhost/workforce'
print('Banco de dados CONECTADO')

db = SQLAlchemy(app)  # Instanciando a aplicação para o SQLAlchemy


# Criando classe para as informações das tabelas

class Departamentos(db.Model):
    __tablename__ = 'departamentos'

    id_departamento = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    nome_departamento = db.Column(db.String(100))
    id_gerente = db.Column(db.Integer, unique=True)

    def __repr__(self):
        return '<Name %r>' % self.name


class Cargos(db.Model):
    __tablename__ = 'cargos'

    id_cargo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_cargo = db.Column(db.String(100))

    def __repr__(self):
        return '<Name %r>' % self.name


class Funcionarios(db.Model):
    __tablename__ = 'funcionarios'

    id_func = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_func = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100))
    tel1 = db.Column(db.String(15), nullable=False)
    tel2 = db.Column(db.String(15))
    data_contratacao = db.Column(db.Date, nullable=False)
    salario = db.Column(db.Numeric(10, 2), nullable=False)
    status_func = db.Column(
        db.Enum('EFETIVO', 'FERIAS', 'DEMITIDO', 'ATESTADO'))

    # Criando as foreign key da tabela
    fk_id_cargo = db.Column(db.Integer, db.ForeignKey(
        'cargos.id_cargo'), nullable=False)
    fk_id_departamento = db.Column(db.Integer, db.ForeignKey(
        'departamentos.id_departamento'), nullable=False)

    # Criando as relações entre as tabelas
    cargo = db.relationship('Cargos', backref='funcionarios')
    departamento = db.relationship('Departamentos', backref='funcionarios')

    def __repr__(self):
        return '<Name %r>' % self.name


class Folha_pagamento(db.Model):
    __tablename__ = 'folha_pagamento'

    id_pagamento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_pagamento = db.Column(db.Date, nullable=False)
    salario_base = db.Column(db.Numeric(10, 2), nullable=False)
    deducoes = db.Column(db.Numeric(10, 2), nullable=False)
    salario_liquido = db.Column(db.Numeric(10, 2), nullable=False)

    # Criando a Foreign Key da tabela
    fk_id_func = db.Column(db.Integer, db.ForeignKey(
        'funcionarios.id_func'), nullable=False)

    # Criando a relação da tabela 'folha_pagamento' com 'funcionarios'
    funcionario = db.relationship('Funcionarios', backref='folha_pagamentos')

    def __repr__(self):
        return '<Name %r>' % self.name

# OBS: o db.Numeric é o equivalente ao Decimal do SQL. Esse é o tipo correspondente no SQLAlchemy.


@app.route('/')
def index():
    return render_template('index.html', titulo="Página principal")


@app.route('/lista')
def lista_de_funcionarios():
    lista_func = Funcionarios.query.order_by(Funcionarios.id_func).all()
    return render_template('lista.html', lista_func=lista_func, titulo="Lista de Funcionários")


@app.route('/cadastro', methods=['POST', ])
def cadastro_funcionario():
    return render_template('cadastro.html')


# Essa rota, redireciona o usuário para o formulario de criação/cadastro
@app.route('/novo_funcionario')
def novo_funcionario():
    return render_template("cadastro.html", titulo="Cadastrar Funcionário")


# Essa rota coleta o que foi digitado no formulario e cria/cadastra o funcionário
@app.route('/criando_funcionario', methods=['POST',])
def criando_funcionario():
    # Requisitando as informações do fórmulario:
    nome = request.form['nome_func']
    email = request.form['email']
    tel1 = request.form['tel1']
    tel2 = request.form['tel2']
    data_contratacao = request.form['contratacao']
    salario = request.form['salary']

    # Aqui faremos uma consulta ao banco de dados utilizando o método 'query', para assim
    # tentarmos encontrar por meio do nome(nome_func), se já tem algum registro do funcionário
    # E o 'filter_by' vai servir para filtrar os registros onde o campo nome_func corresponde ao nome fornecido.
    # Caso o resultado disso tenha sido encontrado ou não um funcionario, ele será atribuido a váriavel 'funcionario'.

    funcionario = Funcionarios.query.filter_by(nome_func=nome).first()
    # OBS(29/09): remodelar o banco de dados para adicionar um campo de CPF, para assim facilitar
    #             a busca pelos registros de algum funcionário e a verificação ser melhor

    print("VERIFICANDO SE EXISTE FUNCIONÁRIO...")

    # Se a consulta, por acaso retornar um funcionário, ele entrará nesse bloco
    if funcionario:
        flash('Funcionário já está cadastrado!')
        return redirect(url_for('lista_de_funcionarios'))

    # Se não retornar nenhum funcionário na consulta:

    # Instânciando um funcionário, passando os valores do fórmulario como argumentos
    novo_funcionario = Funcionarios(nome_func=nome,
                                    email=email,
                                    tel1=tel1,
                                    tel2=tel2,
                                    data_contratacao=data_contratacao,
                                    salario=salario)

    print("ADICIONAND FUNCIONÁRIO NA TABELA")

    # Salvando o novo_funcionario no banco de dados
    # o objeto novo_funcionario é adicionado à sessão do banco de dados.
    db.session.add(novo_funcionario)
    # Aqui, as mudanças, que são a inserção de um novo registro, são confirmadas/comitadas.
    db.session.commit()

    print("REDIRECIONANDO PARA A LISTA DE FUNCIONÁRIOS")
    flash('Funcionário cadastrado com sucesso!')

    # Após a coleta das informações do formulario, a rota/função terá um retorno
    # de redirect para outra página, que é básicamente a página de lista de funcionários
    return redirect(url_for('lista_de_funcionarios'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
