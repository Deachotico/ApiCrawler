# content of test_sample.py
import pytest
import Crawler

def test_input():
    Crawler.spider(['https://canaltech.com.br/', 'https://jovemnerd.com.br/'], 'google', 2)
    

def teste_input_errors():
    with pytest.raises(IndexError):
        #parametros digitados sem forma de array
        Crawler.spider(('https://canaltech.com.br/', 'https://jovemnerd.com.br/'), 'google', 2)
    with pytest.raises(AttributeError):
        #Urls incompletas
        Crawler.spider(['https://canaltech.com.br/', 'jovemnerd.com.br/'], 'google', 2)
        #Parametros que não representam urls
        Crawler.spider(('https://canaltech.com.br/, https://jovemnerd.com.br/'), 'google', 2)
        #Página completamente em flash não há como fazer busca
        Crawler.spider(('https://mono-1.com/monoface/main.html'), 'google', 2)
        #termo de pesquisa vazio é inválido
        Crawler.spider(['https://canaltech.com.br/', 'https://jovemnerd.com.br/'], '  ', 2)