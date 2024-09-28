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
            id_departamento INT PRIMARY KEY AUTO_INCREMENT,
            nome_departamento VARCHAR(100) NOT NULL,
            id_gerente INT UNIQUE
        );''')


# Criando tabela cargos
TABLES['cargos'] = ('''
        CREATE TABLE cargos (
	        id_cargo INT PRIMARY KEY AUTO_INCREMENT,
            nome_cargo VARCHAR(100)
        );''')


TABLES['funcionarios'] = ('''
        CREATE TABLE funcionarios (
            `id_func` INT PRIMARY KEY AUTO_INCREMENT,
            `nome_func` VARCHAR(100) UNIQUE NOT NULL,
            `email` VARCHAR(100),
            `tel1` VARCHAR(15) NOT NULL,
            `tel2` VARCHAR(15),
            `data_contratacao` DATE NOT NULL,
            `salario` DECIMAL(10, 2),
            `status_func` ENUM('EFETIVO', 'FERIAS' , 'DEMITIDO', 'ATESTADO'),
            `fk_id_cargo` INT,
            `fk_id_departamento` INT, 
            CONSTRAINT `fk_funcionario_cargo`
                FOREIGN KEY (`fk_id_cargo`)
                REFERENCES cargos (`id_cargo`)
                ON DELETE CASCADE 
                ON UPDATE CASCADE,
            
            CONSTRAINT `fk_funcionario_departamento`
                FOREIGN KEY (`fk_id_departamento`)
                REFERENCES departamentos (`id_departamento`)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        ); ''')

TABLES['folha_pagamento'] = ('''
        CREATE TABLE folha_pagamento (
            `id_pagamento` INT PRIMARY KEY AUTO_INCREMENT,
            `data_pagamento` DATE NOT NULL,
            `salario_base` DECIMAL(10, 2) NOT NULL,
            `deducoes` DECIMAL(10, 2) NOT NULL,
            `salario_liquido` DECIMAL(10, 2) NOT NULL,
            `fk_id_func` INT,
            CONSTRAINT `fk_folhaPagamento_funcionario`
                FOREIGN KEY (`fk_id_func`)
                REFERENCES funcionarios (`id_func`)
                ON DELETE CASCADE
                ON UPDATE CASCADE
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

departamento_query_sql = 'INSERT INTO departamentos (nome_departamento, id_gerente) VALUES (%s, %s)'
departamentos = [
    ('Recursos Humanos', 1),
    ('Financeiro', 2),
    ('TI', 3),
    ('Marketing', 4)
]
cursor.executemany(departamento_query_sql, departamentos)
# o método `executemany` serve para executar a inserção de vários registros de uma única vez.


cargos_query_sql = 'INSERT INTO cargos (nome_cargo) VALUES (%s)'
cargos = [
    ('Analista de RH', ),
    ('Gerente Financeiro', ),
    ('Desenvolvedor', ),
    ('Coordenador de Marketing', )
]
cursor.executemany(cargos_query_sql, cargos)
# OBS: precisa-se colocar uma virgula após o valor, porque para o `executemany`, espera-se uma lista de tuplas.
#  Mas se caso eu passar as informações sem uma virgula, o Python tratará isso como uma String, não como uma tupla.


funcionarios_query_sql = 'INSERT INTO funcionarios (nome_func, email, tel1, tel2, data_contratacao, salario, status_func, fk_id_cargo, fk_id_departamento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
funcionarios = [
    ('Carlos Silva', 'carlos.silva@empresa.com', '99999-9999',
     '98888-8888', '2020-01-10', 4500.00, 'EFETIVO', 1, 1),

    ('Ana Souza', 'ana.souza@empresa.com', '98888-7777',
     '97777-6666', '2019-05-15', 6000.00, 'FERIAS', 2, 2),

    ('Marcos Lima', 'marcos.lima@empresa.com', '96666-5555',
     '95555-4444', '2021-07-01', 5000.00, 'EFETIVO', 3, 3),

    ('Fernanda Costa', 'fernanda.costa@empresa.com',
     '94444-3333', None, '2018-12-20', 7000.00, 'EFETIVO', 4, 4)
]
# None vai ser o mesmo que NULL, vai colocar None quando o valor da inserção for NULL
cursor.executemany(funcionarios_query_sql, funcionarios)


folha_pagamento_query_sql = 'INSERT INTO folha_pagamento (data_pagamento, salario_base, deducoes, salario_liquido, fk_id_func) VALUES (%s, %s, %s, %s, %s)'
folha_pagamentos = [
    ('2023-09-30', 4500.00, 500.00, 4000.00, 1),
    ('2023-09-30', 6000.00, 800.00, 5200.00, 2),
    ('2023-09-30', 5000.00, 300.00, 4700.00, 3),
    ('2023-09-30', 7000.00, 700.00, 6300.00, 4)
]
cursor.executemany(folha_pagamento_query_sql, folha_pagamentos)


# COMMINTANDO se não nada tem efeito, ou seja, confirmando as alterações
conectar.commit()

cursor.close()
conectar.close()
