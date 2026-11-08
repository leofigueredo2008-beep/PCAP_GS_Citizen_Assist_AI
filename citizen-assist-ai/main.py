
from base_conhecimento import BaseConhecimento
from assistente import Assistente


base = BaseConhecimento("citizen-assist-ai/data/base_conhecimento.json")
base.carregar()

assistente = Assistente("Citizen Assist AI", base)
assistente.iniciar()
