import mysql.connector  # pip install mysql-connector-python
from mysql.connector import errorcode
import bcrypt  # pip install bcrypt

print("CONECTANDO...")

try:
    conectar = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='jp2004'
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('Existe algo errado no nome de usuário ou senha.')
    else:
        print(err)

print('BANCO DE DADOS CONECTADO!')
cursor = conectar.cursor()


# Criando a base de dados e usando-a
cursor.execute("DROP DATABASE IF EXISTS `workforce`;")
print('CRIANDO DATABASE')
cursor.execute("CREATE DATABASE `workforce`;")
cursor.execute("USE `workforce`;")
print('DATABASE CRIADO')


# Criando as tabelas necessárias

# Criando tabela pessoas
cursor.execute('''
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
cursor.execute('''
    CREATE TABLE funcionarios (
        `id_func` INT PRIMARY KEY AUTO_INCREMENT,
        `fk_id_pessoa` INT NOT NULL,
        `email` VARCHAR(100),
        `data_contratacao` DATE NOT NULL,
        `nome_cargo` VARCHAR(100),
        `status_func` ENUM('EFETIVO', 'FERIAS', 'DEMITIDO', 'ATESTADO') NOT NULL DEFAULT 'EFETIVO',
        `fk_id_departamento` INT,
        CONSTRAINT `fk_funcionario_pessoa` 
            FOREIGN KEY (`fk_id_pessoa`) 
            REFERENCES pessoas (`id_pessoa`) 
            ON DELETE CASCADE 
            ON UPDATE CASCADE
    );
''')

# Criando tabela departamentos
cursor.execute('''
    CREATE TABLE departamentos (
        `id_departamento` INT PRIMARY KEY AUTO_INCREMENT,
        `nome_departamento` VARCHAR(100) NOT NULL,
        `fk_id_func` INT,
        CONSTRAINT `fk_departamento_funcionario`
            FOREIGN KEY (`fk_id_func`) 
            REFERENCES funcionarios (`id_func`) 
            ON DELETE SET NULL 
            ON UPDATE CASCADE
    );
''')

# Criando tabela login_usuarios
cursor.execute('''
    CREATE TABLE login_usuarios(
        `id` INT PRIMARY KEY AUTO_INCREMENT,
        `login_user` VARCHAR(50) NOT NULL UNIQUE,
        `senha_hash` VARCHAR(255) NOT NULL,
        `role` ENUM('ADMIN', 'USER') DEFAULT 'USER',
        `ativo` BOOLEAN DEFAULT TRUE,
        `fk_id_func` INT,
        CONSTRAINT `fk_login_funcionarios`
        FOREIGN KEY(`fk_id_func`)
        REFERENCES funcionarios(`id_func`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );
''')

# Criando a função para gerar o hash da senha
def gerar_senha_hash(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

# Inserindo dados fictícios
departamento_query_sql = 'INSERT INTO departamentos (nome_departamento) VALUES (%s)'
departamentos = [
    ('Recursos Humanos', ),
    ('Financeiro', ),
    ('T.I.', ),
    ('Transporte', ),
    ('Comercial', )
]
cursor.executemany(departamento_query_sql, departamentos)

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

funcionarios_query_sql = 'INSERT INTO funcionarios (fk_id_pessoa, email, data_contratacao, nome_cargo, status_func, fk_id_departamento) VALUES (%s, %s, %s, %s, %s, %s)'
funcionarios = [
    (1, 'alice.silva@empresa.com', '2023-01-10', 'Analista de RH', 'EFETIVO', 1),
    (2, 'carlos.pereira@empresa.com', '2022-06-05', 'Contador', 'EFETIVO', 2),
    (3, 'rafa.ela.junior@empresa.com', '2024-10-29', 'Supervisora T.I.', 'EFETIVO', 3)
]
cursor.executemany(funcionarios_query_sql, funcionarios)

# Inserindo dados na tabela login_usuarios com hash de senha
login_usuarios_query_sql = 'INSERT INTO login_usuarios (login_user, senha_hash, role, ativo, fk_id_func) VALUES (%s, %s, %s, %s, %s)'

# Senha de exemplo
senha = 'minha_senha'
senha_hash = gerar_senha_hash(senha)  # Gerando o hash da senha

# Dados de exemplo para o login
login_usuarios = [
    ('alice.silva', senha_hash, 'ADMIN', True, 1),
    ('carlos.pereira', senha_hash, 'USER', True, 2),
    ('rafaela.junior', senha_hash, 'USER', True, 3)
]

cursor.executemany(login_usuarios_query_sql, login_usuarios)

# Confirmando as alterações no banco
conectar.commit()

cursor.close()
conectar.close()
