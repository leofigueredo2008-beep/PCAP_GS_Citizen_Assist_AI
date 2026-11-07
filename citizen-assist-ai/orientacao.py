class Orientacao:

    def __init__(self, id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
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
