import asyncio
from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
from re import sub
import os
import asyncio
import aiohttp

async def controlespider(url, word, ignorecache): #Consumer + Producer  
    #Testa se o termo de pesquisa não é vazio
    if (not word.strip()):
        print("Termo de pesquisa vazio")
        raise AttributeError
    
    #inicia e controla o loop
    parser = LinkParser()
    
    #Filas utilizadas pra transitar os dados
    loop = asyncio._get_running_loop()
    ToProcessUrlQueue = asyncio.Queue(loop=loop) #Fila de urls a serem baixadas pela getlinks
    ToConsumeDataQueue =  asyncio.Queue(loop=loop) #HTML em string baixado pela getlinks PARA PROCESSAMENTO DA ConsumeHtml
    ToConsumeUrlQueue =  asyncio.Queue(loop=loop) #URL do html baixado pela getlinks PARA PROCESSAMENTO DA ConsumeHtml
    ToStoreDataQueue =  asyncio.Queue(loop=loop) #HTML em string baixado pela getlinks PARA PROCESSAMENTO DA storecache
    ToStoreUrlQueue =  asyncio.Queue(loop=loop) #URL do html baixado pela getlinks PARA PROCESSAMENTO DA storecache
    FinalQueue = asyncio.Queue(loop=loop)
    
    #inicia e aguarda os processos necessários
    await spider(url, ignorecache, ToProcessUrlQueue)
    await parser.getLinks(ToProcessUrlQueue, ToConsumeDataQueue, ToConsumeUrlQueue, ToStoreDataQueue, ToStoreUrlQueue)
    await ConsumeHtml (word, ToConsumeDataQueue, ToConsumeUrlQueue, FinalQueue)
    await storeCache(ToStoreDataQueue, ToStoreUrlQueue)
    var = await createreturn(FinalQueue)
    return var

#Cria o objeto final a ser retornado
async def createreturn(FinalQueue):
    Jsonreturn = {}
    while True:
        item = await FinalQueue.get()
        #se encontrar o fim da fila retorna o objeto
        if item is None:
            return Jsonreturn
        times = await FinalQueue.get()
        Jsonreturn[item] = times


# Crawler que recebe as urls a pesquisar, deleta o cache se necessário e insere as urls para processamento
async def spider(url, ignorecache, ToProcessUrlQueue):
    pagesToVisit = url  #Lista de urls
    
    #Indica a quantidade inicial de urls para o controle do fim das filas
    global lengthpagesToVisit
    lengthpagesToVisit = len(pagesToVisit)
    # Laço principal.
    
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
        #Deleta o arquivo de cache
            if os.path.exists(pathcachefolder+"/"+localurl+'.html'):
                os.remove(pathcachefolder+"/"+localurl+'.html')
        try:
            # Insere as urls na fila de processamento
            await ToProcessUrlQueue.put(url)
        except:
            print(" ERRO: verifique a url: ", url, " Deve estar no formato http://site.com")
    #Insere None ao final da fila
    await ToProcessUrlQueue.put(None)

class LinkParser(HTMLParser): #Producer
    # retorna o html das páginas e indica o fim das filas
    async def getLinks(self, ToProcessUrlQueue, ToConsumeDataQueue, ToConsumeUrlQueue, ToStoreDataQueue, ToStoreUrlQueue): #producer 
        #Contador de controle para inserir None ao fim das filas
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
                #Busca o HTML do site usando aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        htmlString = await response.text()
                #insere nas filas da consumehtml
                await ToConsumeDataQueue.put(htmlString)
                await ToConsumeUrlQueue.put(url)
                #insere nas filas da storecache
                await ToStoreDataQueue.put(htmlString)
                await ToStoreUrlQueue.put(url)
            else:
                #Se existir o cache local busca no disco
                cachelocal = open(pathcachefolder+'/'+localurl+'.html', 'r', encoding="utf-8")
                #insere nas filas da consumehtml
                await ToConsumeDataQueue.put(cachelocal.read())
                await ToConsumeUrlQueue.put(url)
                #insere nas filas da storecache
                await ToStoreDataQueue.put(cachelocal.read())
                await ToStoreUrlQueue.put(url)
            endflag += 1
            if lengthpagesToVisit == endflag:
            #Quando o contador indica que não há mais urls a serem processadas, sinaliza o fim de todas as filas
                await ToConsumeDataQueue.put(None)
                await ToConsumeUrlQueue.put(None)
                await ToStoreDataQueue.put(None)
                await ToStoreUrlQueue.put(None)
                break


async def storeCache(ToStoreDataQueue, ToStoreUrlQueue): #Guarda o cache em disco
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

#Busca o termo no html e se for encontrado insere na fila final
async def ConsumeHtml (word, ToConsumeDataQueue, ToConsumeUrlQueue, FinalQueue):
    while True:
        data = await ToConsumeDataQueue.get()
        data = str(data) #Caso erro de tipo   
        url = await ToConsumeUrlQueue.get()
        url = str(url) #Caso erro de tipo 
        if url is None or url == "None":
            break
        foundWord = False   #Boolean para teste de o termo existe na página
        try:
            #Regex que Remove as tags do html e deixa só o conteúdo em texto
            data = sub('<.*?>', ' ', data)
            #Confirma se o termo está na página
            if data.find(word)>-1:
                foundWord = True
                #Conta as ocorrências e adiciona na fila de ocorrências
                print ("página: " + url)
                print("Termo encontrado: ",data.count(word) , " vezes")
                await FinalQueue.put(url)
                await FinalQueue.put(data.count(word))
            else:
                print("Termo não encontrado em: "+url)
        except:
            print(" ERRO: verifique a url: ", url, " Deve estar no formato http://site.com")
    #Indica o fim da fila com as ocorrências do termo
    await FinalQueue.put(None)