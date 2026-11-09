import json
import os

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
 "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}
class BaseConhecimento:

    def __init__(self, caminho="data/base_conhecimento.json"):
        self.caminho = caminho
        self.orientacoes = []

    @staticmethod
    def normalizar(texto):
        texto = texto.lower().strip()
        for letra, troca in ACENTOS.items():
            texto = texto.replace(letra, troca)
        for sinal in "?!.,;:()°-º":
            texto = texto.replace(sinal, " ")
        return " " + " ".join(texto.split()) + " "

    def carregar(self):
        self.orientacoes = []

        if not os.path.exists(self.caminho):
            print(f"Aviso: arquivo de conhecimento nao encontrado: {self.caminho}")
            return False

        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

            if not isinstance(dados, list):
                print("Erro: a base de conhecimento deve ser uma lista JSON.")
                return False

            campos_obrigatorios = {
                "id",
                "categoria",
                "titulo",
                "palavras_chave",
                "resposta",
                "documentos",
                "onde",
                "fonte",
                "verificado_em",
            }

            for indice, registro in enumerate(dados, start=1):
                if not isinstance(registro, dict):
                    print(f"Aviso: registro {indice} ignorado (formato invalido).")
                    continue

                faltando = campos_obrigatorios - registro.keys()
                if faltando:
                    campos = ", ".join(sorted(faltando))
                    print(
                        f"Aviso: registro {indice} ignorado "
                        f"(campos obrigatorios ausentes: {campos})."
                    )
                    continue

                if not isinstance(registro["palavras_chave"], list):
                    print(
                        f"Aviso: registro {indice} ignorado "
                        "(palavras_chave deve ser uma lista)."
                    )
                    continue

                try:
                    orientacao = Orientacao(
                        id=registro["id"],
                        categoria=registro["categoria"],
                        titulo=registro["titulo"],
                        palavras_chave=registro["palavras_chave"],
                        resposta=registro["resposta"],
                        documentos=registro["documentos"],
                        onde=registro["onde"],
                        fonte=registro["fonte"],
                        verificado_em=registro["verificado_em"],
                    )
                    self.orientacoes.append(orientacao)

                except Exception as erro:
                    print(f"Aviso: registro {indice} nao foi carregado: {erro}")

            print(
                f"Base de conhecimento carregada: "
                f"{len(self.orientacoes)} orientacao(oes)."
            )
            return True

        except json.JSONDecodeError as erro:
            print(f"Erro: o arquivo JSON esta corrompido ou invalido: {erro}")
            return False
        except OSError as erro:
            print(f"Erro ao ler a base de conhecimento: {erro}")
            return False

    def categorias(self):
        categorias_encontradas = {
            orientacao.categoria for orientacao in self.orientacoes
        }
        return sorted(categorias_encontradas, key=str.casefold)

    def por_categoria(self, categoria):
        categoria_normalizada = self.normalizar(categoria)

        return [
            orientacao
            for orientacao in self.orientacoes
            if self.normalizar(orientacao.categoria) == categoria_normalizada
        ]

    def pontuar(self, pergunta, orientacao):

        pergunta_normalizada = self.normalizar(pergunta)
        titulo_normalizado = self.normalizar(orientacao.titulo)
        palavras_chave = orientacao.palavras_chave

        pontos = 0


        for palavra_chave in palavras_chave:
            chave_normalizada = self.normalizar(palavra_chave)


            if chave_normalizada.strip() and chave_normalizada in pergunta_normalizada:
                pontos += 3

        palavras_pergunta = set(pergunta_normalizada.split())

        for palavra in palavras_pergunta:
            if len(palavra) >= 4 and (" " + palavra + " ") in titulo_normalizado:
                pontos += 1

        return pontos

    def buscar(self, pergunta):
        resultados = []

        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            resultados.append((pontos, orientacao))

        resultados.sort(key=lambda resultado: resultado[0], reverse=True)

        return resultados