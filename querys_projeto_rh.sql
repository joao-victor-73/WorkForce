USE workforce;


SHOW TABLES;




-- VERIFICANDO AS TABELAS
DESC pessoas;
DESC funcionarios;
DESC departamentos;

DESC folha_pagamento;
DESC folha_deducoes;
DESC folha_proventos;
DESC deducoes_fpg;
DESC proventos_fpg;


-- FAZENDO OS SELECT

SELECT * FROM pessoas;
SELECT * FROM departamentos;
SELECT * FROM funcionarios;

SELECT * FROM folha_pagamento;

SELECT * FROM deducoes_fpg;
SELECT * FROM proventos_fpg;

SELECT * FROM folha_proventos;
SELECT * FROM folha_deducoes;










-- tabela departamentos
INSERT INTO departamentos (nome_departamento, fk_id_func)
VALUES 
('Recursos Humanos', NULL),
('Desenvolvimento', NULL),
('Marketing', NULL);

-- tabela pessoas
INSERT INTO pessoas (nome, cpf, data_nascimento, tel1, tel2, endereco, cidade)
VALUES
('Carlos Silva', '123.456.789-00', '1990-05-15', '99999-1234', '88888-4321', 'Rua A, 123', 'São Paulo'),
('Ana Pereira', '987.654.321-11', '1985-12-30', '99999-4321', '87777-5678', 'Rua B, 456', 'Rio de Janeiro'),
('Marcos Souza', '741.852.963-22', '1992-08-25', '91111-5678', '92222-7890', 'Rua C, 789', 'Belo Horizonte');


-- tabela proventos_fpg
INSERT INTO proventos_fpg (desc_provento, valor_provento)
VALUES
('Salário Base', 3000.00),
('Bônus de Desempenho', 500.00),
('Comissão', 250.00);


-- tabela deducoes_fpg
INSERT INTO deducoes_fpg (desc_deducao, valor_deducao)
VALUES
('INSS', 300.00),
('Imposto de Renda', 450.00),
('Plano de Saúde', 200.00);


-- DESC folha_pagamento;
-- tabela folha de pagamentos
INSERT INTO folha_pagamento (data_pagamento, tipo, num_banco, num_agencia, conta_deposito, salario_base, fk_id_func)
VALUES
('2024-10-01', 'MENSALISTA', '001', '1234', '98765-0', 3000.00, 1),
('2024-10-01', 'MENSALISTA', '033', '5678', '54321-9', 4500.00, 2),
('2024-10-01', 'MENSALISTA', '104', '8765', '11122-0', 3500.00, 3);


-- DESC funcionarios;
-- tabela funcionarios
INSERT INTO funcionarios (fk_id_pessoa, email, data_contratacao, nome_cargo, status_func, fk_id_departamento)
VALUES
(1, 'carlos@empresa.com', '2022-01-10', 'Analista de RH', 'EFETIVO', 1),
(2, 'ana@empresa.com', '2021-03-15', 'Desenvolvedora Sênior', 'EFETIVO', 2),
(3, 'marcos@empresa.com', '2023-07-20', 'Gerente de Marketing', 'EFETIVO', 3);


-- tabela folha_proventos
INSERT INTO folha_proventos (fk_id_pagamento, fk_id_provento)
VALUES
(4, 1),  -- Carlos Silva: Salário Base
(4, 2),  -- Carlos Silva: Bônus de Desempenho
(5, 1),  -- Ana Pereira: Salário Base
(5, 3),  -- Ana Pereira: Comissão
(6, 1);  -- Marcos Souza: Salário Base


-- tabela folha_deducoes
INSERT INTO folha_deducoes (fk_id_pagamento, fk_id_deducao)
VALUES
(4, 1),  -- Carlos Silva: INSS
(4, 3),  -- Carlos Silva: Plano de Saúde
(5, 2),  -- Ana Pereira: Imposto de Renda
(5, 3),  -- Ana Pereira: Plano de Saúde
(6, 1),  -- Marcos Souza: INSS
(6, 2);  -- Marcos Souza: Imposto de Renda


SELECT * FROM funcionarios;

SELECT 
	f.id_func,
    p.nome AS nome_funcionario,
    d.nome_departamento,
    f.nome_cargo,
    f.status_func,
    fp.data_pagamento,
    fp.salario_base,
    fp.nome_banco,
    fp.num_agencia,
    fp.conta_deposito
FROM 
    funcionarios f
INNER JOIN pessoas p 
ON f.fk_id_pessoa = p.id_pessoa
	LEFT JOIN departamentos d 
    ON f.fk_id_departamento = d.id_departamento
		INNER JOIN folha_pagamento fp 
        ON f.id_func = fp.fk_id_func
ORDER BY 
    f.id_func;

SELECT * FROM departamentos;
SELECT * FROM pessoas;
SELECT * FROM funcionarios;
SELECT * FROM folha_pagamento;

DELETE FROM pessoas
WHERE id_pessoa = 11;

DELETE FROM departamentos
WHERE id_departamento = 7;



-- TESTANDO MANEIRAS PARA DELETAR O CADASTRO DE UM FUNCIONÁRIO
-- (para teste, usaremos o id do funcionário: Paulo Freire = 7)

-- Primeiramente, garantir que o funcionário existe
SELECT * FROM funcionarios 
WHERE id_func = 7;

-- Excluindo funcionário (o que aciona as exclusões em cascata nas tabelas relacionadas)
DELETE FROM funcionarios 
WHERE id_func = 7;

-- Excluindo os dados pessoais, se não forem mais necessários
DELETE FROM pessoas WHERE id_pessoa = (
    SELECT fk_id_pessoa FROM funcionarios 
    WHERE id_func = 7
);


select * from funcionarios
INNER JOIN pessoas
ON fk_id_pessoa = id_pessoa
where pessoas.cidade = 'Timbauba';


-- BUSCANDO AS INFORMAÇÕES DO FUNCIONÁRIO + PESSOAIS
select * from funcionarios
INNER JOIN pessoas
ON fk_id_pessoa = id_pessoa;


-- BUSCANDO TODAS AS INFORMAÇÕES DO FUNCIONARIO (PESSOAIS, PAGAMENTOS E TRABALHO)
select * from funcionarios
INNER JOIN pessoas
ON fk_id_pessoa = id_pessoa
	INNER JOIN folha_pagamento
    on fk_id_func = id_func;



-- BUSCANDO INFORMAÇÕES COMPLETAS (INCLUNDO OS PROVENTOS E DEDUÇÕES)
-- Ainda tem algumas coisas a resolver, está dando duplicada de informações
SELECT 
    f.id_func AS funcionario_id,
    p.nome AS nome_funcionario,
    fp.id_pagamento AS folha_id,
    fp.data_pagamento,
    fp.salario_base,
    d.desc_deducao AS deducao_descricao,
    d.valor_deducao,
    pr.desc_provento AS provento_descricao,
    pr.valor_provento
FROM Funcionarios f
INNER JOIN Pessoas p 
ON f.fk_id_pessoa = p.id_pessoa -- Relacionamento com a tabela de pessoas
	LEFT JOIN folha_pagamento fp 
    ON fp.fk_id_func = f.id_func -- Relacionamento com folha de pagamento
		LEFT JOIN folha_deducoes fd 
        ON fd.fk_id_pagamento = fp.id_pagamento -- Relacionamento com deduções da folha
			LEFT JOIN deducoes_fpg d 
			ON fd.fk_id_deducao = d.id_deducao -- Detalhes das deduções
				LEFT JOIN folha_proventos fpv 
				ON fpv.fk_id_pagamento = fp.id_pagamento -- Relacionamento com proventos da folha
					LEFT JOIN proventos_fpg pr 
					ON fpv.fk_id_provento = pr.id_provento -- Detalhes dos proventos
ORDER BY f.id_func, fp.id_pagamento;

-- WHERE fp.data_pagamento BETWEEN '2024-11-01' AND '2024-11-30' -- Filtrar por período (opcional)

SELECT * FROM deducoes_fpg;
SELECT * FROM proventos_fpg;

select * from login_usuarios;

-- VERIFICANDO LOGINS ASSOCIADOS A FUNCIONARIOS
SELECT * FROM login_usuarios 
inner join funcionarios
on fk_id_func = id_func;


-- VERIFICANDO A QUANTIDADE DE FUNCIONÁRIOS POR DEPARTAMENTOS
select * from departamentos;
select * from funcionarios;

SELECT d.nome_departamento AS Departamento, COUNT(f.id_func) AS total_funcionarios
FROM departamentos d
LEFT JOIN funcionarios f ON d.id_departamento = f.fk_id_departamento
GROUP BY d.id_departamento, d.nome_departamento;


-- VERIFICANDO QUAIS FUNCIONARIOS SÃO SUPERVISORES E O NOME DO DEPARTAMENTO
describe funcionarios;
SELECT * FROM departamentos;
SELECT * FROM funcionarios;


SELECT f.id_func, p.nome AS nome_funcionario, d.nome_departamento
FROM Funcionarios f
INNER JOIN Pessoas p 
ON f.fk_id_pessoa = p.id_pessoa
	INNER JOIN departamentos d
    ON f.fk_id_departamento = d.id_departamento
WHERE f.id_func IN (SELECT fk_id_func FROM departamentos WHERE fk_id_func IS NOT NULL);


SELECT f.id_func, p.nome AS nome_funcionario, d.nome_departamento
FROM Funcionarios f
INNER JOIN Pessoas p 
ON f.fk_id_pessoa = p.id_pessoa
	INNER JOIN departamentos d
    ON f.fk_id_departamento = d.id_departamento
WHERE f.id_func = 6;


SELECT id_departamento, nome_departamento, fk_id_func
FROM Departamentos
WHERE id_departamento BETWEEN 1 AND 10;
