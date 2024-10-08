from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy  # pip install flask-SQLAlchemy
import enum


app = Flask(__name__)
app.secret_key = 'random_key'

# Fazendo a conexão com o banco de dados através do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:darc147@localhost/workforce'
print('Banco de dados CONECTADO')

db = SQLAlchemy(app)  # Instanciando a aplicação para o SQLAlchemy


# Criando classe para as informações das tabelas

# Enumeração para o status do funcionário
class StatusFunc(enum.Enum):
    EFETIVO = "EFETIVO"
    FERIAS = "FERIAS"
    DEMITIDO = "DEMITIDO"
    ATESTADO = "ATESTADO"


class Pessoas(db.Model):
    __tablename__ = 'pessoas'

    id_pessoa = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    data_nascimento = db.Column(db.Date)
    tel1 = db.Column(db.String(20))
    tel2 = db.Column(db.String(20))
    endereco = db.Column(db.String(100))
    cidade = db.Column(db.String(30))

    def __repr__(self):
        return f"<Funcionarios id: {self.id_func}, nome: {self.pessoa.nome}>"


class Departamentos(db.Model):
    __tablename__ = 'departamentos'

    id_departamento = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    nome_departamento = db.Column(db.String(100), nullable=False)
    nome_supervisor = db.Column(db.String(100))

    def __repr__(self):
        return '<Name %r>' % self.name


class Funcionarios(db.Model):
    __tablename__ = 'funcionarios'

    id_func = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100))
    data_contratacao = db.Column(db.Date, nullable=False)
    salario = db.Column(db.Numeric(10, 2), nullable=False)
    nome_cargo = db.Column(db.String(100))
    status_func = db.Column(db.Enum(StatusFunc),
                            nullable=False, default=StatusFunc.EFETIVO)
    # Criando as foreign key da tabela
    fk_id_departamento = db.Column(db.Integer, db.ForeignKey(
        'departamentos.id_departamento', ondelete='SET NULL', onupdate='CASCADE'))

    fk_id_pessoa = db.Column(db.Integer, db.ForeignKey(
        'pessoas.id_pessoa', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    # Criando as relações entre as tabelas
    pessoa = db.relationship('Pessoas', backref='funcionarios')
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
        'funcionarios.id_func', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

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
    # lista_func = Funcionarios.query.order_by(Funcionarios.id_func).all()

    # Consulta para obter todos os funcionários com seus departamentos
    lista_func = db.session.query(
        Funcionarios,
        Departamentos.nome_departamento
    ).outerjoin(Departamentos, Funcionarios.fk_id_departamento == Departamentos.id_departamento).all()

    for funcionario, departamento in lista_func:
        print(f"Funcionário: {
              funcionario.pessoa.nome}, Departamento: {departamento}")

    return render_template('lista.html', lista_func=lista_func, titulo="Lista de Funcionários")


@app.route('/cadastro', methods=['POST', ])
def cadastro_funcionario():
    return render_template('lista.html')


# Essa rota, redireciona o usuário para o formulario de criação/cadastro
@app.route('/novo_funcionario')
def novo_funcionario():
    # Passando a lista de departamentos para ter opção na hora docadastramento
    lista_departamentos = Departamentos.query.all()

    return render_template("cadastro.html", titulo="Cadastrar Funcionário", departamentos=lista_departamentos)


# Essa rota coleta o que foi digitado no formulario e cria/cadastra o funcionário
@app.route('/criando_funcionario', methods=['POST',])
def criando_funcionario():
    # Requisitando as informações PESSOAIS:
    nome = request.form['nome']
    cpf = request.form['cpf']
    data_nascimento = request.form['data_nascimento']
    tel1 = request.form['tel1']
    tel2 = request.form['tel2']
    endereco = request.form['endereco']
    cidade = request.form['cidade']

    # Requisitando as INFORMAÇÕES DO EMPREGO:
    email = request.form['email']
    data_contratacao = request.form['data_contratacao']
    salario = request.form['salario']
    cargo = request.form['cargo']

    # Usando o ID do departamento diretamente do formulário
    fk_id_departamento = request.form['departamento']  # Aqui você pega o ID

    status = request.form['status']
    status_enum = StatusFunc[status]  # convertendo a string para o Enum

    # Aqui faremos uma consulta ao banco de dados utilizando o método 'query', para assim
    # tentarmos encontrar por meio do cpf se já tem algum registro de pessoa.
    # E o 'filter_by' vai servir para filtrar os registros onde o campo cpf corresponde ao cpf fornecido.
    # Caso o resultado disso tenha sido encontrado ou não um cpf já existente, ele será atribuido a váriavel 'funcionario'.

    pessoa = Pessoas.query.filter_by(cpf=cpf).first()

    print("VERIFICANDO SE EXISTE A PESSOA...")

    # Se a consulta, por acaso retornar um cpf cadastrado, ele entrará nesse bloco
    # Pensar em como lidar caso seja encontrado alguma pessoa já cadastrada. (método temporário abaixo)
    if pessoa:
        flash('Pessoa já está cadastrado! Redirecionando para a lista de funcionários')
        return redirect(url_for('lista_de_funcionarios'))

    # Se não retornar nenhum funcionário na consulta:

    # Instânciando um funcionário, passando os valores do fórmulario como argumentos
    nova_pessoa = Pessoas(nome=nome,
                          cpf=cpf,
                          data_nascimento=data_nascimento,
                          tel1=tel1,
                          tel2=tel2,
                          endereco=endereco,
                          cidade=cidade)

    print("ADICIONAND PESSOA NA TABELA")
    # Adicionando a nova pessoa ao banco
    db.session.add(nova_pessoa)
    db.session.commit()

    # Buscando o departamento
    departamento_obj = Departamentos.query.filter_by(
        id_departamento=fk_id_departamento).first()

    # Pensar em como lidar caso não seja encontrado alguma departamento. (método temporário abaixo)
    if not departamento_obj:
        # Se o departamento não for encontrado, devemos reverter a inserção da nova pessoa
        db.session.delete(nova_pessoa)  # Remove a nova pessoa
        db.session.commit()  # Comita a exclusão
        flash("Departamento não encontrado! Cadastro do funcionário não foi realizado.")
        return redirect(url_for('lista_de_funcionarios'))

    # Criando um novo funcionário com as informações da Pessoa recém-criada
    novo_funcionario = Funcionarios(fk_id_pessoa=nova_pessoa.id_pessoa,
                                    email=email,
                                    data_contratacao=data_contratacao,
                                    salario=salario,
                                    nome_cargo=cargo,
                                    status_func=status_enum,
                                    fk_id_departamento=departamento_obj.id_departamento)

    # Salvando o novo_funcionario no banco de dados
    # o objeto novo_funcionario é adicionado à sessão do banco de dados.
    db.session.add(novo_funcionario)
    # Aqui, as mudanças, que são a inserção de um novo registro, são confirmadas/comitadas.
    db.session.commit()

    flash('Funcionário cadastrado com sucesso!')
    print("REDIRECIONANDO PARA A LISTA DE FUNCIONÁRIOS")

    # Após a coleta das informações do formulario, a rota/função terá um retorno
    # de redirect para outra página, que é básicamente a página de lista de funcionários
    return redirect(url_for('lista_de_funcionarios'))


@app.route('/editar_informacoes/<int:id_func>')
def editar_informacoes(id_func):
    # funcionario = Funcionarios.query.filter_by(id_func=id_func)
    # pessoa = Pessoas.query.filter_by(id_pessoa=funcionario.fk_id_pessoa)

    funcionario = Funcionarios.query.get_or_404(
        id_func)  # Obtendo diretamente pelo ID
    pessoa = Pessoas.query.get_or_404(funcionario.fk_id_pessoa)
    departamentos = Departamentos.query.all()

    return render_template("editar.html", titulo="Cadastrar Funcionário", funcionario=funcionario, pessoa=pessoa, departamentos=departamentos)


@app.route('/atualizar_informacoes', methods=['POST',])
def atualizar_informacoes():

    # Atualiza as informações pessoais
    atualiza_pessoa = Pessoas.query.filter_by(
        id_pessoa=request.form['id_pessoa']).first()

    atualiza_pessoa.nome = request.form['nome']
    atualiza_pessoa.cpf = request.form['cpf']
    atualiza_pessoa.data_nascimento = request.form['data_nascimento']
    atualiza_pessoa.tel1 = request.form['tel1']
    atualiza_pessoa.tel2 = request.form['tel2']
    atualiza_pessoa.endereco = request.form['endereco']
    atualiza_pessoa.cidade = request.form['cidade']

    # Atualiza as informações de emprego
    atualiza_emprego = Funcionarios.query.filter_by(
        id_func=request.form['id_func']).first()

    atualiza_emprego.email = request.form['email']
    atualiza_emprego.data_contratacao = request.form['data_contratacao']
    atualiza_emprego.salario = request.form['salario']
    atualiza_emprego.nome_cargo = request.form['cargo']
    atualiza_emprego.status_func = request.form['status']

    """# Pode ser obtido de um select
    departamento = Departamentos.query.filter_by(
        nome_departamento=request.form['departamento']).first()"""


    # Atualiza o departamento usando o ID do departamento enviado
    departamento_id = request.form['departamento']
    atualiza_emprego.fk_id_departamento = departamento_id

    # Salva as alterações no banco de dados
    db.session.add(atualiza_pessoa)
    db.session.add(atualiza_emprego)
    db.session.commit()

    flash('Funcionário atualizado com sucesso!')

    return redirect(url_for('lista_de_funcionarios'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
