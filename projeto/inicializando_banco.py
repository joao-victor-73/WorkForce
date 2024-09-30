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
            `nome_supervisor` VARCHAR(100)
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
        `id_func` INT PRIMARY KEY AUTO_INCREMENT,
        `fk_id_pessoa` INT NOT NULL,
        `email` VARCHAR(100),
        `data_contratacao` DATE NOT NULL,
        `salario` DECIMAL(10, 2) NOT NULL,
        `nome_cargo` INT,
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


# Criando tabela folha_pagamento
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
    ); ''')

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

departamento_query_sql = 'INSERT INTO departamentos (nome_departamento, nome_supervisor) VALUES (%s, %s)'
departamentos = [
    ('Recursos Humanos', 'Ana Clara Silva'),
    ('Desenvolvimento', 'Marcos Almeida'),
    ('Vendas', 'Fernanda Costa'),
    ('Marketing', 'Lucas Pereira')
]
cursor.executemany(departamento_query_sql, departamentos)
# o método `executemany` serve para executar a inserção de vários registros de uma única vez.


pessoas_query_sql = 'INSERT INTO pessoas (nome, cpf, data_nascimento, tel1, tel2, endereco, cidade) VALUES (%s, %s, %s, %s, %s, %s, %s)'
pessoas = [
    ('João Carlos', '123.456.789-00', '1985-06-12',
     '(11) 99999-1111', '(11) 98888-2222', 'Rua A, 123', 'São Paulo'),
    ('Maria Souza', '987.654.321-00', '1990-08-25',
     '(21) 99999-3333', None, 'Av. B, 456', 'Rio de Janeiro'),
    ('Pedro Lima', '456.789.123-00', '1982-04-15', '(31) 99999-4444',
     '(31) 98888-5555', 'Rua C, 789', 'Belo Horizonte'),
    ('Carla Mendes', '789.123.456-00', '1995-09-30',
     '(41) 99999-6666', None, 'Av. D, 321', 'Curitiba')
]
cursor.executemany(pessoas_query_sql, pessoas)
# OBS: precisa-se colocar uma virgula após o valor, porque para o `executemany`, espera-se uma lista de tuplas.
#  Mas se caso eu passar as informações sem uma virgula, o Python tratará isso como uma String, não como uma tupla.


funcionarios_query_sql = 'INSERT INTO funcionarios (fk_id_pessoa, email, data_contratacao, salario, nome_cargo, status_func, fk_id_departamento) VALUES (%s, %s, %s, %s, %s, %s, %s)'
funcionarios = [
    (1, 'joao.carlos@empresa.com', '2020-01-10', 3500.00, 1, 'EFETIVO', 1),
    (2, 'maria.souza@empresa.com', '2018-07-15', 4500.00, 2, 'FERIAS', 2),
    (3, 'pedro.lima@empresa.com', '2015-05-22', 6000.00, 3, 'EFETIVO', 3),
    (4, 'carla.mendes@empresa.com', '2019-10-12', 3200.00, 4, 'ATESTADO', 4)
]
# None vai ser o mesmo que NULL, vai colocar None quando o valor da inserção for NULL
cursor.executemany(funcionarios_query_sql, funcionarios)


folha_pagamento_query_sql = 'INSERT INTO folha_pagamento (data_pagamento, salario_base, deducoes, salario_liquido, fk_id_func) VALUES (%s, %s, %s, %s, %s)'
folha_pagamentos = [
    ('2024-09-01', 3500.00, 300.00, 3200.00, 1),
    ('2024-09-01', 4500.00, 500.00, 4000.00, 2),
    ('2024-09-01', 6000.00, 600.00, 5400.00, 3),
    ('2024-09-01', 3200.00, 200.00, 3000.00, 4)
]
cursor.executemany(folha_pagamento_query_sql, folha_pagamentos)


# COMMINTANDO se não nada tem efeito, ou seja, confirmando as alterações
conectar.commit()

cursor.close()
conectar.close()
