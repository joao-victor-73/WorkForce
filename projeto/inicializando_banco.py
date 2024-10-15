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

# Criando a base de dados e usando-a
cursor.execute("CREATE DATABASE `workforce`;")
cursor.execute("USE `workforce`;")


# Criando as tabelas necessárias (criando através do mysql-connector):

# cria-se um dicionário, onde a chave é no nome da table e o valor é a instrução SQL.
TABLES = {}

# Criando tabela departamentos
TABLES['departamentos'] = ('''
        CREATE TABLE departamentos (
            `id_departamento` INT PRIMARY KEY AUTO_INCREMENT,
            `nome_departamento` VARCHAR(100) NOT NULL,
            `fk_id_func` INT -- Supervisor também é um funcionário
        );''')


# Criando tabela pessoas
TABLES['pessoas'] = ('''
    CREATE TABLE pessoas (
        `id_pessoa` INT PRIMARY KEY AUTO_INCREMENT,
        `nome` VARCHAR(100) NOT NULL,
        `cpf` VARCHAR(14) UNIQUE NOT NULL,
        `data_nascimento` DATE,
        `tel1` VARCHAR(20),
        `tel2` VARCHAR(20),
        `endereco` VARCHAR(100),
        `cidade` VARCHAR(30)
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
            ON UPDATE CASCADE,
        
        CONSTRAINT `fk_funcionario_departamento` 
            FOREIGN KEY (`fk_id_departamento`) 
            REFERENCES departamentos (`id_departamento`) 
            ON DELETE SET NULL 
            ON UPDATE CASCADE
    ); ''')


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
        `data_pagamento` DATE NOT NULL,
        `tipo` ENUM('HORISTA', 'FOLGUISTA', 'INTERMITENTE', 'MENSALISTA', 'PJ') NOT NULL DEFAULT 'HORISTA',
        `num_banco` VARCHAR(100),
        `num_agencia` VARCHAR(50),
        `conta_deposito` VARCHAR(50),
        `salario_base` DECIMAL(10, 2) NOT NULL DEFAULT 1414.00,
        `fk_id_func` INT,
        `fk_id_proventos` INT,
        `fk_id_deducoes` INT,
        
        CONSTRAINT `fk_folhaPagamento_funcionario` 
            FOREIGN KEY (`fk_id_func`) 
            REFERENCES funcionarios (`id_func`) 
            ON DELETE CASCADE 
            ON UPDATE CASCADE,
            
        CONSTRAINT `fk_folhaPagamento_Deducoes`
            FOREIGN KEY (`fk_id_deducoes`)
            REFERENCES deducoes_fpg (`id_deducao`)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
        
        CONSTRAINT `fk_folhaPagamento_Proventos`
            FOREIGN KEY (`fk_id_proventos`)
            REFERENCES proventos_fpg (`id_provento`)
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


# INSERINDO REGISTROS FICTICIOS NAS TABELAS

"""
Os placeholders %s são marcadores usados em consultas SQL para 
indicar onde os valores devem ser inseridos de forma segura.
"""

departamento_query_sql = 'INSERT INTO departamentos (nome_departamento) VALUES (%s)'
departamentos = [
    ('Recursos Humanos', ),
    ('Tecnologia da Informação', ),
    ('Marketing', ),
    ('Vendas', )
]
cursor.executemany(departamento_query_sql, departamentos)
# o método `executemany` serve para executar a inserção de vários registros de uma única vez.


pessoas_query_sql = 'INSERT INTO pessoas (nome, cpf, data_nascimento, tel1, tel2, endereco, cidade) VALUES (%s, %s, %s, %s, %s, %s, %s)'
pessoas = [
    ('Carlos Silva', '123.456.789-00', '1985-06-15',
     '11999999999', None, 'Rua A, 100', 'São Paulo'),
    ('Ana Costa', '987.654.321-00', '1990-09-20', '11988888888',
     '1133333333', 'Rua B, 200', 'Rio de Janeiro'),
    ('Bruno Oliveira', '456.789.123-00', '1982-11-30',
     '11977777777', None, 'Rua C, 300', 'Curitiba')
]
cursor.executemany(pessoas_query_sql, pessoas)
# OBS: precisa-se colocar uma virgula após o valor, porque para o `executemany`, espera-se uma lista de tuplas.
#  Mas se caso eu passar as informações sem uma virgula, o Python tratará isso como uma String, não como uma tupla.
# None vai ser o mesmo que NULL, vai colocar None quando o valor da inserção for NULL


funcionarios_query_sql = 'INSERT INTO funcionarios (fk_id_pessoa, email, data_contratacao, nome_cargo, status_func, fk_id_departamento) VALUES (%s, %s, %s, %s, %s, %s)'
funcionarios = [
    (1, 'carlos.silva@empresa.com', '2022-01-15', 'Gerente de RH', 'EFETIVO', 1),
    (2, 'ana.costa@empresa.com', '2023-02-01',
     'Analista de Sistemas', 'EFETIVO', 2),
    (3, 'bruno.oliveira@empresa.com', '2021-07-10',
     'Coordenador de Marketing', 'EFETIVO', 3)
]
cursor.executemany(funcionarios_query_sql, funcionarios)


proventos_fpg_query_sql = 'INSERT INTO proventos_fpg (desc_provento, valor_provento) VALUES (%s, %s)'
proventos_fpg = [
    ('Salário Base', 3000.00),
    ('Bônus por Desempenho', 500.00),
    ('Comissão', 700.00)
]
cursor.executemany(proventos_fpg_query_sql, proventos_fpg)


deducoes_fpg_query_sql = 'INSERT INTO deducoes_fpg (desc_deducao, valor_deducao) VALUES (%s, %s)'
deducoes_fpg = [
    ('INSS', 330.00),
    ('Imposto de Renda', 250.00),
    ('Plano de Saúde', 150.00)
]
cursor.executemany(deducoes_fpg_query_sql, deducoes_fpg)


folha_pagamento_query_sql = 'INSERT INTO folha_pagamento (data_pagamento, tipo, num_banco, num_agencia, conta_deposito, salario_base, fk_id_func, fk_id_proventos, fk_id_deducoes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
folha_pagamentos = [
    ('2024-10-05', 'MENSALISTA', '001', '1234-5', '987654', 3000.00, 1, 1, 1),
    ('2024-10-05', 'MENSALISTA', '237', '4321-0', '123456', 3000.00, 2, 2, 2),
    ('2024-10-05', 'MENSALISTA', '104', '5678-9', '654321', 3000.00, 3, 3, 3)
]
cursor.executemany(folha_pagamento_query_sql, folha_pagamentos)


folha_proventos_query_sql = 'INSERT INTO folha_proventos (fk_id_pagamento, fk_id_provento) VALUES (%s, %s)'
folha_proventos = [
    (1, 1),  # Provento de salário base para o pagamento 1
    (1, 2),  # Provento de bônus para o pagamento 1
    (2, 1),  # Provento de salário base para o pagamento 2
    (3, 1),  # Provento de salário base para o pagamento 3
    (3, 3)  # Provento de comissão para o pagamento 3
]
cursor.executemany(folha_proventos_query_sql, folha_proventos)

folha_deducoes_query_sql = ' INSERT INTO folha_deducoes (fk_id_pagamento, fk_id_deducao) VALUES (%s, %s)'
folha_deducoes = [
    (1, 1),  # Deducao INSS para o pagamento 1
    (1, 2),  # Deducao IR para o pagamento 1
    (2, 1),  # Deducao INSS para o pagamento 2
    (3, 1),  # Deducao INSS para o pagamento 3
    (3, 3)  # Deducao Plano de Saúde para o pagamento 3
]
cursor.executemany(folha_deducoes_query_sql, folha_deducoes)


# COMMINTANDO se não nada tem efeito, ou seja, confirmando as alterações
conectar.commit()

cursor.close()
conectar.close()
