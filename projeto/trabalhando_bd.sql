-- CRIANDO DATABASE
DROP DATABASE IF EXISTS workforce;

CREATE DATABASE workforce;
USE workforce;


-- Criando tabela departamentos
-- Armazena os departamentos da empresa
CREATE TABLE departamentos (
	id_departamento INT PRIMARY KEY AUTO_INCREMENT,
    nome_departamento VARCHAR(100) NOT NULL,
    fk_id_func INT -- Supervisor também é um funcionário

    CONSTRAINT fk_departamento_funcionario
        FOREIGN KEY (fk_id_func) 
        REFERENCES funcionarios(id_func) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE

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
    id_func INT PRIMARY KEY AUTO_INCREMENT, -- Vai ser como a matricula do funcionário
    fk_id_pessoa INT NOT NULL,
    email VARCHAR(100),
    data_contratacao DATE NOT NULL, -- Admissão
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



-- As duas tabelas abaixo serviram para informar sobre proventos e deduções, e a descrição sobre cada um deles

-- Armazena diferentes tipos de proventos (por exemplo, salário base, comissão, bônus, etc.).
CREATE TABLE proventos_fpg (
	id_provento INT PRIMARY KEY AUTO_INCREMENT, -- o id aqui vai ser tipo um código para servir de identificação
    desc_provento VARCHAR(300) NOT NULL,
    valor_provento DECIMAL(10, 2)
);


-- Armazena diferentes tipos de deduções (imposto de renda, INSS, etc.).
CREATE TABLE deducoes_fpg (
	id_deducao INT PRIMARY KEY AUTO_INCREMENT, -- o id aqui vai ser tipo um código para servir de identificação
    desc_deducao VARCHAR(300) NOT NULL,
    valor_deducao DECIMAL(10, 2)
);


-- Criando tabela folha_pagamentos
-- Armazena informações sobre os pagamentos dos funcionários.
CREATE TABLE folha_pagamento (
    id_pagamento INT PRIMARY KEY AUTO_INCREMENT,
    data_pagamento DATE NOT NULL,
    tipo ENUM('HORISTA', 'FOLGUISTA', 'INTERMITENTE', 'MENSALISTA', 'PJ') NOT NULL DEFAULT 'HORISTA',
    nome_banco VARCHAR(100),
    num_agencia VARCHAR(50),
    conta_deposito VARCHAR(50),
    salario_base DECIMAL(10, 2) NOT NULL DEFAULT 1414.00,
    fk_id_func INT,
    
    CONSTRAINT fk_folhaPagamento_funcionario 
		FOREIGN KEY (fk_id_func) 
        REFERENCES funcionarios (id_func) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- CRIAÇÃO DE TABELAS INTERMEDIARIAS
-- As tabelas intermediárias vão relacionar múltiplos proventos e deduções a uma única folha de pagamento.
-- Assim permitindo que um funcinário tenha múltiplas informações na folha de pagamento.

CREATE TABLE folha_proventos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fk_id_pagamento INT,
    fk_id_provento INT,
    CONSTRAINT fk_folha_provento_pagamento
        FOREIGN KEY (fk_id_pagamento) REFERENCES folha_pagamento(id_pagamento) ON DELETE CASCADE,
    CONSTRAINT fk_folha_provento_provento
        FOREIGN KEY (fk_id_provento) REFERENCES proventos_fpg(id_provento) ON DELETE CASCADE
);


CREATE TABLE folha_deducoes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fk_id_pagamento INT,
    fk_id_deducao INT,
    CONSTRAINT fk_folha_deducao_pagamento
        FOREIGN KEY (fk_id_pagamento) REFERENCES folha_pagamento(id_pagamento) ON DELETE CASCADE,
    CONSTRAINT fk_folha_deducao_deducao
        FOREIGN KEY (fk_id_deducao) REFERENCES deducoes_fpg(id_deducao) ON DELETE CASCADE
);


-- INSERINDO REGISTROS NAS TABELAS
-- Os INSERT's servirão para fazer testes na aplicação, não são de extrema necessidade
-- Para fazer a inserção dos dados, seguir a ordem como está


-- Tabela departamentos
INSERT INTO departamentos (nome_departamento) 
VALUES ('Recursos Humanos'), ('Tecnologia da Informação'), ('Marketing');


-- tabela pessoas
INSERT INTO pessoas (nome, cpf, data_nascimento, tel1, tel2, endereco, cidade)
VALUES 
('Carlos Silva', '123.456.789-00', '1985-06-15', '11999999999', NULL, 'Rua A, 100', 'São Paulo'),
('Ana Costa', '987.654.321-00', '1990-09-20', '11988888888', '1133333333', 'Rua B, 200', 'Rio de Janeiro'),
('Bruno Oliveira', '456.789.123-00', '1982-11-30', '11977777777', NULL, 'Rua C, 300', 'Curitiba');


-- tabela funcionarios
INSERT INTO funcionarios (fk_id_pessoa, email, data_contratacao, nome_cargo, status_func, fk_id_departamento)
VALUES 
(1, 'carlos.silva@empresa.com', '2022-01-15', 'Gerente de RH', 'EFETIVO', 1),
(2, 'ana.costa@empresa.com', '2023-02-01', 'Analista de Sistemas', 'EFETIVO', 2),
(3, 'bruno.oliveira@empresa.com', '2021-07-10', 'Coordenador de Marketing', 'EFETIVO', 3);


-- tabela proventos_fpg
INSERT INTO proventos_fpg (desc_provento, valor_provento)
VALUES 
('Salário Base', 3000.00),
('Bônus por Desempenho', 500.00),
('Comissão', 700.00);


-- tabela deducoes_fpg
INSERT INTO deducoes_fpg (desc_deducao, valor_deducao)
VALUES 
('INSS', 330.00),
('Imposto de Renda', 250.00),
('Plano de Saúde', 150.00);


-- tabela folha_pagamento
INSERT INTO folha_pagamento (data_pagamento, tipo, nome_banco, num_agencia, conta_deposito, salario_base, fk_id_func, fk_id_proventos, fk_id_deducoes)
VALUES 
('2024-10-05', 'MENSALISTA', 'Banco do Brasil', '1234-5', '987654', 3000.00, 1, 1, 1),
('2024-10-05', 'MENSALISTA', 'Bradesco', '4321-0', '123456', 3000.00, 2, 2, 2),
('2024-10-05', 'MENSALISTA', 'Bradesco', '5678-9', '654321', 3000.00, 3, 3, 3);


-- tabela folha_proventos
INSERT INTO folha_proventos (fk_id_pagamento, fk_id_provento)
VALUES 
(1, 1), -- Provento de salário base para o pagamento 1
(1, 2), -- Provento de bônus para o pagamento 1
(2, 1), -- Provento de salário base para o pagamento 2
(3, 1), -- Provento de salário base para o pagamento 3
(3, 3); -- Provento de comissão para o pagamento 3


-- tabela folha_deducoes
INSERT INTO folha_deducoes (fk_id_pagamento, fk_id_deducao)
VALUES 
(1, 1), -- Deducao INSS para o pagamento 1
(1, 2), -- Deducao IR para o pagamento 1
(2, 1), -- Deducao INSS para o pagamento 2
(3, 1), -- Deducao INSS para o pagamento 3
(3, 3); -- Deducao Plano de Saúde para o pagamento 3
