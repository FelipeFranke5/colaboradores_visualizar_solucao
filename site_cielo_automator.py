"""Módulo de automação para visualizar a solução de EC's no Site Cielo."""

import json
import time

from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By

import listagem
from validacoes import (ArquivoEnvFaltando, FalhaCarregamento,
                        SiteCieloValidator)


def carregar_driver():
    """Retorna o driver do Selenium com a página de Login."""
    # 1
    arquivo_url = dotenv_values('.env')
    url_login = arquivo_url.get('URL_LOGIN')

    if not url_login:
        raise ArquivoEnvFaltando('URL login esta faltando.')

    driver = webdriver.Edge()
    driver.get(url_login)

    if not 'Login' in driver.title:
        raise FalhaCarregamento('Erro ao carregar a página.')
    return driver


def botao_outros_acessos(driver: webdriver.Edge):
    """Acessa e clica no botão de 'Outros Acessos', para colaboradores."""
    # 2
    outros_acessos = driver.find_element(By.ID, 'bt-other-access')
    outros_acessos.click()
    time.sleep(1)


def enviar_credenciais(driver: webdriver.Edge):
    """Preenche o Usuário e Senha."""
    # 3
    usuario = driver.find_element(By.XPATH, '//input[@name="username"]')
    senha = driver.find_element(By.XPATH, '//input[@name="password"]')

    usuario.clear()
    senha.clear()
    arquivo = dotenv_values('.env')

    usuario.send_keys(arquivo.get('USUARIO_SITE'))
    senha.send_keys(arquivo.get('SENHA_SITE'))
    time.sleep(1)


def fazer_login(driver: webdriver.Edge):
    """Executa a autenticação."""
    # 4
    entrar = driver.find_element(By.ID, 'bt-enter')
    entrar.click()
    time.sleep(5)

    if not 'Cielo - Bem-vindo' in driver.title:
        raise ValueError('Dados de entrada inválidos.')


def olhar_solucao(driver: webdriver.Edge):
    """Salva o resultado das buscas em um arquivo JSON."""
    # 5
    lista_ecs = listagem.carregar_cadastros()
    resultados: dict[str, str] = {}
    url_arquivo = dotenv_values('.env')
    url = url_arquivo.get('URL_MAIN')
    validador = SiteCieloValidator(driver)

    if not url:
        raise ArquivoEnvFaltando('URL Main não informada.')

    if not lista_ecs:
        raise ValueError('Listagem de ECs esta vazia.')

    for ec in lista_ecs:
        resultado = validador.pesquisar_ec(ec)
        resultados[ec] = resultado
        driver.get(url)
        time.sleep(3)

        if validador.mensagem_cookies_existe():
            validador.acao_mensagem_cookies()

        if validador.mensagem_urgente_existe():
            validador.acao_mensagem_urgente()

        validador.trocar_ec()

    objeto = json.dumps(resultados, indent=4)
    with open('resultado.json', 'w', encoding='utf-8') as arq:
        arq.write(objeto)


def main():
    """Script que inicializa o programa."""
    # 0
    print('--------------------------------------------')
    print('\n.. Iniciando Automator ..')
    print('\n--------------------------------------------')

    driver = carregar_driver()
    botao_outros_acessos(driver)
    enviar_credenciais(driver)
    fazer_login(driver)
    olhar_solucao(driver)
    driver.close()

    print('--------------------------------------------')
    print('\n.. Fim da execução ..')
    print('\n--------------------------------------------')


if __name__ == '__main__':
    main()
