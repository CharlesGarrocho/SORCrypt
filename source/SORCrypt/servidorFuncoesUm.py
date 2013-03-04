#coding: utf-8

"""
Modulo responsavel por tratar as requisições como soma, divisao do software.
"""

import socket
import pickle
import settings
from threading import Thread
from Crypto.PublicKey import RSA
from Crypto.Util import randpool


def soma(conexao, valores):
    """
    Envia ao cliente a soma de dois valores.
    """
    try:
        return '{0}'.format(float(valores[1]) + float(valores[2]))
    except:
        return 'ERRO'


def subtracao(conexao, valores):
    """
    Envia ao cliente a subtração de dois valores.
    """
    try:
        return '{0}'.format(float(valores[1]) - float(valores[2]))
    except:
        return 'ERRO'


def produto(conexao, valores):
    """
    Envia ao cliente o produto de dois valores.
    """
    try:
        return '{0}'.format(float(valores[1]) * float(valores[2]))
    except:
        return 'ERRO'   


def trata_cliente(conexao, endereco, chavePrivada, chavePublica):
    """
    Trata as novas requisições dos clientes.
    """

    chavePublicaCliente = pickle.loads(conexao.recv(1024))
    conexao.send(pickle.dumps(chavePublica))

    requisicao = chavePrivada.decrypt(conexao.recv(1024))
    requisicao = requisicao.split('_')
    resposta = 'ERRO'

    print 'Endereço: {0} Requisição: {1}'.format(endereco, requisicao[0])

    # Requisição de soma.
    if requisicao[0] == settings.SOMA:
        resposta = soma(conexao, requisicao)
        
    # Requisição de sobtração.
    elif requisicao[0] == settings.SUBTRACAO:
        resposta = subtracao(conexao, requisicao)        

    # Requisição de produto.
    elif requisicao[0] == settings.PRODUTO:
        resposta = produto(conexao, requisicao)

    try:
        resposta = chavePublicaCliente.encrypt(resposta.encode('ascii', 'ignore'), 32)[0]
    except:
        resposta = 'GRANDE'
        resposta = chavePublicaCliente.encrypt(resposta.encode('ascii', 'ignore'), 32)[0]
    conexao.send(resposta)

    # Após a requisição ser realizada, a conexão é fechada.
    conexao.close()


def loop_servidor():
    """
    Cria um novo soquete e aguarda conexoes.
    """
    
    arqPoll = randpool.RandomPool()
    chavePrivada = RSA.generate(1024, arqPoll.get_bytes)
    chavePublica = chavePrivada.publickey()

    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soquete.bind((settings.HOST_FUNCOES, settings.PORTA_FUNCOES))
    soquete.listen(settings.LISTEN)

    # Fica aqui aguardando novas conexões.
    while True:

        # Para cada nova conexão é criado um novo processo para tratar as requisições.
        conexao = soquete.accept()
        novaConexao = []
        novaConexao.append(conexao[0])
        novaConexao.append(conexao[1])
        novaConexao.append(chavePrivada)
        novaConexao.append(chavePublica)
        Thread(target=trata_cliente, args=(novaConexao)).start()


if __name__  == '__main__':
    print 'Servidor de Funções Iniciou na Porta {0}'.format(settings.PORTA_FUNCOES)
    Thread(target=loop_servidor).start()
