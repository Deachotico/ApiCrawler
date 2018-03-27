# coding: utf-8
#!/usr/bin/python3
from flask import Flask
from flask import request
from flask import jsonify
import subprocess
import Crawler
app = Flask(__name__)

#Referencia de url para ser utilizada
@app.route('/')
def root():
    return '''
    <b>O formato correto de chamada é:</b> </br> http://127.0.0.1:5000/findword?urls=[url1,url2]&termo=termo_a_pesquisar</br>
    <b>Parâmetro opcional: </b>
    A Api armazena um cache em disco para uso posterior, caso queira ignorar esse cache envie o parâmetro <b>ingorecache</b></br>
    http://127.0.0.1:5000/findword?urls=[url1,url2]&termo=termo_a_pesquisar<b>&ignorecache=True</b>
    </br>
    </br><b>Termo de não pode ser pesquisa vazio<b></br>
    </br><b>A lista precisa conter urls válidas<b></br>
    '''

#Recebe os orgumentos e 
@app.route('/findword')
def findword():
    #Verifica se os perâmetros foram enviados
    if (request.args.get('urls', default = [], type = str) and request.args.get('termo', default = "error", type = str) ):
    #Pega a string com as urls e trata para se tornar uma lista de urls
        array = request.args.get('urls', default = [], type = str)
    #Tratamento contra erros básicos
        array = array.replace("[", "")
        array = array.replace("]", "")
        array = array.replace("'", "")
        array = array.replace('"', "")
        array = array.split(",")
        #verifica se contém . na url e se contem o protocolo http ou https
        for i in range(len(array)):
            #se não tiver ponto dá erro
            if not (array[i].find('.')>-1):
                return root()
            #se não contém adiciona ao começo da string
            if not (array[i].find('http')>-1):
                array[i] = 'http://'+(array[i].strip())

    #Atribui o termo
        word = request.args.get('termo', default = "", type = str)
    #verifica se não é vazio
        if (not word.strip() ):
            return root()
    #verifica e atribui o parâmetro opcional ignorecache
        ignorecache = request.args.get('ignorecache', default = 'False', type = str)
        if (ignorecache == 'False' or ignorecache == 'false' or ignorecache == '0' or ignorecache == ''):
            return jsonify(Crawler.spider(array, word , len(array) , False))
        #Qualquer caso que não seja parametro inexistente ou igual a false passa True
        return jsonify(Crawler.spider(array, word , len(array) , True))
    #Caso os parametros não sejam passados retorna a página com referencia de parametros
    return root()