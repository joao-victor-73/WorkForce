from flask import Flask, render_template, request, redirect, session, flash, url_for, send_file, make_response
from flask_sqlalchemy import SQLAlchemy  # pip install flask-SQLAlchemy
from sqlalchemy import func, or_

# Para essas bibliotecas: pip install flask-login flask-wtf flask-bcrypt
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import generate_password_hash, check_password_hash, Bcrypt
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

import io
import enum
from datetime import datetime, timezone

from weasyprint import HTML
# pip install weasyprint (biblioteca para importar p/ PDF)
# baixar também: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases


app = Flask(__name__)
app.secret_key = 'random_key'

# Fazendo a conexão com o banco de dados através do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:darc147@localhost/workforce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print('Banco de dados CONECTADO')
db = SQLAlchemy(app)  # Instanciando a aplicação para o SQLAlchemy

bcrypt = Bcrypt(app)

# Configurações para gerenciar a autenticação de usuários.
login_manager = LoginManager(app)
login_manager.login_view = 'login'
"""
login_view especifica o nome da rota onde está a página de login. Quando um usuário tentar 
acessar uma rota protegida (decorada com @login_required) sem estar autenticado, ele será 
automaticamente redirecionado para essa página (a /login).

O valor de login_view deve corresponder ao nome da função que define a rota de login na 
sua aplicação Flask.
"""


# Criando classe para as informações das tabelas

# Enumeração para o status do funcionário
class StatusFunc(enum.Enum):
    EFETIVO = "EFETIVO"
    FERIAS = "FERIAS"
    DEMITIDO = "DEMITIDO"
    ATESTADO = "ATESTADO"


class StatusTipo(enum.Enum):
    HORISTA = "HORISTA"
    FOLGUISTA = "FOLGUISTA"
    INTERMITENTE = "INTERMITENTE"
    MENSALISTA = "MENSALISTA"


class Departamentos(db.Model):
    __tablename__ = 'departamentos'

    id_departamento = db.Column(db.Integer, primary_key=True)
    nome_departamento = db.Column(db.String(100), nullable=False)
    fk_id_func = db.Column(db.Integer, db.ForeignKey(
        'funcionarios.id_func'))  # Supervisor

    # Relacionamento com a tabela de funcionários (funcionários do departamento)
    funcionarios = db.relationship('Funcionarios', backref='departamento',
                                   lazy=True, foreign_keys='Funcionarios.fk_id_departamento')

    # Relacionamento com o supervisor do departamento
    supervisor = db.relationship(
        'Funcionarios', backref='departamentos_supervisionados', foreign_keys=[fk_id_func])

    def __repr__(self):
        return f'<Departamento {self.nome_departamento}>'


class Pessoas(db.Model):
    __tablename__ = 'pessoas'

    id_pessoa = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date)
    tel1 = db.Column(db.String(20))
    tel2 = db.Column(db.String(20))
    rua = db.Column(db.String(100))
    bairro = db.Column(db.String(50))
    num_residencia = db.Column(db.String(10))
    cidade = db.Column(db.String(30))
    cep = db.Column(db.String(15))

    # Relacionamento com a tabela de funcionários
    funcionario = db.relationship('Funcionarios', backref='pessoa', lazy=True)

    def __repr__(self):
        return f"<Funcionarios id: {self.id_func}, nome: {self.pessoa.nome}>"


class Funcionarios(db.Model):
    __tablename__ = 'funcionarios'

    id_func = db.Column(db.Integer, primary_key=True)
    fk_id_pessoa = db.Column(db.Integer, db.ForeignKey(
        'pessoas.id_pessoa'), nullable=False)
    email = db.Column(db.String(100))
    data_contratacao = db.Column(
        db.Date, nullable=False, default=datetime.now(timezone.utc))
    nome_cargo = db.Column(db.String(100))
    status_func = db.Column(db.Enum(
        'EFETIVO', 'FERIAS', 'DEMITIDO', 'ATESTADO'), nullable=False, default='EFETIVO')
    status_informacao = db.Column(db.Boolean, default=True)

    fk_id_departamento = db.Column(
        db.Integer, db.ForeignKey('departamentos.id_departamento'))

    # Relacionamento com folha de pagamento
    folha_pagamento = db.relationship(
        'Folha_pagamento', backref='funcionarios', lazy=True)

    def __repr__(self):
        return f'<Funcionario {self.nome_cargo}>'


# Modelo para Proventos (proventos_fpg)
class Provento(db.Model):
    __tablename__ = 'proventos_fpg'

    id_provento = db.Column(db.Integer, primary_key=True)
    desc_provento = db.Column(db.String(300), nullable=False)
    valor_provento = db.Column(db.Numeric(10, 2))


# Modelo para Deducoes (deducoes_fpg)
class Deducao(db.Model):
    __tablename__ = 'deducoes_fpg'

    id_deducao = db.Column(db.Integer, primary_key=True)
    desc_deducao = db.Column(db.String(300), nullable=False)
    valor_deducao = db.Column(db.Numeric(10, 2))


# Modelo para Folha_pagamento
class Folha_pagamento(db.Model):
    __tablename__ = 'folha_pagamento'

    id_pagamento = db.Column(db.Integer, primary_key=True)
    data_pagamento = db.Column(db.String(15), nullable=False)
    tipo = db.Column(db.Enum('HORISTA', 'FOLGUISTA', 'INTERMITENTE',
                     'MENSALISTA'), nullable=False, default='HORISTA')
    nome_banco = db.Column(db.String(100))
    num_agencia = db.Column(db.String(50))
    conta_deposito = db.Column(db.String(50))
    salario_base = db.Column(db.Numeric(
        10, 2), nullable=False, default=1414.00)
    geracao_folha = db.Column(db.Date, default=datetime.now(timezone.utc))

    # Relacionamentos
    fk_id_func = db.Column(db.Integer, db.ForeignKey(
        'funcionarios.id_func'), nullable=False)
    fk_id_proventos = db.Column(
        db.Integer, db.ForeignKey('proventos_fpg.id_provento'))
    fk_id_deducoes = db.Column(
        db.Integer, db.ForeignKey('deducoes_fpg.id_deducao'))

    def __repr__(self):
        return f'<Folha_pagamento {self.nome_banco}>'

# OBS: o db.Numeric é o equivalente ao Decimal do SQL. Esse é o tipo correspondente no SQLAlchemy.


# Tabelas intermediárias para folha_proventos e folha_deducoes (Many-to-Many)
# Modelo intermediário para FolhaProventos
class FolhaProventos(db.Model):
    __tablename__ = 'folha_proventos'

    id = db.Column(db.Integer, primary_key=True)
    fk_id_pagamento = db.Column(db.Integer, db.ForeignKey(
        'folha_pagamento.id_pagamento'), nullable=False)
    fk_id_provento = db.Column(db.Integer, db.ForeignKey(
        'proventos_fpg.id_provento'), nullable=False)


# Modelo intermediário para FolhaDeducoes
class FolhaDeducoes(db.Model):
    __tablename__ = 'folha_deducoes'

    id = db.Column(db.Integer, primary_key=True)
    fk_id_pagamento = db.Column(db.Integer, db.ForeignKey(
        'folha_pagamento.id_pagamento'), nullable=False)
    fk_id_deducao = db.Column(db.Integer, db.ForeignKey(
        'deducoes_fpg.id_deducao'), nullable=False)


# Modelo para Login de Usuários
class LoginUsuarios(db.Model, UserMixin):
    __tablename__ = 'login_usuarios'

    id = db.Column(db.Integer, primary_key=True)
    login_user = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('ADMIN', 'USER'), default='USER')
    ativo = db.Column(db.Boolean, default=True)
    fk_id_func = db.Column(db.Integer, db.ForeignKey(
        'funcionarios.id_func'), nullable=False)

    # Relacionamento
    infor_func = db.relationship(
        'Funcionarios', backref='login_usuarios', lazy=True)

    # Método is_active
    @property
    def is_active(self):
        return self.ativo  # Retorna o valor da coluna ativo

    def set_password(self, senha):  # Durante o Cadastro:
        # Este método é usado para definir a senha de um usuário ao cadastrá-lo no sistema.
        self.senha_hash = bcrypt.generate_password_hash(
            senha).decode('utf-8')

        # self.senha_hash: Atributo da classe (criptografado e armazenado no banco de dados).
        # senha_digitada: Senha recebida em texto plano.

    def check_password(self, senha):  # Durante o Login:
        # Este método verifica se a senha fornecida pelo usuário corresponde
        # ao hash armazenado no banco de dados.
        return bcrypt.check_password_hash(self.senha_hash, senha)


@login_manager.user_loader
def load_user(user_id):
    # Este decorador é usado para informar ao Flask-Login como carregar um
    # usuário a partir do seu ID armazenado na sessão.
    return LoginUsuarios.query.get(int(user_id))


# CRIANDO FÓRMULARIOS DE LOGIN E REGISTRO

# Login
class LoginForm(FlaskForm):
    login_user = StringField('Login', validators=[
                             DataRequired(), Length(min=4, max=25)])
    senha_hash = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

# Registro


class RegisterForm(FlaskForm):
    login_user = StringField('Login', validators=[
                             DataRequired(), Length(min=4, max=25)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
                                    DataRequired(), EqualTo('senha')])
    funcionario_id = SelectField(
        'Funcionário', coerce=int, validators=[DataRequired()])
    role = SelectField('Função', choices=[
                       ('USER', 'Usuário'), ('ADMIN', 'Administrador')], default='USER')
    submit = SubmitField('Registrar')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        # Preencher o SelectField com todos os funcionários disponíveis no banco de dados
        self.funcionario_id.choices = [
            (f.id_func, f.pessoa.nome) for f in Funcionarios.query.all()]

        """
        Essa última linha do método cria uma lista de tuplas, onde o primeiro valor é o 
        `id_func` e o segundo é o nome do funcionário, para que o usuário selecione o funcionário.
        """


# ROTAS

@app.route('/')
@login_required
def index():
    departamentos = db.session.query(
        Departamentos.nome_departamento,
        func.count(Funcionarios.id_func).label('total_funcionarios')
    ).outerjoin(Funcionarios, Funcionarios.fk_id_departamento == Departamentos.id_departamento) \
     .group_by(Departamentos.id_departamento, Departamentos.nome_departamento).all()

    """
    O func (que vem do import de sqlalchemy) atua como um proxy que cria objetos 
    representando chamadas de funções SQL.

    func.count() gera a expressão SQL COUNT().
    func.sum() gera a expressão SQL SUM().
    """

    return render_template('index.html', departamentos=departamentos)


@app.route('/lista', methods=['GET', ])
@login_required
def lista_de_funcionarios():
    # Obtém o termo de busca da URL
    termo_busca = request.args.get('busca', '')
    departamento_filtro = request.args.get(
        'departamento', '')  # Filtro por departamento

    # Filtro por data de contratação (Intervalo (de uma data até outra) )
    data_contratacao_inicio = request.args.get('data_contratacao_inicio', '')
    data_contratacao_fim = request.args.get('data_contratacao_fim', '')

    # Filtro para o status do funcionario
    status_filtro = request.args.get('status', '')

    # Consulta para obter todos os funcionários com seus departamentos
    consulta_base = db.session.query(
        Funcionarios,
        Departamentos.nome_departamento
    ).outerjoin(Departamentos, Funcionarios.fk_id_departamento == Departamentos.id_departamento).filter(Funcionarios.status_informacao == True)

    # Filtra os resultados se houver um termo de busca e também é como um filtro pelo nome
    if termo_busca:
        consulta_base = consulta_base.filter(
            Funcionarios.pessoa.has(Pessoas.nome.ilike(f'%{termo_busca}%'))
        )

    # Filtro por departamento
    if departamento_filtro:
        consulta_base = consulta_base.filter(
            Departamentos.nome_departamento == departamento_filtro
        )

    # Filtro por data de contratação (intervalo)
    if data_contratacao_inicio and data_contratacao_fim:
        try:
            data_inicio = datetime.strptime(
                data_contratacao_inicio, '%Y-%m-%d')
            data_fim = datetime.strptime(data_contratacao_fim, '%Y-%m-%d')
            consulta_base = consulta_base.filter(
                Funcionarios.data_contratacao.between(data_inicio, data_fim))
        except ValueError:
            flash("Formato de data inválido. Use 'AAAA-MM-DD'.", "error")

    # Filtro por status
    if status_filtro:
        consulta_base = consulta_base.filter(
            Funcionarios.status_func.ilike(f'%{status_filtro}%'))

    # Obter todos os departamentos
    lista_de_departamentos = db.session.query(
        Departamentos.nome_departamento).all()

    lista_func = consulta_base.all()

    return render_template(
        'lista.html',
        lista_func=lista_func,
        lista_de_departamentos=lista_de_departamentos,
        busca=termo_busca,
        departamento=departamento_filtro,
        data_contratacao_inicio=data_contratacao_inicio,
        data_contratacao_fim=data_contratacao_fim,
        status=status_filtro
    )


@app.route('/cadastro', methods=['POST', ])
@login_required
def cadastro_funcionario():
    return render_template('lista.html')


# Essa rota, redireciona o usuário para o formulario de criação/cadastro
@app.route('/novo_funcionario')
@login_required
def novo_funcionario():
    # Passando a lista de departamentos para ter opção na hora docadastramento
    lista_departamentos = Departamentos.query.all()

    return render_template("cadastro.html", titulo="Cadastrar Funcionário", departamentos=lista_departamentos)


# Essa rota coleta o que foi digitado no formulario e cria/cadastra o funcionário
@app.route('/criando_funcionario', methods=['POST',])
@login_required
def criando_funcionario():
    # Requisitando as informações PESSOAIS:
    nome = request.form['nome']
    cpf = request.form['cpf']
    data_nascimento = request.form['data_nascimento']
    tel1 = request.form['tel1']
    tel2 = request.form['tel2']
    rua = request.form['rua']
    bairro = request.form['bairro']
    num_residencia = request.form['num_residencia']
    cidade = request.form['cidade']
    cep = request.form['cep']

    # Requisitando as INFORMAÇÕES DO EMPREGO:
    email = request.form['email']
    data_contratacao = request.form['data_contratacao']
    cargo = request.form['cargo']

    # Usando o ID do departamento diretamente do formulário
    fk_id_departamento = request.form['departamento']  # Aqui você pega o ID

    status = request.form['status']
    print(f'Status recebido do formulário: {status}')  # Verifique o valor aqui
    status_enum = StatusFunc[status]
    # Verifique o valor do Enum
    print(f'Status convertido para Enum: {status_enum}')

    # Requisitando as INFORMAÇÕES DE PAGAMENTO:
    nome_banco = request.form['nome_banco']
    num_agencia = request.form['num_agencia']
    conta_deposito = request.form['conta_deposito']
    salario_base = request.form['salario_base']
    data_pagamento = request.form['data_pagamento']

    tipo_contratacao = request.form['tipo_contratacao']
    tipo_contratacao_enum = StatusTipo[tipo_contratacao]

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
                          rua=rua,
                          bairro=bairro,
                          num_residencia=num_residencia,
                          cidade=cidade,
                          cep=cep)

    print("ADICIONAND PESSOA NA TABELA")
    # Adicionando a nova pessoa ao banco

    try:
        db.session.add(nova_pessoa)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Erro ao adicionar uma nova pessoa:", e)
        flash('Erro ao cadastrar uma nova pessoa.')
        return redirect(url_for('lista_de_funcionarios'))

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
                                    nome_cargo=cargo,
                                    status_func=status_enum.value,
                                    fk_id_departamento=departamento_obj.id_departamento)

    # Salvando o novo_funcionario no banco de dados
    # o objeto novo_funcionario é adicionado à sessão do banco de dados.
    try:
        db.session.add(novo_funcionario)
        # Aqui, as mudanças, que são a inserção de um novo registro, são confirmadas/comitadas.
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print("Erro ao adicionar uma nova pessoa:", e)
        flash('Erro ao cadastrar uma nova pessoa.')
        return redirect(url_for('lista_de_funcionarios'))

    if novo_funcionario.id_func:
        nova_folha_pagamento = Folha_pagamento(fk_id_func=novo_funcionario.id_func,
                                               salario_base=salario_base,
                                               num_agencia=num_agencia,
                                               nome_banco=nome_banco,
                                               conta_deposito=conta_deposito,
                                               data_pagamento=data_pagamento,
                                               tipo=tipo_contratacao_enum.value)

        try:
            db.session.add(nova_folha_pagamento)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print("Erro ao adicionar uma nova pessoa:", e)
            flash('Erro ao cadastrar uma nova pessoa.')
            return redirect(url_for('lista_de_funcionarios'))

    if nova_folha_pagamento.id_pagamento:
        # Recupera a dedução INSS (se ela já existir)
        inss = Deducao.query.filter_by(desc_deducao='INSS').first()
        if not inss:
            # Criar a dedução INSS se ela ainda não existir
            # Define o valor na tabela Deducoes
            inss = Deducao(desc_deducao='INSS',
                           valor_deducao=salario_base * 0.08)

        try:
            db.session.add(inss)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print("Erro ao adicionar uma nova pessoa:", e)
            flash('Erro ao cadastrar uma nova pessoa.')
            return redirect(url_for('lista_de_funcionarios'))

    salario_base_float = float(salario_base)
    # Associar a dedução ao pagamento usando FolhaDeducoes
    folha_deducao = FolhaDeducoes(
        fk_id_pagamento=nova_folha_pagamento.id_pagamento,
        fk_id_deducao=inss.id_deducao  # Relaciona com a dedução já criada
    )

    try:
        db.session.add(folha_deducao)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print("Erro ao adicionar uma nova pessoa:", e)
        flash('Erro ao cadastrar uma nova pessoa.')
        return redirect(url_for('lista_de_funcionarios'))

    flash('Funcionário cadastrado com sucesso!')
    print("REDIRECIONANDO PARA A LISTA DE FUNCIONÁRIOS")

    # Após a coleta das informações do formulario, a rota/função terá um retorno
    # de redirect para outra página, que é básicamente a página de lista de funcionários
    return redirect(url_for('lista_de_funcionarios'))


@app.route('/editar_informacoes/<int:id_func>')
@login_required
def editar_informacoes(id_func):
    # funcionario = Funcionarios.query.filter_by(id_func=id_func)
    # pessoa = Pessoas.query.filter_by(id_pessoa=funcionario.fk_id_pessoa)

    # Obtém o `funcionário` e a `pessoa` associada (Obtendo diretamente pelo ID)
    funcionario = Funcionarios.query.get_or_404(id_func)
    pessoa = Pessoas.query.get_or_404(funcionario.fk_id_pessoa)

    # Obtém todos os departamentos para o select de departamentos
    departamentos = Departamentos.query.all()

    # Verifica se o funcionário tem uma folha de pagamento associada
    folha_pagamento = Folha_pagamento.query.filter_by(
        fk_id_func=id_func).first()

    return render_template("editar.html", funcionario=funcionario, pessoa=pessoa, departamentos=departamentos, folha_pagamento=folha_pagamento)


@app.route('/atualizar_informacoes', methods=['POST',])
@login_required
def atualizar_informacoes():

    # Atualiza as informações pessoais
    atualiza_pessoa = Pessoas.query.filter_by(
        id_pessoa=request.form['id_pessoa']).first()

    atualiza_pessoa.nome = request.form['nome']
    atualiza_pessoa.cpf = request.form['cpf']
    atualiza_pessoa.data_nascimento = request.form['data_nascimento']
    atualiza_pessoa.tel1 = request.form['tel1']
    atualiza_pessoa.tel2 = request.form['tel2']
    atualiza_pessoa.rua = request.form['rua']
    atualiza_pessoa.bairro = request.form['bairro']
    atualiza_pessoa.num_residencia = request.form['num_residencia']
    atualiza_pessoa.cidade = request.form['cidade']
    atualiza_pessoa.cep = request.form['cep']

    # Atualiza as informações de emprego
    atualiza_emprego = Funcionarios.query.filter_by(
        id_func=request.form['id_func']).first()

    atualiza_emprego.email = request.form['email']
    atualiza_emprego.data_contratacao = request.form['data_contratacao']
    atualiza_emprego.nome_cargo = request.form['cargo']
    atualiza_emprego.status_func = request.form['status']

    # Atualiza o departamento usando o ID do departamento enviado
    departamento_id = request.form['departamento']
    atualiza_emprego.fk_id_departamento = departamento_id

    # Atualizar informações salariais
    if 'id_pagamento' in request.form:
        folha_pagamento = Folha_pagamento.query.filter_by(
            id_pagamento=request.form['id_pagamento']).first()
        print(folha_pagamento)

        if folha_pagamento:
            folha_pagamento.salario_base = request.form['salario_base']
            folha_pagamento.data_pagamento = request.form['data_pagamento']
            folha_pagamento.nome_banco = request.form['nome_banco']
            folha_pagamento.num_agencia = request.form['num_agencia']
            folha_pagamento.conta_deposito = request.form['conta_deposito']

        else:
            # Criar um novo registro de folha de pagamento
            folha_pagamento = Folha_pagamento(
                id_pagamento=request.form['id_pagamento'],
                salario_base=request.form['salario_base'],
                data_pagamento=request.form['data_pagamento'],
                nome_banco=request.form['nome_banco'],
                num_agencia=request.form['num_agencia'],
                conta_deposito=request.form['conta_deposito']
            )
        db.session.add(folha_pagamento)

    # Salva as alterações no banco de dados
    try:
        db.session.add(atualiza_pessoa)
        db.session.add(atualiza_emprego)
        db.session.commit()
    except Exception as e:
        print("Erro ao salvar no banco:", str(e))
        db.session.rollback()

    flash('Funcionário atualizado com sucesso!')

    return redirect(url_for('lista_de_funcionarios'))


# Rota para mostrar todas as informações do funcionário
@app.route('/funcionario_detalhes/<int:id_func>')
@login_required
def funcionario_detalhes(id_func):
    funcionario = Funcionarios.query.get_or_404(id_func)
    folha_pagamento = funcionario.folha_pagamento

    folha_pagamento_mais_recente = folha_pagamento[-1] if folha_pagamento else None

    return render_template('funcionario_detalhes.html', funcionario=funcionario, folha_pagamento=folha_pagamento_mais_recente)


# Rota para deletar o cadastro de um funcionário
@app.route('/deletar/<int:id_func>')
@login_required
def deletar_informacoes(id_func):
    funcionario = Funcionarios.query.get_or_404(id_func)

    try:
        # Recupera e exclui o funcionário e suas informações associadas
        pessoa = Pessoas.query.get(funcionario.fk_id_pessoa)
        db.session.delete(funcionario)
        db.session.commit()

        # Exclui também o registro pessoal associado
        db.session.delete(pessoa)
        db.session.commit()

        flash("Funcionário e informações associadas excluídos com sucesso.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao tentar excluir o funcionário.", "danger")

    # Redireciona para a lista de funcionários após exclusão
    return redirect(url_for('lista_de_funcionarios'))


# Rota para criar folha de pagamentos do funcionário
@app.route('/gerar_folha_pagamento/<int:id_func>')
@login_required
def gerar_folha_pagamento(id_func):
    # Buscar o funcionário
    funcionario = Funcionarios.query.get_or_404(id_func)

    # Buscar a folha de pagamento mais recente
    folha = Folha_pagamento.query.filter_by(fk_id_func=id_func).order_by(
        Folha_pagamento.data_pagamento.desc()).first()

    # Buscar proventos e deduções associados à folha de pagamento
    proventos = db.session.query(Provento).join(FolhaProventos).filter(
        FolhaProventos.fk_id_pagamento == folha.id_pagamento).all()
    deducoes = db.session.query(Deducao).join(FolhaDeducoes).filter(
        FolhaDeducoes.fk_id_pagamento == folha.id_pagamento).all()

    return render_template('folha_pagamento.html', funcionario=funcionario, folha=folha, proventos=proventos, deducoes=deducoes)


# Rota para adicionar proventos a um funcionário
@app.route('/add_proventos/<int:id_pagamento>', methods=['POST', 'GET'])
@login_required
def add_proventos(id_pagamento):
    folha_pagamento = Folha_pagamento.query.get_or_404(id_pagamento)

    # Recupera os proventos existentes
    proventos_existentes = Provento.query.all()

    if request.method == 'POST':
        descricao = request.form['desc_provento']
        valor = request.form['valor_provento']

        # Caso o usuário tenha escolhido um provento existente
        provento_selecionado = request.form.get('provento')

        if provento_selecionado:
            # Se o usuário selecionou um provento existente
            provento = Provento.query.get(provento_selecionado)

            # Adiciona esse provento à folha de pagamento
            folha_provento = FolhaProventos(
                fk_id_pagamento=id_pagamento, fk_id_provento=provento.id_provento)
            db.session.add(folha_provento)
            db.session.commit()
            flash('Provento associado com sucesso!')

        else:
            # Se o usuário quer adicionar um novo provento
            novo_provento = Provento(
                desc_provento=descricao, valor_provento=valor)
            db.session.add(novo_provento)
            db.session.commit()

            # Associa o novo provento à folha de pagamento
            folha_provento = FolhaProventos(
                fk_id_pagamento=id_pagamento, fk_id_provento=novo_provento.id_provento)
            db.session.add(folha_provento)
            db.session.commit()

            flash('Novo Provento adicionado com sucesso!')

        return redirect(url_for('gerar_folha_pagamento', id_func=folha_pagamento.fk_id_func))

    return render_template('add_proventos.html', folha_pagamento=folha_pagamento, proventos_existentes=proventos_existentes, titulo="Adicionar Provento")


# Rota para adicionar deduções a um funcionário
@app.route('/add_deducoes/<int:id_pagamento>', methods=['POST', 'GET'])
@login_required
def add_deducoes(id_pagamento):
    folha_pagamento = Folha_pagamento.query.get_or_404(id_pagamento)

    # Recupera as deduções existentes
    deducoes_existentes = Deducao.query.all()

    if request.method == 'POST':
        descricao = request.form['desc_deducao']
        valor = request.form['valor_deducao']

        # Caso o usuário tenha escolhido uma dedução existente
        deducao_selecionado = request.form.get('deducao')

        if deducao_selecionado:
            # Se o usuário selecionou uma dedução existente
            deducao = Deducao.query.get(deducao_selecionado)

            # Adicionar essa dedução a folha de pagamento
            folha_deducao = FolhaDeducoes(fk_id_pagamento=id_pagamento,
                                          fk_id_deducao=deducao.id_deducao)
            db.session.add(folha_deducao)
            db.session.commit()
            flash('Dedução associada com sucesso!')

        else:
            # Se o usuário quer adicionar um novo provento
            nova_deducao = Deducao(desc_deducao=descricao, valor_deducao=valor)
            db.session.add(nova_deducao)
            db.session.commit()

            # Associa a dedução à folha de pagamento
            folha_deducao = FolhaDeducoes(fk_id_pagamento=id_pagamento,
                                          fk_id_deducao=nova_deducao.id_deducao)
            db.session.add(folha_deducao)
            db.session.commit()

            flash('Dedução adicionada com sucesso!')

        return redirect(url_for('gerar_folha_pagamento', id_func=folha_pagamento.fk_id_func))

    return render_template('add_deducoes.html', folha_pagamento=folha_pagamento, deducoes_existentes=deducoes_existentes, titulo="Adicionar Dedução")


# Rota para gerar o PDF da folha de pagamento
@app.route('/imprimir_folha_pagamento/<int:id_pagamento>')
@login_required
def imprimir_folha_pagamento(id_pagamento):
    # Recupera a folha de pagamento, proventos e deduções
    folha = Folha_pagamento.query.get_or_404(id_pagamento)
    proventos = db.session.query(Provento).join(FolhaProventos).filter(
        FolhaProventos.fk_id_pagamento == folha.id_pagamento).all()
    deducoes = db.session.query(Deducao).join(FolhaDeducoes).filter(
        FolhaDeducoes.fk_id_pagamento == folha.id_pagamento).all()

    # Vai servir básicamente só para pegar o nome do funcionário
    funcionario = Funcionarios.query.get_or_404(folha.fk_id_func)
    nome_funcionario = funcionario.pessoa.nome

    # Calcular totais
    total_proventos = sum(provento.valor_provento for provento in proventos)
    total_deducoes = sum(deducao.valor_deducao for deducao in deducoes)
    salario_base = folha.salario_base
    salario_liquido = salario_base + total_proventos - total_deducoes

    # Gerar HTML para o PDF (pensar em uma maneira melhor de passar tudo isso para o html)
    html_content = render_template('pdf_folhaPagamento.html',
                                   folha=folha,
                                   proventos=proventos,
                                   deducoes=deducoes,
                                   total_proventos=total_proventos,
                                   total_deducoes=total_deducoes,
                                   salario_liquido=salario_liquido,
                                   funcionario=funcionario)

    # Criar o PDF a partir do HTML
    pdf = HTML(string=html_content).write_pdf()

    # Retorna o PDF gerado como um arquivo para download
    return send_file(io.BytesIO(pdf), as_attachment=True, download_name=f"{funcionario.pessoa.nome}_folha_pagamento.pdf", mimetype='application/pdf')

    # as_attachment=True indica que o arquivo será enviado como um anexo (em vez de ser exibido diretamente no navegador)
    # o arquivo será enviado automáticamente ao usuário como download, assim não salvando no servidor.


# Rota para gerar uma lista de todos os funcionários em PDF
# depois buscar entender cada coisa aqui, para não ficar perdido
@app.route('/gerar_listaFuncionarios_pdf')
@login_required
def gerar_listaFuncionarios_pdf():
    # Buscar todos os funcionários do banco de dados
    lista_func = db.session.query(Funcionarios, Departamentos.nome_departamento).outerjoin(
        Departamentos, Funcionarios.fk_id_departamento == Departamentos.id_departamento).all()

    # Renderizar o template HTML com a lista de funcionários
    rendered = render_template(
        'pdf_listaFuncionarios.html', lista_func=lista_func)

    # Converter o HTML para PDF usando o WeasyPrint
    pdf = HTML(string=rendered).write_pdf()

    # Criar a resposta HTTP com o PDF gerado
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=lista_funcionarios.pdf'
    return response


# ROTA PARA LISTAR OS DEPARTAMENTOS DISPONÍVEIS
@app.route('/listar_departamentos', methods=['POST', 'GET'])
def listar_departamentos():
    dados_departamentos = db.session.query(
        Departamentos.id_departamento,
        Departamentos.nome_departamento,
        Pessoas.nome.label('nome')
    ).outerjoin(Funcionarios, Departamentos.fk_id_func == Funcionarios.id_func) \
        .outerjoin(Pessoas, Funcionarios.fk_id_pessoa == Pessoas.id_pessoa).all()

    return render_template('departamentos.html', dados_departamentos=dados_departamentos)


# ROTA PARA CRIAR / EDITAR UM DEPARTAMENTO
@app.route('/departamentos/editar/<int:id_obtido>', methods=['GET', 'POST'])
@app.route('/departamentos/novo', methods=['GET', 'POST'])
def editar_departamento(id_obtido=None):
    departamento = None
    nome_supervisor = None  # Variável para o nome do supervisor

    if id_obtido:
        departamento_data = db.session.query(
            Departamentos.id_departamento,
            Departamentos.nome_departamento,
            Departamentos.fk_id_func,
            Pessoas.nome.label('nome')
        ).outerjoin(Funcionarios, Departamentos.fk_id_func == Funcionarios.id_func) \
            .outerjoin(Pessoas, Funcionarios.fk_id_pessoa == Pessoas.id_pessoa) \
            .filter(Departamentos.id_departamento == id_obtido).first()

        # Separar os dados do departamento e o nome do supervisor
        if departamento_data:
            departamento = departamento_data._asdict()  # Transformar o Row em um dicionário
            # Acessar o nome do supervisor diretamente
            nome_supervisor = departamento_data.nome

    # Carregar lista de funcionários para o dropdown
    funcionarios = db.session.query(
        Funcionarios.id_func,
        Pessoas.nome
    ).join(Pessoas, Funcionarios.fk_id_pessoa == Pessoas.id_pessoa).all()

    if request.method == 'POST':
        nome_departamento = request.form.get('nome_departamento').strip()
        fk_id_func = request.form.get(
            'fk_id_func') or None  # Converte vazio para None

        if departamento:  # Atualizar departamento existente
            departamento_obj = Departamentos.query.get(id_obtido)
            departamento_obj.nome_departamento = nome_departamento
            print("O nome do departamento está salvo")
            departamento_obj.fk_id_func = fk_id_func
            print("O id do departamento está salvo (atualizando o supervisor)")

        else:  # Criar um novo departamento
            novo_departamento = Departamentos(
                nome_departamento=nome_departamento,
                fk_id_func=fk_id_func
            )
            db.session.add(novo_departamento)

        db.session.commit()
        flash('Departamento salvo com sucesso!', 'success')
        return redirect(url_for('listar_departamentos'))

    return render_template('editar_departamento.html', departamento=departamento, funcionarios=funcionarios, nome_supervisor=nome_supervisor)


# ROTA PARA EXCLUIR UM DEPARTAMENTO
@app.route('/departamentos/excluir/<int:id_obtido>', methods=['POST'])
def excluir_departamento(id_obtido):
    departamento = Departamentos.query.get(id_obtido)
    if departamento:
        db.session.delete(departamento)
        db.session.commit()
    return redirect(url_for('listar_departamentos'))


# ROTA PARA LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = LoginUsuarios.query.filter_by(
            login_user=form.login_user.data).first()

        # Verifica se o usuário foi encontrado no banco
        print(f"Usuário encontrado: {user}")
        # Verifica a senha fornecida
        print(f"Senha fornecida: {form.senha_hash.data}")
        # Verifica a senha criptografada no banco
        print(f"Senha armazenada: {user.senha_hash}")

        if user and user.check_password(form.senha_hash.data):
            print("Senha correta!")  # Confirma se a senha está correta
            session['user_id'] = user.id
            # Armazena o nível de permissão na sessão
            session['role'] = user.role

            login_user(user)  # Salva o usuário na sessão

            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            print("Usuário ou senha incorretos!")  # Exibe erro no terminal
            flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html', form=form)


# ROTA PARA REGISTRAR
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    form = RegisterForm()

    if form.validate_on_submit():
        # Recupera o funcionário já existente pelo ID
        funcionario = Funcionarios.query.filter_by(
            id_func=form.funcionario_id.data).first()

        if funcionario:
            novo_login = LoginUsuarios(login_user=form.login_user.data)
            novo_login.set_password(form.senha.data)
            # Associando o login ao funcionário existente
            novo_login.fk_id_func = funcionario.id_func
            novo_login.role = form.role.data  # Definir o role do usuário

            db.session.add(novo_login)
            db.session.commit()

            flash('Cadastro realizado com sucesso! Você já pode fazer login.', 'success')
            return redirect(url_for('login'))

        else:
            flash('Funcionário não encontrado.', 'danger')

    else:
        print(form.errors)  # Mostra os erros de validação

    return render_template('registro.html', form=form)


# ROTA PARA LOGOUT
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


# pip freeze > requirements.txt

# pip install -r requirements.txt

# web: gunicorn main:app
