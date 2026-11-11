# Citizen Assist AI

Assistente digital de orientação ao cidadão, executado no terminal e feito em Python, para a Global Solution 2026.2 da FIAP.

Este repositório reúne a entrega de **duas disciplinas**:

- **Pensamento Computacional e Automação com Python (PCAP):** o assistente, a busca por pontuação, as classes, o histórico, os indicadores e o CSV.
- **Soluções em Energias Renováveis e Sustentáveis (SERS):** a análise de consumo e a comparação entre eficiência (LED) e geração solar. Está descrita na **seção 11**, com os arquivos identificados.

O assistente responde **somente com o que está na base de conhecimento verificada**, mostra a fonte e a data de verificação em toda resposta, avisa que não é um canal oficial e **não coleta dados pessoais**.

## Sumário

1. [Integrantes](#1-integrantes)
2. [Público e problema](#2-público-e-problema)
3. [ODS relacionados](#3-ods-relacionados)
4. [Como executar](#4-como-executar)
5. [Estrutura do projeto](#5-estrutura-do-projeto)
6. [Classes e composição](#6-classes-e-composição)
7. [Regra de pontuação](#7-regra-de-pontuação)
8. [Regras de atendimento](#8-regras-de-atendimento)
9. [Histórico, indicadores e CSV](#9-histórico-indicadores-e-csv)
10. [Teste com usuários](#10-teste-com-usuários)
11. [Contribuição de SERS: energia e sustentabilidade](#11-contribuição-de-sers-energia-e-sustentabilidade)
12. [Fontes consultadas](#12-fontes-consultadas)
13. [Limitações](#13-limitações)
    
## 1. Integrantes

| Nome | RM |
|------|----|
| Leonardo Figueredo dos Santos | 573653 |
| Lucas Ramos de Souza | 573901 |
| Pablo Renato dos Santos Sobral de Carvalho | 569894 |

## 2. Público e problema

**Público:** famílias de baixa renda e consumidores residenciais.

**Problema:** muitas famílias perdem tempo para descobrir a quem recorrer, quais documentos levar e como acessar programas públicos de educação, assistência social e energia. A informação existe, mas está espalhada, em linguagem técnica e misturada com páginas que parecem oficiais e não são. Na conta de luz, falta também uma forma simples de avaliar se vale a pena economizar ou gerar energia.

**Solução:** um assistente que orienta, em linguagem simples, sobre **12 temas em 3 categorias**, e que ainda simula alternativas de economia e geração de energia.

| Categoria | Orientações |
|-----------|-------------|
| Educação | ProUni, FIES, Pé-de-Meia |
| Assistência social | Cadastro Único, Bolsa Família, Gás do Povo, Minha Casa Minha Vida, BPC |
| Energia e serviços essenciais | Luz para Todos, Tarifa Social de Energia Elétrica, lâmpadas LED, energia solar fotovoltaica |

## 3. ODS relacionados

- **ODS 1 – Erradicação da pobreza:** orienta sobre programas de proteção social.
- **ODS 4 – Educação de qualidade:** orienta sobre acesso ao ensino superior e permanência no ensino médio.
- **ODS 7 – Energia limpa e acessível:** orienta sobre tarifa social, acesso à energia, eficiência e energia solar.
- **ODS 10 – Redução das desigualdades:** facilita o acesso a direitos por quem tem menos informação.
- **ODS 13 – Ação contra a mudança global do clima:** apresenta a geração renovável e a redução do desperdício de energia.
- **ODS 16 – Instituições eficazes:** informação com fonte oficial e transparência.

## 4. Como executar

Requisitos: Python 3.8 ou superior. Não há bibliotecas externas.

```bash
git clone https://github.com/leofigueredo2008-beep/citizen-assist-ai.git
cd citizen-assist-ai
python main.py
```

### Menu principal

| Opção | O que faz |
|-------|-----------|
| 1 | Fazer uma pergunta em texto livre |
| 2 | Navegar por categorias e orientações |
| 3 | Analisar consumo e alternativas de energia (**SERS**) |
| 0 | Sair: pede a nota de facilidade (1 a 5), mostra os indicadores e exporta o CSV |

Em todas as telas, **0 volta** para a tela anterior.

## 5. Estrutura do projeto

```
citizen-assist-ai/
├── README.md
├── main.py                       # carrega a base e inicia o assistente
├── orientacao.py                 # classe Orientacao
├── base_conhecimento.py          # classe BaseConhecimento
├── assistente.py                 # classe Assistente (inclui a análise de energia)
└── data/
    ├── base_conhecimento.json    # as 12 orientações
    ├── analise_energia.json      # [SERS] premissas, dados e referências da análise de energia
    ├── historico.json            # criado pelo programa a cada atendimento
    └── atendimentos.csv          # exportado pelo programa
```

## 6. Classes e composição

```
Assistente
└── base: BaseConhecimento
     └── orientacoes: [Orientacao, Orientacao, ...]
```

| Classe | Responsabilidade | Atributos | Principais métodos |
|--------|------------------|-----------|--------------------|
| `Orientacao` | Guarda os dados de uma orientação e a exibe | `id`, `categoria`, `titulo`, `palavras_chave`, `resposta`, `documentos`, `onde`, `fonte`, `verificado_em` | `exibir()` |
| `BaseConhecimento` | Lê o JSON, lista categorias e busca a melhor orientação | `caminho`, `orientacoes` | `carregar()`, `categorias()`, `por_categoria()`, `normalizar()`, `pontuar()`, `buscar()` |
| `Assistente` | Faz o atendimento, guarda o histórico e calcula os indicadores | `nome`, `base`, `historico` | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`, `analisar_energia()` |

Cada registro do `base_conhecimento.json` é um **dicionário**, e o JSON inteiro é uma **lista** de dicionários. O método `buscar()` devolve uma **lista de tuplas** `(pontos, orientacao)`.

## 7. Regra de pontuação

A "inteligência" do assistente é baseada em regras: a pergunta é comparada com cada orientação, que recebe pontos, e a de maior pontuação é exibida.

**Normalização:** pergunta, palavras-chave e título são comparados em minúsculas, sem acentos e sem pontuação (`? ! . , ; : ( ) ° º -`). O texto normalizado recebe um espaço no começo e no fim, para que `" sus "` não seja encontrado dentro de outra palavra.

| Regra | Pontos |
|-------|--------|
| Palavra-chave da orientação que aparece na pergunta | +3 (por palavra-chave) |
| Palavra da pergunta com 4 letras ou mais que aparece no título | +1 (cada palavra conta uma vez, mesmo repetida) |

| Melhor pontuação | Resultado |
|------------------|-----------|
| 6 pontos ou mais | Confiança **ALTA** |
| 3 a 5 pontos | Confiança **MÉDIA** |
| Menos de 3 pontos | "Não encontrei": sugere outras palavras ou as categorias |

O assistente mostra a melhor orientação e até **2 alternativas** que tenham pelo menos 3 pontos.

### Exemplo real

Pergunta: **"Como solicitar atendimento pelo Luz para Todos"**
Normalizada: `" como solicitar atendimento pelo luz para todos "`

| Cálculo | Pontos |
|---------|--------|
| Palavra-chave `luz para todos` aparece na pergunta | +3 |
| Palavras da pergunta com 4+ letras que estão no título: `como`, `solicitar`, `atendimento`, `pelo`, `para`, `todos` | +6 |
| **Total** | **9 pontos: confiança ALTA** (orientação 7, Luz para Todos) |

## 8. Regras de atendimento

- **Entradas inválidas:** letras, números fora da faixa, resposta vazia e s/n inválido nunca encerram o programa.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Pergunta com 8 ou mais dígitos ou com `@` é recusada e **não é registrada**.
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso "Este assistente NÃO é um canal oficial".
- **Arquivos:** se a base JSON estiver ausente, corrompida ou com formato inválido, o programa avisa e não trava. Registros com campos faltando são ignorados com aviso. O mesmo vale para o histórico e para o `analise_energia.json`.

## 9. Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com: `data`, `origem`, `pergunta`, `id_orientacao`, `encontrou`, `ajudou`, `tentativas`, `tempo_segundos` e `facilidade`. O tempo é medido com `time.time()`. Ao sair, o assistente pede a nota de facilidade de 1 a 5, que é gravada nos atendimentos daquela sessão. Os atendimentos são exportados para `data/atendimentos.csv` com `csv.DictWriter`.

O programa calcula e exibe: resposta encontrada (%), taxa de acerto (ajudou, %), tempo médio, tentativas por atendimento, facilidade de uso (1 a 5) e a lista de dúvidas sem solução. A taxa de acerto é calculada sobre os atendimentos em que a pessoa respondeu s/n.

## 10. Teste com usuários

Os atendimentos abaixo foram feitos por **pessoas de fora da equipe**, antes da gravação do vídeo, e estão em `data/historico.json` e `data/atendimentos.csv`. Não foram registrados nomes nem dados pessoais.

- Atendimentos: **11**
- Pessoas de fora da equipe: **3** (Atendimentos: 1, 2 e 3 (Que foram feitos pela mesma pessoa, por isso mostra a mesma pergunta) e 4)
- Data dos testes: 09/11/2026

### Indicadores obtidos

Calculados pelo próprio programa (`indicadores()`) a partir dos 11 atendimentos:

| Indicador | Resultado |
|-----------|-----------|
| Resposta encontrada | **100,0%** (11 de 11) |
| Taxa de acerto (ajudou) | **72,7%** (8 de 11) |
| Tempo médio para encontrar | **38,3 segundos** |
| Tentativas por atendimento | **1,0** |
| Facilidade de uso | **3,8 / 5** |
| Dúvidas sem solução | Nenhuma: o assistente sempre mostrou uma orientação. Em 3 atendimentos, porém, a orientação mostrada **não resolveu** a dúvida (veja abaixo). |

### Histórico dos atendimentos

| # | Hora | Pergunta | Orientação mostrada | Ajudou | Tempo (s) | Nota |
|---|------|----------|---------------------|--------|-----------|------|
| 1 | 15:27 | Como faço para conseguir uma bolsa pelo ProUni? | 1 – ProUni | Sim | 39,9 | 3 |
| 2 | 15:28 | Quero entrar na faculdade, mas não tenho dinheiro para pagar. Existe algum financiamento? | 1 – ProUni | **Não** | 54,1 | 3 |
| 3 | 15:32 | Quero entrar na faculdade, mas não tenho dinheiro para pagar. Existe algum financiamento? | 2 – FIES | Sim | 42,3 | 5 |
| 4 | 15:33 | Como funciona o Pé-de-Meia? | 3 – Pé-de-Meia | Sim | 36,1 | 5 |
| 5 | 15:35 | Como faço para me cadastrar no Cadastro Único? | 4 – Cadastro Único | Sim | 35,8 | 4 |
| 6 | 15:36 | Como faço para receber o Bolsa Família? | 5 – Bolsa Família | Sim | 54,0 | 4 |
| 7 | 15:37 | Existe algum benefício do governo para ajudar a comprar gás de cozinha? | 6 – Gás do Povo | Sim | 39,9 | 4 |
| 8 | 15:38 | Minha comunidade ainda não tem acesso adequado à energia elétrica. Existe algum programa que possa ajudar? | 8 – Tarifa Social | **Não** | 37,8 | 4 |
| 9 | 15:38 | Como solicitar atendimento pelo Luz para Todos | 7 – Luz para Todos | Sim | 13,8 | 4 |
| 10 | 15:40 | Minha família não tem casa própria. Como funciona o Minha Casa, Minha Vida? | 9 – Minha Casa, Minha Vida | Sim | 14,4 | 3 |
| 11 | 15:41 | Quero diminuir minha conta de luz. Vale a pena trocar as lâmpadas comuns por lâmpadas LED? | 8 – Tarifa Social | **Não** | 53,6 | 3 |

### Dúvidas que a orientação não resolveu

1. **Atendimentos 2 e 3, financiamento de faculdade.** A pergunta mostrou o ProUni (que é bolsa).
2. **Atendimento 8, comunidade sem energia elétrica.** A pergunta mostrou a Tarifa Social, e era necessário mostrar o programa Luz para Todos
3. **Atendimento 11, trocar lâmpadas por LED.** A pergunta mostrou a Tarifa Social, e não a orientação sobre LED.

### Melhorias feitas a partir do teste

| Problema encontrado | Ajuste | Resultado |
|---------------------|--------|-----------|
| "Financiamento" mostrava o ProUni (atendimento 2) | Palavras-chave da orientação do FIES, como `financiamento` e `financiar faculdade` | A mesma pergunta passou a mostrar o FIES e **ajudou** (atendimento 3). Hoje: 4 pontos para o FIES contra 3 do ProUni |
| "Trocar lâmpadas por LED" mostrava a Tarifa Social (atendimento 11) | Palavras-chave novas na orientação de LED (`lampada led`, `lampada`, `led`, `economizar energia`...) | Hoje a mesma pergunta mostra a orientação de LED, com 4 pontos, contra 3 da Tarifa Social |

## 11. Contribuição de SERS: energia e sustentabilidade

> Esta seção identifica a contribuição da disciplina **Soluções em Energias Renováveis e Sustentáveis**. Arquivos da disciplina: `data/analise_energia.json` (dados e premissas), `assistente.py` (método `analisar_energia()`), as 4 orientações da categoria "Energia e serviços essenciais" em `data/base_conhecimento.json` e esta seção do README.

### 11.1 Contexto

- **Público:** famílias de baixa renda e consumidores residenciais.
- **Necessidade energética:** manter os serviços elétricos da residência, **reduzindo o consumo comprado da rede** e o valor da conta de luz.
- **Como o assistente contribui:** responde dúvidas sobre programas de energia (Tarifa Social, Luz para Todos), orienta sobre LED e energia solar e, pela opção 3 do menu, **simula e compara** duas alternativas com os números do usuário.

### 11.2 Funcionalidades de energia

| Funcionalidade | Onde |
|----------------|------|
| Perguntar em texto livre sobre conta de luz, LED, energia solar, Tarifa Social ou Luz para Todos | Opção 1 (busca por pontuação) |
| Navegar pela categoria "Energia e serviços essenciais" | Opção 2 |
| Simular e comparar **LED × energia solar** com valores editáveis, ver custos, impactos, limitações e referências | Opção 3 (`analisar_energia()`) |
| Registrar a análise no histórico e perguntar se ajudou | Opção 3 |

Na opção 3, o usuário pode alterar o consumo mensal (kWh), a tarifa (R$/kWh), a quantidade de lâmpadas e as horas de uso por dia. Aceitar Enter mantém o valor padrão, e 0 volta ao menu.

### 11.3 Dados e premissas

Arquivo: `data/analise_energia.json`.

| Dado | Valor | Tipo | Origem |
|------|-------|------|--------|
| Consumo residencial mensal de referência | 166,5 kWh | Público (média brasileira, 2025) | Boletim de informações energéticas (ARSP-ES), out.–dez. 2025 |
| Tarifa média residencial com tributos | R$ 0,8941/kWh (R$ 894,1/MWh) | Público (out. 2025) | Mesmo boletim |
| Custo médio de instalação solar | R$ 2,66/Wp | Público, **referência histórica** (1º semestre de 2024), não é cotação atual | EPE, relatório sobre microrredes |
| Eficiência de lâmpadas | Consulta e etiqueta | Referência | Inmetro (PBE) |
| Quantidade de lâmpadas | 5 | **Estimado** (didático) | Premissa da equipe |
| Potência da lâmpada convencional | 60 W | **Estimado** (hipotético) | Premissa da equipe |
| Potência da lâmpada LED | 9 W | **Estimado** (hipotético) | Premissa da equipe |
| Uso diário / dias por mês | 4 h / 30 dias | **Estimado** | Premissa da equipe |
| Preço de cada LED | R$ 10,00 | **Estimado** (substituir por cotação local) | Premissa da equipe |
| Sistema solar | 1,5 kWp | **Estimado** | Premissa da equipe |
| Horas de sol pico por dia | 4,5 h | **Estimado** (premissa de simulação, não é medição do local) | Premissa da equipe |
| Fator de desempenho solar | 0,8 | **Estimado** (perdas do sistema) | Premissa da equipe |

### 11.4 Cálculos

Todos os cálculos são feitos no `analisar_energia()`.

```
Energia (kWh/mês)    = quantidade × potência (W) × horas por dia × dias ÷ 1000
Economia LED (kWh)   = consumo das lâmpadas antigas − consumo das lâmpadas LED
Economia (R$/mês)    = energia (kWh) × tarifa (R$/kWh)
Investimento LED     = quantidade × preço unitário
Geração solar (kWh)  = potência (kWp) × horas de sol pico × dias × fator de desempenho
Energia solar usada  = menor valor entre o consumo da casa e a geração
Investimento solar   = potência (kWp) × 1000 × custo (R$/Wp)
Retorno simples      = investimento ÷ economia mensal
```

**Necessidade comum e período de referência:** as duas alternativas respondem à mesma necessidade (reduzir a energia comprada da rede em uma residência com consumo de 166,5 kWh/mês) e são comparadas **por mês e em 12 meses**.

### 11.5 Comparação das alternativas (valores padrão)

| | Alternativa 1: lâmpadas LED | Alternativa 2: energia solar (renovável) |
|---|---|---|
| Descrição | Trocar 5 lâmpadas de 60 W por LED de 9 W | Sistema de 1,5 kWp |
| Energia | 36,00 kWh/mês → 5,40 kWh/mês | Gera 162,00 kWh/mês |
| Economia de energia | **30,60 kWh/mês** (18,4% do consumo de referência) | Até 162,00 kWh/mês (97,3% do consumo, em teoria) |
| Investimento estimado | R$ 50,00 | R$ 3.990,00 |
| Economia em R$ | R$ 27,36/mês | R$ 144,84/mês (teórica) |
| Retorno simples | 1,8 meses | 27,5 meses (cerca de 2,3 anos) |
| Resultado em 12 meses (economia − investimento) | + R$ 278,31 | − R$ 2.251,87 (o investimento ainda não voltou) |
| Fonte | Renovável? Não: reduz o desperdício | **Renovável** |

Os números acima foram conferidos à mão e batem com a execução do programa (opção 3, valores padrão). **As economias das duas alternativas não devem ser somadas**, pois foram calculadas separadamente sobre o mesmo consumo.

### 11.6 Justificativa das recomendações

**Custos.** A troca por LED custa pouco e se paga rapidamente nas premissas usadas, o que combina com famílias de baixa renda. A energia solar exige um investimento muito maior e, pelas premissas, só se paga depois de mais de 2 anos, sem contar manutenção, financiamento e substituição de equipamentos.

**Viabilidade.** A LED não depende de obras nem de imóvel próprio. A energia solar depende de telhado adequado, orientação, inclinação, sombreamento, permissão para instalar, regras de conexão e compensação da distribuidora e do capital inicial. Por isso a recomendação do assistente é **começar pela eficiência** e **avaliar a solar com orçamento técnico**.

**Impactos ambientais.** A LED reduz a demanda de eletricidade e o desperdício. A solar usa uma fonte renovável e pode reduzir a energia comprada da rede. Nas duas, é preciso cuidar do descarte adequado dos equipamentos.

**Programas que complementam a análise.** Para famílias de baixa renda, o assistente também orienta sobre a **Tarifa Social** (desconto na conta de luz) e, para quem não tem acesso à rede, o **Luz para Todos**.

### 11.7 Como o assistente usa a análise

- As orientações 11 (LED) e 12 (energia solar) trazem na resposta os conceitos, a fórmula de consumo e os cuidados da análise, com fonte e data.
- A opção 3 aplica os cálculos com os dados do usuário e mostra, na mesma tela: cenário, resultados das duas alternativas, impactos, limitações, referências e o aviso de que a simulação é educativa.

### 11.8 Limitações das estimativas

Os resultados são **estimativas, não garantias**.

- A geração solar depende de localização, orientação, inclinação e sombreamento.
- A conta de luz pode ter cobrança mínima, encargos e componentes que **não foram calculados**.
- O custo solar é uma **referência histórica**, e não uma cotação atual.
- O retorno financeiro **não considera** manutenção, degradação, financiamento nem troca de equipamentos.
- A economia solar é **teórica**: não considera regras de compensação, tributos específicos nem a simultaneidade entre geração e consumo.
- Lâmpadas, potências e preço do LED são **estimativas didáticas**. O usuário deve conferir a potência real e fazer cotação local.

### 11.9 Referências de SERS

| Tema | Fonte |
|------|-------|
| Consumo residencial médio e tarifa média | https://arsp.es.gov.br/Media/arsi/Energia/Boletins/Boletins/4%20-%20INFORMACOES_ENERGETICAS_OUT_DEZ_2025.pdf |
| Custo de instalação de sistemas solares | https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-957/RT%20-%20Microrredes%20-%20FINAL.pdf |
| Eficiência energética de lâmpadas | https://www.gov.br/inmetro/pt-br/assuntos/regulamentacao/avaliacao-da-conformidade/programa-brasileiro-de-etiquetagem/tabelas-de-eficiencia-energetica/lampadas/ |
| Tarifa Social de Energia Elétrica | https://www.gov.br/aneel/pt-br/assuntos/tarifas/tarifa-social |
| Luz para Todos | https://www.gov.br/mme/pt-br/destaques/Programa%20Luz%20para%20Todos/saiba-como-solicitar-acesso/saiba-como-solicitar-acesso |

### 11.10 Testes com usuários: situações de energia

Das situações testadas na seção 10, estas são de energia:

| # | Situação | Resultado | Ajuste |
|---|----------|-----------|--------|
| 8 | Comunidade sem acesso à energia elétrica | Mostrou a Tarifa Social e **não ajudou** | **Ainda não resolvido** (veja a seção 10) |
| 9 | Pedido direto sobre o Luz para Todos | Mostrou a orientação certa e **ajudou** em 13,8 s | Nenhum |
| 11 | "Vale a pena trocar lâmpadas por LED?" | Mostrou a Tarifa Social e **não ajudou** | Palavras-chave adicionadas à orientação de LED |

**Teste da análise de consumo (opção 3):** PREENCHER. Registre quantas pessoas usaram, o que entenderam, os comentários recebidos e o ajuste feito.

## 12. Fontes consultadas

Cada orientação do `base_conhecimento.json` traz o link da fonte oficial e a data em que foi conferida (`verificado_em`).

| # | Orientação | Fonte |
|---|-----------|-------|
| 1 | ProUni | https://www.gov.br/pt-br/servicos/obter-bolsa-de-estudo-do-prouni |
| 2 | FIES | https://www.gov.br/pt-br/servicos/obter-financiamento-do-fies |
| 3 | Pé-de-Meia | https://www.gov.br/mec/pt-br/pe-de-meia/pe-de-meia |
| 4 | Cadastro Único | https://www.gov.br/mds/pt-br/acoes-e-programas/cadastro-unico |
| 5 | Bolsa Família | https://www.gov.br/pt-br/servicos/receber-o-bolsa-familia |
| 6 | Gás do Povo | https://www.gov.br/mds/pt-br/acoes-e-programas/gas-do-povo/gas-do-povo |
| 7 | Luz para Todos | https://www.gov.br/mme/pt-br/destaques/Programa%20Luz%20para%20Todos/saiba-como-solicitar-acesso/saiba-como-solicitar-acesso |
| 8 | Tarifa Social de Energia Elétrica | https://www.gov.br/aneel/pt-br/assuntos/tarifas/tarifa-social |
| 9 | Minha Casa, Minha Vida | https://www.gov.br/cidades/pt-br/acesso-a-informacao/perguntas-frequentes/habitacao |
| 10 | BPC | https://www.gov.br/mds/pt-br/acoes-e-programas/SUAS/beneficios-assistenciais/beneficio-assistencial-ao-idoso-e-a-pessoa-com-deficiencia-bpc |
| 11 | Lâmpadas LED | https://www.gov.br/inmetro/pt-br/assuntos/regulamentacao/avaliacao-da-conformidade/programa-brasileiro-de-etiquetagem/tabelas-de-eficiencia-energetica/lampadas/ |
| 12 | Energia solar fotovoltaica | https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-957/RT%20-%20Microrredes%20-%20FINAL.pdf |

Data de verificação de todas as orientações: 09/11/2026.

## 13. Limitações

- A busca é por regras: **não entende sinônimos, erros de digitação nem o sentido da frase**. Se a pessoa usar uma palavra que não está nas palavras-chave, a orientação pode não ser encontrada ou ser a errada.
- A base tem só 12 orientações. As regras e os valores de programas públicos mudam, e por isso cada resposta mostra a data de verificação.
- Várias respostas dependem da situação da família e do município. O assistente dá a orientação geral e indica onde confirmar.
- A análise de energia usa premissas estimadas e valores de referência; **não substitui orçamento técnico**.
- Este assistente **não é canal oficial** e não substitui a consulta ao órgão responsável.
- O histórico fica em um arquivo local e não identifica pessoas diferentes.
