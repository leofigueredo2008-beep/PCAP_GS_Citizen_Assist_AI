
import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente


def main():
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))

    caminho_base = os.path.join(
        pasta_projeto,
        "data",
        "base_conhecimento.json"
    )

    print("=" * 50)
    print("INICIANDO CITIZEN ASSIST AI")
    print("=" * 50)

    base = BaseConhecimento(caminho_base)

    if not base.carregar():
        print("\nNão foi possível carregar a base de conhecimento.")
        return

    if not base.orientacoes:
        print("\nA base foi carregada, mas não possui orientações válidas.")
        return

    print("\nCategorias disponíveis:", base.categorias())

    assistente = Assistente("Citizen Assist AI", base)

    assistente.iniciar()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário.")

    except Exception as erro:
        print(f"\nOcorreu um erro inesperado: {erro}")
