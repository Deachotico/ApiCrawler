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
    O formato correto de chamada eh: http://127.0.0.1:5000/findword?urls=[url1,url2]&termo=termo_a_pesquisar"
    '''

#Recebe os orgumentos e 
@app.route('/findword')
def findword():
    #Verifica se os perâmetros foram enviados
    if (request.args.get('urls', default = [], type = str) and request.args.get('termo', default = "error", type = str) ):
    #Pega a string com as urls e trata para se tornar uma lista de urls
        array = request.args.get('urls', default = [], type = str)
        array = array.replace("[", "")
        array = array.replace("]", "")
        array = array.split(",")
    #Atribui o termo
        word = request.args.get('termo', default = "error", type = str)
    #Converte a resposta para json e entrega
        return jsonify(Crawler.spider(array, word , len(array)))
    #Caso os parametros não sejam passados retorna a página com referencia de parametros
    return root()
    