<div align="center">

![readme_banner](src/templates/src/img/Banner.png)
</div>
<br id="top">
<p align="center" id="pseudo_nav">
    <a href="#sobre">Sobre</a> •
    <a href="#backlog">Backlog</a> •
    <a href="#doc">Documentação</a> •
    <a href="#metodologia">Metodologia</a> •
    <a href="#contato">Contatos</a> •
    <a href="#instalacao">Instalação</a>
</p>

<span id="sobre">

## •Sobre o Projeto
Baseado nos requisitos apresentados pelo cliente a Py.nk está desenvolvendo um sistema que fomentado sobre metodologias ágeis entrega um internet banking com funções básicas de funcionamento e uma interface de administração para gerenciamento da aplicação. Para a realização deste, três principais atores foram levantados: o **cliente** que pode ser chamado também de usuário comum, deve poder realizar a requisição de cadastro, login, emissão de extrato bancário, movimentações em conta (depósito em caixa, saque e transferência) que geram no momento de execução um comprovante, requisição de atualização de dados e requisição de fechamento de conta; o **gerente de agência** é a entidade que gerencia uma unidade do banco (agência), deve poder realizar qualquer operação que um usuário comum realiza e além disso deve conseguir aceitar ou recusar requisições de abertura de conta de usuário, aceitar ou recusar requisições de alteração de dados de clientes, realizar a conferência de depósito em caixa.

## •Sobre a API
• [To the top ↑](#top)

<span id="backlog">

## •Backlog
• [To the top ↑](#top)

<span id="doc">

## •Documentação
• [To the top ↑](#top)

<span id="metodologia">

## •Metodologia
• [To the top ↑](#top)

<span id="contato">

## •Contatos
• [To the top ↑](#top)

<span id="instalacao">

## •Instalação e utilização da aplicação
•Instalação
1. Baixe o Python
    
    No site oficial do Python na aba de downloads procure pelo seu sistema operacional e siga os passos de instalação.
    https://www.python.org/downloads/

2. Adicionando ao Path (sistemas Windows somente)

    Durante a instalação do Python no Windows se a opção de adicionar o Python no Path não for assinalada o sistema operacional não vai conseguir reconhecer o comando 'python' na linha de comando como uma variável de ambiente que remete as funções do Python, essa funcionalidade é necessária para a utilização da nossa aplicação. Portanto **DURANTE A INSTALAÇÃO DO PYTHON NO WINDOWS ASSINALE A OPÇÃO "ADD PYTHON <VERSÃO> TO PATH"**

•UTILIZANDO A APLICAÇÃO
1. Crie um diretório
- Crie um diretório e navegue até ele atraves da linha de comando.

```console 
    mkdir <nome do diretório>
    cd <nome do diretório>
```

2. Clone o repositório

```console 
    git clone https://github.com/pynkAPI/API-1-DSM_22.git .
```
- Repare que no final tem um ponto, ele é colocado propositalmente para que não seja criado mais um diretório dentro desse recém criado por você.

3. Crie um ambiente virutal

```console
    python -m venv <nome do ambiente>
```
- Utilizamos a variável de ambiente 'python' citada na sessão de instalação, caso esse comando falhe no seu ambiente tente:
```console
    python3 -m venv <nome do ambiente>
```
- Caso mesmo assim o diretório com o nome do ambiente não seja criado assegure-se que o **python está configurado em suas variáveis de ambiente** e tente novamente o processo. 

4. Executar o ambiente virtual

- No Windows:

```console
    cd <nome do ambiente>\Scripts
    activate.bat
```

- No Unix(Linux)/MacOS:
```console
    source <nome do ambiente>/bin/activate
```

5. Instalando dependências:

```console
    pip install -r requirements.txt
``` 

6. Executando a aplicação

- Navegue até a pasta src dentro dessa pasta raíz através da linha de comando e execute o arquivo 'app.py'. 
- Caso esteja usando Windows e esteja seguindo exatamente o que foi descrito no guia:

```console
    cd ..
    cd ..
    cd src
    python app.py
``` 

- Caso esteja usando Unix e esteja seguindo exatamente o que foi descrito no guia:

```console
    cd src
    python app.py
``` 

7. Entrando na aplicação
- Abra o navegador e digite a url que aparecerá no cmd após a execução do 'app.py'.
- **IMPORTANTE:** Não feche a janela do cmd enquanto estiver utilizando a aplicação. 

• [To the top ↑](#top)