from email.message import EmailMessage
import ssl
import smtplib
from importlib.metadata import requires
from flask import Flask, render_template,request, url_for, redirect, session
from flask_mysqldb import MySQL
import datetime
import random

app = Flask(__name__)
app.secret_key = 'super secret key'

mysql = MySQL(app)

def SlcMySQL(TabelaBd,CampoBd,CampoFm):
    x=0
    cursor = mysql.connection.cursor()
    textoSQL = f' SELECT * FROM {TabelaBd} where'
    for values in CampoBd:
        if x==0:
            textoSQL+= f' {CampoBd[x]} = "{CampoFm[x]}" '
        else:
            textoSQL+= f' and {CampoBd[x]} = "{CampoFm[x]}"'
        x+=1

    cursor.execute(textoSQL)
    resultado = cursor.fetchall()
    mysql.connection.commit()
    cursor.close()
    return resultado

def SlcEspecificoMySQL(TabelaBd,CampoBd,CampoFm, CampoEs):
    x=0
    y=0
    cursor = mysql.connection.cursor()
    textoSQL = ''
    for values in CampoEs:
        if y==0:
            textoSQL += f'SELECT {CampoEs[y]}'
        else:
            textoSQL += f', {CampoEs[y]}'
        y+=1
    textoSQL += f' FROM {TabelaBd}'
    for values in CampoBd:
        if x==0:
            textoSQL+= f' WHERE {CampoBd[x]} = "{CampoFm[x]}" '
        else:
            textoSQL+= f' and {CampoBd[x]} = "{CampoFm[x]}"'
        x+=1
    cursor.execute(textoSQL)
    resultado = cursor.fetchall()
    mysql.connection.commit()
    cursor.close()
    return resultado

def InsMySQL(TabelaBd,CampoBd,CampoFm):
    x=0
    ValuesBD = '('
    ValuesFm = '('
    cursor = mysql.connection.cursor()
    textoSQL = f' INSERT INTO {TabelaBd} '
    for values in CampoBd:
        if values == CampoBd[-1]:
            ValuesBD += f'{CampoBd[x]})'
            ValuesFm += f'"{CampoFm[x]}")'
        else:
            ValuesBD += f'{CampoBd[x]},'
            ValuesFm += f'"{CampoFm[x]}",'
        x+=1
    textoSQL += f' {ValuesBD} VALUES{ValuesFm}'
    cursor.execute(textoSQL)
    mysql.connection.commit()
    cursor.close()

def upMySQL(TabelaBd,CampoBd,CampoFm,CampoWr,CampoPs):
    x=0
    y=0
    cursor = mysql.connection.cursor()
    textoSQL = f' UPDATE {TabelaBd} SET '
    for values in CampoBd:
        if x == 0:
            textoSQL += f'{CampoBd[x]} = "{CampoFm[x]}" '
        else:
            textoSQL += f', {CampoBd[x]} = "{CampoFm[x]}" '
        x+=1

    for values in CampoWr:
        if y == 0:
            textoSQL += f'WHERE {CampoWr[y]} = "{CampoPs[y]}"'
        else:
            textoSQL += f'AND {CampoWr[y]} = "{CampoPs[y]}"'
        y+=1

    cursor.execute(textoSQL)
    mysql.connection.commit()
    cursor.close()

def DelMySQL(TabelaBd,CampoBd,CampoFm):
    x=0
    cursor = mysql.connection.cursor()
    textoSQL = f' DELETE FROM {TabelaBd} WHERE '
    for values in CampoBd:
        if x==0:
            textoSQL+= f'{CampoBd[x]} = {CampoFm[x]} '
        else:
            textoSQL+= f' and {CampoBd[x]} = {CampoFm[x]}'
        x+=1
    cursor.execute(textoSQL)
    resultado = cursor.fetchone()
    mysql.connection.commit()
    cursor.close()
    return resultado


def geraId(nome, agencia, cpf):
    #O id é gerado a partir de alguns processos de criptografia
    #os primeiros 4 digitos são gerados a partir do id da agência
    #os próximos 4 digitos são valores randomicos do cpf do usuario
    #os próximos 4 digitos são valores criptografados a partir do nome do usuario
    alfabetoCript = ['e', 'd', 'n', 'z', 'w', 'f', 't', 'u', 'p', 'o', 's', 'v', 'y', 'r', 'j', 'x', 'i', 'a', 'm', 'b', 'q', 'c', 'g', 'h', 'k', 'l']
    nome = nome.lower()
    arr_nome = nome.split(" ")
    letra_prim_nome = arr_nome[0][0:1]
    letra_seg_nome = ''
    if len(arr_nome)<1:
        letra_seg_nome = arr_nome[1][0:1]
    format_agencia = ""
    arr_cpf = []
    cont_caractere = 0

    #completa com zeros a esquerda caso a agência tenha menos que 4 caracteres no id
    if len(agencia) < 4:
        qt_zeros = 4 - len(agencia)
        while qt_zeros != 0:
            format_agencia += '0'
            qt_zeros -= 1
        format_agencia += agencia
        agencia = format_agencia

    nummeroConta = agencia

    #gerando um array com os valores splitados
    for num in cpf:
        arr_cpf.append(num)

    #gerando e adicionando 4 valores random a string idUsuario
    while cont_caractere < 4:
        #gerar valor aleatorio 4 vezes dentro do limite do array (lenght)
        random_index = random.randint(0, len(arr_cpf)-1)
        nummeroConta += arr_cpf [random_index]
        cont_caractere += 1

    nummeroConta += str(alfabetoCript.index(letra_prim_nome))
    if letra_seg_nome:
        nummeroConta += str(alfabetoCript.index(letra_seg_nome))

    #caso não some 12 caracteres esse while concatena zeros ao final da string
    while len(nummeroConta)<12:
        nummeroConta += '0'

    return nummeroConta

def TirarPontoeTraco(CPF):
    CPF = CPF.replace(".","")
    CPF = CPF.replace("-","")
    return CPF

def Transacao(conta_origem, conta_destino, tipo, valor, status):
    data = datetime.datetime.now()
    InsMySQL('tb_transacao',
            CampoBd = ['id_conta_origem','id_conta_destino','Datatime','tipo','valor', 'status_transacao'],
            CampoFm = [conta_origem, conta_destino, data, tipo, valor, status])

    id_ultima_movimentacao = SlcEspecificoMySQL(TabelaBd='tb_transacao',
                                                CampoBd=['id_conta_origem'],
                                                CampoFm=[conta_origem],
                                                CampoEs=['max(id_transacao)'])

    dados_transacao = SlcEspecificoMySQL(TabelaBd='tb_transacao',
                                        CampoBd=['id_transacao'],
                                        CampoFm=[id_ultima_movimentacao[0][0]],
                                        CampoEs=['*'])
    
    nome_origem = SlcEspecificoMySQL (TabelaBd='tb_usuario',
                                    CampoBd=[],
                                    CampoFm=[],
                                    CampoEs=[])
    movimentacao = {
        'conta_origem' : '123456',
        'nome_origem' : 'Alisson Fabricio da Silva',
        'conta_destino' : '000193029000',
        'nome_destino' : 'Otávio Abreu dos Santos Silva',
        'tipo' : 'Transferência',
        'dataHora' : '2022-10-06 17:34:51',
        'id' : '1',
        'valor' : '20340'
    }
    
    # if tipo == "Saque":

    # elif tipo == "Depósito":
    
    # elif tipo == "Transferência":
    
    

def LoadConfig():
    config = {}
    conf = open("config.conf", "r")
    for line in conf:
        line = line.strip()
        if line[:4] == 'host':
            config['host'] = line[7:]
        elif line[:4] == 'port':
            config['port'] = int(line[6:])
        elif line[:4] == 'user':
            config['user'] = line[7:]
        elif line[:8] == 'password':
            config['password'] = line[11:]
        elif line[:2] == 'db':
            config['db'] = line[5:]
    conf.close()
    return config

def cancelMySQL(id_usuario):
    cursor = mysql.connection.cursor()
    SlcEspecificoMySQL('tb_contabancaria','id_usuario',id_usuario, saldo)
    if saldo > 0:
        return "Saque seu dinheiro antes de cancelar sua conta!"
    elif saldo < 0:
        return "Corrija sua situação bancária antes de cancelar sua conta!"
    else:
        textoSQL = f'UPDATE tb_usuario set ativo = "0" where id_usuario = {id_usuario}'

    cursor.execute(textoSQL)
    resultado = cursor.fetchall()
    mysql.connection.commit()
    cursor.close()
    return "Cancelamento efetuado com sucesso"

def mandaEmail(id, destinatario, aceite):
    remetente = "py.nk.fatec@gmail.com"
    senha = "hjdixtkskjwtvxqr"
    if aceite == True:
        numeroconta = SlcEspecificoMySQL('tb_contabancaria',
                                         CampoBd=['id_conta'],
                                         CampoFm=[id],
                                         CampoEs=['numeroconta'])
        
        
        assunto = 'Bem vindo ao Py.NK!'
        corpo = f'''Seja bem vindo(a)! 
        Nós do PyNK agradecemos a preferência, utilize o código {str(numeroconta)[3:-5]} para acessar sua conta.'''

    elif aceite == False:
        assunto = 'Irregularidade no cadastro Py.NK.'
        corpo = f'''Olá, algo de errado aconteceu.
        Durante a triagem do seu cadastro o Py.NK encontrou algumas divergências, sua conta não foi criada.'''

    em = EmailMessage()
    em['From'] = remetente
    em['To'] = destinatario
    em['subject'] = assunto
    em.set_content(corpo)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(remetente, senha)
        smtp.sendmail(remetente, destinatario, em.as_string())
     
erro = {'400': 'O servidor não entendeu a requisição pois está com uma sintaxe inválida.',
'401': 'Antes de fazer essa requisição se autentifique. Credenciais inválidas.',
'404': 'Página não encontrada.',
'403': 'Acesso restrito.',
'500': 'Erro interno do servidor.',
'503': 'Serviço indisponível.',
'504': 'Gateway timeout'}
