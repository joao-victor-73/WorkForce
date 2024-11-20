-- CRIANDO DATABASE
DROP DATABASE IF EXISTS workforce;

CREATE DATABASE workforce;
USE workforce;


-- Criando tabela pessoas
-- Armazena informações pessoais dos colaboradores.
CREATE TABLE pessoas (
    id_pessoa INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    data_nascimento DATE,
    tel1 VARCHAR(20),
    tel2 VARCHAR(20),
    rua VARCHAR(100),
    bairro VARCHAR(50),
    num_residencia VARCHAR(10),
    cidade VARCHAR(30),
    cep VARCHAR(15)
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
        ON UPDATE CASCADE
);

-- Criando tabela departamentos
-- Armazena os departamentos da empresa
CREATE TABLE departamentos (
	id_departamento INT PRIMARY KEY AUTO_INCREMENT,
    nome_departamento VARCHAR(100) NOT NULL,
    fk_id_func INT, -- Supervisor também é um funcionário

    CONSTRAINT fk_departamento_funcionario
        FOREIGN KEY (fk_id_func) 
        REFERENCES funcionarios(id_func) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
);


ALTER TABLE funcionarios
ADD CONSTRAINT fk_funcionario_departamento 
	FOREIGN KEY (fk_id_departamento) 
	REFERENCES departamentos (id_departamento) 
	ON DELETE SET NULL 
	ON UPDATE CASCADE;



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
    data_pagamento VARCHAR(15) NOT NULL,
    tipo ENUM('HORISTA', 'FOLGUISTA', 'INTERMITENTE', 'MENSALISTA') NOT NULL DEFAULT 'HORISTA',
    nome_banco VARCHAR(100),
    num_agencia VARCHAR(50),
    conta_deposito VARCHAR(50),
    salario_base DECIMAL(10, 2) NOT NULL DEFAULT 1414.00,
    fk_id_func INT,
    fk_id_proventos INT,
    fk_id_deducoes INT,
    geracao_folha DATETIME DEFAULT CURRENT_TIMESTAMP,
        
        CONSTRAINT fk_folhaPagamento_funcionario
            FOREIGN KEY (fk_id_func) 
            REFERENCES funcionarios (id_func) 
            ON DELETE CASCADE 
            ON UPDATE CASCADE,
                             
        CONSTRAINT fk_folhaPagamento_provento
            FOREIGN KEY (fk_id_proventos)
            REFERENCES proventos_fpg (id_provento)
            ON DELETE CASCADE,
                             
        CONSTRAINT fk_folhaPagamento_deducao
            FOREIGN KEY (fk_id_deducoes)
            REFERENCES deducoes_fpg (id_deducao)
            ON DELETE CASCADE
);

-- CRIAÇÃO DE TABELAS INTERMEDIARIAS
-- As tabelas intermediárias vão relacionar múltiplos proventos e deduções a uma única folha de pagamento.
-- Assim permitindo que um funcinário tenha múltiplas informações na folha de pagamento.

CREATE TABLE folha_proventos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fk_id_pagamento INT,
    fk_id_provento INT,
    CONSTRAINT fk_folha_provento_pagamento
        FOREIGN KEY (fk_id_pagamento) 
        REFERENCES folha_pagamento(id_pagamento) 
        ON DELETE CASCADE,

    CONSTRAINT fk_folha_provento_provento
        FOREIGN KEY (fk_id_provento) 
        REFERENCES proventos_fpg(id_provento) 
        ON DELETE CASCADE
);


CREATE TABLE folha_deducoes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fk_id_pagamento INT,
    fk_id_deducao INT,
    CONSTRAINT fk_folha_deducao_pagamento
        FOREIGN KEY (fk_id_pagamento) 
        REFERENCES folha_pagamento(id_pagamento) 
        ON DELETE CASCADE,

    CONSTRAINT fk_folha_deducao_deducao
        FOREIGN KEY (fk_id_deducao) 
        REFERENCES deducoes_fpg(id_deducao) 
        ON DELETE CASCADE
);


-- CRIANDO TABELA LOGIN
-- Servirá para armazenar os registros para logar no sistema
CREATE TABLE login_usuarios (
	id INT PRIMARY KEY AUTO_INCREMENT,
    login_user VARCHAR(50) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL, 
    role ENUM('ADMIN', 'USER') DEFAULT 'USER',
    ativo BOOLEAN DEFAULT TRUE,
    fk_id_func INT,
    
    CONSTRAINT fk_login_funcionarios
		FOREIGN KEY (fk_id_func)
        REFERENCES funcionarios(id_func)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);



-- INSERINDO REGISTROS NAS TABELAS
-- Os INSERT's servirão para fazer testes na aplicação, não são de extrema necessidade
-- Para fazer a inserção dos dados, seguir a ordem como está


-- Inserindo dados na tabela pessoas
INSERT INTO pessoas (nome, cpf, data_nascimento, tel1, tel2, rua, bairro, num_residencia, cidade, cep)
VALUES 
('Alice Silva', '123.456.789-00', '1990-05-21', '(11) 91234-5678', '(11) 92345-6789', 'Rua das Flores', 'Centro', '123', 'São Paulo', '01001-000'),
('Carlos Pereira', '987.654.321-00', '1985-11-15', '(11) 99876-5432', NULL, 'Av. Paulista', 'Bela Vista', '456', 'São Paulo', '20040-001'),
('Rafaela Silvana Junior', '655.321.888-78', '1998-06-20', '(11) 99774-8552', NULL, 'Av. Paulista', 'Bela Vista', '23', 'São Paulo', '20040-001');

-- Inserindo dados na tabela departamentos
INSERT INTO departamentos (nome_departamento, fk_id_func)
VALUES 
('Recursos Humanos', NULL), 
('Financeiro', NULL),
('T.I.', NULL),
('Transporte', NULL),
('Comercial', NULL);

-- Inserindo dados na tabela funcionarios
INSERT INTO funcionarios (fk_id_pessoa, email, data_contratacao, nome_cargo, status_func, fk_id_departamento)
VALUES 
(1, 'alice.silva@empresa.com', '2023-01-10', 'Analista de RH', 'EFETIVO', 1),
(2, 'carlos.pereira@empresa.com', '2022-06-05', 'Contador', 'EFETIVO', 2),
(3, 'rafa.ela.junior@empresa.com', '2024-10-29','Supervisora T.I.', 'EFETIVO', 3);

-- Inserindo dados na tabela proventos_fpg
INSERT INTO proventos_fpg (desc_provento, valor_provento)
VALUES 
('Vale Alimentação', 50.00), 
('Bônus de Desempenho', 500.00), 
('Horas Extras', 200.00);

-- Inserindo dados na tabela deducoes_fpg
INSERT INTO deducoes_fpg (desc_deducao, valor_deducao)
VALUES 
('INSS', 120.00), 
('Imposto de Renda', 50.00), 
('Plano de Saúde', 100.00);

-- Inserindo dados na tabela folha_pagamento
INSERT INTO folha_pagamento (data_pagamento, tipo, nome_banco, num_agencia, conta_deposito, salario_base, fk_id_func)
VALUES 
('06-10', 'MENSALISTA', 'Banco do Brasil', '1234', '00012345-6', 1414.00, 1),
('06-10', 'HORISTA', 'Bradesco', '5678', '00098765-4', 1414.00, 2),
('06-10', 'HORISTA', 'Bradesco', '8899', '00014556-4', '3600.00', 3);

-- Inserindo dados na tabela folha_proventos
INSERT INTO folha_proventos (fk_id_pagamento, fk_id_provento)
VALUES 
(1, 1),  -- Relaciona o Salário Base com o pagamento 1
(1, 2),  -- Relaciona o Bônus de Desempenho com o pagamento 1
(2, 1),  -- Relaciona o Salário Base com o pagamento 2
(2, 3),  -- Relaciona as Horas Extras com o pagamento 2
(3, 1),
(3, 2);

-- Inserindo dados na tabela folha_deducoes
INSERT INTO folha_deducoes (fk_id_pagamento, fk_id_deducao)
VALUES 
(1, 1),  -- Relaciona o INSS com o pagamento 1
(1, 2),  -- Relaciona o Imposto de Renda com o pagamento 1
(2, 1),  -- Relaciona o INSS com o pagamento 2
(2, 3),  -- Relaciona o Plano de Saúde com o pagamento 2
(3, 1),
(3, 2);


-- Inserindo Logins para os usuários
INSERT INTO login_usuarios (login_user, senha_hash, role, fk_id_func) 
VALUES
('alice', '123456', 'admin', '1'),
('carlos', '654321', 'admin', '2');