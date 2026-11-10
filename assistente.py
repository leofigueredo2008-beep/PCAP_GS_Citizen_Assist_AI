
import os
import json
import csv
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

# Configuração da análise de energia

        self.caminho_analise_energia = os.path.join(
            pasta, "data", "analise_energia.json"
            )

        self.configuracao_energia = self.carregar_configuracao_energia()

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



    def carregar_configuracao_energia(self):
        """Carrega os dados utilizados na análise energética."""

        if not os.path.exists(self.caminho_analise_energia):
            print(
                "Aviso: arquivo analise_energia.json não encontrado. "
                "A análise de energia ficará indisponível."
            )
            return None

        try:
            with open(
                self.caminho_analise_energia,
                "r",
                encoding="utf-8"
            ) as arquivo:
                dados = json.load(arquivo)

            if not isinstance(dados, dict):
                print("Aviso: configuração de energia inválida.")
                return None

            if "premissas" not in dados or "referencias" not in dados:
                print("Aviso: faltam dados na configuração de energia.")
                return None

            return dados

        except (json.JSONDecodeError, OSError) as erro:
            print(f"Aviso: não foi possível carregar os dados de energia: {erro}")
            return None


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

            print("Entrada inválida. Digite s ou n")


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


    @staticmethod
    def _ler_numero_positivo(mensagem, padrao, inteiro=False):
        """Recebe um número positivo. Digitar 0 permite voltar."""

        while True:
            entrada = input(
                f"{mensagem} [{padrao}] (0 para voltar): "
            ).strip()

            if entrada == "0":
                return None

            if entrada == "":
                return int(padrao) if inteiro else float(padrao)

            try:
                valor = float(entrada.replace(",", "."))

                if valor <= 0:
                    raise ValueError

                if inteiro and not valor.is_integer():
                    raise ValueError

                return int(valor) if inteiro else valor

            except ValueError:
                if inteiro:
                    print("Digite um número inteiro positivo.")
                else:
                    print("Digite um número positivo válido.")


    @staticmethod
    def _formatar_moeda(valor):
        """Formata valores monetários no padrão brasileiro."""

        valor_formatado = f"{valor:,.2f}"

        valor_formatado = (
            valor_formatado
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return f"R$ {valor_formatado}"


    def analisar_energia(self):

        if not self.configuracao_energia:
            print("\nA análise de energia não está disponível.")
            return

        inicio = time.time()

        premissas = self.configuracao_energia["premissas"]

        print("\n========== ANÁLISE DE ENERGIA ==========")
        print(
            "Esta simulação compara duas alternativas para uma "
            "residência: eficiência com LED e geração solar."
        )
        print("Os valores podem ser alterados pelo usuário.")
        print("Os resultados são estimativas, não garantias.")

        consumo = self._ler_numero_positivo(
            "Consumo mensal da residência em kWh",
            premissas["consumo_mensal_referencia_kwh"]
        )

        if consumo is None:
            return

        tarifa = self._ler_numero_positivo(
            "Tarifa efetiva média em R$/kWh",
            premissas["tarifa_referencia_rs_kwh"]
        )

        if tarifa is None:
            return

        quantidade_lampadas = self._ler_numero_positivo(
            "Quantidade de lâmpadas convencionais",
            premissas["numero_lampadas"],
            inteiro=True
        )

        if quantidade_lampadas is None:
            return

        horas_uso = self._ler_numero_positivo(
            "Horas de uso por dia de cada lâmpada",
            premissas["horas_uso_diario"]
        )

        if horas_uso is None:
            return

        dias_mes = premissas["dias_por_mes"]

        potencia_atual = premissas["potencia_lampada_atual_w"]
        potencia_led = premissas["potencia_led_w"]
        preco_led = premissas["preco_unitario_led_rs"]

        # ALTERNATIVA 1: substituição por lâmpadas LED

        consumo_antigo = (
            quantidade_lampadas
            * potencia_atual
            * horas_uso
            * dias_mes
            / 1000
        )

        consumo_led = (
            quantidade_lampadas
            * potencia_led
            * horas_uso
            * dias_mes
            / 1000
        )

        economia_led_kwh = max(
            0,
            consumo_antigo - consumo_led
        )

        economia_led_kwh = min(
            consumo,
            economia_led_kwh
        )

        consumo_apos_led = max(
            0,
            consumo - economia_led_kwh
        )

        investimento_led = quantidade_lampadas * preco_led

        economia_led_reais = economia_led_kwh * tarifa

        retorno_led = (
            investimento_led / economia_led_reais
            if economia_led_reais > 0
            else None
        )

        # ALTERNATIVA 2: sistema solar fotovoltaico

        potencia_solar = premissas["potencia_sistema_solar_kwp"]
        horas_sol = premissas["horas_sol_pico_diarias"]
        fator_desempenho = premissas["fator_desempenho_solar"]
        custo_por_wp = premissas["custo_solar_rs_por_wp"]

        geracao_solar = (
            potencia_solar
            * horas_sol
            * dias_mes
            * fator_desempenho
        )

        energia_solar_utilizada = min(
            consumo,
            geracao_solar
        )

        consumo_apos_solar = max(
            0,
            consumo - energia_solar_utilizada
        )

        investimento_solar = (
            potencia_solar * 1000 * custo_por_wp
        )

        economia_solar_reais = (
            energia_solar_utilizada * tarifa
        )

        retorno_solar = (
            investimento_solar / economia_solar_reais
            if economia_solar_reais > 0
            else None
        )

        # RESULTADOS

        print("\n========== CENÁRIO ANALISADO ==========")
        print(f"Consumo mensal informado: {consumo:.2f} kWh")
        print(f"Tarifa utilizada: {self._formatar_moeda(tarifa)}/kWh")

        print("\n--- ALTERNATIVA 1: LÂMPADAS LED ---")

        print(
            f"Consumo atual das lâmpadas: "
            f"{consumo_antigo:.2f} kWh/mês"
        )

        print(
            f"Consumo das lâmpadas LED: "
            f"{consumo_led:.2f} kWh/mês"
        )

        print(
            f"Economia estimada: "
            f"{economia_led_kwh:.2f} kWh/mês"
        )

        print(
            f"Consumo residencial após a troca: "
            f"{consumo_apos_led:.2f} kWh/mês"
        )

        print(
            f"Investimento estimado: "
            f"{self._formatar_moeda(investimento_led)}"
        )

        print(
            f"Economia financeira mensal estimada: "
            f"{self._formatar_moeda(economia_led_reais)}"
        )

        if retorno_led is not None:
            print(
                f"Retorno simples estimado: "
                f"{retorno_led:.1f} meses"
            )

        print("\n--- ALTERNATIVA 2: ENERGIA SOLAR ---")

        print(
            f"Potência do sistema: {potencia_solar:.2f} kWp"
        )

        print(
            f"Geração mensal estimada: "
            f"{geracao_solar:.2f} kWh"
        )

        print(
            f"Energia considerada para compensação: "
            f"{energia_solar_utilizada:.2f} kWh"
        )

        print(
            f"Consumo residual teórico da rede: "
            f"{consumo_apos_solar:.2f} kWh"
        )

        print(
            f"Investimento estimado: "
            f"{self._formatar_moeda(investimento_solar)}"
        )

        print(
            f"Valor mensal teórico da energia solar utilizada: "
            f"{self._formatar_moeda(economia_solar_reais)}"
        )

        if retorno_solar is not None:
            print(
                f"Retorno simples teórico: "
                f"{retorno_solar:.1f} meses"
            )

        # IMPACTOS E LIMITAÇÕES

        print("\n========== IMPACTOS AMBIENTAIS ==========")

        print(
            "- LED: reduz a demanda de eletricidade da residência "
            "e diminui o desperdício de energia."
        )

        print(
            "- Solar: utiliza uma fonte renovável e pode reduzir "
            "a energia comprada da rede durante o período analisado."
        )

        print(
            "- Ambas as alternativas exigem atenção ao descarte "
            "adequado dos equipamentos."
        )

        print("\n========== LIMITAÇÕES ==========")

        print(
            "- A geração solar depende da localização, orientação, "
            "inclinação e sombreamento dos painéis."
        )

        print(
            "- A conta de luz pode manter cobranças mínimas, "
            "encargos e componentes que não foram calculados."
        )

        print(
            "- O custo solar utilizado é uma referência histórica, "
            "não uma cotação atual."
        )

        print(
            "- O retorno financeiro não considera manutenção, "
            "degradação, financiamento ou substituição de equipamentos."
        )

        print(
            "- As duas alternativas foram calculadas separadamente. "
            "Suas economias não devem ser somadas."
        )

        referencias = self.configuracao_energia["referencias"]

        print("\n========== REFERÊNCIAS ==========")

        for nome, referencia in referencias.items():
            print(f"\n{nome.upper()}:")
            print(referencia["descricao"])
            print(referencia["url"])

        print(
            "\nAviso: esta simulação é educativa e não substitui "
            "um orçamento técnico ou a avaliação de um profissional."
        )

        ajudou = self.perguntar_sim_nao(
            "\nEssa análise ajudou a entender as alternativas? (s/n): "
        )

        tempo = round(time.time() - inicio, 1)

        self.registrar(
            origem="energia",
            pergunta="Análise de consumo e alternativas de energia",
            orientacao=None,
            encontrou=True,
            ajudou=ajudou,
            tentativas=1,
            tempo=tempo
        )

        print("\nAnálise registrada no histórico.")



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
            print("3 - Analisar consumo e alternativas de energia")
            print("0 - Sair")

            escolha = input("\nEscolha uma opção: ").strip()

            if escolha == "1":
                self.perguntar()

            elif escolha == "2":
                self.navegar()

            elif escolha == "3":
                self.analisar_energia()    

            elif escolha == "0":
                print("\nEncerrando o atendimento...")

                self.avaliar_facilidade()
                self.indicadores()
                self.exportar_csv()

                print(f"\nObrigado por utilizar o {self.nome}!")
                break

            else:
                print("Opção inválida. Escolha 1, 2, 3 ou 0.")
