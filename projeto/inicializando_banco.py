import mysql.connector  # pip install mysql-connector-python
from mysql.connector import errorcode

print("CONECTANDO...")

try:
    conectar = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='darc147'
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('Existe algo errado no nome de usuário ou senha.')
    else:
        print(err)

print('BANCO DE DADOS CONECTADO!')
cursor = conectar.cursor()


"""
-> A função `mysql.connector.connect()` tenta estabelecer uma conexão com o banco de dados.

-> `errorcode.ER_ACCESS_DENIED_ERROR`: Verifica se o erro é de acesso negado, o que pode 
    ocorrer se o nome de usuário ou senha estiverem errados.

-> `conectar.cursor()`: Após a conexão ser estabelecida, você cria um cursor, que é um objeto 
    usado para interagir com o banco de dados. Com ele, você pode executar comandos SQL, como SELECT, INSERT, UPDATE, DELETE, entre outros.
"""


# Caso a tabela já exista, o comando abaixo irá apaga-lá
cursor.execute("DROP DATABASE IF EXISTS `workforce`;")

print('CRIANDO DATABASE')
# Criando a base de dados e usando-a
cursor.execute("CREATE DATABASE `workforce`;")
cursor.execute("USE `workforce`;")

print('DATABASE CRIADO')


# Criando as tabelas necessárias (criando através do mysql-connector):

# cria-se um dicionário, onde a chave é no nome da table e o valor é a instrução SQL.
TABLES = {}


# Criando tabela pessoas
TABLES['pessoas'] = ('''
    CREATE TABLE pessoas (
        `id_pessoa` INT PRIMARY KEY AUTO_INCREMENT,
        `nome` VARCHAR(100) NOT NULL,
        `cpf` VARCHAR(14) UNIQUE NOT NULL,
        `data_nascimento` DATE,
        `tel1` VARCHAR(20),
        `tel2` VARCHAR(20),
        `rua` VARCHAR(100),
        `bairro` VARCHAR(50),
        `num_residencia` VARCHAR(10),
        `cidade` VARCHAR(30),
        `cep` VARCHAR(15)
    );
''')


# Criando tabela funcionarios
TABLES['funcionarios'] = ('''
    CREATE TABLE funcionarios (
        `id_func` INT PRIMARY KEY AUTO_INCREMENT, -- Vai ser como a matricula do funcionário
        `fk_id_pessoa` INT NOT NULL,
        `email` VARCHAR(100),
        `data_contratacao` DATE NOT NULL, -- Admissão
        `nome_cargo` VARCHAR(100),
        `status_func` ENUM('EFETIVO', 'FERIAS', 'DEMITIDO', 'ATESTADO') NOT NULL DEFAULT 'EFETIVO',
        `fk_id_departamento` INT,
        
        CONSTRAINT `fk_funcionario_pessoa` 
            FOREIGN KEY (`fk_id_pessoa`) 
            REFERENCES pessoas (`id_pessoa`) 
            ON DELETE CASCADE 
            ON UPDATE CASCADE
    );''')


# Criando tabela departamentos
TABLES['departamentos'] = ('''
    CREATE TABLE departamentos (
        `id_departamento` INT PRIMARY KEY AUTO_INCREMENT,
        `nome_departamento` VARCHAR(100) NOT NULL,
        `fk_id_func` INT, -- Supervisor também é um funcionário
        
        CONSTRAINT `fk_departamento_funcionario`
            FOREIGN KEY (`fk_id_func`) 
            REFERENCES funcionarios (`id_func`) 
            ON DELETE SET NULL 
            ON UPDATE CASCADE
    );''')


# As duas tabelas abaixo serviram para informar sobre proventos e deduções, e a
# descrição sobre cada um deles

# Armazena diferentes tipos de proventos (por exemplo, salário base, comissão, bônus, etc.).
TABLES['proventos_fpg'] = ('''
    CREATE TABLE proventos_fpg (
        `id_provento` INT PRIMARY KEY AUTO_INCREMENT, -- o id aqui vai ser tipo um código para servir de identificação
        `desc_provento` VARCHAR(300) NOT NULL,
        `valor_provento` DECIMAL(10, 2)
    ); ''')


# Armazena diferentes tipos de deduções(imposto de renda, INSS, etc.).
TABLES['deducoes_fpg'] = ('''
    CREATE TABLE deducoes_fpg(
        `id_deducao` INT PRIMARY KEY AUTO_INCREMENT, -- o id aqui vai ser tipo um código para servir de identificação
        `desc_deducao` VARCHAR(300) NOT NULL,
        `valor_deducao` DECIMAL(10, 2)
    )''')


# Criando tabela folha_pagamento
TABLES['folha_pagamento'] = ('''
    CREATE TABLE folha_pagamento (
        `id_pagamento` INT PRIMARY KEY AUTO_INCREMENT,
        `data_pagamento` VARCHAR(15) NOT NULL,
        `tipo` ENUM('HORISTA', 'FOLGUISTA', 'INTERMITENTE', 'MENSALISTA') NOT NULL DEFAULT 'HORISTA',
        `nome_banco` VARCHAR(100),
        `num_agencia` VARCHAR(50),
        `conta_deposito` VARCHAR(50),
        `salario_base` DECIMAL(10, 2) NOT NULL DEFAULT 1414.00,
        `fk_id_func` INT,
        `geracao_folha` DATETIME DEFAULT CURRENT_TIMESTAMP,
        
        CONSTRAINT `fk_folhaPagamento_funcionario` 
            FOREIGN KEY (`fk_id_func`) 
            REFERENCES funcionarios (`id_func`) 
            ON DELETE CASCADE 
            ON UPDATE CASCADE
    ); ''')


# CRIAÇÃO DE TABELAS INTERMEDIARIAS
# As tabelas intermediárias vão relacionar múltiplos proventos e deduções
# a uma única folha de pagamento.

# Assim permitindo que um funcinário tenha múltiplas informações na folha de pagamento.

TABLES['folha_proventos'] = ('''
    CREATE TABLE folha_proventos (
        `id` INT PRIMARY KEY AUTO_INCREMENT,
        `fk_id_pagamento` INT,
        `fk_id_provento` INT,
        
        CONSTRAINT `fk_folha_provento_pagamento`
            FOREIGN KEY (`fk_id_pagamento`) 
            REFERENCES folha_pagamento(`id_pagamento`) 
            ON DELETE CASCADE,
                             
        CONSTRAINT `fk_folha_provento_provento`
            FOREIGN KEY (`fk_id_provento`) 
            REFERENCES proventos_fpg(`id_provento`) 
            ON DELETE CASCADE
);''')


TABLES['folha_deducoes'] = ('''
    CREATE TABLE folha_deducoes(
        `id` INT PRIMARY KEY AUTO_INCREMENT,
        `fk_id_pagamento` INT,
        `fk_id_deducao` INT,
                            
        CONSTRAINT `fk_folha_deducao_pagamento`
        FOREIGN KEY(`fk_id_pagamento`) 
            REFERENCES folha_pagamento(`id_pagamento`) 
            ON DELETE CASCADE,
                            
        CONSTRAINT `fk_folha_deducao_deducao`
            FOREIGN KEY(`fk_id_deducao`) 
            REFERENCES deducoes_fpg(`id_deducao`) 
            ON DELETE CASCADE
);''')


# Criando um loop for para percorrer o dicionario TABLES
# e fazer a criação das tabelas
for tabela_nome in TABLES:
    tabela_sql = TABLES[tabela_nome]

    try:
        print(f'CRIANDO TABELA {tabela_nome}', end=' ')
        cursor.execute(tabela_sql)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print('Tabela já existente!')
        else:
            print(err.msg)
    else:
        print('OK')


# Alterar a tabela funcionários para aceitar a F.K. de Departamentos
alter_table_funcionarios = '''
    ALTER TABLE funcionarios
    ADD CONSTRAINT fk_funcionario_departamento
        FOREIGN KEY(fk_id_departamento)
        REFERENCES departamentos(id_departamento)
        ON DELETE SET NULL
        ON UPDATE CASCADE
'''
cursor.execute(alter_table_funcionarios)
conectar.commit()


# INSERINDO REGISTROS FICTICIOS NAS TABELAS

"""
Os placeholders %s são marcadores usados em consultas SQL para 
indicar onde os valores devem ser inseridos de forma segura.
"""

departamento_query_sql = 'INSERT INTO departamentos (nome_departamento) VALUES (%s)'
departamentos = [
    ('Recursos Humanos', ),
    ('Financeiro', ),
    ('T.I.', ),
    ('Transporte', ),
    ('Comercial', )
]
cursor.executemany(departamento_query_sql, departamentos)
# o método `executemany` serve para executar a inserção de vários registros de uma única vez.


pessoas_query_sql = 'INSERT INTO pessoas (nome, cpf, data_nascimento, tel1, tel2, rua, bairro, num_residencia, cidade, cep) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
pessoas = [
    ('Alice Silva', '123.456.789-00', '1990-05-21', '(11) 91234-5678',
     '(11) 92345-6789', 'Rua das Flores', 'Centro', '123', 'São Paulo', '01001-000'),
    ('Carlos Pereira', '987.654.321-00', '1985-11-15', '(11) 99876-5432',
     None, 'Av. Paulista', 'Bela Vista', '456', 'São Paulo', '20040-001'),
    ('Rafaela Silvana Junior', '655.321.888-78', '1998-06-20', '(11) 99774-8552',
     None, 'Av. Paulista', 'Bela Vista', '23', 'São Paulo', '20040-001')

]
cursor.executemany(pessoas_query_sql, pessoas)
# OBS: precisa-se colocar uma virgula após o valor, porque para o `executemany`, espera-se uma lista de tuplas.
#  Mas se caso eu passar as informações sem uma virgula, o Python tratará isso como uma String, não como uma tupla.
# None vai ser o mesmo que NULL, vai colocar None quando o valor da inserção for NULL


funcionarios_query_sql = 'INSERT INTO funcionarios (fk_id_pessoa, email, data_contratacao, nome_cargo, status_func, fk_id_departamento) VALUES (%s, %s, %s, %s, %s, %s)'
funcionarios = [
    (1, 'alice.silva@empresa.com', '2023-01-10', 'Analista de RH', 'EFETIVO', 1),
    (2, 'carlos.pereira@empresa.com', '2022-06-05', 'Contador', 'EFETIVO', 2),
    (3, 'rafa.ela.junior@empresa.com', '2024-10-29', 'Supervisora T.I.', 'EFETIVO', 3)
]
cursor.executemany(funcionarios_query_sql, funcionarios)


proventos_fpg_query_sql = 'INSERT INTO proventos_fpg (desc_provento, valor_provento) VALUES (%s, %s)'
proventos_fpg = [
    ('Vale Alimentação', 50.00),
    ('Bônus de Desempenho', 500.00),
    ('Horas Extras', 200.00)
]
cursor.executemany(proventos_fpg_query_sql, proventos_fpg)


deducoes_fpg_query_sql = 'INSERT INTO deducoes_fpg (desc_deducao, valor_deducao) VALUES (%s, %s)'
deducoes_fpg = [
    ('INSS', 120.00),
    ('Imposto de Renda', 50.00),
    ('Plano de Saúde', 100.00)
]
cursor.executemany(deducoes_fpg_query_sql, deducoes_fpg)


folha_pagamento_query_sql = 'INSERT INTO folha_pagamento (data_pagamento, tipo, nome_banco, num_agencia, conta_deposito, salario_base, fk_id_func) VALUES (%s, %s, %s, %s, %s, %s, %s)'
folha_pagamentos = [
    ('06-10', 'MENSALISTA', 'Banco do Brasil', '1234', '00012345-6', 1414.00, 1),
    ('06-10', 'HORISTA', 'Bradesco', '5678', '00098765-4', 1414.00, 2),
    ('06-10', 'HORISTA', 'Bradesco', '8899', '00014556-4', '3600.00', 3)
]
cursor.executemany(folha_pagamento_query_sql, folha_pagamentos)


folha_proventos_query_sql = 'INSERT INTO folha_proventos (fk_id_pagamento, fk_id_provento) VALUES (%s, %s)'
folha_proventos = [
    (1, 1),  # Relaciona o Salário Base com o pagamento 1
    (1, 2),  # Relaciona o Bônus de Desempenho com o pagamento 1
    (2, 1),  # Relaciona o Salário Base com o pagamento 2
    (2, 3),  # Relaciona as Horas Extras com o pagamento 2
    (3, 1),
    (3, 2)
]
cursor.executemany(folha_proventos_query_sql, folha_proventos)

folha_deducoes_query_sql = ' INSERT INTO folha_deducoes (fk_id_pagamento, fk_id_deducao) VALUES (%s, %s)'
folha_deducoes = [
    (1, 1),  # Relaciona o INSS com o pagamento 1
    (1, 2),  # Relaciona o Imposto de Renda com o pagamento 1
    (2, 1),  # Relaciona o INSS com o pagamento 2
    (2, 3),  # Relaciona o Plano de Saúde com o pagamento 2
    (3, 1),
    (3, 2)
]
cursor.executemany(folha_deducoes_query_sql, folha_deducoes)


# COMMINTANDO se não nada tem efeito, ou seja, confirmando as alterações
conectar.commit()

cursor.close()
conectar.close()
