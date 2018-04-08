# coding: utf-8
from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
from re import sub
import os
import asyncio
import aiohttp
import random
import time
start_time = time.time()


class LinkParser(HTMLParser): #Producer
    # retorna o html das páginas
    #async def getLinks(self, ToProcessUrlQueue, ToConsumeDataQueue, ToConsumeUrlQueue, ToStoreDataQueue, ToStoreUrlQueue): #producer 
    async def getLinks(self, ToProcessUrlQueue, ToConsumeDataQueue, ToConsumeUrlQueue, ToStoreDataQueue, ToStoreUrlQueue, ToRemoveCacheUrlQueue): #producer 
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
            #     response = urlopen(url) #Preciso de um await nesta operação
            #     htmlBytes = response.read()
            # #Transforma os bytes da página em texto
            #     htmlString = htmlBytes.decode("utf-8")
            #return htmlString #DataQueue put
                async with aiohttp.ClientSession() as session:
                    htmlString = await fetch(session, url)
                #Queues do consumehtml
                await ToConsumeDataQueue.put(htmlString)
                await ToConsumeUrlQueue.put(url)
                #queues do storecache
                await ToStoreDataQueue.put(htmlString)
                await ToStoreUrlQueue.put(url)
            else:
                cachelocal = open(pathcachefolder+'/'+localurl+'.html', 'r')
                #return cachelocal.read() #DataQueue put
                await ToConsumeDataQueue.put(cachelocal)
                await ToConsumeUrlQueue.put(url)
                #queues do storecache
                await ToStoreDataQueue.put(cachelocal)
                await ToStoreUrlQueue.put(url)
            endflag += 1
            #print (endflag)
            if lengthpagesToVisit == endflag:
                print ("HUe")
            #Última operação sinaliza o fim de todas as filas
                await ToProcessUrlQueue.put(None)
                await ToConsumeDataQueue.put(None)
                await ToConsumeUrlQueue.put(None)
                await ToStoreDataQueue.put(None)
                await ToStoreUrlQueue.put(None)
                await ToRemoveCacheUrlQueue.put(None)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def storeCache(ToStoreDataQueue, ToStoreUrlQueue, ToRemoveCacheUrlQueue): #producer sem retorno #DataQueue e UrlQueue
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
                cachefile = open(cachepath,"w")
                cachefile.write(data)
                cachefile.close()
            #Em caso de erro deleta o arquivo criado
            except:
                cachefile.close()
                #removeCache(url) # put Toremovecachequeue
                print("Não foi possível armazenar o cache")
                await ToRemoveCacheUrlQueue.put(url)

async def removeCache(ToRemoveCacheUrlQueue): #Síncrona UrlQueue
    while True:
        url = await ToRemoveCacheUrlQueue.get()
        url = str(url) #Caso erro de tipo 
        if url is None or url == "None":
            break    
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

# Crawler que recebe as urls a pesquisar, o termo a ser pesquisado e a quantidade de urls enviadas pela api.
#async def spider(url, ignorecache, ToProcessUrlQueue, ToRemoveCacheUrlQueue, ToConsumeDataQueue, ToConsumeUrlQueue, ToStoreDataQueue, ToStoreUrlQueue): #Insere none ao final de todas as filas
async def spider(url, ignorecache, ToProcessUrlQueue, ToRemoveCacheUrlQueue): #Insere none ao final de todas as filas
    pagesToVisit = url  #Lista de urls
    #JsonReturn = {}     #Objeto com todas as urls e ocorrências retornado #Dicionario principal
    # Laço principal.
    # Valida se ainda restam urls a visitar
    global lengthpagesToVisit
    lengthpagesToVisit = len(pagesToVisit)
    while pagesToVisit != []:
        #retira a primeira url da coleção
        url = pagesToVisit[0]
        pagesToVisit = pagesToVisit[1:]
        #apaga o cache se solicitado
        if ignorecache:
            #removeCache(url) #Put Toremovecacheurlqueue
            await ToRemoveCacheUrlQueue.put(url)
            await asyncio.sleep(random.random()) #Random pra desalocar o processador
        try:
            print("Procurando em:", url, "Restam ", len(pagesToVisit)+1," páginas.")
            #parser = LinkParser()
        # getLinks retorna o html da página
            #Enviado lá na inicialização do loop
            #data = parser.getLinks(url)   #put ToProcessUrlQueue
            await ToProcessUrlQueue.put(url)
            await asyncio.sleep(random.random()) #Random pra desalocar o processador
            #ConsumeHtml (word, data, url) #não existe no produto assíncrono
        except:
            print(" ERRO: verifique a url: ", url, " Deve estar no formato http://site.com")
            #pass  


async def ConsumeHtml (word, ToConsumeDataQueue, ToConsumeUrlQueue):
    while True:
        data = await ToConsumeDataQueue.get()
        data = str(data) #Caso erro de tipo   
        url = await ToConsumeUrlQueue.get()
        url = str(url) #Caso erro de tipo 
        if url is None or url == "None":
            break
        foundWord = False   #Boolean para teste de o termo existe na página
        urlscalled = []     #Lista de urls em que o termo existe
        timesfound = []     #Lista com a quantidade de ocorrencias dos termos
    # cria o arquivo de cache
        try:
            #storeCache(data, url) #Não precisa existir
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
            pass
        print (urlscalled)
    #problema - tirar dados do async
    #Solução - queue pra colocar todos os dados, função que remove todos da fila e formata
        #monta o objeto retornado a api
        # for i in range(len(urlscalled)):
        #     JsonReturn[urlscalled[i]] = timesfound[i]
        # if urlscalled:
        #     #Retorna como string já que o Flasker não aceita receber json ou dict
        #     return  (str(JsonReturn))
        # else:
        #     #retorna um objeto vazio se o termo não for encontrado
        #     return  ({})


def controlespider(url, word, ignorecache): #Consumer + Producer  
    #Testa se o termo de pesquisa não é vazio
    if (not word.strip() ):
        print("Termo de pesquisa vazio")
        raise AttributeError

    #inicia e controla o loop
    parser = LinkParser()
    
    loop = asyncio.get_event_loop() #descenessário com a api Quart
    queue = asyncio.Queue(loop=loop)

    ToProcessUrlQueue = asyncio.Queue(loop=loop) #Fila de urls a serem baixadas pela getlinks
    ToConsumeDataQueue =  asyncio.Queue(loop=loop) #HTML em string baixado pela getlinks PARA PROCESSAMENTO DA ConsumeHtml
    ToConsumeUrlQueue =  asyncio.Queue(loop=loop) #URL do html baixado pela getlinks PARA PROCESSAMENTO DA ConsumeHtml
    ToStoreDataQueue =  asyncio.Queue(loop=loop) #HTML em string baixado pela getlinks PARA PROCESSAMENTO DA storecache
    ToStoreUrlQueue =  asyncio.Queue(loop=loop) #URL do html baixado pela getlinks PARA PROCESSAMENTO DA storecache
    ToRemoveCacheUrlQueue = asyncio.Queue(loop=loop) #URL do arquivo a remover do disco em caso de erro no armazenamento
    
    Spider_coro = spider(url, ignorecache, ToProcessUrlQueue, ToRemoveCacheUrlQueue) #Insere na fila de urls a serem baixadas
    #Spider_coro = spider(url, ignorecache, ToProcessUrlQueue, ToRemoveCacheUrlQueue, ToConsumeDataQueue, ToConsumeUrlQueue, ToStoreDataQueue, ToStoreUrlQueue) #Teste
    #GetLinks_coro = parser.getLinks(ToProcessUrlQueue, ToConsumeDataQueue, ToConsumeUrlQueue, ToStoreDataQueue, ToStoreUrlQueue) #Baixa o html e insere para processamento do conteúdo e armazenamento de cache
    GetLinks_coro = parser.getLinks(ToProcessUrlQueue, ToConsumeDataQueue, ToConsumeUrlQueue, ToStoreDataQueue, ToStoreUrlQueue, ToRemoveCacheUrlQueue)
    StoreCache_coro = storeCache(ToStoreDataQueue, ToStoreUrlQueue, ToRemoveCacheUrlQueue) #Processa o armazenamento do cache
    RemoveCache_coro = removeCache(ToRemoveCacheUrlQueue) #Remove do disco os arquivos de cache necessários
    ConsumeHtml_coro = ConsumeHtml (word, ToConsumeDataQueue, ToConsumeUrlQueue)

    loop.run_until_complete(asyncio.gather(Spider_coro, GetLinks_coro, StoreCache_coro, RemoveCache_coro, ConsumeHtml_coro)) #Testes
    #asyncio.gather(producer_coro, consumer_coro) #api Quart

    #Aguarda o fim de todos os processos
    asyncio.wait(Spider_coro)
    asyncio.wait(GetLinks_coro)
    asyncio.wait(StoreCache_coro)
    asyncio.wait(RemoveCache_coro)
    asyncio.wait(ConsumeHtml_coro)
    
    print("\n\n\n\n\n\n\n\n\n\n\n")
    print("TEMPO API ASYNC")
    print("--- %s seconds ---" % (time.time() - start_time))
    

controlespider(['https://jovemnerd.com.br' ,'https://techcrunch.com/', 'https://canaltech.com.br/ultimas/p2/', 'http://globoesporte.globo.com/', 'https://www.youtube.com/'], 'video', True)
#controlespider(['https://jovemnerd.com.br', 'https://www.youtube.com/'], 'video', True)