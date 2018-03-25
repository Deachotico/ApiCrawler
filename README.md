# ApiCrawler

Api que recebe uma lista de URLS e um termo a ser pesquisado seguindo o formato:
  http://127.0.0.1:5000/findword?array=[url1,url2]&word=termo_a_pesquisar

Api utiliza Flask como base, e Pytest para os testes.

# Deploy
Instalação do Pip para python 3
  sudo apt-get install python3-pip

Instalação do flask para python 3
  pip3 install flask

Exportar e rodar a aplicação
  export FLASK_APP=Api.py
  flask run

Basta usar a url passando os parâmetros
  http://127.0.0.1:5000/findword?array=[url1,url2]&word=termo_a_pesquisar

# Testes
Instalação Pytest
  pip3 install -U pytest

Rodar o comando pytest na pasta
  pytest


