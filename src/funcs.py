from logging import raiseExceptions
import math
import os
from dateutil.relativedelta import relativedelta
from importlib.metadata import requires
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from importlib.metadata import requires
from flask import Flask, render_template,request, url_for, redirect, session, abort
from flask_mysqldb import MySQL
from datetime import datetime
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

def SlcEspecificoComORMySQL(TabelaBd,CampoBd,CampoFm, CampoEs,CampoWrAO):
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
        if CampoWrAO[x] == 0:
            if x==0:
                textoSQL+= f' WHERE {CampoBd[x]} = "{CampoFm[x]}" '
            else:
                if CampoWrAO[x+1] == 0:
                    textoSQL+= f' and {CampoBd[x]} = "{CampoFm[x]}"'
                else:
                    textoSQL+= f' and ({CampoBd[x]} = "{CampoFm[x]}"'
        else:
            if x==0:
                textoSQL+= f' WHERE {CampoBd[x]} = "{CampoFm[x]}" '
            else:
                textoSQL+= f' or {CampoBd[x]} = "{CampoFm[x]}"'
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
    data = datetime.now()
    InsMySQL('tb_transacao',
            CampoBd = ['id_conta_origem','id_conta_destino','Datatime','tipo','valor', 'status_transacao'],
            CampoFm = [conta_origem, conta_destino, data, tipo, valor, status])

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

def cancelMySQL(id_usuario, senha, numeroconta):
    pesquisa = SlcEspecificoMySQL(TabelaBd='tb_contabancaria INNER JOIN tb_usuario ON tb_contabancaria.id_usuario = tb_usuario.id_usuario',
                               CampoBd=['tb_usuario.id_usuario', 'tb_contabancaria.numeroconta'],
                               CampoFm=[id_usuario, numeroconta], 
                               CampoEs=['saldo', 'tb_usuario.senha'])
    saldo = pesquisa[0][0]
    senhaUsuario = pesquisa[0][1]
    if senha == senhaUsuario:
            upMySQL(TabelaBd='tb_contabancaria',
                CampoBd=['status_contabancaria'],
                CampoFm=[2],
                CampoWr=['id_usuario', 'numeroconta'],
                CampoPs=[id_usuario, numeroconta])
    else:
        raise Exception('401')


def periodoEntreDatas(data1, data2):
    data1 = datetime.strptime(data1, "%Y-%m-%d")
    data2 = datetime.strptime(data2, "%Y-%m-%d")
    return abs((data2 - data1).days)

def verificaAniversarioDeposito(data1, data2):
    aniversario = False
    contadora = 0
    data1 = data1 + relativedelta(months=1)
    if data1 >= data2:
        contadora += 1
        aniversario = True
        while data1 >= data2:
            data1 = data1 + relativedelta(months=1)
            contadora += 1    
    retorna = [aniversario, contadora]
    return retorna



     
erro = {'400': 'O servidor não entendeu a requisição pois está com uma sintaxe inválida.',
'401': 'Antes de fazer essa requisição se autentifique. Credenciais inválidas.',
'404': 'Página não encontrada.',
'403': 'Acesso restrito.',
'500': 'Erro interno do servidor.',
'503': 'Serviço indisponível.',
'504': 'Gateway timeout',
'601' : 'Você ainda possui saldo em conta, realize o saque e depois prossiga com o cancelamento',
'602' : 'Você ainda possui pendências  com o banco, regularize sua situação antes de prosseguir com o cancelamento',
'603' : 'Você cancelou a sua conta com sucesso.',
'604' : 'Esta agência já existe.'}

def calculaChequeEspecial(valorDevido, tempo, porecentagem):
    #Calcula o juros composto por dia
    valor = ((1+porecentagem)**tempo)*valorDevido
    #realiza o truncamento para maior precisão 
    valorTruncado = truncar(numero=valor,casaDecimal=3)
    #realiza a correção de acordo com a regra feita pelo cliente
    valorTruncado = valorTruncado - 0.005
    #realiza o truncamento para a correção do valor em duas casas decimais
    valorTruncado = truncar(numero=valorTruncado,casaDecimal=2)
    return valorTruncado

def calculaPoupanca(valorPoupanca, tempo, porecentagem):
    valor = ((1+porecentagem)**tempo)*valorPoupanca
    valorTruncado = truncar(numero=valor,casaDecimal=3)
    valorTruncado = valorTruncado - 0.005
    valorTruncado = truncar(numero=valorTruncado,casaDecimal=2)
    return valorTruncado

def truncar(numero, casaDecimal):
    s = '{}'.format(numero)
    if 'e' in s or 'E' in s:
        valorTruncado='{0:.{1}f}'.format(numero, casaDecimal)
        return float(valorTruncado)
    i, p, d = s.partition('.')
    valorTruncado = '.'.join([i, (d+'0'*casaDecimal)[:casaDecimal]])
    return float(valorTruncado)
   
   

def ValEmReal(valor):
    valor = f"{valor:.2f}".replace(".",",")
    return valor

def criaAgencia(localidade, numeroAgencia, idGerenteAgencia):
    InsMySQL(TabelaBd='tb_agencia',
            CampoBd=['localidade', 'numero_agencia', 'status_agencia', 'id_funcionario'],
            CampoFm=[str(localidade), str(numeroAgencia), '1', idGerenteAgencia])

def criaGA(dados):
    cpf = dados['cpf']
    cpf = cpf.replace(".","")
    cpf = cpf.replace("-","")

    existe = SlcEspecificoMySQL(TabelaBd='tb_usuario',
                                      CampoEs=['cpf'],
                                      CampoBd=['cpf'],
                                      CampoFm=[cpf])
    
    if existe == ():
        matricula = geraValor(8,'n')

        InsMySQL(TabelaBd='tb_usuario',
                CampoBd=['nome', 'email', 'cpf', 'genero', 'endereco', 'datanascimento', 'senha', 'ativo'],
                CampoFm=[dados['nome'], dados['email'], cpf, dados['genero'], dados['endereco'], dados['dataNasc'], geraValor(8,'l&n'), '1'])
        
        idGerente = SlcEspecificoMySQL(TabelaBd='tb_usuario',
                                       CampoEs=['id_usuario'],
                                       CampoBd=['cpf'],
                                       CampoFm=[cpf])

        existe = SlcEspecificoMySQL(TabelaBd='tb_funcionario',
                                      CampoEs=['num_matricula'],
                                      CampoBd=['num_matricula'],
                                      CampoFm=[matricula])
        
        #impede de gerar um valor repetido de matricula
        while existe != ():
            matricula = geraValor(8,'n')
            existe = SlcEspecificoMySQL(TabelaBd='tb_funcionario',
                                      CampoEs=['num_matricula'],
                                      CampoBd=['num_matricula'],
                                      CampoFm=[matricula])
        
        InsMySQL(TabelaBd='tb_funcionario',
                CampoBd=['id_usuario','papel','num_matricula','login'],
                CampoFm=[str(idGerente[0][0]),'GERENTE DE AGÊNCIA', matricula, matricula])
    else:
        matricula = geraValor(8,'n')

        upMySQL(TabelaBd='tb_usuario',
                CampoBd=['nome', 'email', 'cpf', 'genero', 'endereco', 'datanascimento', 'senha', 'ativo'],
                CampoFm=[dados['nome'], dados['email'], cpf, dados['genero'], dados['endereco'], dados['dataNasc'], geraValor(8,'l&n'), '1'],
                CampoWr=['cpf'],
                CampoPs=[cpf])
        
        existe = SlcEspecificoMySQL(TabelaBd='tb_funcionario',
                                      CampoEs=['num_matricula'],
                                      CampoBd=['num_matricula'],
                                      CampoFm=[matricula])
        
        #impede de gerar um valor repetido de matricula
        while existe != ():
            matricula = geraValor(8,'n')
            existe = SlcEspecificoMySQL(TabelaBd='tb_funcionario',
                                      CampoEs=['num_matricula'],
                                      CampoBd=['num_matricula'],
                                      CampoFm=[matricula])

        idGerente = SlcEspecificoMySQL(TabelaBd='tb_usuario',
                                       CampoEs=['id_usuario'],
                                       CampoBd=['cpf'],
                                       CampoFm=[cpf])
        InsMySQL(TabelaBd='tb_funcionario',
                CampoBd=['id_usuario','papel','num_matricula','login'],
                CampoFm=[str(idGerente[0][0]),'GERENTE DE AGÊNCIA', matricula, matricula])

    senha = SlcEspecificoMySQL(TabelaBd='tb_usuario',
                                       CampoEs=['senha'],
                                       CampoBd=['cpf'],
                                       CampoFm=[cpf])  

    acesso = {
        'matricula': matricula,
        'senha': senha[0][0]
    }  

    return acesso

def dadosGA(IdFuncionario):
    cursor = mysql.connection.cursor()
    
    Select = f'''SELECT nome, email, cpf, genero, endereco, datanascimento, senha, login 
    FROM tb_usuario INNER JOIN tb_funcionario 
    ON tb_usuario.id_usuario = tb_funcionario.id_usuario 
    WHERE id_funcionario = {IdFuncionario};'''

    cursor.execute(Select)
    pesquisaSQL = cursor.fetchall()
    mysql.connection.commit() 
    cursor.close()

    dados = {
        'IdFuncionario': IdFuncionario,
        'nome': pesquisaSQL[0][0],
        'email': pesquisaSQL[0][1],
        'cpf': pesquisaSQL[0][2],
        'genero': pesquisaSQL[0][3],
        'endereco': pesquisaSQL[0][4],
        'dataNasc': pesquisaSQL[0][5],
        'senha': pesquisaSQL[0][6],
        'login': pesquisaSQL[0][7]
    }

    return dados

def dadosU(numeroConta, idFuncionario):
    #bloco funcionario
    if numeroConta == '':
        idUsuario = SlcEspecificoMySQL(TabelaBd='tb_funcionario',
                                        CampoBd=['id_usuario'],
                                        CampoFm=[idFuncionario],
                                        CampoEs=['id_usuario'])


        Select = f'''SELECT nome, email, cpf, genero, endereco, datanascimento, login, senha
        FROM tb_usuario tu INNER JOIN tb_funcionario tf 
        ON tu.id_usuario = tf.id_usuario  
        WHERE tu.id_usuario = {idUsuario[0][0]};'''
        

        cursor = mysql.connection.cursor()
        cursor.execute(Select)
        pesquisaSQL = cursor.fetchall()
        mysql.connection.commit() 
        cursor.close()

        
        dados = {
        'numeroAgencia':'',
        'idUsuario':idUsuario[0][0],
        'idFuncionario':idFuncionario,
        'nome':pesquisaSQL[0][0],
        'email':pesquisaSQL[0][1],
        'cpf':pesquisaSQL[0][2],
        'genero':pesquisaSQL[0][3],
        'endereco':pesquisaSQL[0][4],
        'dataNasc':pesquisaSQL[0][5],
        'login':pesquisaSQL[0][6],
        'senha':pesquisaSQL[0][7]
        }

    #bloco usuario
    else:
        idUsuario = SlcEspecificoMySQL(TabelaBd='tb_contabancaria',
                                        CampoBd=['numeroconta'],
                                        CampoFm=[numeroConta],
                                        CampoEs=['id_usuario', 'id_agencia'])

        pesquisaSQL = SlcEspecificoMySQL(TabelaBd='tb_usuario',
                                        CampoBd=['id_usuario'],
                                        CampoFm=[idUsuario[0][0]],
                                        CampoEs=['nome','email','cpf','genero','endereco','datanascimento','senha'])
        
        numeroAgencia = SlcEspecificoMySQL(TabelaBd='tb_agencia',
                                            CampoBd=['id_agencia'],
                                            CampoFm=[idUsuario[0][1]],
                                            CampoEs=['numero_agencia'])
        
        dados = {
        'numeroAgencia':numeroAgencia[0][0],
        'idUsuario':idUsuario[0][0],
        'idFuncionario':idFuncionario,
        'nome':pesquisaSQL[0][0],
        'email':pesquisaSQL[0][1],
        'cpf':pesquisaSQL[0][2],
        'genero':pesquisaSQL[0][3],
        'endereco':pesquisaSQL[0][4],
        'dataNasc':pesquisaSQL[0][5],
        'login':'',
        'senha':pesquisaSQL[0][6]
        }
    return dados

def alteraGA(dados):
    idUsuario = SlcEspecificoMySQL(TabelaBd='tb_funcionario',
                                   CampoBd=['id_funcionario'],
                                   CampoFm=[dados['idfuncionario']],
                                   CampoEs=['id_usuario'])
    
    upMySQL(TabelaBd='tb_usuario',
            CampoBd=['nome','email','cpf','genero','endereco','datanascimento','senha'],
            CampoFm=[dados['nome'],dados['email'],dados['cpf'],dados['genero'],dados['endereco'],dados['dataNasc'],dados['senha']],
            CampoWr=['id_usuario'],
            CampoPs=[idUsuario[0][0]])

    upMySQL(TabelaBd='tb_funcionario',
            CampoBd=['login'],
            CampoFm=[dados['login']],
            CampoWr=['id_funcionario'],
            CampoPs=[dados['idfuncionario']])
    return 

def desligaGA(IdFuncionario, novoResp):
    IdUsuario = SlcEspecificoMySQL(TabelaBd='tb_funcionario',
                                        CampoBd=['id_funcionario'],
                                        CampoFm=[IdFuncionario],
                                        CampoEs=['id_usuario'])

    if novoResp != 'Null':
        upMySQL(TabelaBd='tb_agencia',
                CampoBd=['id_funcionario'],
                CampoFm=[novoResp],
                CampoWr=['id_funcionario'],
                CampoPs=[IdFuncionario])
        
        existe = SlcEspecificoMySQL(TabelaBd='tb_contabancaria',
                                        CampoBd=['id_usuario'],
                                        CampoFm=[IdUsuario[0][0]],
                                        CampoEs=['id_usuario'])

        if existe == ():
            DelMySQL(TabelaBd='tb_funcionario',
                    CampoBd=['id_funcionario'],
                    CampoFm=[IdFuncionario])
            DelMySQL(TabelaBd='tb_usuario',
                    CampoBd=['id_usuario'],
                    CampoFm=[IdUsuario[0][0]])
        else:
            DelMySQL(TabelaBd='tb_funcionario',
                    CampoBd=['id_funcionario'],
                    CampoFm=[IdFuncionario])
    else:
        existe = SlcEspecificoMySQL(TabelaBd='tb_contabancaria',
                                        CampoBd=['id_usuario'],
                                        CampoFm=[IdUsuario[0][0]],
                                        CampoEs=['id_usuario'])
        if existe == ():
            DelMySQL(TabelaBd='tb_funcionario',
                    CampoBd=['id_funcionario'],
                    CampoFm=[IdFuncionario])
            DelMySQL(TabelaBd='tb_usuario',
                    CampoBd=['id_usuario'],
                    CampoFm=[IdUsuario[0][0]])
        else:
            DelMySQL(TabelaBd='tb_funcionario',
                    CampoBd=['id_funcionario'],
                    CampoFm=[IdFuncionario])
    return 

def verificaAgencia():
    cursor = mysql.connection.cursor()
    
    Select = f'''SELECT tb_agencia.id_agencia,
                 CASE WHEN count(tb_contabancaria.id_agencia) IS NOT NULL THEN count(tb_contabancaria.id_agencia)  ELSE 0 END as conta
                 FROM tb_agencia  
                 left JOIN  tb_contabancaria
                 ON tb_agencia.id_agencia = tb_contabancaria.id_agencia
                 group by tb_agencia.id_agencia  
                 order by count(tb_contabancaria.id_agencia) asc
                 LIMIT 1;'''

    cursor.execute(Select)
    pesquisaSQL = cursor.fetchall()
    mysql.connection.commit() 
    cursor.close()
    idAgencia = pesquisaSQL[0][0]
    return idAgencia

def verificaAgenciaGerente(idGerente):
    cursor = mysql.connection.cursor()
    
    Select = f'''SELECT id_agencia FROM tb_agencia 
    INNER JOIN tb_funcionario 
    ON tb_funcionario.id_funcionario = tb_agencia.id_funcionario      
    where tb_funcionario.id_usuario = {idGerente};'''

    cursor.execute(Select)
    pesquisaSQL = cursor.fetchall()
    mysql.connection.commit() 
    cursor.close()
    idAgencia = pesquisaSQL[0][0]
    return idAgencia

def alteraU(novosDados, tipo):
    #se o status alteração for 0 esta em aguardo e se for 1 foi resolvido
    #se a requisicao tem id do usuario e não tem id do funcionario aparece pro GA e pro GG
    #se a requisicao tem id do usuario e id do funcionario aparece para o GG
    novosDados['cpf'] = novosDados['cpf'].replace('.','')
    novosDados['cpf'] = novosDados['cpf'].replace('-','')
    text = '['
    for chave, valor in novosDados.items():
        text += f'{str(chave)}:{str(valor)} , '
    text += ']'
    print(text, tipo)
    if tipo == 2:
        return InsMySQL(TabelaBd='tb_requisicoes',
                CampoBd=['status_alteracao','id_usuario','id_funcionario','descricao'],
                CampoFm=[0,novosDados['idUsuario'], novosDados['idFuncionario'],text])
    else: 
        return InsMySQL(TabelaBd='tb_requisicoes',
                CampoBd=['status_alteracao','id_usuario','descricao'],
                CampoFm=[0,novosDados['idUsuario'], text])


#Pode gerar letras, numeros ou letras e numeros aleatorios 
#tipo pode receber:
#   -l (somente letras)
#   -n (somente numeros)
#   -l&n (letras e numeros)
def geraValor(qtdCaracteres, tipo):
    senha = ""

    if tipo == 'l&n':
        caracteres = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9']
        for caractere in range(int(qtdCaracteres)):
            senha += caracteres[random.randint(0,35)]
    elif tipo == 'l':
        caracteres = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        for caractere in range(int(qtdCaracteres)):
            senha += caracteres[random.randint(0,25)]
    elif tipo == 'n':
        caracteres = ['0','1','2','3','4','5','6','7','8','9']
        for caractere in range(qtdCaracteres):
            senha += caracteres[random.randint(0,9)]

    return senha

def verificaQuantidadeRendimento(data1, data2):
    contadora = 0
    dataSoma = data1
    while dataSoma < data2:
        contadora += 1
        dataSoma = data1 + relativedelta(months=contadora)
    return contadora


def altAG(id_agencia):
    upMySQL(TabelaBd='tb_agencia',
            CampoBd=['localidade','id_funcionario'],
            CampoFm=[localidade, id_funcionario],
            CampoWr=['id_agencia'],
            CampoPs=[id_agencia])
    
    return 0

def geraComprovante(dados):
    nomeArq = f"movimentacao_{dados[0][2]}_{dados[0][1]}.pdf"
    nomeArq = nomeArq.replace(":","")
    nomeArq = nomeArq.replace("/","_")
    c = canvas.Canvas(nomeArq, pagesize=A4)
    c.setFont('Courier', 11)
    width, height = A4
    line = 0.9
    c.drawCentredString(width*0.5, height*line,'PYNKSYS - SISTEMA DE EMISSÃO DE COMPROVANTES DIGITAIS')
    line-=0.02
    c.drawCentredString(width*0.5, height*0.1, 'PY.NK, o seu banco em qualquer lugar a qualquer hora.')
    if dados[0][0] == 'Depósito':
        if dados[0][4] == 'Em Aprovação':
            c.drawCentredString(width*0.5, height*line,'COMPROVANTE DE DEPÓSITO (EM APROVAÇÃO)')
            line-=0.04
        else:
            c.drawCentredString(width*0.5, height*line,'COMPROVANTE DE DEPÓSITO')
            line-=0.04
        c.drawString(width*0.1, height*line, f'CLIENTE: {str(dados[0][10]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'NÚMERO DA CONTA: {str(dados[0][11]).upper()}')
        line-=0.02
        c.line(width*0.1, height*line, width*0.9, height*line)
        line-=0.02
        c.drawCentredString(width*0.5, height*line, 'DADOS DA MOVIMENTAÇÃO')
        line-=0.02
        c.drawString(width*0.1, height*line, f'VALOR: R${str(dados[0][3]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'DATA: {str(dados[0][2]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'HORA: {str(dados[0][1]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'ID DA MOVIMENTAÇÃO: {str(dados[0][12]).upper()}')
        line-=0.02
        c.showPage()
        c.save()
        return nomeArq
    elif dados[0][0] == 'Saque':
        c.drawCentredString(width*0.5, height*line,'COMPROVANTE DE SAQUE')
        line-=0.04
        c.drawString(width*0.1, height*line, f'CLIENTE: {str(dados[0][10]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'NÚMERO DA CONTA: {str(dados[0][11]).upper()}')
        line-=0.02
        c.line(width*0.1, height*line, width*0.9, height*line)
        line-=0.02
        c.drawCentredString(width*0.5, height*line, 'DADOS DA MOVIMENTAÇÃO')
        line-=0.02
        c.drawString(width*0.1, height*line, f'VALOR: R${str(dados[0][3]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'DATA: {str(dados[0][2]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'HORA: {str(dados[0][1]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'ID DA MOVIMENTAÇÃO: {str(dados[0][12]).upper()}')
        line-=0.02
        c.showPage()
        c.save()
        return nomeArq
    elif dados[0][0] == 'Transferência':
        c.drawCentredString(width*0.5, height*line,'COMPROVANTE DE TRANSFERÊNCIA')
        line-=0.04
        c.drawString(width*0.1, height*line, f'CLIENTE: {str(dados[0][10]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'NÚMERO DA CONTA: {str(dados[0][11]).upper()}')
        line-=0.02
        c.line(width*0.1, height*line, width*0.9, height*line)
        line-=0.02
        c.drawCentredString(width*0.5, height*line, 'DADOS DA MOVIMENTAÇÃO')
        line-=0.02
        c.drawString(width*0.1, height*line, f'VALOR: R${str(dados[0][3]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'DATA: {str(dados[0][2]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'HORA: {str(dados[0][1]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'ID DA MOVIMENTAÇÃO: {str(dados[0][12]).upper()}')
        line-=0.02
        c.line(width*0.1, height*line, width*0.9, height*line)
        line-=0.02
        c.drawCentredString(width*0.5, height*line, 'DADOS DO DESTINATÁRIO')
        line-=0.02
        c.drawString(width*0.1, height*line, f'TRANSFERIDO PARA: {str(dados[0][8]).upper()}')
        line-=0.02
        c.drawString(width*0.1, height*line, f'NÚMERO DA CONTA: {str(dados[0][9]).upper()}')
        line-=0.02
        c.showPage()
        c.save()
        return nomeArq

def geraExtrato(dados, id):
    nomeArq = f"extrato_{dados[0][3]}_{dados[0][4]}.pdf"
    nomeArq = nomeArq.replace(":","")
    nomeArq = nomeArq.replace("/","_")
    c = canvas.Canvas(nomeArq, pagesize=A4)
    c.setFont('Courier', 11)
    width, height = A4
    line = 0.9
    c.drawCentredString(width*0.5, height*line,'PYNKSYS - SISTEMA DE EMISSÃO DE COMPROVANTES DIGITAIS')
    line-=0.02
    c.drawCentredString(width*0.5, height*line,'COMPROVANTE DE EXTRATO')
    line-=0.04  
    c.drawCentredString(width*0.5, height*0.1, 'PY.NK, o seu banco em qualquer lugar a qualquer hora.')
    c.drawCentredString(width*0.18, height*line, 'DATA/HORA')
    c.drawCentredString(width*0.5, height*line, 'DESCRIÇÃO')
    c.drawCentredString(width*0.82, height*line, 'VALOR')
    line-=0.012
    c.setFont('Courier', 9)

    for row in dados:
        if line < 0.148:
            c.line(width*0.1, height*line, width*0.9, height*line)
            c.showPage()
            c.setFont('Courier', 11)
            line = 0.9
            c.drawCentredString(width*0.18, height*line, 'DATA/HORA')
            c.drawCentredString(width*0.5, height*line, 'DESCRIÇÃO')
            c.drawCentredString(width*0.82, height*line, 'VALOR')
            c.drawCentredString(width*0.5, height*0.1, 'PY.NK, o seu banco em qualquer lugar a qualquer hora.')
            line-=0.012
            c.setFont('Courier', 9)
        else:
            if row[1] == 'Depósito':
                c.line(width*0.1, height*line, width*0.9, height*line)
                c.line(width*0.26, height*line, width*0.26, height*(line-0.036))
                c.line(width*0.74, height*line, width*0.74, height*(line-0.036))
                line-=0.012
                c.drawString(width*0.11, height*(line-0.001), f'{row[3]}')
                c.drawString(width*0.27, height*(line-0.001), f'{row[1]}({row[5]})')
                if row[5]== 'Aguardando':
                    c.drawString(width*0.75, height*(line-0.001), f'[#]R${row[2]}')
                else:
                    c.drawString(width*0.75, height*(line-0.001), f'[+]R${row[2]}')
                line-=0.012
                c.drawString(width*0.11, height*(line-0.001), f'{row[4]}')
                c.drawString(width*0.27, height*(line-0.001), f'Depósito em conta')
                line-=0.012
            elif row[1] == 'Saque':
                c.line(width*0.1, height*line, width*0.9, height*line)
                c.line(width*0.26, height*line, width*0.26, height*(line-0.036))
                c.line(width*0.74, height*line, width*0.74, height*(line-0.036))
                line-=0.012
                c.drawString(width*0.11, height*(line-0.003), f'{row[3]}')
                c.drawString(width*0.27, height*(line-0.003), f'{row[1]}')
                c.drawString(width*0.75, height*(line-0.003), f'[-]R${row[2]}')
                line-=0.012
                c.drawString(width*0.11, height*(line-0.001), f'{row[4]}')
                c.drawString(width*0.27, height*(line-0.003), f'Saque em conta')
                line-=0.012
            else:
                c.line(width*0.1, height*line, width*0.9, height*line)
                c.line(width*0.26, height*line, width*0.26, height*(line-0.048))
                c.line(width*0.74, height*line, width*0.74, height*(line-0.048))
                line-=0.012
                if row[8] == 'Origem':
                    c.drawString(width*0.11, height*(line-0.003), f'{row[3]}')
                    c.drawString(width*0.27, height*(line-0.003), f'{row[1]} Realizada')
                    c.drawString(width*0.75, height*(line-0.003), f'[-]R${row[2]}')
                    line-=0.012
                    c.drawString(width*0.11, height*(line-0.001), f'{row[4]}')
                    c.drawString(width*0.27, height*(line-0.003), f'Origem: {row[6]}')
                    line-=0.012
                    c.drawString(width*0.27, height*(line-0.003), f'Destino: {row[7]}')
                    line-=0.012
                else:
                    c.drawString(width*0.11, height*(line-0.003), f'{row[3]}')
                    c.drawString(width*0.27, height*(line-0.003), f'{row[1]} Recebida')
                    c.drawString(width*0.75, height*(line-0.003), f'[+]R${row[2]}')
                    line-=0.012
                    c.drawString(width*0.11, height*(line-0.001), f'{row[4]}')
                    c.drawString(width*0.27, height*(line-0.003), f'Origem: {row[6]}')
                    line-=0.012
                    c.drawString(width*0.27, height*(line-0.003), f'Destino: {row[7]}')
                    line-=0.012
    c.line(width*0.1, height*line, width*0.9, height*line)

    c.showPage()
    c.save() 

    return nomeArq

def temReq(idContaBancaria, tipo):
    # Se for usuario
    if tipo == 1:
        idUsuario = SlcEspecificoMySQL(TabelaBd='tb_contabancaria',
                                        CampoBd=['id_conta'],
                                        CampoFm=[idContaBancaria],
                                        CampoEs=['id_usuario'])
        
        cursor = mysql.connection.cursor()
        
        Select = f'''SELECT MAX(id_requisicao)
                    FROM tb_requisicoes
                    WHERE id_usuario = {idUsuario[0][0]};'''

        cursor.execute(Select)
        ultimaReq = cursor.fetchall()
        mysql.connection.commit() 
        cursor.close()
        

    # Se for Gerente
    else:
        idUsuario = idContaBancaria
            
        cursor = mysql.connection.cursor()
        
        Select = f'''SELECT MAX(id_requisicao)
                    FROM tb_requisicoes
                    WHERE id_usuario = {idUsuario};'''

        cursor.execute(Select)
        ultimaReq = cursor.fetchall()
        mysql.connection.commit() 
        cursor.close()


    if ultimaReq != []:
        statusAlteracao = SlcEspecificoMySQL(TabelaBd='tb_requisicoes',
                                            CampoBd=['id_requisicao'],
                                            CampoFm=[ultimaReq[0][0]],
                                            CampoEs=['status_alteracao'])

        print(statusAlteracao)
        if statusAlteracao != ():
            if str(statusAlteracao [0][0]) == '0':
                return True
            else: 
                return False
    else:
        return False

