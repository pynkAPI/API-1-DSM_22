#from crypt import methods
from importlib.metadata import requires
from flask import Flask, render_template,request, url_for, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'super secret key'
# Conexão ao banco de dados
app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_PORT'] = 3307 #Caso a porta seja a padrão, comentar linha.
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mcs2809'
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

#Pagina de cadastro
@app.route("/cadastro.html")
def chama_cadastro():
    return render_template('cadastro.html')
#------------------------------

#Pagina de login
@app.route("/cadastro.html", methods = ['POST', 'GET'])
def cadastro():
    if request.method == "POST":
        #Variaveis vindas do FORM vindas do cadastro.html
        name = request.form['name']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        datanasc = request.form['datanasc']
        genero = request.form['genero']
        senha = request.form['senha']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO tb_usuario (cpf, nome, genero, endereco, senha, datanascimento) VALUES(%s,%s,%s,%s,%s,%s)''',(cpf,name,genero,endereco,senha,datanasc))
        mysql.connection.commit()
        cursor.close()
    return render_template('cadastro.html')
#------------------------------

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == "POST":
        cpf = request.form['cpf']
        senha = request.form['senha']
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT * FROM tb_usuario WHERE cpf = %s AND senha = %s ''',(cpf,senha))
        resultado = cursor.fetchone()
        mysql.connection.commit()
        cursor.close()
    if resultado:
        session['login'] = True
        session['nome'] = resultado[1]

        return redirect(url_for('home'))
    else:
        return render_template('login.html')


@app.route("/home", methods = ['POST', 'GET'])
def home():
    return render_template('home.html')

#Bloco para subir o site.
if __name__ == "__main__":
    app.run(debug=True)
   
