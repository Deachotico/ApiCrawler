# coding: utf-8
#!/usr/bin/python3
from quart import Quart
from quart import jsonify
from quart import request
import AsyncCrawler
import asyncio
app = Quart(__name__)

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

#Recebe os orgumentos
@app.route('/findword')
async def findword():
    #Verifica se os perâmetros foram enviados
    if (request.args.get('urls', default = []) and request.args.get('termo', default = "error") ):
    #Pega a string com as urls e trata para se tornar uma lista de urls
        array = request.args.get('urls', default = [])
    #Tratamento contra erros básicos
        array = array.replace("[", "")
        array = array.replace("]", "")
        array = array.replace("'", "")
        array = array.replace('"', "")
        array = array.replace(" ", "")
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
        word = request.args.get('termo', default = "")
    #verifica se não é vazio
        if (not word.strip() ):
            return root()
    #verifica e atribui o parâmetro opcional ignorecache
        ignorecache = request.args.get('ignorecache', default = 'False')
        if (ignorecache == 'False' or ignorecache == 'false' or ignorecache == '0' or ignorecache == ''):
            return jsonify (await AsyncCrawler.controlespider(array, word , False))
        #Qualquer caso que não seja parametro inexistente ou igual a false envia True
        return jsonify (await AsyncCrawler.controlespider(array, word , True))
app.run()    