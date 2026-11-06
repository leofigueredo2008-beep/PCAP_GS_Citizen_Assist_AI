class Orientacao:

    def __init__(self, id, categoria, titulo, palavra_chave, resposta, documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavra_chave = palavra_chave
        self.resposta = resposta
        self.documentos = documentos 
        self.onde = onde 
        self.fonte = fonte 
        self.verificado_em = verificado_em

    def exibir(self):
        print(f"\n>> {self.titulo}  [{self.categoria}]")
        print(f"{self.resposta}")
        print(f"Documentos necessários:")
        for i in self.documentos:
            print(f"-{i}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} ({self.verificado_em})")
        print("Aviso: Este assistente NÃO é um canal oficial.")

#apenas para teste
teste = Orientacao("0","teste","vamos testar","teste","veja se o teste funcionou",["teste1","teste2","teste3"], "Brasil", "vozes da minha cabeca", "2026-11-06")
teste.exibir()