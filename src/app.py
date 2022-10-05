import email
from email.message import EmailMessage
from datetime import datetime
from tokenize import Double
from flask import Flask, render_template,request, url_for, redirect, session, flash, abort
from flask_mysqldb import MySQL
import funcs
import random

config = funcs.LoadConfig()

app = Flask(__name__)
app.secret_key = 'super secret key'
# Conexão ao banco de dados
app.config['MYSQL_HOST'] = config['host']
app.config['MYSQL_PORT'] = config['port'] #Caso a porta seja a padrão, comentar linha.
app.config['MYSQL_USER'] = config['user']
app.config['MYSQL_PASSWORD'] = config['password']
app.config['MYSQL_DB'] = config['db']

mysql = MySQL(app)
# Bloco de Paginas.

# Resumo dos comandos
    #Route  -> Caminho das paginas.
    #Def    -> Função de exibição da pagina.

#Pagina inicial
@app.route("/")
def index():
    session['login'] = False
    session['nome']  = None
    session['conta'] = None
    session['tipo']  = None
    return render_template('login.html')
#------------------------------

#Pagina Home
@app.route("/home", methods = ['POST', 'GET'])
def home():
    if session['login'] == False:
        abort(401)
    else:
        saldo = None
        itens = []
        idusu = []
        if session['tipo'] == 1:
            saldo = f"{session['saldo']:.2f}".replace(".",",")
            return render_template('home.html',saldo=saldo)
        else:
            # return render_template("requisicao.html", cabecalhoTabela=cabecalho, pesquisaSQLTabela=pesquisaSQL)
            saldo = f"{session['saldo']:.2f}".replace(".",",")
            return render_template('homeG.html',saldo=saldo,itens=itens)
#------------------------------

#Pagina Deposito
@app.route("/deposito")
def deposito():
    if session['saldo'] != None:
        saldo = f"{session['saldo']:.2f}".replace(".",",")
    return render_template('deposito.html',saldo=saldo)

#------------------------------

#Pagina Saque
@app.route("/saque")
def saque():
    saldo = f"{session['saldo']:.2f}".replace(".",",")
    return render_template('saque.html',saldo=saldo)
#------------------------------

@app.route("/SaqueConta",  methods = ['POST', 'GET'])
def SaqueConta():
    if request.method == "POST":
        valor = Double(request.form['valor'])
        if valor >= 0:
            capital_total = funcs.SlcEspecificoMySQL('tb_capitaltotal',
                                                    CampoBd=['id_capitaltotal'],
                                                    CampoFm=['1'],
                                                    CampoEs=['capitalinicial'])

            capital_externo = funcs.SlcEspecificoMySQL('tb_capitaltotal',
                                                    CampoBd=['id_capitaltotal'],
                                                    CampoFm=['1'],
                                                    CampoEs=['capitalexterno'])

            if valor <= capital_total[0][0]:
                valor = Double(session['saldo']) - valor

                funcs.upMySQL('tb_contabancaria',
                               CampoBd=['saldo'],
                               CampoFm=[valor],
                               CampoWr=['numeroconta'],
                               CampoPs=[session['conta']])

                saldoAtualizado = funcs.SlcEspecificoMySQL('tb_contabancaria ',
                                                            CampoBd=['numeroconta'],
                                                            CampoFm=[session['conta']],
                                                            CampoEs=['saldo'])

                idConta = funcs.SlcEspecificoMySQL('tb_contabancaria',
                                                            CampoBd=['numeroconta'],
                                                            CampoFm=[session['conta']],
                                                            CampoEs=['id_conta'])

                funcs.Transacao(idConta[0][0], idConta[0][0], 'Saque', Double(request.form['valor']), '1')

                for row in saldoAtualizado:
                    session['saldo'] = row[0]
                return saque()
            else:
                flash ("Não é possivel realizar o saque!")
                return redirect(url_for('saque'))
        else:
            return saque()

#------------------------------
#Deposito de Conta
@app.route("/depositoConta",  methods = ['POST', 'GET'])
def depositoConta():
    if request.method == "POST":

        valor = float(request.form['valor'])
        if valor >= 0:

            valor = valor + float(session['saldo'])

            saldoAtualizado = funcs.SlcEspecificoMySQL('tb_contabancaria ',
                                                        CampoBd=['numeroconta'],
                                                        CampoFm=[session['conta']],
                                                        CampoEs=['saldo'])

            idConta = funcs.SlcEspecificoMySQL('tb_contabancaria',
                                                        CampoBd=['numeroconta'],
                                                        CampoFm=[session['conta']],
                                                        CampoEs=['id_conta'])

            funcs.Transacao(idConta[0][0], idConta[0][0], 'Depósito', float(request.form['valor']), '0')

            for row in saldoAtualizado:
                session['saldo'] = row[0]
            return deposito()
        return deposito()

#Pagina de Cadastro
@app.route("/cadastro.html", methods = ['POST', 'GET'])
def cadastro():
    if request.method == "POST":
        #Variaveis vindas do FORM vindas do cadastro.html
        nome            = request.form['name']
        cpf             = funcs.TirarPontoeTraco(request.form['cpf'])
        endereco        = request.form['endereco']
        dataNascimento  = request.form['datanasc']
        genero          = request.form['genero']
        senha           = request.form['senha']
        tipoConta       = request.form['tipoconta']
        email           = request.form['email']

        funcs.InsMySQL('tb_usuario',CampoBd=['cpf', 'nome', 'genero', 'endereco', 'senha', 'datanascimento','ativo', 'email'],
                       CampoFm=[cpf,nome,genero,endereco, senha,dataNascimento,'0', email])

        resultado = funcs.SlcEspecificoMySQL('tb_usuario', CampoBd=['cpf'], CampoFm=[cpf], CampoEs=['id_usuario'])
        for row in resultado:
            id_usuario = row[0]
        #Gera o numero da conta, usando o nome do usuário, id da agência e o cpf do usuário
        numeroCampo = funcs.geraId(str(nome),str(1),str(cpf))
        funcs.InsMySQL('tb_contabancaria',
                        CampoBd=['id_usuario', 'id_agencia', 'tipo', 'data_abertura', 'numeroconta', 'saldo', 'status_contabancaria'],
                        CampoFm=[id_usuario, 1, tipoConta, datetime.today(), numeroCampo, 0, '0'])
        flash(numeroCampo)
        return render_template('login.html')

    return render_template('cadastro.html')
#------------------------------

#Pagina de Login
@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == "POST":
        #login do usuário comum
        numeroconta = request.form['numeroconta']
        senha       = request.form['senha']
        resultado   = funcs.SlcMySQL('''tb_usuario
                                        INNER JOIN tb_contabancaria
                                        ON tb_contabancaria.id_usuario = tb_usuario.id_usuario ''',
                                    CampoBd=['tb_contabancaria.numeroconta','tb_usuario.senha','tb_contabancaria.status_contabancaria'],
                                    CampoFm=[numeroconta,senha,'1'])

        if resultado:
            for row in resultado:
                session['nome']     = row[1]
                session['saldo']    = row[15]
            session['login'] = True
            session['conta'] = numeroconta
            session['tipo']  = 1
            return home()
        else:
            #Login de gerente geral e gerente de agência
            resultado   = funcs.SlcMySQL('''tb_usuario
                                            INNER JOIN tb_funcionario
                                            ON tb_funcionario.id_usuario = tb_usuario.id_usuario ''',
                                        CampoBd=['login','senha'],
                                        CampoFm=[numeroconta,senha])
            resultadocap = funcs.SlcMySQL('tb_capitaltotal',CampoBd=['id_capitaltotal'],CampoFm=['1'])
            if resultado:
                for row in resultado:
                    session['nome'] = row[1]
                session['login']    = True
                session['conta']    = numeroconta
                session['tipo']     = 2
                for row2 in resultadocap:
                    session['saldo']  = row2[1]
                return home()
            else:
                return index()
    else:
        abort(401)
#------------------------------

#Bloco de requisição padrão

@app.route("/deletarConta",  methods = ['POST', 'GET'])
def deletarConta():

    id_usuario = request.form['IdUsuario']

    funcs.DelMySQL(TabelaBd='tb_usuario',
                   CampoBd=['id_usuario'],
                   CampoFm=[id_usuario])

    return RequisicaoPadrao()


#------------------------------

#Bloco de requisição padrão

@app.route("/a")
def RequisicaoPadrao():
    cabecalho = ('Nome', 'CPF', 'Data Nasc', 'Endereço', 'Genero', '')

    pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_usuario',
                                           CampoEs=['id_usuario','nome', 'cpf','datanascimento','endereco','genero'],
                                           CampoBd=[],
                                           CampoFm=[])


    return render_template("requisicao.html", cabecalhoTabela=cabecalho, pesquisaSQLTabela=pesquisaSQL)


#------------------------------

#Bloco de conferência de depósito pendentes

@app.route("/ConferenciaDepositoTabela")
def ConferenciaDepositoTabela():
    if session['login'] == True:
        cabecalho = ('Nome', 'Número Conta', 'Valor', 'Data', '', '')

        pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_transacao INNER JOIN tb_contabancaria ON tb_contabancaria.id_conta = tb_transacao.id_conta_origem AND tb_contabancaria.id_conta = tb_transacao.id_conta_destino INNER JOIN tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                            CampoEs=['tb_transacao.id_transacao','tb_usuario.nome','tb_contabancaria.numeroconta' ,'tb_transacao.valor', 'tb_transacao.Datatime',],
                                            CampoBd=['status_transacao'],
                                            CampoFm=[0])

        return render_template("conferencia.html", cabecalhoTabela=cabecalho, pesquisaSQLTabela=pesquisaSQL)
    else:
        abort(401)

#Bloco de conferência de depósito pendentes

@app.route("/ConferenciaDeposito", methods = ['POST', 'GET'])
def ConferenciaDeposito():
    if request.method == "POST":

        botao = request.form.to_dict()

        IdTransacao =   request.form['IdTransacao']
        if botao['botao'] == 'Confirmar':

            pesquisaSQLTransacao =  funcs.SlcEspecificoMySQL(TabelaBd='tb_transacao',
                                                        CampoEs=['valor', 'id_conta_origem'],
                                                        CampoBd=['id_transacao'],
                                                        CampoFm=[IdTransacao])

            IdContaOrigem = pesquisaSQLTransacao[0][1]
            valorTransacao = pesquisaSQLTransacao[0][0]

            pesquisaSQLConta = funcs.SlcEspecificoMySQL(TabelaBd='tb_transacao INNER JOIN tb_contabancaria ON tb_contabancaria.id_conta = tb_transacao.id_conta_origem AND tb_contabancaria.id_conta = tb_transacao.id_conta_destino INNER JOIN tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                        CampoEs=['tb_contabancaria.id_conta' ,'tb_contabancaria.saldo'],
                                                        CampoBd=['id_transacao', 'tb_contabancaria.id_conta'],
                                                        CampoFm=[IdTransacao, IdContaOrigem])
            saldoConta = pesquisaSQLConta[0][1]
            valor = valorTransacao + saldoConta

            funcs.upMySQL(TabelaBd='tb_transacao',
                      CampoBd=['status_transacao'],
                      CampoFm=[1],
                      CampoPs=[IdTransacao],
                      CampoWr=['id_transacao'])

            funcs.upMySQL('tb_contabancaria',
                          CampoBd=['saldo'],
                          CampoFm=[valor],
                          CampoWr=['id_conta'],
                          CampoPs=[IdContaOrigem])
            return ConferenciaDepositoTabela()
        else:
            funcs.upMySQL(TabelaBd='tb_transacao',
                      CampoBd=['status_transacao'],
                      CampoFm=[2],
                      CampoPs=[IdTransacao],
                      CampoWr=['id_transacao'])
            return ConferenciaDepositoTabela()
 

#------------------------------

#Bloco de requisição padrão

@app.route("/AceiteConta", methods = ['POST', 'GET'])
def AceiteConta():
    if request.method == "POST":

        botao = request.form.to_dict()
        IdConta = request.form['IdConta']
        
        email = ''
        email = funcs.SlcEspecificoMySQL('tb_usuario INNER JOIN tb_contabancaria ON tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                     CampoBd=['tb_contabancaria.id_conta'],
                                     CampoFm=[IdConta],
                                     CampoEs=['tb_usuario.email'])

        if botao['botao'] == 'Confirmar':
            funcs.upMySQL('tb_contabancaria',CampoBd=['status_contabancaria'],CampoFm=[1],
                                        CampoWr=['id_conta'],CampoPs=[IdConta])
            funcs.mandaEmail(IdConta, email, True)  
            return AceiteContaTabela()
        else:    
            funcs.upMySQL('tb_contabancaria',CampoBd=['status_contabancaria'],CampoFm=[2],
                                        CampoWr=['id_conta'],CampoPs=[IdConta])
            funcs.mandaEmail(IdConta, email, False)  
            return AceiteContaTabela()
       

#------------------------------

#Bloco de requisição de Abertura de Conta

@app.route("/AceiteContaTabela")
def AceiteContaTabela():

    cabecalho = ('Nome', 'CPF', 'Número Conta', 'Data Nasc', 'Endereço', 'Genero', 'Tipo Conta', '', '')

    pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_usuario INNER JOIN tb_contabancaria ON tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                           CampoEs=['tb_contabancaria.id_conta','tb_usuario.nome', 'tb_usuario.cpf', 'tb_contabancaria.numeroconta','tb_usuario.datanascimento','tb_usuario.endereco','tb_usuario.genero', 'tb_contabancaria.tipo'],
                                           CampoBd=['tb_contabancaria.status_contabancaria'],
                                           CampoFm=[0])

    return render_template("AceiteConta.html", cabecalhoTabela=cabecalho, pesquisaSQLTabela=pesquisaSQL)

#------------------------------

#Tratamento de Erros
@app.errorhandler(Exception)
def excecao(e):
    cod_excecao = str(e)
    cod_excecao = cod_excecao[:3]
    print(f'{cod_excecao} - {funcs.erro[cod_excecao]}')
    return render_template("erro.html", cod_erro=cod_excecao, desc_erro=funcs.erro[cod_excecao])

#Bloco para subir o site.
if __name__ == "__main__":
     app.run(debug=True)
