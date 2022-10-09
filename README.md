<div align="center">

![readme_banner](doc/img/bannerPynk.png)
</div>
<br id="top">
<p align="center" id="pseudo_nav">
    <a href="#sobre">Sobre</a> •
    <a href="#metodologia">Metodologia</a> •
    <a href="#backlogEus">Backlog e US</a> •
    <a href="#contato">Contatos</a> •
    <a href="#instalacao">Instalação</a>
</p>

<span id="sobre">

## •Sobre o Projeto
Baseado nos requisitos apresentados pelo cliente a Py.nk está desenvolvendo um sistema que fomentado sobre metodologias ágeis entrega um internet banking com funções básicas de funcionamento e uma interface de administração para gerenciamento da aplicação. Para a realização deste, três principais atores foram levantados: o **cliente** que pode ser chamado também de usuário comum, deve poder realizar a requisição de cadastro, login, emissão de extrato bancário, movimentações em conta (depósito em caixa, saque e transferência) que geram no momento de execução um comprovante, requisição de atualização de dados e requisição de fechamento de conta; o **gerente de agência** é a entidade que gerencia uma unidade do banco (agência), deve poder realizar qualquer operação que um usuário comum realiza e além disso deve conseguir aceitar ou recusar requisições de abertura de conta de usuário, aceitar ou recusar requisições de alteração de dados de clientes, realizar a conferência de depósito em caixa e requerir alteração de seus próprios dados ao gerente geral; o **gerente geral** (além de todas as outras funcionalidades citadas das outras entidades) deve ter acesso ao gerenciamento das agências, dos gerentes de agência e do montante total do banco. Além das funcionalidades dos usuário o banco também deve conter tratativas para problemas como o arredondamento de casas decimais, rendimento de poupança e etc.

## •Sobre a API
#### •Sprint 1
A Sprint 1 ocorreu dentro dos conformes, erramos detalhes de execução como comentários pouco descritivos no Git e apresentação. Porém, foi muito importante no sentido de entendermos o passo do time, reconhecermos fragilidades e barreiras pessoais. Os **acertos** percebidos pelo time foram a **cooperação**, **empenho**, **entrega** e **organização**. Enquanto que os **erros** foram mal organização da **sprint planning**, **tempo de estudo irreal** e **ausência** de alguns integrantes do grupo. É bom ressaltar que muitos desses erros foram causados por falta de conhecimento ou pouca experiência do grupo e que esses pontos foram levantados em conjunto com todos os integrantes.

**Destaque da Sprint 1**: Felipe Augusto Graciano

**Burndown Chart da Sprint 1**:

<img src="/doc/img/Burndown Sprint 1.png">

- Nota: Como podemos observar no Burndown, nós erramos no planejamento e estouramos as horas que estavam planejadas. Isso se deve a falta de familiaridade com o próprio tempo de desenvolvimento e pela falta de um método lógico para estimativa de tempo durante a sprint planning.

**GIF do Produto entregue na Sprint 1**:

<img src="/doc/img/Gif Programa Sprint 1.gif">


• [To the top ↑](#top)

<span id="metodologia">

## •Metodologia

O projeto está sendo desenvolvido utilizando **metodologias ágeis** de gerenciamento, no nosso caso o **SCRUM**.
Também achamos pertinente adotar um método de **estimativa de tempo de desenvolvimento** chamado **Estimativa PERT (Program Evaluation and Review Technique)** que consiste em uma fórmula que pondera matematicamente um espectro de estimativas que possui três possiveis elementos de tempo: **otimista**, **mais provavel** e **pessimista**. O que a fórmula faz é reajustar a amostra para algo que apesar de considerar extremos, avalia eles como avaria dando um peso maior pro tempo que comumente vai acontecer mais (mais provável). A fórmula foi implementada na Sprint 2 e tem se mostrado muito assertiva. Outro ponto interessante para ser abordado é que apesar de o nome ser **API** o programa não é uma **Application Programming Interface**, isso pois o nome se dá a metodologia de aprendizado implantada na **Fatec SJC** que inclusive atingiu **reconhecimento internacional** pelo **MIT (Massachusetts Institute of Technology)** com um selo chamado **CDIO (Conceive Design Implement Operate)**. **Aprendizagem por Projetos Integrados** é o nome da metodologia de ensino que por padrão esta contemplada no nome do projeto.

• [To the top ↑](#top)

<span id="backlog">

## •Backlog e US

- Nota: A coluna ID Requisição do Backlog está associada a um arquivo de circulação interna acordado com o cliente. Este não está contemplado por motivos de privacidade do mesmo, entretanto, a coluna foi mantida para fins avaliativos.

<div align="center" class="stories">

#### User Stories

|  ID  |                                                                                                 US                                                                                                | Sprint |
|:----:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:------:|
| US01 | Eu, enquanto usuário comum, desejo realizar depósitos em espécie, para conseguir realizar operações com meu dinheiro dentro do banco.                                                             |    1   |
| US02 | Eu, enquanto usuário comum, desejo realizar saques em caixa, para retirar o dinheiro guardado no banco.                                                                                           |    1   |
| US03 | Eu, enquanto usuário comum, desejo realizar requisição de abertura de conta, para abrir uma conta dentro do banco.                                                                                |    1   |
| US04 | Eu, enquanto usuário comum, desejo realizar a requisição de alteração de dados, para atualizar meus dados cadastrais.                                                                             |    2   |
| US05 | Eu, enquanto usuário comum, desejo realizar a requisição de cancelamento de conta, para cancelar uma conta dentro do banco.                                                                       |    2   |
| US06 | Eu, enquanto usuário comum, desejo realizar movimentações de dinheiro da minha conta para outra conta do mesmo banco utilizando uma "chave", para realizar transferências de dinheiro.            |    2   |
| US07 | Eu, enquanto usuário comum, desejo que seja realziado emissão de comprovantes imediatamente após qualquer operação, para conseguir comprovar minhas movimentações feitas em minha conta bancária  |    2   |
| US08 | Eu, enquanto Gerente de Agência, desejo ter todas as funcionalidades de um usuário comum, para poder ter um conta dentro do banco como um cliente.                                                |    2   |
| US09 | Eu, enquanto Gerente de Agência, desejo ver todas operações de depósito em caixa de minha agência, para após a conferência "física" aceitar ou recusar a operação.                                |    2   |
| US10 | Eu, enquanto Gerente de Agência, desejo ver todas as requisições de abertura de conta de minha agência, para poder recusar ou aceitar a abertura de conta.                                        |    2   |
| US11 | Eu, enquanto Gerente de Agência, desejo ver as requisições de alteração de dados cadastrais de usuários de minha agência, para aceitar ou recusar a operação.                                     |    2   |
| US12 | Eu, enquanto Gerente de Agência, desejo ver todas as requisições de cancelamento de conta bancárias, para poder cancelar uma conta que não esteja devendo ou tenha nenhum dinheiro guardado.      |    2   |
| US13 | Eu, enquanto Gerente Geral, desejo ter todas as funcionalidades de um usuário comum e um Gerente de Agência, para que não haja restrições internas de sistema.                                    |    3   |
| US14 | Eu enquanto gerente Geral, desejo gerenciar usuário do tipo gerente de agência, para poder alterar, criar, deletar, ver todos os Gerentes de Agências e ver atrelar um gerente a uma Agência.     |    3   |
| US15 | Eu, enquanto Gerente Geral, desejo gerenciar Agências, para poder alterar, criar, deletar e ver todas as Agências.                                                                                |    3   |
| US16 | Eu, enquanto Gerente Geral, desejo alterar o capital total do banco, para atualizar o capital do banco e corrigir inconsistências.                                                                |    3   |
| US17 | Eu, enquanto usuário comum (cliente), desejo ter uma interface acessível e intuitiva, para ter uma boa experiência durante a utilização do sistema.                                               |    3   |
| US18 | Eu, enquanto Gerente Geral, desejo que toda movimentação de dinheiro altera o valor total de acordo com o tipo de transação, para que o capital total do banco tenha consistência com a realidade |    4   |
| US19 | Eu, enquanto Usuário comum, desejo que quando meu saldo fique negativo minha conta em status de cheque especial, para que eu posso realizar empréstimos do banco                                  |    4   |

#### Product Backlog
| **Sprint** | **ID US** | **ID Função** | **ID Requisição** | **Funções**                                                                               | **Prioridade** | **Status**   |
|------------|-----------|---------------|-------------------|-------------------------------------------------------------------------------------------|----------------|--------------|
|      1     |    US01   |      F.1      |        RF.3       | Depósito em espécie                                                                       |      ALTA      |     Feito    |
|      1     |    US02   |      F.2      |        RF.3       | Saque em espécie                                                                          |      ALTA      |     Feito    |
|      1     |    US10   |      F.3      |        RF.3       | Criação de conta de usuário comum                                                         |      ALTA      |     Feito    |
|      2     |    US07   |      F.4      |        RF.3       | Geração de extratos                                                                       |      MÉDIA     |     Feito    |
|      2     |    US07   |      F.4      |        RF.3       | Emissão de Comprovante                                                                    |      MÉDIA     |     Feito    |
|      2     |    US09   |      F.5      |        RF.2       | Conferência de depósito                                                                   |      MÉDIA     |     Feito    |
|      2     |    US04   |      F.6      |        RF.3       | Requisição de alteração de dados                                                          |      MÉDIA     | Em andamento |
|      2     |    US05   |      F.7      |        RF.3       | Requisição de cancelamento de conta                                                       |      MÉDIA     | Em andamento |
|      2     |    US03   |      F.8      |        RF.3       | Requisição de criação de conta                                                            |      MÉDIA     | Em andamento |
|      2     |    US06   |      F.9      |        RF.3       | Transferência em contas do mesmo banco*                                                   |      MÉDIA     |     Feito    |
|      2     |    US18   |      F.10     |        RF.6       | Não aceitar qualquer saque que extrapole o valor total do banco.                          |      MÉDIA     |     Feito    |
|      2     |    US10   |      F.11     |        RF.2       | Aceite ou recusa de requisição de abertura de conta                                       |      MÉDIA     |     Feito    |
|      2     |    US11   |      F.12     |        RF.2       | Aceite ou recusa de requisição alteração de dados de usuário                              |      MÉDIA     |     Feito    |
|      3     |    US12   |      F.13     |        RF.2       | Aceite ou recusa de requisição de fechamento de conta de usuário                          |      MÉDIA     |  Em aguardo  |
|      3     |    US15   |      F.14     |        RF.1       | Criar Agência                                                                             |      MÉDIA     |  Em aguardo  |
|      3     |    US14   |      F.15     |        RF.1       | Criar Gerente de Agência                                                                  |      MÉDIA     |  Em aguardo  |
|      3     |    US14   |      F.16     |        RF.1       | Alterar dados de Gerente de Agência                                                       |      BAIXA     |  Em aguardo  |
|      3     |    US14   |      F.17     |        RF.1       | Deletar Gerente de Agência                                                                |      BAIXA     |  Em aguardo  |
|      3     |    US14   |      F.18     |        RF.1       | Atrelar Gerente de Agência a uma Agência                                                  |      BAIXA     |  Em aguardo  |
|      4     |    US16   |      F.19     |        RF.1       | Gerenciar o capital total do banco                                                        |      BAIXA     |  Em aguardo  |
|      4     |    US15   |      F.20     |        RF.1       | Fechamento de agência                                                                     |      BAIXA     |  Em aguardo  |
|      4     |    US15   |      F.21     |        RF.1       | Alterar dados de Agência                                                                  |      BAIXA     |  Em aguardo  |
|      4     |    US18   |      F.22     |     RF.4, RF.5    | Alteração do capital total do banco de acordo com os saques e Depósitos                   |      BAIXA     |  Em aguardo  |
|      4     |    US19   |      F.23     |    RF.12, RF.13   | Função de cheque especial                                                                 |      BAIXA     |  Em aguardo  |
|      4     |    US20   |      F.24     |        RF.7       | Truncamento dos valores com as correções apropriadas para evitar inconsistência de dados. |      BAIXA     |  Em aguardo  |


</div>

• [To the top ↑](#top)

<span id="contato">

## •Contatos
<div align="center" class="contatos">

|               Nome              |      Cargo     |                GitHub               |                            LinkedIn                            |
|:-------------------------------:|:--------------:|:-----------------------------------:|:--------------------------------------------------------------:|
|      Miguel Carvalho Soares     |      P.O.      |     https://github.com/Miguel-C1    |  https://www.linkedin.com/in/miguel-carvalho-soares-722b161a3/ |
|  Otávio Abreu dos Santos Silva  |     Master     |   https://github.com/otavioabreu27  |              https://www.linkedin.com/in/o-abreu/              |
|    Yasmin Helena Souza Mosena   | Desenvolvedora |      https://github.com/ymosena     |    https://www.linkedin.com/in/yasmin-m%C3%B3sena-11b256249/   |
|     Matheus Guermandi Costa     |  Desenvolvedor |  https://github.com/mguermandi1204  | https://www.linkedin.com/in/matheus-guermandi-costa-07a029244/ |
| Pedro Henrique Silva De Almeida |  Desenvolvedor | https://github.com/PedroHSdeAlmeida |          https://www.linkedin.com/in/pedrohsalmeidaa/          |
|        Felipe Silva Alves       |  Desenvolvedor |     https://github.com/fealvesfe    |    https://www.linkedin.com/in/felipe-silva-alves-b43651200/   |
|      Augusto Henrique Buin      |  Desenvolvedor |    https://github.com/AugustoBuin   |  https://www.linkedin.com/in/augusto-henrique-buin-a58bb0208/  |
|     Felipe Augusto Graciano     |  Desenvolvedor |      https://github.com/Yetgvg      |                                -                               |

</div>

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

- Navegue até a raiz do diretório e execute o comando:
```console
    pip install -r requirements.txt
```

6. Executando a aplicação

- Navegue até a pasta src dentro dessa pasta raíz através da linha de comando e execute o arquivo 'app.py'.

```console
    cd src
    python app.py
```  

7. Entrando na aplicação
- Abra o navegador e digite a url que aparecerá no cmd após a execução do 'app.py'.
- **IMPORTANTE:** Não feche a janela do cmd enquanto estiver utilizando a aplicação.

•Banco de dados
1. Abra o seu SGBD e importe o Script SQL
- Dentro do seu sistema de gerenciamento de banco de dados procure pela opção de importar Script SQL.
- Após importado execute todas as linhas.

2. Credenciais do Banco
- Dentro da pasta src existe um arquivo chamado "config.conf", altere as credenciais do banco respeitando os espaçamentos de acordo com o seu ambiente, para isso utilize o editor de texto de sua preferência.

• [To the top ↑](#top)
