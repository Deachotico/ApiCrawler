# ApiCrawler

Api que recebe uma lista de URLS e um termo a ser pesquisado seguindo o formato:

`http://127.0.0.1:5000/findword?array=[url1,url2]&word=termo_a_pesquisar`

Api utiliza Flask como base, e Pytest para os testes.

## Deploy
Instalação do Pip para python 3

`sudo apt-get install python3-pip`

Instalação do flask para python 3

`pip3 install flask`

Exportar e rodar a aplicação

`export FLASK_APP=Api.py`

`flask run`

Basta usar a url passando os parâmetros

`http://127.0.0.1:5000/findword?urls=[url1,url2]&termo=termo_a_pesquisar`

## Parâmetros
### Obrigatórios
* urls: É a lista de urls que serão utilizadas para busca do termo
* termo: É o termo que vai ser pesquisado nos sites enviados
### Opcional
* ignorecache: Define se o cache em disco será utilizado (False) ou ignorado e os dados baixados novamente (True)

### Exemplo com todos os parâmetros
`http://127.0.0.1:5000/findword?urls=['https://www.jovemnerd.com.br', 'canaltech.com.br']&termo=nerd<b>&ignorecache=True`

## Testes
Instalação Pytest

`pip3 install -U pytest`

Rodar o comando pytest na pasta

`pytest`


