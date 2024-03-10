"""Módulo de listagem de cadastros."""

def carregar_cadastros():
    """Retorna a lista de EC's obtida através do arquivo de cadastros."""
    with open('cadastros.txt', encoding='utf-8') as arq:
        lista_ec = arq.read().splitlines()
        return lista_ec
