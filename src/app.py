#from crypt import methods
#from importlib.metadata import requires
from datetime import datetime
#from types import CellType
from flask import Flask, render_template,request, url_for, redirect, session,flash
from flask_mysqldb import MySQL
import funcs
import random

app = Flask(__name__)
app.secret_key = 'super secret key'
# Conexão ao banco de dados
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3307 #Caso a porta seja a padrão, comentar linha.
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'yyyetygvg1'
app.config['MYSQL_DB'] = 'pynk'

mysql = MySQL(app)
# Bloco de Paginas.

# Resumo dos comandos 
    #Route  -> Caminho das paginas.
    #Def    -> Função de exibição da pagina.

#Pagina inicial
@app.route("/")
def index():
    return render_template('login.html')
#------------------------------

#Pagina Home
@app.route("/home", methods = ['POST', 'GET'])
def home():
    saldo = f"{session['IDUsu']:.2f}".replace(".",",")
    return render_template('home.html',saldo=saldo)
#------------------------------

#Pagina Deposito
@app.route("/deposito")
def deposito():
    saldo = f"{session['IDUsu']:.2f}".replace(".",",")
    return render_template('deposito.html',saldo=saldo)
#------------------------------

#Pagina Saque
@app.route("/saque")
def saque():
    saldo = f"{session['IDUsu']:.2f}".replace(".",",")
    return render_template('saque.html',saldo=saldo)
#------------------------------

#Pagina de Cadastro
@app.route("/cadastro.html", methods = ['POST', 'GET'])
def cadastro():
    if request.method == "POST":
        #Variaveis vindas do FORM vindas do cadastro.html
        nome            = request.form['name']
        cpf             = request.form['cpf']
        endereco        = request.form['endereco']
        datanascimento  = request.form['datanasc']
        genero          = request.form['genero']
        senha           = request.form['senha']
        tipoconta       = request.form['tipoconta']
        funcs.InsMySQL('tb_usuario',CampoBd=['cpf', 'nome', 'genero', 'endereco', 'senha', 'datanascimento'],
                       CampoFm=[cpf,nome,genero,endereco, senha,datanascimento])
        
        id_usuario = funcs.SlcEspecificoMySQL('tb_usuario', CampoBd=['cpf'], CampoFm=[cpf], CampoEs=['id_usuario'])
        numerocampo = funcs.geraId(str(nome),str(id_usuario[0]),str(cpf))
        funcs.InsMySQL('tb_contabancaria', 
                        CampoBd=['id_usuario', 'id_agencia', 'tipo', 'data_abertura', 'numeroconta', 'saldo'],
                        CampoFm=[id_usuario[0], 1, tipoconta, datetime.today(), numerocampo, 0])
        flash(numerocampo)
        return render_template('login.html')
        
    return render_template('cadastro.html')
#------------------------------

#Pagina de Login
@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == "POST":
        numeroconta = request.form['numeroconta']
        senha       = request.form['senha']
        resultado   = funcs.SlcMySQL('''tb_usuario 
                                        INNER JOIN tb_contabancaria 
                                        ON tb_contabancaria.id_usuario = tb_usuario.id_usuario ''',
                                    CampoBd=['numeroconta','senha'],
                                    CampoFm=[numeroconta,senha])
    if resultado:
        session['login'] = True
        session['nome']  = resultado[1]
        session['IDUsu'] = resultado[13]
        return home()
    else:     
        return index()
#------------------------------

#Bloco para subir o site.
if __name__ == "__main__":
    app.run(debug=True)
   
