-- CRIANDO DATABASE
CREATE DATABASE workforce;

USE workforce;


-- Criando tabela departamentos
CREATE TABLE departamentos (
	id_departamento INT PRIMARY KEY AUTO_INCREMENT,
    nome_departamento VARCHAR(100) NOT NULL,
    id_gerente INT UNIQUE
);


-- Criando tabela cargos
CREATE TABLE cargos (
	id_cargo INT PRIMARY KEY AUTO_INCREMENT,
    nome_cargo VARCHAR(100)
);


-- Criando tabela funcionarios
CREATE TABLE funcionarios(
	id_func INT PRIMARY KEY AUTO_INCREMENT,
    nome_func VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100),
    tel1 VARCHAR(15) NOT NULL,
    tel2 VARCHAR(15),
    data_contratacao DATE NOT NULL,
    salario DECIMAL(10, 2),
    status_func ENUM('EFETIVO', 'FERIAS' , 'DEMITIDO', 'ATESTADO'),
    fk_id_cargo INT,
    fk_id_departamento INT, 
    CONSTRAINT fk_funcionario_cargo
		FOREIGN KEY (fk_id_cargo)
        REFERENCES cargos (id_cargo)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
	
    CONSTRAINT fk_funcionario_departamento
		FOREIGN KEY (fk_id_departamento)
        REFERENCES departamentos (id_departamento)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- Criando tabela folha_pagamentos
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
DESC funcionarios;
DESC cargos;
DESC departamentos;
DESC folha_pagamento;