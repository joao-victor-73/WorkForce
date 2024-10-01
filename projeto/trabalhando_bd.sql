-- CRIANDO DATABASE
DROP DATABASE IF EXISTS workforce;

CREATE DATABASE workforce;
USE workforce;


-- Criando tabela departamentos
-- Armazena os departamentos da empresa
CREATE TABLE departamentos (
	id_departamento INT PRIMARY KEY AUTO_INCREMENT,
    nome_departamento VARCHAR(100) NOT NULL,
    nome_supervisor VARCHAR(100)
);



-- Criando tabela pessoas
-- Armazena informações pessoais dos colaboradores.
CREATE TABLE pessoas (
    id_pessoa INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    data_nascimento DATE,
    tel1 VARCHAR(20),
    tel2 VARCHAR(20),
    endereco VARCHAR(100),
    cidade VARCHAR(30)
);


-- Criando tabela funcionarios
--  Armazena informações relacionadas aos funcionários, vinculando-os a informações pessoais, cargos e departamentos.
CREATE TABLE funcionarios (
    id_func INT PRIMARY KEY AUTO_INCREMENT,
    fk_id_pessoa INT NOT NULL,
    email VARCHAR(100),
    data_contratacao DATE NOT NULL,
    salario DECIMAL(10, 2) NOT NULL,
    nome_cargo VARCHAR(100),
    status_func ENUM('EFETIVO', 'FERIAS', 'DEMITIDO', 'ATESTADO') NOT NULL DEFAULT 'EFETIVO',
    fk_id_departamento INT,
    
    CONSTRAINT fk_funcionario_pessoa 
		FOREIGN KEY (fk_id_pessoa) 
        REFERENCES pessoas (id_pessoa) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_funcionario_departamento 
		FOREIGN KEY (fk_id_departamento) 
        REFERENCES departamentos (id_departamento) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
);



-- Criando tabela folha_pagamentos
-- Armazena informações sobre os pagamentos dos funcionários.
CREATE TABLE folha_pagamento (
    id_pagamento INT PRIMARY KEY AUTO_INCREMENT,
    data_pagamento DATE NOT NULL,
    salario_base DECIMAL(10, 2) NOT NULL,
    deducoes DECIMAL(10, 2) NOT NULL,
    salario_liquido DECIMAL(10, 2) NOT NULL,
    fk_id_func INT,
    
    CONSTRAINT fk_folhaPagamento_funcionario 
		FOREIGN KEY (fk_id_func) 
        REFERENCES funcionarios (id_func) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);




-- VERIFICANDO AS TABELAS
DESC pessoas;
DESC funcionarios;
DESC departamentos;
DESC folha_pagamento;



-- INSERINDO REGISTROS NAS TABELAS

INSERT INTO departamentos (nome_departamento, nome_supervisor) VALUES 
('Recursos Humanos', 'Ana Clara Silva'),
('Desenvolvimento', 'Marcos Almeida'),
('Vendas', 'Fernanda Costa'),
('Marketing', 'Lucas Pereira');


INSERT INTO pessoas (nome, cpf, data_nascimento, tel1, tel2, endereco, cidade) VALUES 
('João Carlos', '123.456.789-00', '1985-06-12', '(11) 99999-1111', '(11) 98888-2222', 'Rua A, 123', 'São Paulo'),
('Maria Souza', '987.654.321-00', '1990-08-25', '(21) 99999-3333', NULL, 'Av. B, 456', 'Rio de Janeiro'),
('Pedro Lima', '456.789.123-00', '1982-04-15', '(31) 99999-4444', '(31) 98888-5555', 'Rua C, 789', 'Belo Horizonte'),
('Carla Mendes', '789.123.456-00', '1995-09-30', '(41) 99999-6666', NULL, 'Av. D, 321', 'Curitiba');


INSERT INTO funcionarios (fk_id_pessoa, email, data_contratacao, salario, nome_cargo, status_func, fk_id_departamento) VALUES 
(1, 'joao.carlos@empresa.com', '2020-01-10', 3500.00, 1, 'EFETIVO', 1),
(2, 'maria.souza@empresa.com', '2018-07-15', 4500.00, 2, 'FERIAS', 2),
(3, 'pedro.lima@empresa.com', '2015-05-22', 6000.00, 3, 'EFETIVO', 3),
(4, 'carla.mendes@empresa.com', '2019-10-12', 3200.00, 4, 'ATESTADO', 4);


INSERT INTO folha_pagamento (data_pagamento, salario_base, deducoes, salario_liquido, fk_id_func) VALUES 
('2024-09-01', 3500.00, 300.00, 3200.00, 1),
('2024-09-01', 4500.00, 500.00, 4000.00, 2),
('2024-09-01', 6000.00, 600.00, 5400.00, 3),
('2024-09-01', 3200.00, 200.00, 3000.00, 4);


-- TRAZENDO OS REGISTROS

SELECT * FROM pessoas;
SELECT * FROM departamentos;
SELECT * FROM funcionarios;
SELECT * FROM folha_pagamento;