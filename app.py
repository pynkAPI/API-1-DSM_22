from flask import Flask, render_template

app = Flask(__name__)

#Bloco de Paginas.

#Resumo dos comandos 
    #Route  -> Caminho das paginas.
    #Def    -> Função de exibição da pagina.

#Pagina Home
@app.route("/")
def homepage():
    return render_template('index.html')
#------------------------------

#Bloco para subir o site.
if __name__ == "__main__":
    app.run(debug=True)
