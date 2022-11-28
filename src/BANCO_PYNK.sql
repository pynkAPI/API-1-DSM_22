DROP DATABASE IF EXISTS pynk;

CREATE DATABASE pynk;

USE pynk;

CREATE TABLE tb_usuario (
id_usuario int PRIMARY KEY auto_increment,
nome varchar(255) NOT NULL,
email varchar(255) NOT NULL,
cpf varchar(25) NOT NULL UNIQUE,
genero varchar(25) NOT NULL,
endereco varchar(50) NOT NULL,
datanascimento date NOT NULL,
senha varchar(100) NOT NULL,
ativo varchar(1) NOT NULL
);

CREATE TABLE tb_funcionario (
id_funcionario int AUTO_INCREMENT PRIMARY KEY,
id_usuario int NOT NULL,
papel varchar(255) NOT NULL,
num_matricula varchar(255) NOT NULL,
login VARCHAR(255) NOT NULL, 
FOREIGN KEY(id_usuario) REFERENCES tb_usuario (id_usuario)
);

CREATE TABLE tb_capitaltotal (
id_capitaltotal int AUTO_INCREMENT PRIMARY KEY,
capitalinicial double NOT NULL,
capitalexterno double NOT NULL
);

CREATE TABLE tb_contabancaria (
id_conta int AUTO_INCREMENT PRIMARY KEY,
id_usuario int NOT NULL,
id_agencia int NOT NULL,
tipo varchar(255) NOT NULL,
numeroconta varchar(50) NOT NULL UNIQUE,
data_abertura date NOT NULL,
saldo double NOT NULL,
status_contabancaria varchar(1) NOT NULL,
FOREIGN KEY(id_usuario) REFERENCES tb_usuario (id_usuario)
);


CREATE TABLE tb_transacao (
id_transacao int PRIMARY KEY auto_increment,
id_conta_origem int NOT NULL,
id_conta_destino int NOT NULL,
Datatime datetime NOT NULL,
data_aceite_recusa datetime,
tipo varchar(50) NOT NULL,
valor double NOT NULL,
status_transacao varchar(1) NOT NULL
);

CREATE TABLE tb_agencia (
id_agencia int AUTO_INCREMENT PRIMARY KEY,
localidade varchar(255) NOT NULL,
id_funcionario int,
numero_agencia VARCHAR(25) NOT NULL,
status_agencia VARCHAR(1) NOT NULL,
FOREIGN KEY(id_funcionario) REFERENCES tb_funcionario (id_funcionario)
);

CREATE TABLE tb_requisicoes(
id_requisicao int AUTO_INCREMENT PRIMARY KEY,
status_alteracao varchar(1) NOT NULL,
id_usuario INT NOT NULL,
id_funcionario INT,
FOREIGN KEY(id_usuario) REFERENCES tb_usuario (id_usuario),
descricao VARCHAR(255)
);

CREATE TABLE tb_cheque_especial(
id_cheque_especial INT  AUTO_INCREMENT PRIMARY KEY,
id_conta INT NOT NULL,
data_inicio DATE NOT NULL,
data_atualizacao DATE NOT NULL,
data_final DATE,
valor_devido FLOAT NOT NULL,
ativo boolean NOT NULL
);



ALTER TABLE tb_cheque_especial ADD FOREIGN KEY(id_conta) REFERENCES tb_contabancaria (id_conta);

CREATE TABLE tb_poupanca(
id_poupanca INT  AUTO_INCREMENT PRIMARY KEY,
id_conta INT NOT NULL,
data_inicio DATE NOT NULL,
data_atualizacao DATE NOT NULL,
data_final DATE,
valor_poupanca FLOAT NOT NULL,
ativo boolean NOT NULL
);

ALTER TABLE tb_poupanca ADD FOREIGN KEY(id_conta) REFERENCES tb_contabancaria (id_conta);

CREATE TABLE tb_regra_operacoes(
id_regra_operacoes int AUTO_INCREMENT PRIMARY KEY,
descricao varchar(255) NOT NULL,
porcentagem float NOT NULL,
valor_fixo float NOT NULL,
frequencia VARCHAR(55) NOT NULL);

ALTER TABLE tb_transacao ADD FOREIGN KEY(id_conta_origem) REFERENCES tb_contabancaria (id_conta);
ALTER TABLE tb_transacao ADD FOREIGN KEY(id_conta_destino) REFERENCES tb_contabancaria (id_conta);

INSERT INTO tb_regra_operacoes(descricao, porcentagem, valor_fixo, frequencia) VALUES('CHEQUE ESPECIAL',  0, 0, 'Diário');
INSERT INTO tb_regra_operacoes(descricao, porcentagem, valor_fixo, frequencia) VALUES('CONTA POUPANÇA',  0, 0, 'Mensal');


INSERT INTO tb_usuario (nome, cpf, genero, endereco, datanascimento, senha, ativo, email) 
VALUES('GERENTE GERAL', '1',  'O', 'ENDERECO DOS BOBOS', curdate(), 'senha', '1', 'teste@gmail.com');


INSERT INTO tb_funcionario(papel, num_matricula, id_usuario, login) 
VALUES('GERENTE GERAL', '0', 1, 'GG');