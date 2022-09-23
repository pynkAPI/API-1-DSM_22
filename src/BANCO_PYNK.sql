

CREATE DATABASE pynk;

USE pynk;

CREATE TABLE tb_usuario (
id_usuario int PRIMARY KEY auto_increment,
nome varchar(255) NOT NULL,
cpf varchar(25) NOT NULL UNIQUE,
genero varchar(25) NOT NULL,
endereco varchar(50) NOT NULL,
datanascimento date NOT NULL,
senha varchar(100) NOT NULL
);

CREATE TABLE tb_funcionario (
id_funcionario int AUTO_INCREMENT PRIMARY KEY,
id_usuario int NOT NULL,
papel varchar(255) NOT NULL,
num_matricola varchar(255) NOT NULL,
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
FOREIGN KEY(id_usuario) REFERENCES tb_usuario (id_usuario)
);


CREATE TABLE tb_transacao (
id_transacao int PRIMARY KEY auto_increment,
id_conta_origem int NOT NULL,
id_conta_destino int NOT NULL,
Datatime datetime NOT NULL,
tipo varchar(50) NOT NULL,
valor double NOT NULL
);

CREATE TABLE tb_agencia (
id_agencia int AUTO_INCREMENT PRIMARY KEY,
localidade varchar(255) NOT NULL,
id_funcionario int NOT NULL,
numero_agencia VARCHAR(25) NOT NULL,
FOREIGN KEY(id_funcionario) REFERENCES tb_funcionario (id_funcionario)
);


ALTER TABLE tb_transacao ADD FOREIGN KEY(id_conta_origem) REFERENCES tb_contabancaria (id_conta);
ALTER TABLE tb_transacao ADD FOREIGN KEY(id_conta_destino) REFERENCES tb_contabancaria (id_conta);

INSERT INTO tb_capitaltotal 
VALUES(1, 10000,0);
INSERT INTO tb_usuario (nome, cpf, genero, endereco, datanascimento, senha) 
VALUES('GERENTE GERAL', '0',  'OUTROS', 'ENDERECO DOS BOBOS', curdate(), 'senha');
INSERT INTO tb_funcionario(papel, num_matricola, id_usuario, login) 
VALUES('GERENTE DE AGÊNCIA', '0', 1, 'GA1');
INSERT INTO tb_agencia(localidade, id_funcionario, numero_agencia)
VALUES('SP', 1, '0001');