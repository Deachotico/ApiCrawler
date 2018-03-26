# coding: utf-8
from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
from re import sub
#from shutil import rmtree
import os

class LinkParser(HTMLParser):
    # retorna o html das páginas
    def getLinks(self, url):
        #Caso o arquivo de cache não exista
        localurl = url.replace('/', '\\')
        pathcachefolder = os.getcwd()+"/cache"
        if not os.path.isfile(pathcachefolder+'/'+localurl+'.html'):
            response = urlopen(url)
            htmlBytes = response.read()
        #Transforma os bytes da página em texto
            htmlString = htmlBytes.decode("utf-8")
            return htmlString
        cachelocal = open(pathcachefolder+'/'+localurl+'.html', 'r')
        return cachelocal.read()
        

def storeCache(data, url):
    localurl = url.replace('/', '\\')
    pathcachefolder = os.getcwd()+"/cache"
    if not os.path.exists(pathcachefolder):
        os.makedirs(pathcachefolder)       
    if not os.path.isfile(pathcachefolder+'/'+localurl+'.html'):
        cachepath = pathcachefolder+"/"+localurl+'.html'
        cachefile = open(cachepath,'w')
        cachefile.write(data)
        cachefile.close()

def removeCache(url):
#Caminho da pasta de cache e alteração da url
    pathcachefolder = os.getcwd()+"/cache"
    localurl = url.replace('/', '\\')
#Se o arquivo de cache não existir
    if not os.path.exists(pathcachefolder+"/"+localurl+'.html'):
        return
    os.remove(pathcachefolder+"/"+localurl+'.html')
    return



# Crawler que recebe as urls a pesquisar, o termo a ser pesquisado e a quantidade de urls enviadas pela api.
def spider(url, word, maxPages, ignorecache):  
    pagesToVisit = url  #Lista de urls
    foundWord = False   #Boolean para teste de o termo existe na página
    urlscalled = []     #Lista de urls em que o termo existe
    timesfound = []     #Lista com a quantidade de ocorrencias dos termos
    JsonReturn = {}     #Objeto com todas as urls e ocorrências retornado

        #Testa se o termo de pesquisa não é vazio
    if (not word.strip() ):
        print("Termo de pesquisa vazio")
        raise AttributeError

    # Laço principal.
    # Valida se ainda restam urls a visitar
    while pagesToVisit != []:
        #Começa da primeira url da coleção
        url = pagesToVisit[0]
        pagesToVisit = pagesToVisit[1:]
        #apaga o cache se solicitado
        if ignorecache:
            removeCache(url)
        try:
            print("Procurando em:", url, "Restam: ", len(pagesToVisit)+1," páginas.")
            parser = LinkParser()
        # getLinks retorna o html da página
            data = parser.getLinks(url)
        # cria o arquivo de cache
            storeCache(data, url)
        #Remove as tags do html e deixa só o conteúdo em texto
            data = sub('<.*?>', ' ', data)
        #Confirma se o termo está na página
            if data.find(word)>-1:
                foundWord = True
            #Adiciona a url a lista de urls em que o termo foi encontrado
                urlscalled.append(url)
            #Conta as ocorrências e adiciona na lista de ocorrências
                timesfound.append(data.count(word))
                print("Termo encontrado: ",data.count(word) , " vezes")
            else:
                print("Termo não encontrado")
        except:
            print(" ERRO: verifique a url: ", url, " Deve estar no formato http://site.com")
            raise AttributeError

    #monta o objeto retornado a api
    for i in range(len(urlscalled)):
        JsonReturn[urlscalled[i]] = timesfound[i]
    if urlscalled:
        #Retorna como string já que o Flasker não aceita receber json ou dict
        return  (str(JsonReturn))
    else:
        #retorna um objeto vazio se o termo não for encontrado
        return  ({})

#spider(['https://www.jovemnerd.com.br', 'https://canaltech.com.br/ultimas/p2/'], 'nerd', 2, False)