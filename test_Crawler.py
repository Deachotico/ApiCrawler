# content of test_sample.py
import pytest
import Crawler

def test_input():
    Crawler.spider(['https://canaltech.com.br/', 'https://jovemnerd.com.br/'], 'google', 2, False)
    

def teste_input_errors():
    with pytest.raises(IndexError):
        #parametros digitados sem forma de array
        Crawler.spider(('https://canaltech.com.br/', 'https://jovemnerd.com.br/'), 'google', 2, False)
        #Urls incompletas
        Crawler.spider(['https://canaltech.com.br/', 'jovemnerd.com.br/'], 'google', 2, False)
        #Parametros que não representam urls
        Crawler.spider(('https://canaltech.com.br/, https://jovemnerd.com.br/'), 'google', 2, False)
        #Página completamente em flash não há como fazer busca
        Crawler.spider(('https://mono-1.com/monoface/main.html'), 'google', 2, False)
        #termo de pesquisa vazio é inválido
        Crawler.spider(['https://canaltech.com.br/', 'https://jovemnerd.com.br/'], '  ', 2, False)
