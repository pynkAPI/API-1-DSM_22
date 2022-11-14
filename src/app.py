import os
from datetime import date, datetime
from select import select
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

#Pagina inicial
@app.route("/")
@app.route("/login")
def index():
    session['login'] = False
    session['nome']  = None
    session['conta'] = None
    session['tipo']  = None
    session['idContabk'] = None
    return render_template('login.html')
#------------------------------
#Pagina inicial Gerentes
@app.route("/loginG")
def loginG():
    session['login'] = False
    session['nome']  = None
    session['conta'] = None
    session['tipo']  = None
    session['idContaBK'] = None
    return render_template('loginG.html')
#------------------------------

#Pagina Home
@app.route("/home", methods = ['POST', 'GET'])
def home():
    if session['login'] == False:
        abort(401)
    else:
        saldo = None
        if session['tipo'] == 1:
            cabecalho = ('Tipo', 'Valor', 'Data e hora','Status', 'De:', 'Para:')
            saldo = funcs.ValEmReal(session['saldo'])
            VarContador=0
            
            pesquisaSQL = funcs.SlcEspecificoComORMySQL(TabelaBd='tb_transacao',
                                            CampoEs=['id_transacao','tipo','valor','Datatime','status_transacao'],
                                            CampoBd=['id_conta_origem','id_conta_destino'],
                                            CampoFm=[session['idContaBK'],session['idContaBK']],
                                            CampoWrAO=[0,1])
            
            pesquisaContas = funcs.SlcEspecificoComORMySQL(TabelaBd='tb_transacao',
                                            CampoEs=['id_conta_origem', 'id_conta_destino'],
                                            CampoBd=['id_conta_origem','id_conta_destino'],
                                            CampoFm=[session['idContaBK'],session['idContaBK']],
                                            CampoWrAO=[0,1])
            pesquisaChequeEspecial = funcs.SlcEspecificoMySQL(TabelaBd='tb_cheque_especial',
                                                             CampoBd=['id_conta', 'ativo'],
                                                             CampoFm=[session['idContaBK'], '1'],
                                                             CampoEs=['valor_devido', 'data_atualizacao'])
            if pesquisaChequeEspecial:
                valorDevido = pesquisaChequeEspecial[0][0]
                dataAtualizacao = pesquisaChequeEspecial[0][1]
                dataPeriodo = funcs.periodoEntreDatas(data1=str(dataAtualizacao), data2=str(date.today()))
                if dataPeriodo > 0:
                    pesquisaRegraOperacao = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                                                 CampoBd=['id_regra_operacoes'],
                                                                 CampoFm=[1],
                                                                 CampoEs=['porcentagem'])
                    porcentagem = pesquisaRegraOperacao[0][0]
                    valorDevido = funcs.calculaChequeEspecial(valorDevido=valorDevido, porecentagem=porcentagem, tempo=dataPeriodo)
                    funcs.upMySQL(TabelaBd='tb_cheque_especial',
                                  CampoBd=['valor_devido', 'data_atualizacao'],
                                  CampoFm=[valorDevido, date.today()],
                                  CampoWr=['id_conta', 'ativo'],
                                  CampoPs=[session['idContaBK'], '1'])
            else:
                valorDevido = 0
            pesquisaSQL = [list(row) for row in pesquisaSQL]
            for row in pesquisaContas:
                
                nomes1 = funcs.SlcEspecificoMySQL('tb_contabancaria inner join tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                        CampoBd=['tb_contabancaria.id_conta'],
                                                        CampoFm=[row[0]],
                                                        CampoEs=['nome'])
                nomes1 = [list(row) for row in nomes1]
                                            
                nomes2 = funcs.SlcEspecificoMySQL('tb_contabancaria inner join tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                        CampoBd=['tb_contabancaria.id_conta'],
                                                        CampoFm=[row[1]],
                                                        CampoEs=['nome'])
                
                nomes2 = [list(row) for row in nomes2]
                
                pesquisaSQL[VarContador].append(nomes1[0][0])
                pesquisaSQL[VarContador].append(nomes2[0][0])
                pesquisaSQL[VarContador][2] = funcs.ValEmReal(pesquisaSQL[VarContador][2])
                print(pesquisaSQL[VarContador][2])
                
                if pesquisaSQL[VarContador][4] == '1':
                    pesquisaSQL[VarContador][4] = "Efetuado"
                else:
                    if pesquisaSQL[VarContador][4] == '2':
                        pesquisaSQL[VarContador][4] = "Rejeitado"
                    else:
                        pesquisaSQL[VarContador][4] = "Aguardando"
                VarContador+=1
            valorDevidoTotal = valorDevido
            if valorDevido < 0:
                valorDevido = valorDevido - float(session['saldo'])    
            caminhoLogin = '/'
            return render_template('homenew.html',saldo=saldo, chequeEspcial=valorDevido, valorDevidoTotal=valorDevidoTotal,cabecalhoTabela=cabecalho,pesquisaSQLTabela=pesquisaSQL,caminhoLogin=caminhoLogin)
        else:
            req=funcs.SlcEspecificoMySQL('tb_requisicoes',CampoBd=['status_alteracao'], CampoFm=['0'], CampoEs=['count(*)'])
            cursor = mysql.connection.cursor()
        
            textoSQL = f"SELECT count(*) FROM pynk.tb_contabancaria;"
            
            cursor.execute(textoSQL)
            tusuarios = cursor.fetchall()
            mysql.connection.commit() 

            saldo = f"{session['saldo']:.2f}".replace(".",",")
            caminhoLogin = 'loginG'
            if session['tipo'] == 2:
                return homeG()
            else:
                return render_template('homenewgg.html',saldo=saldo,req=req,usuarios=tusuarios,caminhoLogin=caminhoLogin)
#------------------------------

@app.route("/RequisicaoGerenteAgencia", methods = ['POST', 'GET'])
def RequisicaoGerenteAgencia():
    if request.method == "POST":
        requisicao = request.form['requisicao']
        #Conferencia Deposito
        #region
        if requisicao == '0':
            botao = request.form.to_dict()
            IdTransacao =   request.form['Id']
            if botao['botao'] == 'Confirmar':

                pesquisaSQLTransacao =  funcs.SlcEspecificoMySQL(TabelaBd='tb_transacao',
                                                            CampoEs=['valor', 'id_conta_origem'],
                                                            CampoBd=['id_transacao'],
                                                            CampoFm=[IdTransacao])

                IdContaOrigem = pesquisaSQLTransacao[0][1]
                valorTransacao = float(pesquisaSQLTransacao[0][0])

                pesquisaSQLCheque = funcs.SlcEspecificoMySQL(TabelaBd='tb_cheque_especial',
                                                             CampoBd=['id_conta'],
                                                             CampoFm=[IdContaOrigem],
                                                             CampoEs=['valor_devido', 'data_atualizacao'])
                #verifica se quem está depositando está devendo ao banco, caso sim será realizado uma processo especial.       
                if pesquisaSQLCheque:
                    valorDevido = pesquisaSQLCheque[0][0]
                    dataAtualizacao = pesquisaSQLCheque[0][1]
                    #pega a quantidade de dias passados desde o dia em que ele entrou em cheque especial
                    dataPeriodo = funcs.periodoEntreDatas(data1=str(dataAtualizacao), data2=str(date.today()))

                    #verifica se a qtd de dias é > 0
                    if dataPeriodo > 0:
                        pesquisaSQLRegraCheque = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                                                              CampoBd=['id_regra_operacoes'],
                                                                              CampoFm=[1],
                                                                              CampoEs=['porcentagem', 'valor_fixo'])
                        porcentagem = pesquisaSQLRegraCheque[0][0]
                        valorDevido = funcs.calculaChequeEspecial(tempo=dataPeriodo, porecentagem=porcentagem, valorDevido=valorDevido)
                    valorDevido = valorDevido + valorTransacao

                    funcs.upMySQL(TabelaBd='tb_cheque_especial',
                                  CampoPs=[IdContaOrigem, '1'],
                                  CampoWr=['id_conta', 'ativo'],
                                  CampoBd=['valor_devido','data_atualizacao'],
                                  CampoFm=[ valorDevido, datetime.today()])

                    pesquisaSQLConta = funcs.SlcEspecificoMySQL(TabelaBd='tb_transacao INNER JOIN tb_contabancaria ON tb_contabancaria.id_conta = tb_transacao.id_conta_origem AND tb_contabancaria.id_conta = tb_transacao.id_conta_destino INNER JOIN tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                                CampoEs=['tb_contabancaria.id_conta' ,'tb_contabancaria.saldo'],
                                                                CampoBd=['id_transacao', 'tb_contabancaria.id_conta'],
                                                                CampoFm=[IdTransacao, IdContaOrigem])


                    pesquisaTotalBanco = funcs.SlcEspecificoMySQL(TabelaBd='tb_capitaltotal',
                                                                  CampoEs=['capitalinicial'],
                                                                  CampoBd=['id_capitaltotal'],
                                                                  CampoFm=[1])
                    valorTotalBanco = float(pesquisaTotalBanco[0][0])
                    valorTotalBanco = valorTransacao + valorTotalBanco

                    funcs.upMySQL(TabelaBd='tb_transacao',
                              CampoBd=['status_transacao', 'Datatime', 'data_aceite_recusa'],
                              CampoFm=[1, datetime.today(), datetime.today()],
                              CampoPs=[IdTransacao],
                              CampoWr=['id_transacao'])


                    #Verifica se ele conseguiu sair da dívida
                    if valorDevido >= 0:
                        funcs.upMySQL('tb_contabancaria',
                                      CampoBd=['saldo'],
                                      CampoFm=[valorDevido],
                                      CampoWr=['id_conta'],
                                      CampoPs=[IdContaOrigem])
                        funcs.upMySQL(TabelaBd='tb_cheque_especial',
                                      CampoPs=[IdContaOrigem, '0'],
                                      CampoWr=['id_conta', 'ativo'],
                                      CampoBd=['valor_devido', 'data_final'],
                                      CampoFm=[ 0, date.today()])
                    #Atualiza o valor total do Banco
                    funcs.upMySQL(TabelaBd='tb_capitaltotal',
                                  CampoBd=['capitalinicial'],
                                  CampoFm=[valorTotalBanco],
                                  CampoWr=['id_capitaltotal'],
                                  CampoPs=[1])
                    session['saldo'] = valorTotalBanco

                    return homeG(requisicao=requisicao)           

                pesquisaSQLConta = funcs.SlcEspecificoMySQL(TabelaBd='tb_transacao INNER JOIN tb_contabancaria ON tb_contabancaria.id_conta = tb_transacao.id_conta_origem AND tb_contabancaria.id_conta = tb_transacao.id_conta_destino INNER JOIN tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                            CampoEs=['tb_contabancaria.id_conta' ,'tb_contabancaria.saldo'],
                                                            CampoBd=['id_transacao', 'tb_contabancaria.id_conta'],
                                                            CampoFm=[IdTransacao, IdContaOrigem])

                pesquisaTotalBanco = funcs.SlcEspecificoMySQL(TabelaBd='tb_capitaltotal',
                                                            CampoEs=['capitalinicial'],
                                                            CampoBd=['id_capitaltotal'],
                                                            CampoFm=[1])

                valorTotalBanco = float(pesquisaTotalBanco[0][0])
                saldoConta = float(pesquisaSQLConta[0][1])
                valor = valorTransacao + saldoConta

                valorTotalBanco = valor + valorTotalBanco

                funcs.upMySQL(TabelaBd='tb_transacao',
                          CampoBd=['status_transacao', 'Datatime', 'data_aceite_recusa'],
                          CampoFm=[1, datetime.today(), datetime.today()],
                          CampoPs=[IdTransacao],
                          CampoWr=['id_transacao'])


                funcs.upMySQL('tb_contabancaria',
                              CampoBd=['saldo'],
                              CampoFm=[valor],
                              CampoWr=['id_conta'],
                              CampoPs=[IdContaOrigem])

                funcs.upMySQL(TabelaBd='tb_capitaltotal',
                              CampoBd=['capitalinicial'],
                              CampoFm=[valorTotalBanco],
                              CampoWr=['id_capitaltotal'],
                              CampoPs=[1]) 
                session['saldo'] = valorTotalBanco

                return homeG(requisicao=requisicao)
            else:
                funcs.upMySQL(TabelaBd='tb_transacao', 
                          CampoBd=['status_transacao', 'data_aceite_recusa'],
                          CampoFm=[2, datetime.today()],
                          CampoPs=[IdTransacao],
                          CampoWr=['id_transacao'])
                return homeG(requisicao=requisicao)
        #endregion 

        # Aceite de Abertura de Conta
        #region
        elif requisicao == '1':
            botao = request.form.to_dict()
            IdConta = request.form['Id']
            pesquisaAgenciaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_agencia',
                                                          CampoEs=['id_agencia'],
                                                          CampoBd=['id_funcionario'],
                                                          CampoFm=[session['idFunc']])
            idAgencia = pesquisaAgenciaSQL[0][0]
            email = ''
            email = funcs.SlcEspecificoMySQL('tb_usuario INNER JOIN tb_contabancaria ON tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                         CampoBd=['tb_contabancaria.id_conta'],
                                         CampoFm=[IdConta],
                                         CampoEs=['tb_usuario.email'])

            if botao['botao'] == 'Confirmar':
                funcs.upMySQL('tb_contabancaria',
                               CampoBd=['status_contabancaria', 'id_agencia'],
                               CampoFm=[1, idAgencia],
                               CampoWr=['id_conta'],
                               CampoPs=[IdConta])
                return homeG(requisicao=requisicao)
            else:    
                funcs.upMySQL('tb_contabancaria',
                              CampoBd=['status_contabancaria'],
                              CampoFm=[2],
                              CampoWr=['id_conta'],
                              CampoPs=[IdConta])
                return homeG(requisicao=requisicao)
        #endregion 
        else:
            if requisicao == '3':
                idUsuario   =request.form['idUsuario'],
                nome        =request.form['nome']
                email       =request.form['email']
                cpf         =request.form['cpf']
                genero      =request.form['genero']
                endereco    =request.form['endereco']
                datanasc    =request.form['datanasc']
                senha       =request.form['senha']
                
                funcs.upMySQL('tb_usuario',
                                CampoBd=['nome', 'email', 'cpf', 'genero', 'endereco', 'datanascimento', 'senha'],
                                CampoFm=[nome, email,cpf,genero,endereco,datanasc,senha.replace(' ','')],
                                CampoWr=['id_usuario'],
                                CampoPs=[idUsuario[0]])
                return homeG(requisicao=requisicao)
            elif requisicao == '4':
                idUsuario   =request.form['idUsuario'],
                nome        =request.form['nome']
                email       =request.form['email']
                cpf         =request.form['cpf']
                genero      =request.form['genero']
                endereco    =request.form['endereco']
                datanasc    =request.form['datanasc']
                senha       =request.form['senha']
                
                funcs.upMySQL('tb_usuario',
                                CampoBd=['nome', 'email', 'cpf', 'genero', 'endereco', 'datanascimento', 'senha'],
                                CampoFm=[nome, email,cpf,genero,endereco,datanasc,senha.replace(' ','')],
                                CampoWr=['id_usuario'],
                                CampoPs=[idUsuario[0]])
                return home()
            else:
                botao = request.form.to_dict()
                IdConta = request.form['Id']
                if botao['botao'] == 'Confirmar':
                    Desc = request.form['Desc'].replace('[','').replace(']','').split(',')
                    DescSeparada = []
                    for row in Desc:
                        doispontos = row.find(':')+1
                        DescSeparada.append(row[doispontos:])
                    funcs.upMySQL('tb_usuario',
                                CampoBd=['nome', 'email', 'cpf', 'genero', 'endereco', 'datanascimento', 'senha'],
                                CampoFm=[DescSeparada[2], DescSeparada[3],DescSeparada[4],DescSeparada[5],DescSeparada[6],DescSeparada[7],DescSeparada[9].replace(' ','')],
                                CampoWr=['id_usuario'],
                                CampoPs=[DescSeparada[0]])
                    funcs.upMySQL('tb_requisicoes',
                                CampoBd=['status_alteracao'],
                                CampoFm=[1],
                                CampoWr=['id_requisicao'],
                                CampoPs=[IdConta]) 
                    if session['tipo'] == 2:
                        return homeG(requisicao=requisicao)
                    else:
                        return render_template('ListReq.html')
                else:    
                    funcs.upMySQL('tb_requisicoes',
                                CampoBd=['status_alteracao'],
                                CampoFm=[2],
                                CampoWr=['id_requisicao'],
                                CampoPs=[IdConta])
                    if session['tipo'] == 2:
                        return homeG(requisicao=requisicao)
                    else:
                        return render_template('ListReq.html')
            
    return homeG(requisicao=requisicao)
     

@app.route("/homeG", methods = ['POST', 'GET'])
def homeG(requisicao=None):
    req=funcs.SlcEspecificoMySQL('tb_requisicoes',CampoBd=['status_alteracao'], CampoFm=['0'], CampoEs=['count(*)'])
    ausuarios=funcs.SlcEspecificoMySQL('tb_contabancaria',CampoBd=['id_agencia'], CampoFm=['1'], CampoEs=['count(*)'])
    saldo = f"{session['saldo']:.2f}".replace(".",",")
    caminhoLogin = 'loginG'
    if request.method == "POST":
        if requisicao == None:
            requisicao = request.form.get('requisicao1')
        #Tabela de Conferencia de Deposito
        #region
        if requisicao == '0':
            cabecalho = ('Nome', 'Número Conta', 'Valor', 'Data', '')

            pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='''tb_transacao 
                                                               INNER JOIN tb_contabancaria 
                                                               ON tb_contabancaria.id_conta = tb_transacao.id_conta_origem 
                                                               AND tb_contabancaria.id_conta = tb_transacao.id_conta_destino 
                                                               INNER JOIN tb_agencia 
                                                               ON tb_agencia.id_agencia = tb_contabancaria.id_agencia
                                                               INNER JOIN tb_usuario 
                                                               ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario''',
                                                               CampoEs=['tb_transacao.id_transacao','tb_usuario.nome','tb_contabancaria.numeroconta' ,'tb_transacao.valor', 'tb_transacao.Datatime',],
                                                               CampoBd=['status_transacao', 'tb_agencia.id_funcionario'],
                                                               CampoFm=[0, session['idFunc']])
            return render_template('homenewg.html',
                                   saldo=saldo,
                                   req=req,
                                   usuarios=ausuarios, 
                                   caminhoLogin=caminhoLogin, 
                                   cabecalhoTabela=cabecalho,
                                   pesquisaSQLTabela=pesquisaSQL,
                                   requisicao=requisicao)
        #endregion
        elif requisicao == '1':
            cabecalho = ('Nome', 'CPF', 'Número Conta', 'Data Nasc', 'Endereço', 'Genero', 'Tipo Conta', '')

            pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_usuario INNER JOIN tb_contabancaria ON tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                           CampoEs=['tb_contabancaria.id_conta','tb_usuario.nome', 'tb_usuario.cpf', 'tb_contabancaria.numeroconta','tb_usuario.datanascimento','tb_usuario.endereco','tb_usuario.genero', 'tb_contabancaria.tipo'],
                                           CampoBd=['tb_contabancaria.status_contabancaria'],
                                           CampoFm=[0])    
            return render_template('homenewg.html',
                                   saldo=saldo,
                                   req=req,
                                   usuarios=ausuarios, 
                                   caminhoLogin=caminhoLogin, 
                                   cabecalhoTabela=cabecalho,
                                   pesquisaSQLTabela=pesquisaSQL,
                                   requisicao=requisicao)
        elif requisicao == '2':
            cabecalho = ('Nome', 'CPF', 'descricao','')
            pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_requisicoes  INNER JOIN tb_usuario  ON tb_usuario.id_usuario = tb_requisicoes.id_usuario  INNER JOIN tb_contabancaria  ON tb_usuario.id_usuario = tb_contabancaria.id_usuario INNER JOIN tb_agencia ON tb_contabancaria.id_agencia = tb_agencia.id_agencia',
                                                   CampoEs=['tb_requisicoes.id_requisicao','tb_usuario.nome', 'tb_usuario.cpf', 'tb_requisicoes.descricao'],
                                                   CampoBd=['tb_agencia.id_funcionario','tb_requisicoes.status_alteracao'],
                                                   CampoFm=[session['idFunc'],'0'])
            return render_template('homenewg.html',
                                   saldo=saldo,
                                   req=req,
                                   usuarios=ausuarios, 
                                   caminhoLogin=caminhoLogin, 
                                   cabecalhoTabela=cabecalho,
                                   pesquisaSQLTabela=pesquisaSQL,
                                   requisicao=requisicao)
        else:
            return render_template('homenewg.html',
                                saldo=saldo,
                                req=req,
                                usuarios=ausuarios, 
                                caminhoLogin=caminhoLogin)
    return render_template('homenewg.html',
                                saldo=saldo,
                                req=req,
                                usuarios=ausuarios, 
                                caminhoLogin=caminhoLogin)
    
@app.route("/homeGG", methods = ['POST', 'GET'])
def homeGG(requisicao=None):
    if request.method == "POST":
        if requisicao == None:
            requisicao = request.form.get('requisicao1')
        #Tabela de Conferencia de Deposito
        #region
        if requisicao == '0':
            cabecalho = ('Nome', 'Número Conta', 'Valor', 'Data', '', '')

            pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='''tb_transacao 
                                                               INNER JOIN tb_contabancaria 
                                                               ON tb_contabancaria.id_conta = tb_transacao.id_conta_origem 
                                                               AND tb_contabancaria.id_conta = tb_transacao.id_conta_destino 
                                                               INNER JOIN tb_agencia 
                                                               ON tb_agencia.id_agencia = tb_contabancaria.id_agencia
                                                               INNER JOIN tb_usuario 
                                                               ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario''',
                                                               CampoEs=['tb_transacao.id_transacao','tb_usuario.nome','tb_contabancaria.numeroconta' ,'tb_transacao.valor', 'tb_transacao.Datatime',],
                                                               CampoBd=['status_transacao', 'tb_agencia.id_funcionario'],
                                                               CampoFm=[0, session['idFunc']])
            return render_template('ListReq.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho)
        #endregion
        elif requisicao == '1':
            cabecalho = ('Nome', 'CPF', 'Número Conta', 'Data Nasc', 'Endereço', 'Genero', 'Tipo Conta', '', '')

            pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_usuario INNER JOIN tb_contabancaria ON tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                           CampoEs=['tb_contabancaria.id_conta','tb_usuario.nome', 'tb_usuario.cpf', 'tb_contabancaria.numeroconta','tb_usuario.datanascimento','tb_usuario.endereco','tb_usuario.genero', 'tb_contabancaria.tipo'],
                                           CampoBd=['tb_contabancaria.status_contabancaria'],
                                           CampoFm=[0])    
            return render_template('ListReq.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho)
        elif requisicao == '2':
            cabecalho = ('Nome', 'CPF', 'descricao')
            pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_requisicoes  INNER JOIN tb_usuario  ON tb_usuario.id_usuario = tb_requisicoes.id_usuario  INNER JOIN tb_contabancaria  ON tb_usuario.id_usuario = tb_contabancaria.id_usuario INNER JOIN tb_agencia ON tb_contabancaria.id_agencia = tb_agencia.id_agencia',
                                                   CampoEs=['tb_requisicoes.id_requisicao','tb_usuario.nome', 'tb_usuario.cpf', 'tb_requisicoes.descricao'],
                                                   CampoBd=['tb_requisicoes.status_alteracao'],
                                                   CampoFm=['0'])
            print(pesquisaSQL)
            return render_template('ListReq.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho)
        else:
            return render_template('ListReq.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho)
    return render_template('ListReq.html')

#Aplicar filtro no extrato
@app.route("/FiltroExtrato",  methods = ['POST', 'GET'])
def FiltroExtrato():
    if request.method == "POST":
        cabecalho   = ('Tipo', 'Valor','Data e hora', 'De:', 'Para:')
        saldo       = funcs.ValEmReal(session['saldo'])
        VarContador = 0
        DataDe      = request.form['DataExtratoDe']
        DateAte     = request.form['DataExtratoAte']
        cursor = mysql.connection.cursor()
        
        textoSQL = f"""SELECT tipo, valor, Datatime FROM tb_transacao 
        WHERE status_transacao = "1" and Datatime >= '{DataDe} 00:00:00' and Datatime < '{DateAte} 23:59:59' 
        and ( id_conta_origem = "{session['idContaBK']}"or id_conta_destino = "{session['idContaBK']}")"""
        
        cursor.execute(textoSQL)
        pesquisaSQL = cursor.fetchall()
        mysql.connection.commit()     
        
        textoSQL2 = f"""SELECT id_conta_origem, id_conta_destino FROM tb_transacao 
        WHERE status_transacao = "1" and Datatime >= '{DataDe} 00:00:00' and Datatime < '{DateAte} 23:59:59'
        and ( id_conta_origem = "{session['idContaBK']}" or id_conta_destino = "{session['idContaBK']}" )"""
        
        cursor.execute(textoSQL2)
        pesquisaContas = cursor.fetchall()
        mysql.connection.commit()  
        
        
        cursor.close()   
            
        pesquisaSQL = [list(row) for row in pesquisaSQL]
        for row in pesquisaContas:
            nomes1 = funcs.SlcEspecificoMySQL('tb_contabancaria inner join tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                        CampoBd=['tb_contabancaria.id_conta'],
                                                        CampoFm=[row[0]],
                                                        CampoEs=['nome'])  
            nomes2 = funcs.SlcEspecificoMySQL('tb_contabancaria inner join tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                        CampoBd=['tb_contabancaria.id_conta'],
                                                        CampoFm=[row[1]],
                                                        CampoEs=['nome'])
            nomes1 = [list(row) for row in nomes1]   
            nomes2 = [list(row) for row in nomes2]
                
            pesquisaSQL[VarContador].append(nomes1[0][0])
            pesquisaSQL[VarContador].append(nomes2[0][0])
            pesquisaSQL[VarContador][1] = funcs.ValEmReal(pesquisaSQL[VarContador][1])
            VarContador+=1
            
        return render_template('home.html',saldo=saldo,cabecalhoTabela=cabecalho,pesquisaSQLTabela=pesquisaSQL)
    return render_template('home.html')
#------------------------------
#Pagina Deposito
@app.route("/deposito")
def deposito():
    if session['saldo'] != None:
        saldo = f"{session['saldo']:.2f}".replace(".",",")
    return render_template('depositonew.html',saldo=saldo)

#------------------------------
#Pagina Saque
@app.route("/saque")
def saque():
    saldo = f"{session['saldo']:.2f}".replace(".",",")
    return render_template('saquenew.html',saldo=saldo)
#------------------------------
#Saque Conta
@app.route("/SaqueConta",  methods = ['POST', 'GET'])
def SaqueConta():
    if request.method == "POST":
        valor = float(request.form['valor'])
        if valor >= 0:
            capital_total = funcs.SlcEspecificoMySQL('tb_capitaltotal',
                                                    CampoBd=['id_capitaltotal'],
                                                    CampoFm=['1'],
                                                    CampoEs=['capitalinicial'])
            if valor <= capital_total[0][0]:
                valor = float(session['saldo']) - valor
                NewCapTot = capital_total[0][0] - float(request.form['valor'])
                     
                funcs.upMySQL('tb_contabancaria',
                               CampoBd=['saldo'],
                               CampoFm=[valor],
                               CampoWr=['numeroconta'],
                               CampoPs=[session['conta']])
                
                funcs.upMySQL('tb_capitaltotal',
                               CampoBd=['capitalinicial'],
                               CampoFm=[NewCapTot],
                               CampoWr=['id_capitaltotal'],
                               CampoPs=[1])

                saldoAtualizado = funcs.SlcEspecificoMySQL('tb_contabancaria ',
                                                            CampoBd=['numeroconta'],
                                                            CampoFm=[session['conta']],
                                                            CampoEs=['saldo'])

                idConta = funcs.SlcEspecificoMySQL('tb_contabancaria',
                                                            CampoBd=['numeroconta'],
                                                            CampoFm=[session['conta']],
                                                            CampoEs=['id_conta'])
                
                if valor < 0:
                    pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_cheque_especial',
                                                           CampoBd=['id_conta', 'ativo'],
                                                           CampoFm=[idConta[0][0], 1],
                                                           CampoEs=['valor_devido', 'data_atualizacao'])
                    if pesquisaSQL:
                        valorDevido = pesquisaSQL[0][0]
                        dataAtualizacao = pesquisaSQL[0][1]

                        dataPeriodo = funcs.periodoEntreDatas(data1=str(dataAtualizacao),data2=str(date.today()))

                        pesquisaSQLRegraCheque = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                                                          CampoBd=['id_regra_operacoes'],
                                                                          CampoFm=[1],
                                                                          CampoEs=['porcentagem', 'valor_fixo'])
                        porcentagem = pesquisaSQLRegraCheque[0][0]
                        valor_fixo = pesquisaSQLRegraCheque[0][1]

                        if dataPeriodo > 0:
                            valorDevido = funcs.calculaChequeEspecial(tempo=dataPeriodo, porecentagem=porcentagem, valorDevido=valorDevido)
                        valorDevido = valorDevido - float(request.form['valor'])
                        funcs.upMySQL(TabelaBd='tb_cheque_especial',
                                      CampoPs=[idConta[0][0], '1'],
                                      CampoWr=['id_conta', 'ativo'],
                                      CampoBd=['valor_devido','data_atualizacao'],
                                      CampoFm=[ valorDevido, datetime.today()])
                    else:
                        funcs.InsMySQL(TabelaBd='tb_cheque_especial',
                                       CampoBd=['id_conta', 'data_inicio', 'data_atualizacao','data_final', 'valor_devido', 'ativo'],
                                       CampoFm=[idConta[0][0],  datetime.today(), datetime.today(), None, valor, '1'])

                funcs.Transacao(idConta[0][0], idConta[0][0], 'Saque', float(request.form['valor']), '1')

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
#-------------------------------------------
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
#Paginas de Login
@app.route("/login", methods = ['POST', 'GET'])
def login():
    session['tipoLog'] = 0
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
                session['idContaBK']= row[9]
            session['login'] = True
            session['conta'] = numeroconta
            session['tipo']  = 1
            return home()
        else:
            abort(401)
    else:
        abort(401)

@app.route("/AutenticarGerente", methods = ['POST', 'GET'])
def AutenticarGerente():
    session['tipoLog'] = 1
    if request.method == "POST":
        #login do usuário comum
        numeroconta = request.form['numeroconta']
        senha       = request.form['senha']
        #Login de gerente geral e gerente de agência
        resultado   = funcs.SlcMySQL('''tb_usuario
                                        INNER JOIN tb_funcionario
                                        ON tb_funcionario.id_usuario = tb_usuario.id_usuario ''',
                                        CampoBd=['login','senha'],
                                        CampoFm=[numeroconta,senha])
            
        resultadocap = funcs.SlcMySQL('tb_capitaltotal',CampoBd=['id_capitaltotal'],CampoFm=['1'])
        if resultado:
            for row in resultado:
                session['idFunc']   = row[0]
                session['nome']     = row[1]
                papel               = row[11]
            session['login']        = True
            session['conta']        = numeroconta
            for row2 in resultadocap:
                session['saldo']    = row2[1]
            if papel == 'GERENTE DE AGÊNCIA':
                session['tipo']  = 2
            else:
                session['tipo']  = 3
                    
            return home()
        else:
            abort(401)
    else:
        abort(401)

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
            valorTransacao = float(pesquisaSQLTransacao[0][0])

            pesquisaSQLCheque = funcs.SlcEspecificoMySQL(TabelaBd='tb_cheque_especial',
                                                         CampoBd=['id_conta'],
                                                         CampoFm=[IdContaOrigem],
                                                         CampoEs=['valor_devido', 'data_atualizacao'])
            #verifica se quem está depositando está devendo ao banco, caso sim será realizado uma processo especial.       
            if pesquisaSQLCheque:
                valorDevido = pesquisaSQLCheque[0][0]
                dataAtualizacao = pesquisaSQLCheque[0][1]
                #pega a quantidade de dias passados desde o dia em que ele entrou em cheque especial
                dataPeriodo = funcs.periodoEntreDatas(data1=str(dataAtualizacao), data2=str(date.today()))

                #verifica se a qtd de dias é > 0
                if dataPeriodo > 0:
                    pesquisaSQLRegraCheque = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                                                          CampoBd=['id_regra_operacoes'],
                                                                          CampoFm=[1],
                                                                          CampoEs=['porcentagem', 'valor_fixo'])
                    porcentagem = pesquisaSQLRegraCheque[0][0]
                    valorDevido = funcs.calculaChequeEspecial(tempo=dataPeriodo, porecentagem=porcentagem, valorDevido=valorDevido)
                valorDevido = valorDevido + valorTransacao
                
                funcs.upMySQL(TabelaBd='tb_cheque_especial',
                              CampoPs=[IdContaOrigem, '1'],
                              CampoWr=['id_conta', 'ativo'],
                              CampoBd=['valor_devido','data_atualizacao'],
                              CampoFm=[ valorDevido, datetime.today()])
                
                pesquisaSQLConta = funcs.SlcEspecificoMySQL(TabelaBd='tb_transacao INNER JOIN tb_contabancaria ON tb_contabancaria.id_conta = tb_transacao.id_conta_origem AND tb_contabancaria.id_conta = tb_transacao.id_conta_destino INNER JOIN tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                            CampoEs=['tb_contabancaria.id_conta' ,'tb_contabancaria.saldo'],
                                                            CampoBd=['id_transacao', 'tb_contabancaria.id_conta'],
                                                            CampoFm=[IdTransacao, IdContaOrigem])


                pesquisaTotalBanco = funcs.SlcEspecificoMySQL(TabelaBd='tb_capitaltotal',
                                                              CampoEs=['capitalinicial'],
                                                              CampoBd=['id_capitaltotal'],
                                                              CampoFm=[1])
                valorTotalBanco = float(pesquisaTotalBanco[0][0])
                valorTotalBanco = valorTransacao + valorTotalBanco

                funcs.upMySQL(TabelaBd='tb_transacao',
                          CampoBd=['status_transacao', 'Datatime', 'data_aceite_recusa'],
                          CampoFm=[1, datetime.today(), datetime.today()],
                          CampoPs=[IdTransacao],
                          CampoWr=['id_transacao'])


                #Verifica se ele conseguiu sair da dívida
                if valorDevido > 0:
                    funcs.upMySQL('tb_contabancaria',
                                  CampoBd=['saldo'],
                                  CampoFm=[valorDevido],
                                  CampoWr=['id_conta'],
                                  CampoPs=[IdContaOrigem])
                    funcs.upMySQL(TabelaBd='tb_cheque_especial',
                                  CampoPs=[IdContaOrigem, '0'],
                                  CampoWr=['id_conta', 'ativo'],
                                  CampoBd=['valor_devido', 'data_final'],
                                  CampoFm=[ 0, date.today()])
        
                #Atualiza o valor total do Banco
                funcs.upMySQL(TabelaBd='tb_capitaltotal',
                              CampoBd=['capitalinicial'],
                              CampoFm=[valorTotalBanco],
                              CampoWr=['id_capitaltotal'],
                              CampoPs=[1])
                session['saldo'] = valorTotalBanco

                return ConferenciaDepositoTabela()           

            pesquisaSQLConta = funcs.SlcEspecificoMySQL(TabelaBd='tb_transacao INNER JOIN tb_contabancaria ON tb_contabancaria.id_conta = tb_transacao.id_conta_origem AND tb_contabancaria.id_conta = tb_transacao.id_conta_destino INNER JOIN tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                        CampoEs=['tb_contabancaria.id_conta' ,'tb_contabancaria.saldo'],
                                                        CampoBd=['id_transacao', 'tb_contabancaria.id_conta'],
                                                        CampoFm=[IdTransacao, IdContaOrigem])
            
            pesquisaTotalBanco = funcs.SlcEspecificoMySQL(TabelaBd='tb_capitaltotal',
                                                        CampoEs=['capitalinicial'],
                                                        CampoBd=['id_capitaltotal'],
                                                        CampoFm=[1])
                                            
            valorTotalBanco = float(pesquisaTotalBanco[0][0])
            saldoConta = float(pesquisaSQLConta[0][1])
            valor = valorTransacao + saldoConta

            valorTotalBanco = valor + valorTotalBanco

            funcs.upMySQL(TabelaBd='tb_transacao',
                      CampoBd=['status_transacao', 'Datatime', 'data_aceite_recusa'],
                      CampoFm=[1, datetime.today(), datetime.today()],
                      CampoPs=[IdTransacao],
                      CampoWr=['id_transacao'])
            

            funcs.upMySQL('tb_contabancaria',
                          CampoBd=['saldo'],
                          CampoFm=[valor],
                          CampoWr=['id_conta'],
                          CampoPs=[IdContaOrigem])

            funcs.upMySQL(TabelaBd='tb_capitaltotal',
                          CampoBd=['capitalinicial'],
                          CampoFm=[valorTotalBanco],
                          CampoWr=['id_capitaltotal'],
                          CampoPs=[1])
            session['saldo'] = valorTotalBanco
            
            return ConferenciaDepositoTabela()
        else:
            funcs.upMySQL(TabelaBd='tb_transacao', 
                      CampoBd=['status_transacao', 'data_aceite_recusa'],
                      CampoFm=[2, datetime.today()],
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
            funcs.upMySQL('tb_contabancaria',
                           CampoBd=['status_contabancaria'],
                           CampoFm=[1],
                           CampoWr=['id_conta'],
                           CampoPs=[IdConta])
            return AceiteContaTabela()
        else:    
            funcs.upMySQL('tb_contabancaria',CampoBd=['status_contabancaria'],CampoFm=[2],
                                        CampoWr=['id_conta'],CampoPs=[IdConta])
            return AceiteContaTabela()
       
#------------------------------
#Bloco de renderização da tela de Transação
@app.route("/Transacao")
def Transacao():
    if session['saldo'] != None:
        saldo = f"{session['saldo']:.2f}".replace(".",",")
    return render_template('transferencianew.html',saldo=saldo)

#------------------------------
#Bloco de transação entre contas
@app.route("/TransacaoConta",  methods = ['POST', 'GET'])
def TransacaoConta():
    if request.method == 'POST':
        if  float(session['saldo']) > 0  and float(request.form['valor']) > 0 and float(request.form['valor']) < float(session['saldo']):
            numeroConta = request.form['numeroConta']
            valor = float(request.form['valor'])

            pesquisaContaDestino = funcs.SlcEspecificoMySQL(TabelaBd='tb_contabancaria',
                                                CampoBd=['numeroconta'],
                                                CampoFm=[numeroConta],
                                                CampoEs=['id_conta', 'saldo'])

            pesquisaContaOrigem = funcs.SlcEspecificoMySQL(TabelaBd='tb_contabancaria',
                                                CampoBd=['numeroconta'],
                                                CampoFm=[session['conta']],
                                                CampoEs=['id_conta', 'saldo'])
                                                  
            IdContaDestino = pesquisaContaDestino[0][0]
            IdContaOrigem = pesquisaContaOrigem[0][0]
            if IdContaDestino == IdContaOrigem:
                return Transacao()

            pesquisaSQLContaDestinoCheque = funcs.SlcEspecificoMySQL(TabelaBd='tb_cheque_especial',
                                                                     CampoBd=['ativo', 'id_conta'],
                                                                     CampoFm=['1', IdContaDestino],
                                                                     CampoEs=['valor_devido', 'data_atualizacao'])
            #verifica se o usuário da conta Destino está na situação de cheque especial da conta 
            if pesquisaSQLContaDestinoCheque:
                #pega o valor de quanto a conta Destino está devendo ao banco
                valorDevido = pesquisaSQLContaDestinoCheque[0][0]
                #pega o dia da ultima atualização da conta destino
                dataInicio = pesquisaSQLContaDestinoCheque[0][1]
                diasPeriodo = funcs.periodoEntreDatas(data1=str(dataInicio), data2=str(date.today()))
                if diasPeriodo > 0:
                    pesquisaSQLRegraCheque = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                                                          CampoBd=['id_regra_operacoes'],
                                                                          CampoFm=[1],
                                                                          CampoEs=['porcentagem', 'valor_fixo'])
                    porcentagem = pesquisaSQLRegraCheque[0][0]
                    valorDevido = funcs.calculaChequeEspecial(tempo=diasPeriodo, porecentagem=porcentagem, valorDevido=valorDevido)

                valorContaOrigem = pesquisaContaOrigem[0][1]

                valorContaOrigem = valorContaOrigem - valor
                valorDevido = valorDevido + valor

                funcs.upMySQL(TabelaBd='tb_cheque_especial',
                                      CampoBd=['valor_devido', 'data_atualizacao'],
                                      CampoFm=[valorDevido, date.today()],
                                      CampoPs=[IdContaDestino],
                                      CampoWr=['id_conta'])
                if valorDevido >= 0:
                    funcs.upMySQL(TabelaBd='tb_cheque_especial',
                                      CampoBd=['valor_devido', 'data_atualizacao', 'ativo'],
                                      CampoFm=[valorDevido, date.today(), '0'],
                                      CampoPs=[IdContaDestino],
                                      CampoWr=['id_conta'])

                funcs.upMySQL(TabelaBd='tb_contabancaria',
                                  CampoBd=['saldo'],
                                  CampoFm=[valorContaOrigem],
                                  CampoPs=[IdContaOrigem],
                                  CampoWr=['id_conta'])
                if valorContaOrigem < 0:
                    pesquisaContaOrigemCheque = funcs.SlcEspecificoMySQL(TabelaBd='tb_cheque_especial',
                                                                         CampoBd=['id_conta', 'ativo'],
                                                                         CampoFm=[IdContaOrigem, '1'],
                                                                         CampoEs=['valor_devido', 'data_atualizacao'])
                    if pesquisaContaOrigemCheque:
                        valorDevidoContaOrigem = pesquisaContaOrigemCheque[0][0] + valorContaOrigem
                        dataAtualizacao = pesquisaContaOrigemCheque[0][1]
                        dataPeriodo = funcs.periodoEntreDatas(data1=str(dataAtualizacao), data2=str(date.today()))
                        if dataPeriodo > 0:
                            valorDevidoContaOrigem = funcs.calculaChequeEspecial(valorDevido=valorDevidoContaOrigem, porecentagem=porcentagem, tempo=dataPeriodo)
                        funcs.upMySQL(TabelaBd='tb_cheque_especial',
                                      CampoBd=['valor_devido', 'data_atualizacao'],
                                      CampoFm=[valorDevidoContaOrigem, date.today()],
                                      CampoPs=[IdContaOrigem, '1'],
                                      CampoWr=['id_conta', 'ativo'])
                    else:
                        funcs.InsMySQL(TabelaBd='tb_cheque_especial',
                                       CampoBd=['id_conta', 'data_inicio', 'data_atualizacao', 'valor_devido', 'ativo'],
                                       CampoFm=[IdContaOrigem, date.today(), date.today(), valorContaOrigem, '1'])

                funcs.Transacao(conta_origem=IdContaOrigem, conta_destino=IdContaDestino, tipo='transferencia', valor=float(request.form['valor']), status='1')
                return Transacao()

            valorContaDestino = pesquisaContaDestino[0][1]
            valorContaOrigem = pesquisaContaOrigem[0][1]

            valorContaDestino = valorContaDestino + valor
            valorContaOrigem = valorContaOrigem - valor

            funcs.upMySQL(TabelaBd='tb_contabancaria',
                      CampoBd=['saldo'],
                      CampoFm=[valorContaOrigem],
                      CampoPs=[IdContaOrigem],
                      CampoWr=['id_conta'])

            funcs.upMySQL(TabelaBd='tb_contabancaria',
                      CampoBd=['saldo'],
                      CampoFm=[valorContaDestino],
                      CampoPs=[IdContaDestino],
                      CampoWr=['id_conta'])

            session['saldo'] = valorContaOrigem

            funcs.Transacao(conta_origem=IdContaOrigem, conta_destino=IdContaDestino, tipo='transferencia', valor=float(request.form['valor']), status='1')
            return Transacao()
    return Transacao()
        
#------------------------------

#Página configurações

@app.route("/Config")
def Config():
    return render_template("u_config.html")

#------------------------------

# Página Sua Conta Gerente Agencia
@app.route("/SuaContaG")
def SuaContaG():
    return render_template("suaContaG.html",pagina=1)

# Página Sua Conta Gerente Geral
@app.route("/SuaConta")
def SuaContaGG():
    return render_template("suaContaGG.html")
# ------------------------------

#Bloco de requisição de Abertura de Conta

@app.route("/AceiteContaTabela")
def AceiteContaTabela():

    cabecalho = ('Nome', 'CPF', 'Número Conta', 'Data Nasc', 'Endereço', 'Genero', 'Tipo Conta', '', '')

    pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_usuario INNER JOIN tb_contabancaria ON tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                           CampoEs=['tb_contabancaria.id_conta','tb_usuario.nome', 'tb_usuario.cpf', 'tb_contabancaria.numeroconta','tb_usuario.datanascimento','tb_usuario.endereco','tb_usuario.genero', 'tb_contabancaria.tipo'],
                                           CampoBd=['tb_contabancaria.status_contabancaria'],
                                           CampoFm=[0])

    return render_template("AceiteConta.html", cabecalhoTabela=cabecalho, pesquisaSQLTabela=pesquisaSQL)

@app.route("/AceiteAlteracaoTabela")    
def AceiteAlteracaoTabela():

    cabecalho = ('Nome', 'CPF', 'Data Nasc', 'Número Conta', 'Tipo Conta', 'Descrição')

    pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_usuario INNER JOIN tb_contabancaria ON tb_usuario.id_usuario = tb_contabancaria.id_usuario INNER JOIN tb_requisicoes ON tb_usuario.id_usuario = tb_requisicoes.id_usuario',
                                           CampoEs=['tb_contabancaria.id_conta', 'tb_usario.id_usuario','tb_usuario.nome', 'tb_usuario.cpf', 'tb_contabancaria.numeroconta','tb_usuario.datanascimento', 'tb_contabancaria.tipo' , 'tb_requisicoes'],
                                           CampoBd=['status_alteracao'],
                                           CampoFm=[0])

    return render_template("ReqAlt.html", cabecalhoTabela=cabecalho, pesquisaSQLTabela=pesquisaSQL)

@app.route("/ReqAlt")
def ReqAlt():
    return render_template('ReqAlt.html')


@app.route("/Cancelamento")
def Cancelamento():
    return render_template('cancelamento.html')

@app.route("/CancelamentoConta",  methods = ['POST', 'GET'])
def CancelamentoConta():
    if request.method == 'POST':
        id_usuario = funcs.SlcEspecificoMySQL(TabelaBd='tb_contabancaria INNER JOIN tb_usuario ON tb_contabancaria.id_usuario = tb_usuario.id_usuario ',
                                             CampoBd=['numeroconta'],
                                             CampoFm=[session['conta']],
                                             CampoEs=['tb_usuario.id_usuario'])
        senha = request.form['senha']
        funcs.cancelMySQL(id_usuario = id_usuario[0][0], senha= senha, numeroconta= session['conta'])
        

#------------------------------

#Bloco de requisição de Abertura de Conta

@app.route("/RequisicaoAberturaConta")
def RequisicaoAberturaConta():
    return render_template('RequisicaoAberturaConta.html')

@app.route("/AberturaConta", methods = ['POST', 'GET'])
def AberturaConta():
    if request.method == 'POST':

        tipoConta = request.form['tipoconta']
        conta = session['conta']

        pesquisaUsario = funcs.SlcEspecificoMySQL(TabelaBd='tb_contabancaria INNER JOIN tb_usuario ON tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                           CampoEs=['tb_usuario.id_usuario', 'tb_usuario.cpf', 'tb_usuario.nome'],
                                           CampoBd=['numeroconta'],
                                           CampoFm=[conta])
        
        idUsuario = pesquisaUsario[0][0]
        cpf = pesquisaUsario[0][1]
        nome = pesquisaUsario[0][2]
        numeroConta = funcs.geraId(str(nome),str(1),str(cpf))
        
        funcs.InsMySQL(TabelaBd='tb_contabancaria',
                        CampoBd=['tipo', 'id_usuario', 'id_agencia', 'numeroconta', 'data_abertura', 'saldo', 'status_contabancaria'],
                        CampoFm=[tipoConta, idUsuario, 1, numeroConta, datetime.today(), 0, '0'])    

        return RequisicaoAberturaConta()

#------------------------------

#Bloco de alteração do saldo do banco
@app.route("/AltSaldo",  methods = ['POST', 'GET'])
def AltSaldo():
    if request.method == 'POST': 
        NovoSaldoBK = request.form['ValNovoSaldo']
        session['saldo'] =float(NovoSaldoBK)
        funcs.upMySQL('tb_capitaltotal',CampoBd=['capitalinicial'],CampoFm=[NovoSaldoBK],CampoWr=['id_capitaltotal'],CampoPs=['1'])
        
    saldo = f"{session['saldo']:.2f}".replace(".",",")
    saldoV = f"{session['saldo']:.2f}"
    return render_template('AltSaldo.html',saldo=saldo,saldoV=saldoV)    
#------------------------------

#Bloco de Listagem de usuarios
@app.route("/ListUsa",  methods = ['POST', 'GET'])
def ListUsa():
    cursor = mysql.connection.cursor()
        
    cabecalho = ("Nome", "Email", "CPF", "Gênero", "Endereço", "Data de nascimento","Status","Alterar dados")
    
    SelectGA = f"""SELECT TC.id_conta,TU.nome,TU.email,TU.cpf,TU.genero,TU.endereco,TU.datanascimento,IF(TC.status_contabancaria='1', "ativo", "desativado")
    FROM tb_contabancaria as TC INNER JOIN tb_usuario as TU ON TC.id_usuario=TU.id_usuario;"""
    cursor.execute(SelectGA)
    pesquisaSQL = cursor.fetchall()
    
    mysql.connection.commit() 
    
    return render_template('ListUsa.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho,pagina=0)
#------------------------------

#Bloco de Listagem de Requesições
# @app.route("/ListReq",  methods = ['POST', 'GET'])
# def ListReq():
#     cursor = mysql.connection.cursor()
    
#     return render_template('ListReq.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho)
#------------------------------

#Bloco de Listagem de usuarios por agencia
@app.route("/ListUsaGA",  methods = ['POST', 'GET'])
def ListUsaGA():
    cursor = mysql.connection.cursor()
    
    SelectAgencia = f"""SELECT id_agencia FROM tb_agencia where id_funcionario='{session['idFunc']}';"""
    cursor.execute(SelectAgencia)
    pesquisaAgen = cursor.fetchall()
    
    cabecalho = ("Nome", "Email", "CPF", "Gênero", "Endereço", "Data de nascimento","Status","Alterar dados")
    
    SelectGA = f"""SELECT TC.id_conta,TU.nome,TU.email,TU.cpf,TU.genero,TC.tipo,TC.data_abertura,IF(TC.status_contabancaria='1', "ativo", "desativado")
    FROM tb_contabancaria as TC INNER JOIN tb_usuario as TU ON TC.id_usuario=TU.id_usuario where TC.id_agencia={pesquisaAgen[0][0]}"""
    cursor.execute(SelectGA)
    pesquisaSQL = cursor.fetchall()
    
    mysql.connection.commit() 
    
    return render_template('ListUsa.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho,pagina=1)
#------------------------------

#Bloco de Listagem das agencias
@app.route("/ListAG",  methods = ['POST', 'GET'])
def ListAG():
    cursor = mysql.connection.cursor()
       
    cabecalho = ('Localidade','Número agência','Funcionario','Status','Alterar Dados')
       
    SelectGA = f"""SELECT localidade,numero_agencia,nome,IF(status_agencia='1', "ativo", "desativado") as status 
    FROM tb_agencia as TA left join tb_funcionario as TF on TA.id_funcionario=TF.id_funcionario 
    left join tb_usuario as TU on TF.id_usuario=TU.id_usuario order by localidade"""
    cursor.execute(SelectGA)
    pesquisaSQL = cursor.fetchall()
   
    mysql.connection.commit() 
   
    return render_template('ListAG.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho)
#------------------------------
# Tabela e home de agências
@app.route("/agencias", methods = ['POST', 'GET'])
def agencias():
    cabecalho   = ('Localidade','Número agência','Funcionario','Status','Alterar Dados','Excluir')
    cursor = mysql.connection.cursor()
            
    textoSQL = f"""SELECT id_agencia,localidade,numero_agencia,nome,IF(status_agencia='1', "Ativo", "Desativado") as status 
    FROM tb_agencia as TA left join tb_funcionario as TF on TA.id_funcionario=TF.id_funcionario 
    left join tb_usuario as TU on TF.id_usuario=TU.id_usuario order by localidade"""
            
    cursor.execute(textoSQL)
    pesquisaSQL = cursor.fetchall()
    mysql.connection.commit()     
    cursor.close()   
      
    return render_template('agencias.html',cabecalhoTabela=cabecalho, pesquisaSQLTabela=pesquisaSQL)

#-----------------------------------------
#1 [Criar Agencia]
@app.route("/criaAgencia", methods = ['POST', 'GET'])
def criaAgencia():
    if request.method == 'POST':
        localidade = request.form['localidade']
        numeroAgencia = request.form['numeroAgencia']
        idgerenteAgencia = request.form['funcionario']

        existe = funcs.SlcEspecificoMySQL(TabelaBd='tb_agencia',
                                           CampoEs=['numero_agencia'],
                                           CampoBd=['numero_agencia'],
                                           CampoFm=[numeroAgencia])

        if existe == ():
            funcs.criaAgencia(localidade=localidade, numeroAgencia=numeroAgencia, idGerenteAgencia=idgerenteAgencia)
            return agencias()
        else:
            raise Exception('604')
    
    cursor = mysql.connection.cursor()
    
    textoSQL = f"""SELECT tb_usuario.nome,
                   tb_funcionario.id_funcionario
                   FROM tb_funcionario 
                   LEFT JOIN tb_agencia
                   ON tb_agencia.id_funcionario = tb_funcionario.id_funcionario
                   INNER JOIN tb_usuario
                   ON tb_funcionario.id_usuario = tb_usuario.id_usuario
                   WHERE tb_agencia.id_funcionario IS NULL 
                   AND tb_funcionario.papel != 'GERENTE GERAL';"""
            
    cursor.execute(textoSQL)
    pesquisaSQL = cursor.fetchall()
    mysql.connection.commit()     
    cursor.close()
    dicionarioPesquisa = []
    for row in pesquisaSQL:    
        dicionarioPesquisa.append({
        "nome" : row[0],
        "id" : row[1]
        })

    return render_template('criaAgencia.html', listaGerente=dicionarioPesquisa)
#------------------------------

# Página Sua Conta
@app.route("/suaConta")
def suaConta():
    if session['tipo'] == 2:
        #SE TIVER REQUISICAO DE ALTERAÇÃO NO NOME DELE ATIVA, NÃO MOSTRA A OPÇÃO ALTERAR SOMENTE UM SPAN QUE DIZ
        #REQUISIÇÃO EM ESPERA
        dadosUsuario = funcs.dadosU('', session['idFunc'])
        print(dadosUsuario['cpf'])
        cpf = dadosUsuario['cpf'][0:3] + '.' + dadosUsuario['cpf'][3:6] + '.' + dadosUsuario['cpf'][6:9] +'-'+ dadosUsuario['cpf'][9:]
        if dadosUsuario['genero'] == 'M':
            return render_template ("suaConta.html",pagina=session['tipo'],
                                    idUsuario=dadosUsuario['idUsuario'],
                                    idFuncionario=dadosUsuario['idFuncionario'],
                                    nome=dadosUsuario['nome'],
                                    email=dadosUsuario['email'],
                                    cpf=cpf,
                                    genero='Masculino',
                                    endereco=dadosUsuario['endereco'],
                                    dataNasc=dadosUsuario['dataNasc'],
                                    loginVisivel='',
                                    login=dadosUsuario['login'],
                                    senha=dadosUsuario['senha'],)
        elif dadosUsuario['genero'] == 'F':
            return render_template ("suaConta.html",pagina=session['tipo'],
                                    idUsuario=dadosUsuario['idUsuario'],
                                    idFuncionario=dadosUsuario['idFuncionario'],
                                    nome=dadosUsuario['nome'],
                                    email=dadosUsuario['email'],
                                    cpf=cpf,
                                    genero='Feminino',
                                    endereco=dadosUsuario['endereco'],
                                    dataNasc=dadosUsuario['dataNasc'],
                                    loginVisivel='',
                                    login=dadosUsuario['login'],
                                    senha=dadosUsuario['senha'],)
        else:
            return render_template ("suaConta.html",pagina=session['tipo'],
                                    idUsuario=dadosUsuario['idUsuario'],
                                    idFuncionario=dadosUsuario['idFuncionario'],
                                    nome=dadosUsuario['nome'],
                                    email=dadosUsuario['email'],
                                    cpf=cpf,
                                    genero='Outro',
                                    endereco=dadosUsuario['endereco'],
                                    dataNasc=dadosUsuario['dataNasc'],
                                    loginVisivel='',
                                    login=dadosUsuario['login'],
                                    senha=dadosUsuario['senha'],)

    #caso ele seja usuario comum
    elif session['tipo'] == 1:
        #SE TIVER REQUISICAO DE ALTERAÇÃO NO NOME DELE ATIVA, NÃO MOSTRA A OPÇÃO ALTERAR SOMENTE UM SPAN QUE DIZ
        #REQUISIÇÃO EM ESPERA
        dadosUsuario = funcs.dadosU(session['conta'], '')

        cpf = dadosUsuario['cpf'][0:3] + '.' + dadosUsuario['cpf'][3:6] + '.' + dadosUsuario['cpf'][6:9] +'-'+ dadosUsuario['cpf'][9:]

        if dadosUsuario['genero'] == 'M':
            return render_template ("suaConta.html",pagina=session['tipo'],
                                    idUsuario=dadosUsuario['idUsuario'],
                                    idFuncionario='',
                                    nome=dadosUsuario['nome'],
                                    email=dadosUsuario['email'],
                                    cpf=cpf,
                                    genero='Masculino',
                                    endereco=dadosUsuario['endereco'],
                                    dataNasc=dadosUsuario['dataNasc'],
                                    loginVisivel=False,
                                    login='',
                                    senha=dadosUsuario['senha'],)
        elif dadosUsuario['genero'] == 'F':
            return render_template ("suaConta.html",pagina=session['tipo'],
                                    idUsuario=dadosUsuario['idUsuario'],
                                    idFuncionario='',
                                    nome=dadosUsuario['nome'],
                                    email=dadosUsuario['email'],
                                    cpf=cpf,
                                    genero='Feminino',
                                    endereco=dadosUsuario['endereco'],
                                    dataNasc=dadosUsuario['dataNasc'],
                                    loginVisivel=False,
                                    login='',
                                    senha=dadosUsuario['senha'],)
        else:
            return render_template ("suaConta.html",pagina=session['tipo'],
                                    idUsuario=dadosUsuario['idUsuario'],
                                    idFuncionario='',
                                    nome=dadosUsuario['nome'],
                                    email=dadosUsuario['email'],
                                    cpf=cpf,
                                    genero='Outro',
                                    endereco=dadosUsuario['endereco'],
                                    dataNasc=dadosUsuario['dataNasc'],
                                    loginVisivel=False,
                                    login='',
                                    senha=dadosUsuario['senha'],)
    else:
        #SE TIVER REQUISICAO DE ALTERAÇÃO NO NOME DELE ATIVA, NÃO MOSTRA A OPÇÃO ALTERAR SOMENTE UM SPAN QUE DIZ
        #REQUISIÇÃO EM ESPERA
        dadosUsuario = funcs.dadosU('', session['idFunc'])
        print(dadosUsuario['cpf'])
        cpf = dadosUsuario['cpf'][0:3] + '.' + dadosUsuario['cpf'][3:6] + '.' + dadosUsuario['cpf'][6:9] +'-'+ dadosUsuario['cpf'][9:]
        if dadosUsuario['genero'] == 'M':
            return render_template ("suaConta.html",pagina=3,
                                    idUsuario=dadosUsuario['idUsuario'],
                                    idFuncionario=dadosUsuario['idFuncionario'],
                                    nome=dadosUsuario['nome'],
                                    email=dadosUsuario['email'],
                                    cpf=cpf,
                                    genero='Masculino',
                                    endereco=dadosUsuario['endereco'],
                                    dataNasc=dadosUsuario['dataNasc'],
                                    loginVisivel='',
                                    login=dadosUsuario['login'],
                                    senha=dadosUsuario['senha'],)
        elif dadosUsuario['genero'] == 'F':
            return render_template ("suaConta.html",pagina=3,
                                    idUsuario=dadosUsuario['idUsuario'],
                                    idFuncionario=dadosUsuario['idFuncionario'],
                                    nome=dadosUsuario['nome'],
                                    email=dadosUsuario['email'],
                                    cpf=cpf,
                                    genero='Feminino',
                                    endereco=dadosUsuario['endereco'],
                                    dataNasc=dadosUsuario['dataNasc'],
                                    loginVisivel='',
                                    login=dadosUsuario['login'],
                                    senha=dadosUsuario['senha'],)
        else:
            return render_template ("suaConta.html",pagina=3,
                                    idUsuario=dadosUsuario['idUsuario'],
                                    idFuncionario=dadosUsuario['idFuncionario'],
                                    nome=dadosUsuario['nome'],
                                    email=dadosUsuario['email'],
                                    cpf=cpf,
                                    genero='Outro',
                                    endereco=dadosUsuario['endereco'],
                                    dataNasc=dadosUsuario['dataNasc'],
                                    loginVisivel='',
                                    login=dadosUsuario['login'],
                                    senha=dadosUsuario['senha'],)


@app.route("/alteraU", methods = ['POST', 'GET'])
def alteraU():
    # print(request.method)
    if request.method == 'POST':
        if session['tipo'] == 2:
            dadosUsuario = funcs.dadosU('',session['idFunc'])
            cpf = dadosUsuario['cpf'][0:3] + '.' + dadosUsuario['cpf'][3:6] + '.' + dadosUsuario['cpf'][6:9] +'-'+ dadosUsuario['cpf'][9:]
            novosDados = {
                'idUsuario': request.form['idUsuario'],
                'idFuncionario': request.form['idFuncionario'],
                'nome': request.form['nome'],
                'email': request.form['email'],
                'cpf': request.form['cpf'],
                'genero': request.form['genero'],
                'endereco': request.form['endereco'],
                'dataNasc': request.form['datanasc'],
                'login': request.form['login'],
                'senha': request.form['senha']
            }

            funcs.alteraU(novosDados,session['tipo'])
            return suaConta()

        elif session['tipo'] == 1:
            dadosUsuario = funcs.dadosU(session['conta'],'')
            cpf = dadosUsuario['cpf'][0:3] + '.' + dadosUsuario['cpf'][3:6] + '.' + dadosUsuario['cpf'][6:9] +'-'+ dadosUsuario['cpf'][9:]
            novosDados = {
                'idUsuario': request.form['idUsuario'],
                'idFuncionario': request.form['idFuncionario'],
                'nome': request.form['nome'],
                'email': request.form['email'],
                'cpf': request.form['cpf'],
                'genero': request.form['genero'],
                'endereco': request.form['endereco'],
                'dataNasc': request.form['datanasc'],
                'login': request.form['login'],
                'senha': request.form['senha']
            }

            funcs.alteraU(novosDados,session['tipo'])
            return suaConta()

    elif request.method == 'GET':
        if session['tipo'] == 2:
            dadosUsuario = funcs.dadosU('',session['idFunc'])
            cpf = dadosUsuario['cpf'][0:3] + '.' + dadosUsuario['cpf'][3:6] + '.' + dadosUsuario['cpf'][6:9] +'-'+ dadosUsuario['cpf'][9:]
            # if dadosUsuario['genero'] == 'M':
            return render_template ("alteraU.html",pagina=2,novosDados=dadosUsuario,
                                        idUsuario=dadosUsuario['idUsuario'],
                                        idFuncionario=dadosUsuario['idFuncionario'],
                                        nome=dadosUsuario['nome'],
                                        email=dadosUsuario['email'],
                                        cpf=cpf,
                                        endereco=dadosUsuario['endereco'],
                                        dataNasc=dadosUsuario['dataNasc'],
                                        loginVisivel='',
                                        login=dadosUsuario['login'],
                                        senha=dadosUsuario['senha'],
                                        selM='selected',
                                        selF='',
                                        selO='')
        elif session['tipo'] == 1:
            dadosUsuario = funcs.dadosU(session['conta'],'')
            cpf = dadosUsuario['cpf'][0:3] + '.' + dadosUsuario['cpf'][3:6] + '.' + dadosUsuario['cpf'][6:9] +'-'+ dadosUsuario['cpf'][9:]
            # if dadosUsuario['genero'] == 'M':
            return render_template ("alteraU.html",pagina=1,
                                        idUsuario=dadosUsuario['idUsuario'],
                                        idFuncionario=dadosUsuario['idFuncionario'],
                                        nome=dadosUsuario['nome'],
                                        email=dadosUsuario['email'],
                                        cpf=cpf,
                                        endereco=dadosUsuario['endereco'],
                                        dataNasc=dadosUsuario['dataNasc'],
                                        loginVisivel=False,
                                        login=dadosUsuario['login'],
                                        senha=dadosUsuario['senha'],
                                        selM='selected',
                                        selF='',
                                        selO='')
        else:
            dadosUsuario = funcs.dadosU('',session['idFunc'])
            cpf = dadosUsuario['cpf'][0:3] + '.' + dadosUsuario['cpf'][3:6] + '.' + dadosUsuario['cpf'][6:9] +'-'+ dadosUsuario['cpf'][9:]
            # if dadosUsuario['genero'] == 'M':
            return render_template ("alteraU.html",pagina=3,novosDados=dadosUsuario,
                                        idUsuario=dadosUsuario['idUsuario'],
                                        idFuncionario=dadosUsuario['idFuncionario'],
                                        nome=dadosUsuario['nome'],
                                        email=dadosUsuario['email'],
                                        cpf=cpf,
                                        endereco=dadosUsuario['endereco'],
                                        dataNasc=dadosUsuario['dataNasc'],
                                        loginVisivel='',
                                        login=dadosUsuario['login'],
                                        senha=dadosUsuario['senha'],
                                        selM='selected',
                                        selF='',
                                        selO='')
#------------------------------

#Requisição de alteração de dados
@app.route("/reqaltUsuario", methods = ['POST', 'GET'])
def reqaltUsuario():
    if request.method == 'POST':
        IdUsu = session['idContabk']
        nome= request.form['nome']
        email= request.form['email']
        cpf= request.form['cpf']
        genero= request.form['genero']
        endereco= request.form['endereco']
        datanascimento= request.form['datanascimento']
        senha= request.form['senha']
        
        
        formsaltUsuario = funcs.InsMySQL('tb_requisicoes',CampoBd=["nome","email", "cpf", "genero", "endereco", "datanascimento","senha","id_usuario"],
                                CampoFm=[nome, email, cpf, genero, endereco, datanascimento, senha,IdUsu]) 
        
        return render_template('reqaltUsuario',altnome= formsaltUsuario[0][0],
                                               altemail= formsaltUsuario[0][1],
                                               altcpf= formsaltUsuario[0][2],
                                               altgenero= formsaltUsuario[0][3],
                                               altendereco= formsaltUsuario[0][4],
                                               altdatanascimento= formsaltUsuario[0][5],
                                               altsenha= formsaltUsuario [0][6])                                                  
    #falta colocar a confirmação de senha

#------------------------------

#alteração de dados usuario para gerente geral
@app.route("/AltDadosUsuGG", methods = ['POST', 'GET'])
def AltDadosUsuGG():  
    cursor = mysql.connection.cursor()
    IdContaBanc = request.form['IdContaBanc']
    pagina = request.form['pagina']
        
    print(IdContaBanc)
    SelectGA = f"""SELECT * FROM tb_contabancaria as TC INNER JOIN tb_usuario as TU ON TC.id_usuario=TU.id_usuario where TC.id_conta={IdContaBanc};"""
    cursor.execute(SelectGA)
    dados = cursor.fetchall()
    dados = [list(row) for row in dados]
    mysql.connection.commit() 
        
    teste = dados[0][11]
    dados[0][11] = '{}.{}.{}-{}'.format(teste[:3], teste[3:6], teste[6:9], teste[9:])

    return render_template('AltDadosUsuGG.html',dados=dados,pagina=pagina)    

@app.route("/updateUsuGG", methods = ['POST', 'GET'])
def updateUsuGG():
    if request.method == 'POST':
        pagina      = request.form['pagina']
        IdUsu       = request.form['IdUsu']
        nome        = request.form['nome']
        email       = request.form['email']
        endereco    = request.form['endereco']
        cpf         = ((request.form['cpf']).replace('.','')).replace('-','')
        genero      = request.form['genero']
        dataNasc    = request.form['datanasc']
            
        funcs.upMySQL('tb_usuario',CampoBd=["nome","email", "cpf", "genero", "endereco", "datanascimento"],CampoFm=[nome, email, cpf, genero, endereco, dataNasc],CampoWr=['id_usuario'],CampoPs=[IdUsu])
        
    if pagina == 0:    
        return ListUsa()
    else:
        return ListUsaGA()
#------------------------------

#Funcao gerentes do Gerente Geral
@app.route("/gerentes", methods = ['POST', 'GET'])
def gerentes():
    cursor = mysql.connection.cursor()
        
    cabecalho = ('Nome', 'Papel','Matricula')
    
    SelectGA = f"""SELECT id_funcionario, nome, papel, num_matricula FROM tb_funcionario as TF inner join tb_usuario as TU on TU.id_usuario=TF.id_usuario where papel = 'GERENTE DE AGÊNCIA' order by id_funcionario"""
    cursor.execute(SelectGA)
    pesquisaSQL = cursor.fetchall()
    mysql.connection.commit() 
    
    return render_template('gerentes.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho)
#------------------------------

@app.route("/alterarDesligar", methods = ['POST', 'GET'])
def alterarDesligar():
    if request.method == 'POST': 
        botao = request.form.to_dict()
        IdFuncionario = request.form['IdFuncionario']
        if botao['botao'] == 'Alterar':
            dados = funcs.dadosGA(IdFuncionario)
            cpf = dados['cpf'][0:3] + '.' + dados['cpf'][3:6] + '.' + dados['cpf'][6:9] +'-'+ dados['cpf'][9:]
            if dados['genero'] == 'M':
                return render_template('alteraGA.html',
                                idfuncionario=dados['IdFuncionario'],
                                nome=dados['nome'],
                                email=dados['email'],
                                cpf=cpf,
                                genero='MASCULINO',
                                endereco=dados['endereco'],
                                dataNasc=dados['dataNasc'],
                                senha=dados['senha'],
                                login=dados['login'],
                                selM='selected',
                                selF='',
                                selO='')
            elif dados['genero'] == 'F':
                return render_template('alteraGA.html',
                                idfuncionario=dados['IdFuncionario'],
                                nome=dados['nome'],
                                email=dados['email'],
                                cpf=cpf,
                                genero='FEMININO',
                                endereco=dados['endereco'],
                                dataNasc=dados['dataNasc'],
                                senha=dados['senha'],
                                login=dados['login'],
                                selM='',
                                selF='selected',
                                selO='')    
            else:
                return render_template('alteraGA.html',
                                idfuncionario=dados['IdFuncionario'],
                                nome=dados['nome'],
                                email=dados['email'],
                                cpf=cpf,
                                genero='OUTROS',
                                endereco=dados['endereco'],
                                dataNasc=dados['dataNasc'],
                                senha=dados['senha'],
                                login=dados['login'],
                                selM='',
                                selF='',
                                selO='selected')
        elif botao['botao'] == 'Desligar':


            temAgencia = funcs.SlcEspecificoMySQL(TabelaBd='tb_agencia',
                                   CampoBd=['id_funcionario'],
                                   CampoFm=[IdFuncionario],
                                   CampoEs=['id_funcionario'])

            if temAgencia == ():
                funcs.desligaGA(IdFuncionario, "Null")
                return gerentes()

            else:
                cursor = mysql.connection.cursor()
        
                textoSQL = f"""SELECT tb_usuario.nome,
                            tb_funcionario.id_funcionario
                            FROM tb_funcionario 
                            LEFT JOIN tb_agencia
                            ON tb_agencia.id_funcionario = tb_funcionario.id_funcionario
                            INNER JOIN tb_usuario
                            ON tb_funcionario.id_usuario = tb_usuario.id_usuario
                            WHERE tb_agencia.id_funcionario IS NULL 
                            AND tb_funcionario.papel != 'GERENTE GERAL' 
                            AND tb_funcionario.id_funcionario != {IdFuncionario};"""
                        
                cursor.execute(textoSQL)
                pesquisaSQL = cursor.fetchall()
                mysql.connection.commit()     
                cursor.close()
                dicionarioPesquisa = []
                for row in pesquisaSQL:    
                    dicionarioPesquisa.append({
                    "nome" : row[0],
                    "id" : row[1]
                    })

                return render_template('desligaGA.html', listaGerente=dicionarioPesquisa, idfuncionario=IdFuncionario)
        return gerentes()

@app.route("/alteraGA", methods = ['POST', 'GET'])
def alteraGA():
    if request.method == 'POST':
        dados = {
            'idfuncionario': request.form['IdFuncionario'],
            'nome': request.form['nome'],
            'email': request.form['email'],
            'cpf': request.form['cpf'],
            'genero': request.form['genero'],
            'endereco': request.form['endereco'],
            'dataNasc': request.form['datanasc'],
            'senha': request.form['senha'],
            'login': request.form['login']
        }
        dados['cpf'] = dados['cpf'].replace(".","")
        dados['cpf'] = dados['cpf'].replace("-","")
        funcs.alteraGA(dados)
    return gerentes()

@app.route("/desligaGA", methods = ['POST', 'GET'])
def desligaGA():
    if request.method == "POST":
        novoResp = request.form['funcionario']
        IdFuncionario = request.form['IdFuncionario']      
        funcs.desligaGA(IdFuncionario, novoResp)
    return gerentes()
#------------------------------
# Alteração Gerente de Agência
# @app.route("/alteraGA", methods = ['POST', 'GET'])
# def alteraGA(dados):
#     return render_template('alteraGA.html',
#                             nome=dados['nome'],
#                             email=dados['email'],
#                             cpf=dados['cpf'],
#                             genero=dados['genero'],
#                             endereco=dados['endereco'],
#                             dataNasc=dados['dataNasc'],
#                             senha=dados['senha'],
#                             login=dados['login'])

 #------------------------------   

#2 [Cria Gerente de Agencia]
@app.route("/criaGA", methods = ['POST', 'GET'])
def criaGA():
    if request.method == 'POST':
        dados = {
            'nome':'',
            'email':'',
            'endereco':'',
            'cpf':'',
            'genero':'',
            'dataNasc':''
        }
        dados['nome'] = request.form['nome']
        dados['email'] = request.form['email']
        dados['endereco'] = request.form['endereco']
        dados['cpf'] = request.form['cpf']
        dados['genero'] = request.form['genero']
        dados['dataNasc'] = request.form['datanasc']
        acesso = funcs.criaGA(dados)
         
        return render_template ('dadosGA.html',login=acesso['matricula'],senha=acesso['senha'])
    return render_template ('criaGA.html')

#Tratamento de Erros
#@app.errorhandler(Exception)
#def excecao(e):
#    cod_excecao = str(e)
#    cod_excecao = cod_excecao[:3]
#    print(f'{cod_excecao} - {funcs.erro[cod_excecao]}')
#    if session['tipoLog'] == 0:
#        caminhoLogin = '/'
#    else:
#        caminhoLogin = 'loginG'
#    return render_template("erro.html", cod_erro=cod_excecao, desc_erro=funcs.erro[cod_excecao],caminhoLogin=caminhoLogin)
#------------------------------

@app.route("/alterarAG", methods = ['POST', 'GET'])
def alterarAG():
    id_agencia = request.form['Id_agencia']
    
    cursor = mysql.connection.cursor()
            
    textoSQL = f"""SELECT id_agencia,localidade,numero_agencia,nome,TF.id_funcionario FROM tb_agencia as TA 
    left join tb_funcionario as TF on TA.id_funcionario=TF.id_funcionario 
    left join tb_usuario as TU on TF.id_usuario=TU.id_usuario 
    where id_agencia = {id_agencia} order by localidade"""
    
    print(textoSQL)
    
    FuncionarioSQL = f"""SELECT id_funcionario,nome FROM tb_funcionario as TF 
    inner join tb_usuario as TU ON TF.id_usuario=TU.id_usuario 
    where papel = 'GERENTE DE AGÊNCIA';"""
            
    cursor.execute(textoSQL)
    pesquisa = cursor.fetchall()
    
    cursor.execute(FuncionarioSQL)
    dados = cursor.fetchall()
    
    mysql.connection.commit()     
    cursor.close()   
    
    return render_template('alterarAG.html', pesquisa = pesquisa,dados=dados)

@app.route("/UpdateAG", methods = ['POST', 'GET'])
def UpdateAG(): 
    cursor = mysql.connection.cursor()
    if request.method == 'POST': 
        id_agencia = request.form['Id_agencia']
        Localidade = request.form['Localidade']
        NumAge = request.form['NumAge']
        Func = request.form['Func']
        
        textoSQL = f"SELECT id_funcionario FROM tb_agencia WHERE id_agencia = '{id_agencia}'"
        cursor.execute(textoSQL)
        VerFuncionario = cursor.fetchall()
        
        if VerFuncionario[0][0] != Func:
            textoSQLUp = f"UPDATE tb_agencia SET id_funcionario = {VerFuncionario[0][0]} WHERE (id_funcionario = '{Func}');"
        else:
            textoSQLUp = f"UPDATE tb_agencia SET id_funcionario = null WHERE (id_funcionario = '{Func}');"
        
        cursor.execute(textoSQLUp)
        funcs.upMySQL('tb_agencia',CampoBd=['id_funcionario','localidade','numero_agencia'],CampoFm=[Func,Localidade,NumAge],CampoWr=['id_agencia'],CampoPs=[id_agencia])
    if request.method == 'GET':
        id_agencia = request.args['Id_agencia']
        NewAgencia = request.args['IdNewAgencia']
        textoSQL = f"SELECT id_conta FROM tb_contabancaria WHERE id_agencia = '{id_agencia}'"
        cursor.execute(textoSQL)
        ContasBanc = cursor.fetchall()
        
        if ContasBanc:
            for row in ContasBanc:
                funcs.upMySQL('tb_contabancaria',CampoBd=['id_agencia'],CampoFm=[NewAgencia],CampoWr=['id_conta'],CampoPs=[row[0]])
                
        funcs.DelMySQL('tb_agencia',CampoBd=['id_agencia'],CampoFm=[id_agencia])
    return agencias()

@app.route("/configuraCheque")
def configuraCheque():

    pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                           CampoBd=['id_regra_operacoes'],
                                           CampoFm=[1],
                                           CampoEs=['porcentagem'])
    porcentagem = pesquisaSQL[0][0]
    porcentagem = porcentagem*100
    return render_template('configuracaoChequeEspecial.html', porcentagem=porcentagem)

@app.route("/altaraConfigCheque", methods = ['POST', 'GET'])
def altaraConfigCheque():
    if request.method == 'POST':
        porcentagem = request.form.get('porcentagem')
        porcentagem = float(porcentagem)/100
        funcs.upMySQL(TabelaBd='tb_regra_operacoes',
                      CampoBd=['porcentagem'],
                      CampoFm=[porcentagem],
                      CampoPs=[1],
                      CampoWr=['id_regra_operacoes'])

        return configuraCheque()


#-----------------------------------
@app.route("/verMais", methods = ['POST', 'GET'])
def verMais():
    if request.method == 'POST': 
        idTransacao = request.form.get('IdTransacao')
        pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_transacao',
                                                CampoBd=['id_transacao'],
                                                CampoFm=[idTransacao],
                                                CampoEs=['tipo', 'Datatime', 'valor', 'status_transacao', 'id_conta_origem', 'id_conta_destino'])
        idContaOrigem = pesquisaSQL[0][4]
        idContaDestino = pesquisaSQL[0][5]
        tipo = pesquisaSQL[0][0]
        dateTime = pesquisaSQL[0][1]
        valor = pesquisaSQL[0][2]
        statusTransacao = pesquisaSQL[0][3]

        idContaRequisitanteComprovante = int(session['idContaBK'])

        pesquisaSQLContaDestino = funcs.SlcEspecificoMySQL(TabelaBd='tb_contabancaria INNER JOIN tb_usuario on tb_contabancaria.id_usuario = tb_usuario.id_usuario',
                                                          CampoBd=['id_conta'],
                                                          CampoFm=[idContaDestino],
                                                          CampoEs=['numeroconta','nome'])
        
        nomeContaDestino = pesquisaSQLContaDestino[0][1]
        numeroContaDestino = pesquisaSQLContaDestino[0][0]

        pesquisaSQLContaOrigem = funcs.SlcEspecificoMySQL(TabelaBd='tb_contabancaria INNER JOIN tb_usuario on tb_contabancaria.id_usuario = tb_usuario.id_usuario',
                                                          CampoBd=['id_conta'],
                                                          CampoFm=[idContaDestino],
                                                          CampoEs=['numeroconta','nome'])
        nomeContaOrigem = pesquisaSQLContaOrigem[0][1]
        numeroContaOrigem = pesquisaSQLContaOrigem[0][0]

        if statusTransacao == '0':
            statusEscrito = 'Em Aprovação'
        elif statusTransacao == '1':
            statusEscrito = 'Aprovado'
        else:
            statusEscrito = 'Recusado'
        data = str(dateTime.strftime('%x'))
        hora = str(dateTime.strftime('%X'))
        return render_template('verMais.html', 
                                Tipo=tipo,
                                Hora=hora, 
                                Data=data, 
                                Valor=valor, 
                                statusAprovacao=statusEscrito,
                                idContaOrigem=idContaOrigem,
                                idContaDestino=idContaDestino,
                                idContaRequisitanteComprovante=idContaRequisitanteComprovante,
                                nomeContaDestino=nomeContaDestino,
                                numeroContaDestino=numeroContaDestino, 
                                nomeContaOrigem=nomeContaOrigem,
                                numeroContaOrigem=numeroContaOrigem,
                                ID=idTransacao)

#Bloco para subir o site.
if __name__ == "__main__":
    app.run(debug=True)
