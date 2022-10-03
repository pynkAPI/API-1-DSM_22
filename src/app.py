from datetime import datetime
from flask import Flask, render_template,request, url_for, redirect, session,flash
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
    saldo = None
    itens = []
    idusu = []
    if session['tipo'] == 1:
        saldo = f"{session['saldo']:.2f}".replace(".",",")
        return render_template('home.html',saldo=saldo)
    else:
        cabecalho = ('Nome', 'CPF', 'Data Nasc', 'Endereço', 'Genero', '')
        itens = funcs.SlcEspecificoMySQL('tb_contabancaria ',CampoBd=['status_contabancaria'],
                                                        CampoFm=['0'],CampoEs=['id_usuario','id_conta'])

        pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_usuario',
                                           CampoEs=['id_usuario','nome', 'cpf','datanascimento','endereco','genero'],
                                           CampoBd=[],
                                           CampoFm=[])

        # return render_template("requisicao.html", cabecalhoTabela=cabecalho, pesquisaSQLTabela=pesquisaSQL)

        saldo = f"{session['saldo']:.2f}".replace(".",",")
        return render_template('homeG.html',saldo=saldo,itens=itens,cabecalhoTabela=cabecalho, pesquisaSQLTabela=pesquisaSQL)
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
        valor = float(request.form['valor'])
        if valor >= 0:
            valor = float(session['saldo']) - valor

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

            funcs.Transacao(idConta[0][0], idConta[0][0], 'Saque', float(request.form['valor']), '1')

            for row in saldoAtualizado:
                session['saldo'] = row[0]
            return saque()
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

            funcs.Transacao(idConta[0][0], idConta[0][0], 'Depósito', valor, '0')

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
        funcs.InsMySQL('tb_usuario',CampoBd=['cpf', 'nome', 'genero', 'endereco', 'senha', 'datanascimento','ativo'],
                       CampoFm=[cpf,nome,genero,endereco, senha,dataNascimento,'0'])

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
            session['saldo']    = row[14]
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

@app.route("/conferenciaDepositoTabela")
def ConferenciaDepositoTabela():
    cabecalho = ('Nome', 'Número Conta', 'Valor', 'Data')

    pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='''tb_transacao 
                                                       INNER JOIN tb_contabancaria
                                                       ON tb_contabancaria.id_conta = tb_transacao.id_conta_origem
                                                       AND tb_contabancaria.id_conta = tb_transacao.id_conta_destino
                                                       INNER JOIN tb_usuario
                                                       ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario''',
                                           CampoEs=['tb_transacao.id_transacao','tb_usuario.nome','tb_contabancaria.numeroconta' ,'tb_transacao.valor', 'tb_transacao.Datatime',],
                                           CampoBd=['status_transacao'],
                                           CampoFm=[0])
    
    return render_template("conferencia.html", cabecalhoTabela=cabecalho, pesquisaSQLTabela=pesquisaSQL)

#Bloco de conferência de depósito pendentes

@app.route("/conferenciaDepositoTabela")
def ConferenciaDeposito():
    
    if request.method == "POST":

        IdTransacao =   request.form['IdTransacao']

        pesquisaSQLTransacao =  funcs.SlcEspecificoMySQL(TabelaBd='tb_transacao',
                                                        CampoEs=['valor', 'id_conta_origem'], 
                                                        CampoBd=['id_transacao'], 
                                                        CampoFm=[IdTransacao])
        
        pesquisaSQLConta = funcs.SlcEspecificoMySQL(TabelaBd='''tb_transacao 
                                                       INNER JOIN tb_contabancaria
                                                       ON tb_contabancaria.id_conta = tb_transacao.id_conta_origem
                                                       AND tb_contabancaria.id_conta = tb_transacao.id_conta_destino
                                                       INNER JOIN tb_usuario
                                                       ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario''',
                                                    CampoEs=['tb_contabancaria.id_conta' ,'tb_contabancaria.saldo'],
                                                    CampoBd=['id_transacao', 'tb_contabancaria.id_conta_origem'],
                                                    CampoFm=[IdTransacao, pesquisaSQLTransacao[1]])

        valor = pesquisaSQLTransacao[5] + pesquisaSQLConta[1]

        funcs.upMySQL(TabelaBd='tb_transacao',
                      CampoBd=['status_transacao'],
                      CampoFm=[1],
                      CampoPs=[IdTransacao],
                      CampoWr=['id_transacao'])

        funcs.upMySQL('tb_contabancaria',
                          CampoBd=['saldo'],
                          CampoFm=[valor],
                          CampoWr=['numeroconta'],
                          CampoPs=[session['conta']])

        saldoAtualizado = funcs.SlcEspecificoMySQL('tb_contabancaria ',
                                                        CampoBd=['numeroconta'],
                                                        CampoFm=[session['conta']],
                                                        CampoEs=['saldo'])
        

        
        return render_template("conferencia.html")
    return render_template("conferencia.html")
    
   


#------------------------------

#Bloco de requisição padrão

@app.route("/ReqAbertura", methods = ['POST', 'GET'])
def ReqAbertura():
    if request.method == "POST":
        ativo = request.form['verificacao']
        IdConta = request.form['IdConta']
        funcs.upMySQL('tb_contabancaria',CampoBd=['status_contabancaria'],CampoFm=[ativo],
                                        CampoWr=['id_conta'],CampoPs=[IdConta])
    return home()
#------------------------------

#Bloco para subir o site.
if __name__ == "__main__":
    app.run(debug=True)
