from flask import Flask, render_template,request, url_for, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)
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

#Pagina de cadastro
@app.route("/cadastro.html")
def Cadastro():
    return render_template('cadastro.html')
#------------------------------

#Pagina de login
@app.route("/login.html", methods = ['POST', 'GET'])
def login():
    if request.method == "POST":
        #Variaveis vindas do FORM vindas do cadastro.html
        name = request.form['name']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        datanasc = request.form['datanasc']
        genero = request.form['genero']
        senha = request.form['senha']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO tb_usuario (cpf, nome, genero, endereço, senha, datanascimento) VALUES(%s,%s,%s,%s,%s,%s)''',(cpf,name,genero,endereco,senha,datanasc))
        mysql.connection.commit()
        cursor.close()
    return render_template('login.html')
#------------------------------

#Bloco para subir o site.
if __name__ == "__main__":
    app.run(debug=True)
