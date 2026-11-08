
import os
import json
import csv
import re
import time

from datetime import datetime


class Assistente:
    def __init__(self, nome, base):
        self.nome = nome
        self.base = base
        self.historico = []

        pasta = os.path.dirname(os.path.abspath(__file__))

        self.caminho_historico = os.path.join(
            pasta, "data", "historico.json"
        )

        self.caminho_csv = os.path.join(
            pasta, "data", "atendimentos.csv"
        )


        self.facilidade = None
        self.registros_sessao = []

        self.carregar_historico()


    def carregar_historico(self):

        if not os.path.exists(self.caminho_historico):
            self.historico = []
            return

        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

            if isinstance(dados, list):
                self.historico = dados
            else:
                print("Aviso: o histórico possui um formato inválido.")
                self.historico = []

        except (json.JSONDecodeError, OSError):
            print("Aviso: não foi possível carregar o histórico.")
            self.historico = []

    def salvar_historico(self):

        try:
            os.makedirs(
                os.path.dirname(self.caminho_historico),
                exist_ok=True
            )

            with open(
                self.caminho_historico, "w", encoding="utf-8"
            ) as arquivo:
                json.dump(
                    self.historico,
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )

        except OSError:
            print("Erro: não foi possível salvar o histórico.")

    def registrar(
        self,
        origem,
        pergunta,
        orientacao,
        encontrou,
        ajudou,
        tentativas,
        tempo
    ):

        registro = {
            "data": datetime.now().isoformat(timespec="seconds"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": orientacao.id if orientacao else None,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
            "facilidade": None
        }

        self.historico.append(registro)
        self.registros_sessao.append(registro)

        self.salvar_historico()


    def possui_dados_pessoais(self, texto):

        quantidade_digitos = sum(
            caractere.isdigit() for caractere in texto
        )

        return quantidade_digitos >= 8 or "@" in texto


    def perguntar_sim_nao(self, mensagem):

        while True:
            resposta = input(mensagem).strip().lower()

            if resposta in ("s", "n"):
                return resposta == "s"

            if resposta == "0":
                return None

            print("Entrada inválida. Digite s, n ou 0 para voltar.")


    def perguntar(self):

        inicio = time.time()
        tentativas = 0
        pergunta_final = ""
        
        while True:
            pergunta = input(
                "\nDigite sua dúvida (0 para voltar): "
            ).strip()

            if pergunta == "0":
                return

            if not pergunta:
                print("A pergunta não pode ficar vazia.")
                continue

            if self.possui_dados_pessoais(pergunta):
                print(
                    "Atenção: não digite CPF, telefone ou e-mail. "
                    "Reescreva sua pergunta."
                )
                continue

            tentativas += 1
            pergunta_final = pergunta

            resultados = self.base.buscar(pergunta)

            if not resultados or resultados[0][0] < 3:
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Tente utilizar outras palavras ou navegar pelas categorias.")

                tentar_novamente = self.perguntar_sim_nao(
                    "Deseja tentar novamente? (s/n): "
                )

                if tentar_novamente is None:
                    return

                if tentar_novamente:
                    continue

                tempo = round(time.time() - inicio, 1)

                self.registrar(
                    origem="pergunta",
                    pergunta=pergunta_final,
                    orientacao=None,
                    encontrou=False,
                    ajudou=False,
                    tentativas=tentativas,
                    tempo=tempo
                )

                return

            pontos, orientacao = resultados[0]

            if pontos >= 6:
                confianca = "ALTA"
            else:
                confianca = "MÉDIA"

            print(f"\nConfiança da resposta: {confianca} ({pontos} pontos)")

            orientacao.exibir()

            alternativas = [
                resultado
                for resultado in resultados[1:3]
                if resultado[0] >= 3
            ]

            if alternativas:
                print("\nOutras orientações que podem ajudar:")

                for pontos_alt, alternativa in alternativas:
                    print(
                        f"\n- {alternativa.titulo} "
                        f"({pontos_alt} pontos)"
                    )

            ajudou = self.perguntar_sim_nao(
                "\nEssa orientação respondeu sua dúvida? (s/n): "
            )

            if ajudou is None:
                ajudou = None

            tempo = round(time.time() - inicio, 1)

            self.registrar(
                origem="pergunta",
                pergunta=pergunta_final,
                orientacao=orientacao,
                encontrou=True,
                ajudou=ajudou,
                tentativas=tentativas,
                tempo=tempo
            )

            return


    def navegar(self):

        categorias = self.base.categorias()

        if not categorias:
            print("\nNão existem categorias cadastradas.")
            return

        while True:
            print("\n========== CATEGORIAS ==========")

            for indice, categoria in enumerate(categorias, start=1):
                print(f"{indice} - {categoria}")

            print("0 - Voltar")

            escolha = input("\nEscolha uma categoria: ").strip()

            if escolha == "0":
                return

            if not escolha.isdigit():
                print("Opção inválida. Digite um número.")
                continue

            numero = int(escolha)

            if numero < 1 or numero > len(categorias):
                print("Opção fora da faixa. Tente novamente.")
                continue

            categoria_escolhida = categorias[numero - 1]

            orientacoes = self.base.por_categoria(
                categoria_escolhida
            )

            while True:
                print(f"\n========== {categoria_escolhida.upper()} ==========")

                for indice, orientacao in enumerate(
                    orientacoes, start=1
                ):
                    print(f"{indice} - {orientacao.titulo}")

                print("0 - Voltar")

                escolha_orientacao = input(
                    "\nEscolha uma orientação: "
                ).strip()

                if escolha_orientacao == "0":
                    break

                if not escolha_orientacao.isdigit():
                    print("Opção inválida. Digite um número.")
                    continue

                numero_orientacao = int(escolha_orientacao)

                if (
                    numero_orientacao < 1
                    or numero_orientacao > len(orientacoes)
                ):
                    print("Opção fora da faixa. Tente novamente.")
                    continue

                orientacao = orientacoes[numero_orientacao - 1]

                inicio = time.time()

                orientacao.exibir()

                ajudou = self.perguntar_sim_nao(
                    "\nEssa orientação respondeu sua dúvida? (s/n): "
                )

                tempo = round(time.time() - inicio, 1)

                self.registrar(
                    origem="categoria",
                    pergunta=orientacao.titulo,
                    orientacao=orientacao,
                    encontrou=True,
                    ajudou=ajudou,
                    tentativas=1,
                    tempo=tempo
                )
                
                if ajudou is None:
                    break


    def indicadores(self):

        total = len(self.historico)

        print("\n========== INDICADORES ==========")

        if total == 0:
            print("Ainda não existem atendimentos registrados.")
            return

        encontrados = sum(
            1 for registro in self.historico
            if registro["encontrou"]
        )

        avaliados = [
            registro for registro in self.historico
            if registro["ajudou"] is not None
        ]

        ajudaram = sum(
            1 for registro in avaliados
            if registro["ajudou"]
        )

        tempo_medio = sum(
            registro["tempo_segundos"]
            for registro in self.historico
        ) / total

        tentativas_media = sum(
            registro["tentativas"]
            for registro in self.historico
        ) / total

        notas = [
            registro["facilidade"]
            for registro in self.historico
            if registro.get("facilidade") is not None
        ]

        print(
            f"Resposta encontrada: {encontrados / total * 100:.1f}%"
        )

        if avaliados:
            print(
                f"Taxa de acerto (ajudou): "
                f"{ajudaram / len(avaliados) * 100:.1f}%"
            )
        else:
            print("Taxa de acerto: ainda não há avaliações.")

        print(f"Tempo médio: {tempo_medio:.1f} segundos")
        print(f"Tentativas por atendimento: {tentativas_media:.1f}")

        if notas:
            facilidade_media = sum(notas) / len(notas)
            print(f"Facilidade de uso: {facilidade_media:.1f}/5")
        else:
            print("Facilidade de uso: ainda não avaliada.")

        print("\nDúvidas sem solução:")

        sem_solucao = [
            registro for registro in self.historico
            if not registro["encontrou"]
        ]

        if sem_solucao:
            for registro in sem_solucao:
                print(f"- {registro['pergunta']}")
        else:
            print("Nenhuma dúvida sem solução registrada.")


    def exportar_csv(self):

        campos = [
            "data",
            "origem",
            "pergunta",
            "id_orientacao",
            "encontrou",
            "ajudou",
            "tentativas",
            "tempo_segundos",
            "facilidade"
        ]

        try:
            os.makedirs(
                os.path.dirname(self.caminho_csv),
                exist_ok=True
            )

            with open(
                self.caminho_csv,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as arquivo:

                escritor = csv.DictWriter(
                    arquivo,
                    fieldnames=campos
                )

                escritor.writeheader()
                escritor.writerows(self.historico)

            print(f"\nAtendimentos exportados para: {self.caminho_csv}")

        except OSError:
            print("Erro: não foi possível exportar o arquivo CSV.")


    def avaliar_facilidade(self):

        while True:
            nota = input(
                "\nDe 1 a 5, quão fácil foi utilizar o assistente? "
            ).strip()

            if nota.isdigit() and 1 <= int(nota) <= 5:
                self.facilidade = int(nota)

                for registro in self.registros_sessao:
                    registro["facilidade"] = self.facilidade

                self.salvar_historico()
                return

            print("Nota inválida. Digite um número de 1 a 5.")


    def iniciar(self):

        print("=" * 50)
        print(f"BEM-VINDO AO {self.nome.upper()}")
        print("=" * 50)

        print(
            "\nEste assistente oferece orientações com base "
            "em informações cadastradas e verificadas."
        )

        while True:
            print("\n========== MENU PRINCIPAL ==========")
            print("1 - Fazer uma pergunta")
            print("2 - Navegar por categorias")
            print("0 - Sair")

            escolha = input("\nEscolha uma opção: ").strip()

            if escolha == "1":
                self.perguntar()

            elif escolha == "2":
                self.navegar()

            elif escolha == "0":
                print("\nEncerrando o atendimento...")

                self.avaliar_facilidade()
                self.indicadores()
                self.exportar_csv()

                print(f"\nObrigado por utilizar o {self.nome}!")
                break

            else:
                print("Opção inválida. Escolha 1, 2 ou 0.")
