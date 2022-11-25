import os
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from select import select
from tokenize import Double
from flask import Flask, render_template,request, url_for, redirect, session, flash, abort, send_file
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

# Pagina inicial
@app.route("/")
def paginaInicial():
    return render_template('index.html', tituloNavegador='Py.nk')

@app.route("/login")
def index():
    # Zerando session do cliente
    session['login'] = False
    session['nome']  = None
    session['conta'] = None
    session['tipo']  = None
    session['tipoConta'] = None
    session['idContaBK'] = None
    return render_template('login.html', tituloNavegador='Login | Py.nk')
#------------------------------
#Pagina inicial Gerentes
@app.route("/loginG")
def loginG():
    # Zerando session dos gerentes
    session['login'] = False
    session['nome']  = None
    session['conta'] = None
    session['tipo']  = None
    session['idContaBK'] = None
    return render_template('loginG.html', tituloNavegador='Login | Py.nk')
#------------------------------

#Pagina Home
@app.route("/home", methods = ['POST', 'GET'])
def home():
    # Verificando se ocorreu o login
    if session['login'] == False:
        abort(401)
    else:
        saldo = None
        #verificando o tipo de usuário
        if session['tipo'] == 1:
        #region Verificando se o tipo do login é cliente
            cabecalho = ('Tipo', 'Valor', 'Data e hora','Status', 'De:', 'Para:','')
            saldo = funcs.ValEmReal(session['saldo']) # Convertendo saldo para o real
            VarContador=0
            data = datetime.today()
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

            if session['tipoConta'] == 'CONTA POUPANÇA':
                pesquisaContaPoupanca = funcs.SlcEspecificoMySQL(TabelaBd='tb_poupanca',
                                                                 CampoBd=['id_conta', 'ativo'],
                                                                 CampoFm=[session['idContaBK'], 1],
                                                                 CampoEs=['valor_poupanca', 'data_atualizacao'])

                if pesquisaContaPoupanca:
                    valorPoupanca = pesquisaContaPoupanca[0][0]
                    dataAtualizacaoPoupanca = pesquisaContaPoupanca[0][1]
                    dataPeriodoPoupanca = funcs.verificaQuantidadeRendimento(data1=dataAtualizacaoPoupanca, data2=datetime.today())
                    if dataPeriodoPoupanca > 0:
                        pesquisaRegraOperacaoPoupanca = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                                                                 CampoFm=[2],
                                                                                 CampoBd=['id_regra_operacoes'],
                                                                                 CampoEs=['porcentagem'])
                        porcentagemPoupanca = pesquisaRegraOperacaoPoupanca[0][0]
                        valorPoupanca = funcs.calculaPoupanca(valorPoupanca=valorPoupanca, porecentagem=porcentagemPoupanca, tempo=dataPeriodoPoupanca)
                        funcs.upMySQL(TabelaBd='tb_poupanca',
                                      CampoBd=['data_atualizacao', 'valor_poupanca'],
                                      CampoFm=[date.today(), valorPoupanca],
                                      CampoWr=['ativo', 'id_conta'],
                                      CampoPs=[1, session['idContaBK']])
                        funcs.upMySQL(TabelaBd='tb_contabancaria',
                                      CampoBd=['saldo'],
                                      CampoFm=[valorPoupanca],
                                      CampoWr=['id_conta'],
                                      CampoPs=[session['idContaBK']])


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
                
                # Pegando o nome do usuario que é a conta de origem
                nomes1 = funcs.SlcEspecificoMySQL('tb_contabancaria inner join tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                        CampoBd=['tb_contabancaria.id_conta'],
                                                        CampoFm=[row[0]],
                                                        CampoEs=['nome'])

                # Pegando o nome do usuario que é a conta de destino                            
                nomes2 = funcs.SlcEspecificoMySQL('tb_contabancaria inner join tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                        CampoBd=['tb_contabancaria.id_conta'],
                                                        CampoFm=[row[1]],
                                                        CampoEs=['nome'])

                # Convertendo tupla para array
                nomes1 = [list(row) for row in nomes1]
                nomes2 = [list(row) for row in nomes2]
                
                # Juntando os nomes pesquisados para a variavel de geração do extrato
                pesquisaSQL[VarContador].append(nomes1[0][0])
                pesquisaSQL[VarContador].append(nomes2[0][0])

                pesquisaSQL[VarContador][2] = funcs.ValEmReal(pesquisaSQL[VarContador][2])
                
                # Tratando o Status da transação
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
                valorDevido = funcs.truncar(numero=valorDevido,casaDecimal=3)
                valorDevido = valorDevido - 0.005
                valorDevido = funcs.truncar(numero=valorDevido,casaDecimal=2)

            caminhoLogin = '/'
            return render_template('homenew.html',saldo=saldo, chequeEspcial=valorDevido, valorDevidoTotal=valorDevidoTotal,cabecalhoTabela=cabecalho,pesquisaSQLTabela=pesquisaSQL,caminhoLogin=caminhoLogin,IdUsuario=session['idContaBK'])
        else: # Caso seja um gerente
            #region CASO SEJA UM GERENTE
            # Contando a quantidade de requisições
            req=funcs.SlcEspecificoMySQL('tb_requisicoes',CampoBd=['status_alteracao'], CampoFm=['0'], CampoEs=['count(*)'])
            cursor = mysql.connection.cursor()

            # Contando a quantidade de usuários
            textoSQL = f"SELECT count(*) FROM tb_contabancaria;"
            
            cursor.execute(textoSQL)
            tusuarios = cursor.fetchall()
            mysql.connection.commit() 

           
            # Definindo o caminho de volta para o index
            caminhoLogin = 'loginG'
            #Tratamento de envio para a tela do gerente geral ou de agencia
            if session['tipo'] == 2:
                return homeG()
            else:
                pesquisaTotalBanco = funcs.SlcMySQL(TabelaBd='tb_capitaltotal',
                                                    CampoBd=['id_capitaltotal'],
                                                    CampoFm=[1])
                if pesquisaTotalBanco:
                    saldo = funcs.ValEmReal(session['saldo'])
                    return render_template('homenewgg.html',saldo=saldo,req=req,usuarios=tusuarios,caminhoLogin=caminhoLogin)
                else:
                    return cadastroTotalBanco()
            #endregion
#------------------------------

@app.route("/RequisicaoGerenteAgencia", methods = ['POST', 'GET'])
def RequisicaoGerenteAgencia():
    if request.method == "POST":
        requisicao = request.form['requisicao']
     
        #region Conferencia Deposito
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

                pesquisaSQLTipoConta = funcs.SlcEspecificoMySQL(TabelaBd='tb_contabancaria', 
                                                            CampoEs=['tipo'],
                                                            CampoBd=['id_conta'], 
                                                            CampoFm=[IdContaOrigem])
            #region Conta Poupança
            if pesquisaSQLTipoConta[0][0] == 'CONTA POUPANÇA': 
                pesquisaSQLAtivoPoupanca = funcs.SlcEspecificoMySQL(TabelaBd='tb_poupanca', 
                                                                    CampoEs=['ativo', 'valor_poupanca', 'data_atualizacao'],                                                   
                                                                    CampoBd=['id_conta','ativo'], 
                                                                    CampoFm=[IdContaOrigem,1])
                if pesquisaSQLAtivoPoupanca: 

                    valorPoupanca = pesquisaSQLAtivoPoupanca[0][1]
                    dataAtualizacaoPoupanca = pesquisaSQLAtivoPoupanca[0][2]
                    dataPeriodoPoupanca = funcs.verificaQuantidadeRendimento(data1=dataAtualizacaoPoupanca, data2=date.today())
                    if dataPeriodoPoupanca > 0:
                        pesquisaRegraOperacaoPoupanca = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                                                             CampoFm=[2],
                                                                             CampoBd=['id_regra_operacoes'],
                                                                             CampoEs=['porcentagem'])
                        porcentagemPoupanca = pesquisaRegraOperacaoPoupanca[0][0]
                        valorPoupanca = funcs.calculaPoupanca(valorPoupanca=valorPoupanca, porecentagem=porcentagemPoupanca, tempo=dataPeriodoPoupanca)
                        valorPoupanca = valorPoupanca + valorTransacao
                        funcs.upMySQL(TabelaBd='tb_poupanca',
                                      CampoBd=['data_atualizacao', 'valor_poupanca'],
                                      CampoFm=[date.today(), valorPoupanca],
                                      CampoPs=[IdContaOrigem],
                                      CampoWr=['id_conta'])
                    else:
                        valorPoupanca = valorPoupanca + valorTransacao
                        funcs.upMySQL(TabelaBd='tb_poupanca',
                                      CampoBd=['data_atualizacao', 'valor_poupanca'],
                                      CampoFm=[date.today(), valorPoupanca],
                                      CampoPs=[IdContaOrigem], 
                                      CampoWr=['id_conta'])

                else: 
                    funcs.InsMySQL(TabelaBd='tb_poupanca',
                                    CampoBd=['id_conta', 'data_inicio', 'data_atualizacao', 'valor_poupanca', 'ativo'],
                                    CampoFm=[IdContaOrigem, date.today(), date.today(), valorTransacao, 1])
            #endregion

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

                    if session['tipo'] == 2:
                        return homeG(requisicao=requisicao)
                    else:
                        return render_template('ListReq.html',requisicao=requisicao)           

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
                          CampoBd=['status_transacao', 'Datatime'],
                          CampoFm=[1, datetime.today()],
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

                if session['tipo'] == 2:
                    return homeG(requisicao=requisicao)
                else:
                    return render_template('ListReq.html',requisicao=requisicao)
            else:
                funcs.upMySQL(TabelaBd='tb_transacao', 
                          CampoBd=['status_transacao', 'data_aceite_recusa'],
                          CampoFm=[2, datetime.today()],
                          CampoPs=[IdTransacao],
                          CampoWr=['id_transacao'])

                if session['tipo'] == 2:
                    return homeG(requisicao=requisicao)
                else:
                    return render_template('ListReq.html',requisicao=requisicao)
        #endregion 
        #region Aceite de Abertura de Conta
        elif requisicao == '1':
            botao = request.form.to_dict()
            IdConta = request.form['Id']
            # pesquisaAgenciaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_agencia',
            #                                               CampoEs=['id_agencia'],
            #                                               CampoBd=['id_funcionario'],
            #                                               CampoFm=[session['idFunc']])                                                        
            # idAgencia = pesquisaAgenciaSQL[0][0]
            # email = ''
            # email = funcs.SlcEspecificoMySQL('tb_usuario INNER JOIN tb_contabancaria ON tb_usuario.id_usuario = tb_contabancaria.id_usuario',
            #                              CampoBd=['tb_contabancaria.id_conta'],
            #                              CampoFm=[IdConta],
            #                              CampoEs=['tb_usuario.email'])

            if botao['botao'] == 'Confirmar':
                funcs.upMySQL('tb_contabancaria',
                               CampoBd=['status_contabancaria'],
                               CampoFm=[1],
                               CampoWr=['id_conta'],
                               CampoPs=[IdConta])  
            else:    
                funcs.upMySQL('tb_contabancaria',
                              CampoBd=['status_contabancaria'],
                              CampoFm=[2],
                              CampoWr=['id_conta'],
                              CampoPs=[IdConta])

            if session['tipo'] == 2:
                return homeG(requisicao=requisicao)
            else:
                return render_template('ListReq.html',requisicao=requisicao)
                
        #endregion 
        #region Aceitar alteração de dados
        elif requisicao == '2':
            botao = request.form.to_dict()
            if botao['botao'] == 'Confirmar':
                IdConta = request.form['Id']
                Desc = request.form['Desc'].replace('[','').replace(']','').split(',')
                DescSeparada = []
                for row in Desc:
                    doispontos = row.find(':')+1
                    DescSeparada.append(row[doispontos:])
             
            if session['tipo'] == 2:
                return homeG(requisicao=requisicao)
            else:
                return render_template('ListReq.html',requisicao=requisicao)
        #endregion
        #ISSO DAQUI ESTÁ ESTRANHO POR ISSO TA COMENTADO
        # else:
        #     botao = request.form.to_dict()
        #     IdConta = request.form['Id']
        #     if botao['botao'] == 'Confirmar':
        #         Desc = request.form['Desc'].replace('[','').replace(']','').split(',')
        #         DescSeparada = []
        #         for row in Desc:
        #             doispontos = row.find(':')+1
        #             DescSeparada.append(row[doispontos:])
        #         funcs.upMySQL('tb_usuario',
        #                         CampoBd=['nome', 'email', 'cpf', 'genero', 'endereco', 'datanascimento', 'senha'],

        #                         CampoFm=[nome, email,cpf,genero,endereco,datanasc,senha.replace(' ','')],
        #                         CampoWr=['id_usuario'],
        #                         CampoPs=[idUsuario[0]])
             
        #         if session['tipo'] == 2:
        #             return homeG(requisicao=requisicao)
        #         else:
        #             return render_template('ListReq.html',requisicao=requisicao)
        #     else:
        #         botao = request.form.to_dict()
        #         IdConta = request.form['Id']
        #         if botao['botao'] == 'Confirmar':
        #             Desc = request.form['Desc'].replace('[','').replace(']','').split(',')
        #             DescSeparada = []
        #             for row in Desc:
        #                 doispontos = row.find(':')+1
        #                 DescSeparada.append(row[doispontos:])
        #             funcs.upMySQL('tb_usuario',
        #                         CampoBd=['nome', 'email', 'cpf', 'genero', 'endereco', 'datanascimento', 'senha'],
        #                         CampoFm=[DescSeparada[2], DescSeparada[3],DescSeparada[4],DescSeparada[5],DescSeparada[6],DescSeparada[7],DescSeparada[9].replace(' ','')],
        #                         CampoWr=['id_usuario'],
        #                         CampoPs=[DescSeparada[0]])
        #             funcs.upMySQL('tb_requisicoes',
        #                         CampoBd=['status_alteracao'],
        #                         CampoFm=[1],
        #                         CampoWr=['id_requisicao'],
        #                         CampoPs=[IdConta])
                    
        #         if session['tipo'] == 2:
        #                 return homeG(requisicao=requisicao)
        #         else:
        #                 return render_template('ListReq.html')
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
    idAgencia = funcs.verificaAgenciaGerente(session['idFunc'])
    req=funcs.SlcEspecificoMySQL('tb_requisicoes as TR inner join tb_contabancaria as TC on TR.id_usuario=TC.id_usuario INNER JOIN tb_agencia AS TA ON TA.id_agencia = TC.id_agencia', CampoBd=['status_alteracao','TA.id_agencia', 'id_funcionario'], CampoFm=['0',idAgencia, session['idFunc']], CampoEs=['count(*)'])
    ausuarios=funcs.SlcEspecificoMySQL('tb_contabancaria',CampoBd=['id_agencia'], CampoFm=[idAgencia], CampoEs=['count(*)'])
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
            cabecalho = ('Nome', 'CPF', 'Campos Alterados','')
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
                                                               CampoBd=['status_transacao'],
                                                               CampoFm=[0])
            # print(pesquisaSQL);                                                               
            return render_template('ListReq.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho,requisicao=requisicao)
        #endregion
        elif requisicao == '1':
            cabecalho = ('Nome', 'CPF', 'Número Conta', 'Data Nasc', 'Endereço', 'Genero', 'Tipo Conta', '', '')

            pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_usuario INNER JOIN tb_contabancaria ON tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                           CampoEs=['tb_contabancaria.id_conta','tb_usuario.nome', 'tb_usuario.cpf', 'tb_contabancaria.numeroconta','tb_usuario.datanascimento','tb_usuario.endereco','tb_usuario.genero', 'tb_contabancaria.tipo'],
                                           CampoBd=['tb_contabancaria.status_contabancaria'],
                                           CampoFm=[0])    
            return render_template('ListReq.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho,requisicao=requisicao)
        elif requisicao == '2':
            cabecalho = ('Nome', 'CPF', 'Descrição')
            pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_requisicoes  INNER JOIN tb_usuario  ON tb_usuario.id_usuario = tb_requisicoes.id_usuario  INNER JOIN tb_contabancaria  ON tb_usuario.id_usuario = tb_contabancaria.id_usuario INNER JOIN tb_agencia ON tb_contabancaria.id_agencia = tb_agencia.id_agencia',
                                                   CampoEs=['tb_requisicoes.id_requisicao','tb_usuario.nome', 'tb_usuario.cpf', 'tb_requisicoes.descricao'],
                                                   CampoBd=['tb_requisicoes.status_alteracao'],
                                                   CampoFm=['0'])
            print(pesquisaSQL)
            return render_template('ListReq.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho,requisicao=requisicao)
        else:
            return render_template('ListReq.html',pesquisaSQL=pesquisaSQL,cabecalhoTabela=cabecalho,requisicao=requisicao)
    return render_template('ListReq.html')

#Aplicar filtro no extrato
@app.route("/FiltroExtrato",  methods = ['POST', 'GET'])
def FiltroExtrato():
    if request.method == "POST":
        if session['tipo'] == 1:
            cabecalho = ('Tipo', 'Valor', 'Data e hora','Status', 'De:', 'Para:','')
            saldo = funcs.ValEmReal(session['saldo']) # Convertendo saldo para o real
            VarContador=0
            data = datetime.today()

            DataDe      = request.form['DataExtratoDe']
            DateAte     = request.form['DataExtratoAte']
            cursor = mysql.connection.cursor()


            textoSQL = f"""SELECT id_transacao, tipo, valor, Datatime, status_transacao FROM tb_transacao 
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

            if session['tipoConta'] == 'CONTA POUPANÇA':
                pesquisaContaPoupanca = funcs.SlcEspecificoMySQL(TabelaBd='tb_poupanca',
                                                                 CampoBd=['id_conta', 'ativo'],
                                                                 CampoFm=[session['idContaBK'], 1],
                                                                 CampoEs=['valor_poupanca', 'data_atualizacao'])

                if pesquisaContaPoupanca:
                    valorPoupanca = pesquisaContaPoupanca[0][0]
                    dataAtualizacaoPoupanca = pesquisaContaPoupanca[0][1]
                    dataPeriodoPoupanca = funcs.verificaQuantidadeRendimento(data1=dataAtualizacaoPoupanca, data2=datetime.today())
                    if dataPeriodoPoupanca > 0:
                        pesquisaRegraOperacaoPoupanca = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                                                                 CampoFm=[2],
                                                                                 CampoBd=['id_regra_operacoes'],
                                                                                 CampoEs=['porcentagem'])
                        porcentagemPoupanca = pesquisaRegraOperacaoPoupanca[0][0]
                        valorPoupanca = funcs.calculaPoupanca(valorPoupanca=valorPoupanca, porecentagem=porcentagemPoupanca, tempo=dataPeriodoPoupanca)
                        funcs.upMySQL(TabelaBd='tb_poupanca',
                                      CampoBd=['data_atualizacao', 'valor_poupanca'],
                                      CampoFm=[date.today(), valorPoupanca],
                                      CampoWr=['ativo', 'id_conta'],
                                      CampoPs=[1, session['idContaBK']])
                        funcs.upMySQL(TabelaBd='tb_contabancaria',
                                      CampoBd=['saldo'],
                                      CampoFm=[valorPoupanca],
                                      CampoWr=['id_conta'],
                                      CampoPs=[session['idContaBK']])


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
                
                # Pegando o nome do usuario que é a conta de origem
                nomes1 = funcs.SlcEspecificoMySQL('tb_contabancaria inner join tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                        CampoBd=['tb_contabancaria.id_conta'],
                                                        CampoFm=[row[0]],
                                                        CampoEs=['nome'])

                # Pegando o nome do usuario que é a conta de destino                            
                nomes2 = funcs.SlcEspecificoMySQL('tb_contabancaria inner join tb_usuario ON  tb_usuario.id_usuario = tb_contabancaria.id_usuario',
                                                        CampoBd=['tb_contabancaria.id_conta'],
                                                        CampoFm=[row[1]],
                                                        CampoEs=['nome'])

                # Convertendo tupla para array
                nomes1 = [list(row) for row in nomes1]
                nomes2 = [list(row) for row in nomes2]
                
                # Juntando os nomes pesquisados para a variavel de geração do extrato
                pesquisaSQL[VarContador].append(nomes1[0][0])
                pesquisaSQL[VarContador].append(nomes2[0][0])

                pesquisaSQL[VarContador][2] = funcs.ValEmReal(pesquisaSQL[VarContador][2])
                
                # Tratando o Status da transação
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
                valorDevido = funcs.truncar(numero=valorDevido,casaDecimal=3)
                valorDevido = valorDevido - 0.005
                valorDevido = funcs.truncar(numero=valorDevido,casaDecimal=2)

            caminhoLogin = '/'
            return render_template('homenew.html',saldo=saldo, chequeEspcial=valorDevido, valorDevidoTotal=valorDevidoTotal,cabecalhoTabela=cabecalho,pesquisaSQLTabela=pesquisaSQL,caminhoLogin=caminhoLogin)
    return home()
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
def saque(mensagem=''):
    saldo = f"{session['saldo']:.2f}".replace(".",",")
    return render_template('saque.html',saldo=saldo, mensagemSaque=mensagem)
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

            if session['tipoConta']=='CONTA POUPANÇA'and float(session['saldo']) < valor:
                mensagem = "Não é possivel realizar o saque!"
                return saque(mensagem=mensagem)

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
                if session['tipoConta'] == 'CONTA POUPANÇA':
                    pesquisaSQLPoupanca = funcs.SlcEspecificoMySQL(TabelaBd='tb_poupanca',
                                                                   CampoBd=['id_conta', 'ativo'],
                                                                   CampoFm=[idConta, 1],
                                                                   CampoEs=['valor_poupanca', 'data_atualizacao', 'ativo'])
                    dataAtualizacaoPoupanca = pesquisaSQLPoupanca[0][1]
                    valorPoupanca = pesquisaSQLPoupanca[0][0]
                    periododoRendimento = funcs.verificaQuantidadeRendimento(data1=dataAtualizacaoPoupanca, data2=datetime.today())
                    if periododoRendimento > 0:
                        pesquisaSQLRegraPoupanca = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                                                          CampoBd=['id_regra_operacoes'],
                                                                          CampoFm=[2],
                                                                          CampoEs=['porcentagem', 'valor_fixo'])
                        porcentagem = pesquisaSQLRegraPoupanca[0][0]
                        valorPoupanca = funcs.calculaPoupanca(valorPoupanca=valorPoupanca, porecentagem=porcentagem, tempo=periododoRendimento)
                    valorPoupanca = valorPoupanca - valor
                    if valorPoupanca == 0:
                        funcs.upMySQL(TabelaBd='tb_poupanca',
                                  CampoBd=['data_atualizacao', 'data_final', 'ativo', 'valor_poupanca'],
                                  CampoFm=[date.today(), date.today(), 0, valorPoupanca],
                                  CampoWr=['id_conta', 'ativo'],
                                  CampoPs=[idConta, 1])
                    else:
                        funcs.upMySQL(TabelaBd='tb_poupanca',
                                  CampoBd=['data_atualizacao', 'valor_poupanca'],
                                  CampoFm=[date.today(), valorPoupanca],
                                  CampoWr=['id_conta', 'ativo'],
                                  CampoPs=[idConta, 1])
                
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
                                       CampoBd=['id_conta', 'data_inicio', 'data_atualizacao','valor_devido', 'ativo'],
                                       CampoFm=[idConta[0][0],  datetime.today(), date.today(), valor, '1'])

                funcs.Transacao(idConta[0][0], idConta[0][0], 'Saque', float(request.form['valor']), '1')
                

                for row in saldoAtualizado:
                    session['saldo'] = row[0]
                return saque()
            else:
                mensagem = "Não é possivel realizar o saque!"
                return saque(mensagem=mensagem)
        else:
            mensagem = "Não é possivel realizar o saque!"
            return saque(mensagem=mensagem)

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
        
        idAgencia = funcs.verificaAgencia()
        
        funcs.InsMySQL('tb_contabancaria',
                        CampoBd=['id_usuario', 'id_agencia', 'tipo', 'data_abertura', 'numeroconta', 'saldo', 'status_contabancaria'],
                        CampoFm=[id_usuario, idAgencia, tipoConta, datetime.today(), numeroCampo, 0, '0'])
        flash(numeroCampo)
        return render_template('login.html', tituloNavegador='Login | Py.nk')

    return render_template('index.html', tituloNavegador='Cadastro | Py.nk')
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
                session['tipoConta'] = row[12]
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

            pesquisaSQLTipoConta = funcs.SlcEspecificoMySQL(TabelaBd='tb_contabancaria', 
                                                            CampoEs=['tipo'],
                                                            CampoBd=['id_conta'], 
                                                            CampoFm=[IdContaOrigem])
            #region Conta Poupança
            if pesquisaSQLTipoConta[0][0] == 'CONTA POUPANÇA': 
                pesquisaSQLAtivoPoupanca = funcs.SlcEspecificoMySQL(TabelaBd='tb_poupanca', 
                                                                    CampoEs=['ativo', 'valor_poupanca', 'data_atualizacao'],                                                   
                                                                    CampoBd=['id_conta','ativo'], 
                                                                    CampoFm=[IdContaOrigem,1])
                if pesquisaSQLAtivoPoupanca: 

                    valorPoupanca = pesquisaSQLAtivoPoupanca[0][1]
                    dataAtualizacaoPoupanca = pesquisaSQLAtivoPoupanca[0][2]
                    dataPeriodoPoupanca = funcs.verificaQuantidadeRendimento(data1=dataAtualizacaoPoupanca, data2=datetime.today())
                    if dataPeriodoPoupanca > 0:
                        pesquisaRegraOperacaoPoupanca = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                                                             CampoFm=[2],
                                                                             CampoBd=['id_regra_operacoes'],
                                                                             CampoEs=['porcentagem'])
                        porcentagemPoupanca = pesquisaRegraOperacaoPoupanca[0][0]
                        valorPoupanca = funcs.calculaPoupanca(valorPoupanca=valorPoupanca, porecentagem=porcentagemPoupanca, tempo=dataPeriodoPoupanca)
                        valorPoupanca = valorPoupanca + valorTransacao
                        funcs.upMySQL(TabelaBd='tb_poupanca',
                                      CampoBd=['data_atualizacao', 'valor_poupanca'],
                                      CampoFm=[date.today(), valorPoupanca],
                                      CampoPs=[IdContaOrigem],
                                      CampoWr=['id_conta'])
                    else:
                        valorPoupanca = valorPoupanca + valorTransacao
                        funcs.upMySQL(TabelaBd='tb_poupanca',
                                      CampoBd=['data_atualizacao', 'valor_poupanca'],
                                      CampoFm=[date.today(), valorPoupanca],
                                      CampoPs=[IdContaOrigem], 
                                      CampoWr=['id_conta'])

                else: 
                    funcs.InsMySQL(TabelaBd='tb_poupanca',
                                    CampoBd=['id_conta', 'data_inicio', 'data_atualizacao', 'valor_poupanca', 'ativo'],
                                    CampoFm=[IdContaOrigem, date.today(), date.today(), valorTransacao, 1])
            #endregion

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
def Transacao(mensagem=''):
    if session['saldo'] != None:
        saldo = f"{session['saldo']:.2f}".replace(".",",")
    return render_template('transferencia.html',saldo=saldo, mensagemTransacao=mensagem)

#------------------------------
#Bloco de transação entre contas
@app.route("/TransacaoConta",  methods = ['POST', 'GET'])
def TransacaoConta():
    if request.method == 'POST':
                                          
        if float(request.form['valor']) > 0:
            numeroConta = request.form['numeroConta']
            valor = float(request.form['valor'])

            if session['tipoConta']=='CONTA POUPANÇA'and float(session['saldo']) < valor:
                return Transacao(mensagem='Não foi possível realizar a operação')

            pesquisaContaDestino = funcs.SlcEspecificoMySQL(TabelaBd='tb_contabancaria',
                                                CampoBd=['numeroconta'],
                                                CampoFm=[numeroConta],
                                                CampoEs=['id_conta', 'saldo', 'tipo'])

            pesquisaContaOrigem = funcs.SlcEspecificoMySQL(TabelaBd='tb_contabancaria',
                                                CampoBd=['numeroconta'],
                                                CampoFm=[session['conta']],
                                                CampoEs=['id_conta', 'saldo'])
            valorContaOrigem = pesquisaContaOrigem[0][1]
            valorContaOrigem = valorContaOrigem - valor       

            IdContaDestino = pesquisaContaDestino[0][0]
            tipoContaDestino = pesquisaContaDestino[0][2]
            IdContaOrigem = pesquisaContaOrigem[0][0]

            if IdContaDestino == IdContaOrigem:
                return Transacao(mensagem='Não foi possível realziar a operação')
            if session['tipoConta'] == 'CONTA POUPANÇA' and valorContaOrigem < 0:
                return Transacao(mensagem='Não foi possível realziar a operação')
            elif session['tipoConta'] == 'CONTA POUPANÇA' and valorContaOrigem == 0:
                funcs.upMySQL(TabelaBd='tb_poupanca',
                              CampoBd=['valor_poupanca', 'ativo', 'data_final'],
                              CampoFm=[valorContaOrigem, 0, date.today()],
                              CampoWr=['id_conta'],
                              CampoPs=[session['idContaBK']])
        
            DestinoSaiuCheque = True
            OrigemSaiuCheque = True
            pesquisaSQLContaDestinoCheque = funcs.SlcEspecificoMySQL(TabelaBd='tb_cheque_especial',
                                                                     CampoBd=['ativo', 'id_conta'],
                                                                     CampoFm=['1', IdContaDestino],
                                                                     CampoEs=['valor_devido', 'data_atualizacao'])
            #verifica se o usuário da conta Destino está na situação de cheque especial da conta 

           
            if pesquisaSQLContaDestinoCheque:
                #region Verifica Cheque Especial Conta Destino
                DestinoSaiuCheque = False
                #pega o valor de quanto a conta Destino está devendo ao banco
                valorDevido = pesquisaSQLContaDestinoCheque[0][0]
                #pega o dia da ultima atualização da conta destino
                dataAtualizacao = pesquisaSQLContaDestinoCheque[0][1]
                
                dataPeriodo = funcs.periodoEntreDatas(data1= dataAtualizacao, data2= str(date.today))

                if dataPeriodo > 0:
                    pesquisaRegraOperacao = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                                                     CampoBd=['id_regra_operacoes'],
                                                                     CampoFm=[1],
                                                                     CampoEs=['porcentagem'])
                    porcentagem = pesquisaRegraOperacao[0][0]
                    valorDevido = funcs.calculaChequeEspecial(valorDevido=valorDevido, porecentagem=porcentagem, tempo=dataPeriodo)
                valorContaOrigem = valorContaOrigem - valor
                valorDevido = valorDevido + valor
                
                funcs.upMySQL(TabelaBd='tb_cheque_especial',
                                      CampoBd=['valor_devido', 'data_atualizacao'],
                                      CampoFm=[valorDevido, date.today()],
                                      CampoPs=[IdContaDestino],
                                      CampoWr=['id_conta'])
                
                funcs.upMySQL(TabelaBd='tb_contabancaria',
                          CampoBd=['saldo'],
                          CampoFm=[valorContaOrigem],
                          CampoPs=[IdContaOrigem],
                          CampoWr=['id_conta'])
                
                if valorDevido >= 0:
                    DestinoSaiuCheque = True
                    funcs.upMySQL(TabelaBd='tb_cheque_especial',
                                      CampoBd=['valor_devido', 'data_atualizacao', 'ativo'],
                                      CampoFm=[valorDevido, date.today(), '0'],
                                      CampoPs=[IdContaDestino],
                                      CampoWr=['id_conta'])
                #endregion
            else:
                #region CONTA POUPANCA2
                pesquisaContaPoupanca = funcs.SlcEspecificoMySQL(TabelaBd='tb_poupanca',
                                                                 CampoBd=['id_conta', 'ativo'],
                                                                 CampoFm=[IdContaDestino, 1],
                                                                 CampoEs=['valor_poupado', 'data_atualizacao'])
                if pesquisaContaPoupanca:
                    valorPoupado = pesquisaContaPoupanca[0][0] + valor
                    dataPoupado = pesquisaContaPoupanca[0][1]
                    dataPeriodoPoupanca = funcs.verificaQuantidadeRendimento(data1=dataPoupado, data2=datetime.today())
                    if dataPeriodoPoupanca > 0:
                        pesquisaRegraOperacaoPoupanca = funcs.SlcEspecificoMySQL(TabelaBd='tb_regra_operacoes',
                                                                                 CampoFm=[2],
                                                                                 CampoBd=['id_regra_operacoes'],
                                                                                 CampoEs=['porcentagem'])
                        porcentagemPoupanca = pesquisaRegraOperacaoPoupanca[0][0]
                        valorPoupado = funcs.calculaPoupanca(valorPoupanca=valorPoupado, porecentagem=porcentagemPoupanca, tempo=dataPeriodoPoupanca)
                        funcs.upMySQL(TabelaBd='tb_poupanca',
                                      CampoBd=['data_atualizacao', 'valor_poupanca'],
                                      CampoFm=[date.today(), valorPoupado],
                                      CampoWr=['ativo', 'id_conta'],
                                      CampoPs=[1, IdContaDestino])
                        funcs.upMySQL(TabelaBd='tb_contabancaria',
                                      CampoBd=['saldo'],
                                      CampoFm=[valorPoupado],
                                      CampoWr=['id_conta'],
                                      CampoPs=[IdContaDestino])
                elif tipoContaDestino == 'CONTA POUPANÇA':
                    valorContaDestino = valorContaDestino + valor
                    funcs.InsMySQL(TabelaBd='tb_poupanca',
                                   CampoBd=['id_conta', 'data_inicio', 'data_atualizacao', 'valor_poupanca', 'ativo'],
                                   CampoFm=[IdContaDestino, date.today(), date.today(), valorContaDestino, 1])
                    funcs.upMySQL(TabelaBd='tb_contabancaria',
                      CampoBd=['saldo'],
                      CampoFm=[valorContaDestino],
                      CampoPs=[IdContaDestino],
                      CampoWr=['id_conta'])
                    DestinoSaiuCheque = False
                #endregion
     
            if valorContaOrigem < 0:
                #region Verifica CONTA ORIGEM
                pesquisaContaOrigemCheque = funcs.SlcEspecificoMySQL(TabelaBd='tb_cheque_especial',
                                                                     CampoBd=['id_conta', 'ativo'],
                                                                     CampoFm=[IdContaOrigem, '1'],
                                                                     CampoEs=['valor_devido', 'data_atualizacao'])
                if pesquisaContaOrigemCheque:
                    OrigemSaiuCheque = False
                    valorDevidoContaOrigem = pesquisaContaOrigemCheque[0][0] + valorContaOrigem
                    funcs.upMySQL(TabelaBd='tb_cheque_especial',
                                  CampoBd=['valor_devido', 'data_atualizacao'],
                                  CampoFm=[valorDevidoContaOrigem, date.today()],
                                  CampoPs=[IdContaOrigem, '1'],
                                  CampoWr=['id_conta', 'ativo'])
                else:
                    funcs.InsMySQL(TabelaBd='tb_cheque_especial',
                                   CampoBd=['id_conta', 'data_inicio', 'data_atualizacao', 'valor_devido', 'ativo'],
                                   CampoFm=[IdContaOrigem, date.today(), date.today(), valorContaOrigem, '1'])
                #endregion
            if DestinoSaiuCheque == True:
                valorContaDestino = pesquisaContaDestino[0][1]
                valorContaDestino = valorContaDestino + valor
                funcs.upMySQL(TabelaBd='tb_contabancaria',
                      CampoBd=['saldo'],
                      CampoFm=[valorContaDestino],
                      CampoPs=[IdContaDestino],
                      CampoWr=['id_conta'])

            if OrigemSaiuCheque == True:
                funcs.upMySQL(TabelaBd='tb_contabancaria',
                              CampoBd=['saldo'],
                              CampoFm=[valorContaOrigem],
                              CampoPs=[IdContaOrigem],
                              CampoWr=['id_conta'])

            session['saldo'] = valorContaOrigem
            funcs.Transacao(conta_origem=IdContaOrigem, conta_destino=IdContaDestino, tipo='Transferência', valor=float(request.form['valor']), status='1')
            return Transacao()
        else:
           return Transacao(mensagem='Não foi possível realziar a operação')
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

#Bloco de Listagem de usuarios GG
@app.route("/ListUsa",  methods = ['POST', 'GET'])
def ListUsa():
    cursor = mysql.connection.cursor()

    cabecalho = ("Nome", "Email", "CPF", "Gênero", "Endereço", "Data de nascimento","Tipo conta","Status","Alterar dados")
    
    SelectGA = f"""SELECT TC.id_conta,TU.nome,TU.email,TU.cpf,TU.genero,TU.endereco,TU.datanascimento,TC.tipo,IF(TC.status_contabancaria='1', "ativo", "desativado")
    FROM tb_contabancaria as TC INNER JOIN tb_usuario as TU ON TC.id_usuario=TU.id_usuario INNER JOIN tb_agencia as TA ON TA.id_agencia=TC.id_agencia;"""

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
    
    cabecalho = ("Nome", "Email", "CPF", "Gênero", "Tipo conta","Data nascimento","Endereço","Status","Alterar dados")
    
    SelectGA = f"""SELECT TC.id_conta,TU.nome,TU.email,TU.cpf,TU.genero,TC.tipo,TC.data_abertura,TU.endereco,IF(TC.status_contabancaria='1', "ativo", "desativado")
    FROM tb_contabancaria as TC INNER JOIN tb_usuario as TU on TC.id_usuario=TU.id_usuario INNER JOIN tb_agencia as TA ON TA.id_agencia=TC.id_agencia 
    where TC.id_agencia={pesquisaAgen[0][0]}""" 
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
            
    textoSQL = f"""SELECT TA.id_agencia,localidade,numero_agencia,nome,IF(status_agencia='1', "Ativo", "Desativado") as status 
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
        IdUsu = session['idContaBK']
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
        senha    = request.form['senha']
            
        funcs.upMySQL('tb_usuario',CampoBd=["nome","email", "cpf", "genero", "endereco", "datanascimento",'senha'],CampoFm=[nome, email, cpf, genero, endereco, dataNasc, senha],CampoWr=['id_usuario'],CampoPs=[IdUsu])
        
    if pagina == '0':    
        print('entra aq porra')
        return ListUsa()
    else:
        return ListUsa()
#------------------------------

#Funcao gerentes do Gerente Geral
@app.route("/gerentes", methods = ['POST', 'GET'])
def gerentes():
    cursor = mysql.connection.cursor()

    cabecalho = ('Nome', 'Papel','Matricula',"Agência")
    
    SelectGA = f"""SELECT TF.id_funcionario, TU.nome, TF.papel, TF.num_matricula , TA.localidade 
                   FROM tb_funcionario as TF inner join tb_usuario as TU on TU.id_usuario=TF.id_usuario INNER JOIN tb_agencia as TA on TA.id_funcionario=TF.id_funcionario where papel = 'GERENTE DE AGÊNCIA' order by id_funcionario"""

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

@app.route("/cadastroTotalBanco")
def cadastroTotalBanco():
    return render_template("cadastroTotalBanco.html")

#-----------------------------------

@app.route("/cadastrarTotalBanco", methods = ['POST', 'GET'])
def cadastrarTotalBanco():
    if request.method == 'POST':
        valor = float(request.form.get('valor'))
        funcs.InsMySQL(TabelaBd='tb_capitaltotal',
                       CampoBd=['capitalinicial', 'capitalexterno'],
                       CampoFm=[valor, 0])
        return loginG()

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
                                                            CampoFm=[idContaOrigem],
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

@app.route("/download/<id>/<idusuario>", methods = ['GET'])
def download(id, idusuario):
    if id[0:3] == 'ext':
        #preparando os parametros enviados em uma lista
        stringSplit = id[3:].replace('], [','#')
        stringSplit = stringSplit.replace('[[', '')
        stringSplit = stringSplit.replace(']]', '')
        stringSplit = stringSplit.replace('datetime.datetime(', '')
        stringSplit = stringSplit.replace(')','')
        stringSplit = stringSplit.split("#")

        lineSplit = []
        for row in stringSplit:
            lineSplit.append(row.split('", "'))
        
        dados = []

        for cont in range(len(lineSplit)):
            dados.append(lineSplit[cont][0].split(', '))

        for cont in range(len(dados)):
            dados[cont][0] = int(dados[cont][0])
            dados[cont][1] = dados[cont][1].replace("'","")
            dados[cont][2] = dados[cont][2].replace("'","")
            dados[cont][2] = dados[cont][2].replace(",",".")
            dados[cont][2] = float(dados[cont][2])
            dados[cont][9] = dados[cont][9].replace("'","")
            dados[cont][10] = dados[cont][10].replace("'","")
            dados[cont][11] = dados[cont][11].replace("'","")
            if len(dados[cont][6]) < 2:
                dados[cont][6] = '0' + dados[cont][6]
            elif len(dados[cont][7]) < 2:
                dados[cont][7] = '0' + dados[cont][7]
            elif len(dados[cont][8]) < 2:
                dados[cont][8] = '0' + dados[cont][8]
            dados[cont][3] = f'{dados[cont][5]}/{dados[cont][4]}/{dados[cont][3]}'
            dados[cont][4] = f'{dados[cont][6]}:{dados[cont][7]}:{dados[cont][8]}'
            dados[cont].pop(5)
            dados[cont].pop(5)
            dados[cont].pop(5)
            dados[cont].pop(5)

            if dados[cont][1] == 'Transferência':
                pesquisaSQL = funcs.SlcEspecificoMySQL(TabelaBd='tb_transacao',
                                                        CampoBd=['id_transacao'],
                                                        CampoFm=[dados[cont][0]],
                                                        CampoEs=['id_conta_origem'])
                
                if str(pesquisaSQL[0][0]) == idusuario:
                    dados[cont].append('Origem')
                else:
                    dados[cont].append('Destino')
        
        print(dados)
        nomeArq = funcs.geraExtrato(dados,idusuario)
        return send_file(nomeArq, as_attachment=True), os.remove(f'{nomeArq}')

    else:
        idTransacao = id
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
                                                            CampoFm=[idContaOrigem],
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

        dados = ((tipo, hora, data, valor, statusEscrito, idContaOrigem, idContaDestino,
                idContaRequisitanteComprovante, nomeContaDestino, numeroContaDestino,
                nomeContaOrigem, numeroContaOrigem, idTransacao),)

        nomeArq = funcs.geraComprovante(dados)
        print (dados)
        return send_file(nomeArq, as_attachment=True), os.remove(f'{nomeArq}')




#Bloco para subir o site.
if __name__ == "__main__":
    app.run(debug=True)
