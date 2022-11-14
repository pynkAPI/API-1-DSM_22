from logging import raiseExceptions
import math
import os
from importlib.metadata import requires
from reportlab.pdfgen import canvas
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

def criaComprovante (dicionario, numero_conta):
    nome_comp = f"{dicionario['id']}{numero_conta}.pdf"
    c = canvas.Canvas(nome_comp)
    c.setFont("Helvetica", 12)
    if dicionario ['tipo'] == 'Depósito':
        c.drawString(80,750,"Py.NK Internet Banking")
        c.drawString(80,720,"Comprovante de Depósito")
        c.drawString(80,690,f"+R${dicionario['valor']} depositado.")
        c.line(80,675,510,675)
        c.drawString(80,650,f"Data do Depósito: {dicionario['data'][3:5]}/{dicionario['data'][:2]}/{dicionario['data'][6:]}")
        c.drawString(80,620,f"Horário do Depósito: {dicionario['hora']}")
        c.drawString(80,590,f"ID da Transação: {dicionario['id']}")
    elif dicionario ['tipo'] == 'Saque':
        c.drawString(80,750,"Py.NK Internet Banking")
        c.drawString(80,720,"Comprovante de Saque")
        c.drawString(80,690,f"-R${dicionario['valor']} sacado.")
        c.line(80,675,510,675)
        c.drawString(80,650,f"Data do Saque: {dicionario['data'][3:5]}/{dicionario['data'][:2]}/{dicionario['data'][6:]}")
        c.drawString(80,620,f"Horário do Saque: {dicionario['hora']}")
        c.drawString(80,590,f"ID da Transação: {dicionario['id']}")
    elif dicionario['tipo'] == 'transferencia':
        if numero_conta == dicionario['conta_origem']:
            c.drawString(80,750,"Py.NK Internet Banking")
            c.drawString(80,720,f"Comprovante de Transferência Realizada")
            c.drawString(80,690,f"R${dicionario['valor']} transferido para {dicionario['nome_destino']}")
            c.line(80,675,510,675)
            c.drawString(80,650,f"Data da Transferência: {dicionario['data'][3:5]}/{dicionario['data'][:2]}/{dicionario['data'][6:]}")
            c.drawString(80,620,f"Horário da Transferência: {dicionario['hora']}")
            c.drawString(80,590,f"Enviado para: {dicionario['nome_destino']}")
            c.drawString(80,560,f"Numero de conta: {dicionario['conta_destino']}")
            c.drawString(80,530,f"ID da Transação: {dicionario['id']}")
        elif numero_conta == dicionario['conta_destino']:
            c.drawString(80,750,"Py.NK Internet Banking")
            c.drawString(80,720,f"Comprovante de Transferência Recebida")
            c.drawString(80,690,f"R${dicionario['valor']} recebido de {dicionario['nome_origem']}")
            c.line(80,675,510,675)
            c.drawString(80,650,f"Data da Transferência: {dicionario['data'][3:5]}/{dicionario['data'][:2]}/{dicionario['data'][6:]}")
            c.drawString(80,620,f"Horário da Transferência: {dicionario['hora']}")
            c.drawString(80,590,f"Enviado por: {dicionario['nome_origem']}")
            c.drawString(80,560,f"Numero de conta: {dicionario['conta_origem']}")
            c.drawString(80,530,f"ID da Transação: {dicionario['id']}")
    c.showPage()
    c.save()
    return nome_comp 

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
        if saldo > 0: 
            raise Exception('601')
        elif saldo < 0:
            raise Exception('602')
        else:
            upMySQL(TabelaBd='tb_contabancaria',
                CampoBd=['status_contabancaria'],
                CampoFm=[2],
                CampoWr=['id_usuario', 'numeroconta'],
                CampoPs=[id_usuario, numeroconta])
            raise Exception('603')

    else:
        raise Exception('401')


def periodoEntreDatas(data1, data2):
    data1 = datetime.strptime(data1, "%Y-%m-%d")
    data2 = datetime.strptime(data2, "%Y-%m-%d")
    return abs((data2 - data1).days)

     
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
                                        CampoBd=['id_funcionario'],
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
                                        CampoEs=['id_usuario'])

        pesquisaSQL = SlcEspecificoMySQL(TabelaBd='tb_usuario',
                                        CampoBd=['id_usuario'],
                                        CampoFm=[idUsuario[0][0]],
                                        CampoEs=['nome','email','cpf','genero','endereco','datanascimento','senha'])
        
        dados = {
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

def alteraU(novosDados,tipo):
    #se o status alteração for 0 esta em aguardo e se for 1 foi resolvido
    #se a requisicao tem id do usuario e não tem id do funcionario aparece pro GA e pro GG
    #se a requisicao tem id do usuario e id do funcionario aparece para o GG
    novosDados['cpf'] = novosDados['cpf'].replace('.','')
    novosDados['cpf'] = novosDados['cpf'].replace('-','')
    if tipo == 2:
        text = '['
        for chave, valor in novosDados.items():
            text += f'{str(chave)}:{str(valor)} , '
        text += ']'
        return InsMySQL( TabelaBd='tb_requisicoes',
                CampoBd=['status_alteracao','id_usuario','id_funcionario','descricao'],
                CampoFm=[0,novosDados['idUsuario'], novosDados['idFuncionario'],text])
    elif tipo == 1:
        text = '['
        for chave, valor in novosDados.items():
            text += f'{str(chave)}:{str(valor)} , '
        text += ']'
        return InsMySQL(TabelaBd='tb_requisicoes',
                CampoBd=['status_alteracao','id_usuario','descricao'],
                CampoFm=[0,novosDados['idUsuario'],text])


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

def altAG(id_agencia):
    upMySQL(TabelaBd='tb_agencia',
            CampoBd=['localidade','id_funcionario'],
            CampoFm=[localidade, id_funcionario],
            CampoWr=['id_agencia'],
            CampoPs=[id_agencia])
    
    return 0

# def DelAG(id_agencia):
#    pesquisa = SlcEspecificoMySQL(TabelaBd='tb_contabancaria',
#                                 CampoBd= ['id_agencia'],
#                                 CampoFm= [id_agencia],
#                                 CampoEs= ['id_conta']) 
#     for id_conta in pesquisa: 
#          upMySQL(TabelaBd='tb_contabancaria',
#             CampoBd=['id_agencia'],
#             CampoFm=[id_agencia],
#             CampoWr=['id_conta'],
#             CampoPs=[id_conta])

#     upMySQL(TabelaBd='tb_agencia',
#         CampoBd=['status_agencia'],
#         CampoFm=[0],
#         CampoWr=['id_agencia'],
#         CampoPs=[id_agencia])
#     return