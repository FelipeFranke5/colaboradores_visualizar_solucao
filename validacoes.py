"""Módulo que executa as validações durante a navegação do site."""

import time

from dotenv import dotenv_values
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class ArquivoEnvFaltando(Exception):
    """Informações insuficientes no arquivo '.env'."""


class FalhaCarregamento(Exception):
    """Falha no carregamento da página."""


class SiteCieloValidator:
    """Responsável pelas validações que são feitas enquanto o driver do Selenium navega pelo site."""

    def __init__(self, driver: webdriver.Edge):
        """Inicializa a classe com o driver do Selenium."""
        self.driver = driver

    def mensagem_erro_existe(self):
        """Retorna se o EC foi encontrado após a busca."""
        try:
            self.driver.find_element(By.XPATH, '//div[@class="list-item"]/div[1]')
            return False
        except NoSuchElementException:
            return True

    def header_checkout_existe(self):
        """Retorna se o EC possui Backoffice de Checkout."""
        try:
            self.driver.find_element(By.XPATH, '//div[@ng-class="css.checkoutHeader"]')
            return True
        except NoSuchElementException:
            return False

    def mensagem_cookies_existe(self):
        """Retorna se a mensagem de aceitação de cookies foi apresentada."""
        try:
            self.driver.find_element(By.XPATH, '//div[@class="cookiesAlert__13e5"]')
            return True
        except NoSuchElementException:
            return False

    def acao_mensagem_cookies(self):
        """Clica no botão de aceite."""
        botao_ok = self.driver.find_element(By.XPATH, '//div[@class="buttonWrap__2R5y"]')
        botao_ok.click()
        time.sleep(1)

    def mensagem_urgente_existe(self):
        """Retorna se o Modal de Mensagem Urgente foi apresentado."""
        try:
            self.driver.find_element(By.XPATH, '//h2[@class="ng-binding title__2GAN"]')
            return True
        except NoSuchElementException:
            return False

    def tela_mudanca_ec(self):
        """Retorna se o Modal de Mudança de EC está ativo na tela."""
        try:
            self.driver.find_element(
                By.XPATH,
                '//div[@class="modal change-ec-modal-panel fade ng-scope ng-isolate-scope in"]'
            )
            return True
        except NoSuchElementException:
            return False

    def acao_mensagem_urgente(self):
        """Clica no botão OK para fechar o Modal."""
        if self.tela_mudanca_ec():
            return

        botao_ok = self.driver.find_element(
            By.XPATH,
            '//flui-button[@class=""][@type="button"][@theme="primary"]'
        )
        botao_ok.click()
        time.sleep(3)

    def trocar_ec(self):
        """Clica no botão para troca de EC."""
        finalizado = False
        while not finalizado:
            try:
                trocar_ec = self.driver.find_element(
                    By.XPATH,
                    '//input[@placeholder="Pesquisar estabelecimentos"]'
                )
                trocar_ec.click()
                time.sleep(2)
                finalizado = True
            except NoSuchElementException:
                botao_trocar = self.driver.find_element(
                    By.XPATH,
                    '//div[@ng-click="vm.trocarEstabelecimento()"]'
                )
                botao_trocar.click()
                time.sleep(2)

    def pesquisar_ec(self, ec: str):
        """Retorna a solução que o EC possui."""
        pesquisa_ec = self.driver.find_element(By.ID, 'inputSearchEstabelecimento')
        pesquisa_ec.clear()
        pesquisa_ec.send_keys(ec)
        pesquisa_ec.send_keys(Keys.RETURN)
        time.sleep(3)

        if self.mensagem_erro_existe():
            resultado = 'Nao encontrado'
            return resultado

        ec_retornado = self.driver.find_element(
            By.XPATH,
            '//div[@ng-repeat="filho in vm.filhosHierarquia track by $index"]'
        )
        ec_retornado.click()
        acessar = self.driver.find_element(By.ID, 'btnTrocaEc')
        acessar.click()
        time.sleep(3)
        resultado = None

        url_arquivo = dotenv_values('.env')
        url_checkout = url_arquivo.get('URL_CHECKOUT')
        url_api = url_arquivo.get('URL_API')

        if not url_checkout or not url_api:
            raise ArquivoEnvFaltando('URL Checkout ou API estão faltando.')

        self.driver.get(url_checkout)
        time.sleep(5)

        if self.header_checkout_existe():
            resultado = 'Checkout Cielo'

        self.driver.get(url_api)
        time.sleep(5)

        if self.driver.title == '[PRD] Home | Admin':
            if resultado:
                resultado += ' e API 3.0'
            resultado = 'API 3.0'

        if not resultado:
            resultado = 'Sem solucao'
        return resultado
