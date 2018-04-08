import asyncio
from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
from re import sub
import os
import asyncio
import aiohttp
import random


async def controlespider(url, word, ignorecache): #Consumer + Producer  
    #Testa se o termo de pesquisa não é vazio
    if (not word.strip()):
        print("Termo de pesquisa vazio")
        raise AttributeError
    
    #inicia e controla o loop
    parser = LinkParser()
    
    loop = asyncio._get_running_loop()
    ToProcessUrlQueue = asyncio.Queue(loop=loop) #Fila de urls a serem baixadas pela getlinks
    ToConsumeDataQueue =  asyncio.Queue(loop=loop) #HTML em string baixado pela getlinks PARA PROCESSAMENTO DA ConsumeHtml
    ToConsumeUrlQueue =  asyncio.Queue(loop=loop) #URL do html baixado pela getlinks PARA PROCESSAMENTO DA ConsumeHtml
    ToStoreDataQueue =  asyncio.Queue(loop=loop) #HTML em string baixado pela getlinks PARA PROCESSAMENTO DA storecache
    ToStoreUrlQueue =  asyncio.Queue(loop=loop) #URL do html baixado pela getlinks PARA PROCESSAMENTO DA storecache
    FinalQueue = asyncio.Queue(loop=loop)
    
    await spider(url, ignorecache, ToProcessUrlQueue)
    await parser.getLinks(ToProcessUrlQueue, ToConsumeDataQueue, ToConsumeUrlQueue, ToStoreDataQueue, ToStoreUrlQueue)
    await ConsumeHtml (word, ToConsumeDataQueue, ToConsumeUrlQueue, FinalQueue)
    await storeCache(ToStoreDataQueue, ToStoreUrlQueue)
    
    var = await createreturn(FinalQueue)
    return var

async def createreturn(FinalQueue):
    #global Jsonreturn
    Jsonreturn = {}
    while True:
        item = await FinalQueue.get()
        if item is None:
            return Jsonreturn
        times = await FinalQueue.get()
        Jsonreturn[item] = times


# Crawler que recebe as urls a pesquisar, o termo a ser pesquisado e a quantidade de urls enviadas pela api.
async def spider(url, ignorecache, ToProcessUrlQueue): #Insere none ao final de todas as filas
    pagesToVisit = url  #Lista de urls
    # Laço principal.
    # Valida se ainda restam urls a visitar
    global lengthpagesToVisit
    lengthpagesToVisit = len(pagesToVisit)
    for url in pagesToVisit:
        #apaga o cache se solicitado
        if ignorecache:
        #Caminho da pasta de cache e alteração da url
            pathcachefolder = os.getcwd()+"/cache"
        #Formata a url pra poder ser usada como nome do arquivo de cache
            localurl = url.replace('/', '-')
            localurl = localurl.replace('?', '')
            localurl = localurl.replace('"', '')
            localurl = localurl.replace('*', '')
            localurl = localurl.replace(':', '')
            localurl = localurl.replace('<', '')
            localurl = localurl.replace('>', '')
            localurl = localurl.replace('|', '')
        #Se o arquivo de cache não existir
            if os.path.exists(pathcachefolder+"/"+localurl+'.html'):
                os.remove(pathcachefolder+"/"+localurl+'.html')
        try:
            print("Procurando em:", url, "Restam ", len(pagesToVisit)+1," páginas.")
        # getLinks retorna o html da página
            await ToProcessUrlQueue.put(url)
        except:
            print(" ERRO: verifique a url: ", url, " Deve estar no formato http://site.com")
    await ToProcessUrlQueue.put(None)

class LinkParser(HTMLParser): #Producer
    # retorna o html das páginas
    async def getLinks(self, ToProcessUrlQueue, ToConsumeDataQueue, ToConsumeUrlQueue, ToStoreDataQueue, ToStoreUrlQueue): #producer 
        endflag = 0
        while True:
            url = await ToProcessUrlQueue.get()
            url = str(url) #Caso erro de tipo
            if url is None or url == "None":
                break
            #Formata a url pra poder ser usada como nome do arquivo de cache
            localurl = url.replace('/', '-')
            localurl = localurl.replace('?', '')
            localurl = localurl.replace('"', '')
            localurl = localurl.replace('*', '')
            localurl = localurl.replace(':', '')
            localurl = localurl.replace('<', '')
            localurl = localurl.replace('>', '')
            localurl = localurl.replace('|', '')
            pathcachefolder = os.getcwd()+"/cache"
            
            #Caso o arquivo de cache não exista, busca o html na url
            if not os.path.isfile(pathcachefolder+'/'+localurl+'.html'):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        htmlString = await response.text()
                #Queues do consumehtml
                await ToConsumeDataQueue.put(htmlString)
                await ToConsumeUrlQueue.put(url)
                #queues do storecache
                await ToStoreDataQueue.put(htmlString)
                await ToStoreUrlQueue.put(url)
            else:
                cachelocal = open(pathcachefolder+'/'+localurl+'.html', 'r', encoding="utf-8")
                await ToConsumeDataQueue.put(cachelocal.read())
                await ToConsumeUrlQueue.put(url)
                #queues do storecache
                await ToStoreDataQueue.put(cachelocal.read())
                await ToStoreUrlQueue.put(url)
            endflag += 1
            if lengthpagesToVisit == endflag:
                print ("HUe")
            #Última operação sinaliza o fim de todas as filas
                await ToConsumeDataQueue.put(None)
                await ToConsumeUrlQueue.put(None)
                await ToStoreDataQueue.put(None)
                await ToStoreUrlQueue.put(None)
                break


async def fetch(session, url):
    async with session.get(url) as response:
         await response.text()

async def storeCache(ToStoreDataQueue, ToStoreUrlQueue): #producer sem retorno #DataQueue e UrlQueue
    while True:
        data = await ToStoreDataQueue.get()
        data = str(data) #Caso erro de tipo   
        url = await ToStoreUrlQueue.get()
        url = str(url) #Caso erro de tipo 
        if url is None or url == "None":
            break
        #Formata a url pra poder ser usada como nome do arquivo de cache
        localurl = url.replace('/', '-')
        localurl = localurl.replace('?', '')
        localurl = localurl.replace('"', '')
        localurl = localurl.replace('*', '')
        localurl = localurl.replace(':', '')
        localurl = localurl.replace('<', '')
        localurl = localurl.replace('>', '')
        localurl = localurl.replace('|', '')
        pathcachefolder = os.getcwd()+"/cache"
        
        #Cria a pasta de cache se não existir
        if not os.path.exists(pathcachefolder):
            os.makedirs(pathcachefolder)  #possível await  
        # Verifica se o cache existe
        if not os.path.isfile(pathcachefolder+'/'+localurl+'.html'):
            #Tenta criar e escrevcer o arquivo de cache
            try:
                cachepath = pathcachefolder+"/"+localurl+'.html'
                cachefile = open(cachepath,"w", encoding="utf8")
                cachefile.write(data)
                cachefile.close()
            #Em caso de erro deleta o arquivo criado
            except:
                cachefile.close()
                print("Não foi possível armazenar o cache")
                if os.path.exists(pathcachefolder+"/"+localurl+'.html'):
                    os.remove(pathcachefolder+"/"+localurl+'.html')

async def ConsumeHtml (word, ToConsumeDataQueue, ToConsumeUrlQueue, FinalQueue):
    while True:
        data = await ToConsumeDataQueue.get()
        data = str(data) #Caso erro de tipo   
        url = await ToConsumeUrlQueue.get()
        url = str(url) #Caso erro de tipo 
        if url is None or url == "None":
            break
        foundWord = False   #Boolean para teste de o termo existe na página
    # cria o arquivo de cache
        try:
            #Remove as tags do html e deixa só o conteúdo em texto
            data = sub('<.*?>', ' ', data)
            #Confirma se o termo está na página
            if data.find(word)>-1:
                foundWord = True
                #Conta as ocorrências e adiciona na lista de ocorrências
                print ("página: " + url)
                print("Termo encontrado: ",data.count(word) , " vezes")
                await FinalQueue.put(url)
                await FinalQueue.put(data.count(word))
            else:
                print("Termo não encontrado")
        except:
            print(" ERRO: verifique a url: ", url, " Deve estar no formato http://site.com")
    await FinalQueue.put(None)