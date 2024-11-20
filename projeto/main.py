from flask import Flask, render_template, request, redirect, session, flash, url_for, send_file, make_response
from flask_sqlalchemy import SQLAlchemy  # pip install flask-SQLAlchemy
import enum
from datetime import datetime, timezone
from weasyprint import HTML
# pip install weasyprint (biblioteca para importar p/ PDF)
# baixar também: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
import io


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
        return '<Name %r>' % self.name

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


# ROTAS

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
        print(f"Funcionário: {funcionario.pessoa.nome}, Departamento: {
              departamento}, Status {funcionario.status_func}")

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
            # Caso a dedução INSS não exista, cria ela
            inss = Deducao(desc_deducao='INSS')

        try:
            db.session.add(inss)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print("Erro ao adicionar uma nova pessoa:", e)
            flash('Erro ao cadastrar uma nova pessoa.')
            return redirect(url_for('lista_de_funcionarios'))

    # Adiciona a dedução INSS na folha de pagamento
    salario_base_float = float(salario_base)
    folha_deducao = FolhaDeducoes(fk_id_pagamento=nova_folha_pagamento.id_pagamento,
                                  fk_id_deducao=inss.id_deducao,
                                  valor_deducao=salario_base_float * 0.08)  # Exemplo de 8% para INSS
    db.session.add(folha_deducao)
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

    # Obtém o `funcionário` e a `pessoa` associada (Obtendo diretamente pelo ID)
    funcionario = Funcionarios.query.get_or_404(id_func)
    pessoa = Pessoas.query.get_or_404(funcionario.fk_id_pessoa)

    # Obtém todos os departamentos para o select de departamentos
    departamentos = Departamentos.query.all()

    # Verifica se o funcionário tem uma folha de pagamento associada
    folha_pagamento = Folha_pagamento.query.filter_by(
        fk_id_func=id_func).first()

    return render_template("editar.html", titulo="Editar Informações", funcionario=funcionario, pessoa=pessoa, departamentos=departamentos, folha_pagamento=folha_pagamento)


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

    """# Pode ser obtido de um select
    departamento = Departamentos.query.filter_by(
        nome_departamento=request.form['departamento']).first()"""

    # Atualiza o departamento usando o ID do departamento enviado
    departamento_id = request.form['departamento']
    atualiza_emprego.fk_id_departamento = departamento_id

    # Atualizar informações salariais
    if 'id_pagamento' in request.form:
        folha_pagamento = Folha_pagamento.query.filter_by(
            id_folha=request.form['id_pagamento']).first()
        folha_pagamento.salario_base = request.form['salario_base']
        # tem que alterar para nome_banco
        folha_pagamento.nome_banco = request.form['nome_banco']
        folha_pagamento.num_agencia = request.form['num_agencia']
        folha_pagamento.conta_deposito = request.form['conta_deposito']
        db.session.add(folha_pagamento)

    # Salva as alterações no banco de dados
    db.session.add(atualiza_pessoa)
    db.session.add(atualiza_emprego)
    db.session.commit()

    flash('Funcionário atualizado com sucesso!')

    return redirect(url_for('lista_de_funcionarios'))


# Rota para mostrar todas as informações do funcionário
@app.route('/funcionario_detalhes/<int:id_func>')
def funcionario_detalhes(id_func):
    funcionario = Funcionarios.query.get_or_404(id_func)
    folha_pagamento = funcionario.folha_pagamento

    folha_pagamento_mais_recente = folha_pagamento[-1] if folha_pagamento else None

    return render_template('funcionario_detalhes.html', funcionario=funcionario, folha_pagamento=folha_pagamento_mais_recente)


# Rota para deletar o cadastro de um funcionário
@app.route('/deletar/<int:id_func>')
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
    html_content = render_template('pdf_folhaPagamento.html', folha=folha, proventos=proventos, deducoes=deducoes,
                                   total_proventos=total_proventos, total_deducoes=total_deducoes, salario_liquido=salario_liquido, funcionario=funcionario)

    # Criar o PDF a partir do HTML
    pdf = HTML(string=html_content).write_pdf()

    # Retorna o PDF gerado como um arquivo para download
    return send_file(io.BytesIO(pdf), as_attachment=True, download_name=f"{funcionario.pessoa.nome}_folha_pagamento.pdf", mimetype='application/pdf')

    # as_attachment=True indica que o arquivo será enviado como um anexo (em vez de ser exibido diretamente no navegador)
    # o arquivo será enviado automáticamente ao usuário como download, assim não salvando no servidor.


# Rota para gerar uma lista de todos os funcionários em PDF
@app.route('/gerar_listaFuncionarios_pdf')
def gerar_listaFuncionarios_pdf():
    # Buscar todos os funcionários do banco de dados
    lista_func = db.session.query(Funcionarios, Departamentos.nome_departamento).outerjoin(Departamentos, Funcionarios.fk_id_departamento == Departamentos.id_departamento).all()

    # Renderizar o template HTML com a lista de funcionários
    rendered = render_template('pdf_listaFuncionarios.html', lista_func=lista_func)

    # Converter o HTML para PDF usando o WeasyPrint
    pdf = HTML(string=rendered).write_pdf()

    # Criar a resposta HTTP com o PDF gerado
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=lista_funcionarios.pdf'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
