"""Menu interativo para consultas historicas e probabilidades do shoe."""

from pathlib import Path

from analise import (
    carregar_dados, consultar_situacao, executar_analise, tabela_frequencias,
)
from shoe import Shoe, normalizar_carta, valor_da_mao


def ler_cartas(mensagem: str) -> list[str]:
    texto = input(mensagem).replace("+", ",").replace(" ", ",")
    cartas = [parte for parte in texto.split(",") if parte.strip()]
    return [normalizar_carta(carta) for carta in cartas]


def mostrar_percentuais(valores: dict[object, float]) -> None:
    for chave, valor in valores.items():
        rotulo = "A" if chave == 11 else chave
        print(f"{str(rotulo):>4}: {valor:7.2%}")


def mostrar_composicao(shoe: Shoe) -> None:
    print(f"Cartas utilizadas: {shoe.total_utilizado}")
    print(f"Cartas restantes: {shoe.total_restante}")
    print(f"Percentual utilizado: {shoe.percentual_utilizado:.2f}%")
    print("Quantidade restante por valor:")
    for carta, quantidade in shoe.restantes.items():
        print(f"{carta:>2}: {quantidade}")


def resumo(dados) -> None:
    print("\nHISTORICO DAS SIMULACOES")
    print(f"Partidas: {len(dados):,}")
    print(tabela_frequencias(dados).round(2).to_string())


def consulta_historica(dados) -> None:
    try:
        valor = int(input("Valor inicial do jogador: ").strip())
        dealer_texto = normalizar_carta(input("Carta visivel do dealer: "))
        dealer = 11 if dealer_texto == "A" else int(dealer_texto)
    except ValueError as erro:
        print(f"Entrada invalida: {erro}")
        return
    resultado = consultar_situacao(dados, valor, dealer)
    print("\nHISTORICO DAS SIMULACOES")
    if not resultado["ocorrencias"]:
        print("Nenhuma situacao equivalente foi encontrada.")
        return
    for chave, numero in resultado.items():
        if chave.startswith("taxa_"):
            print(f"{chave}: {numero:.2%}")
        else:
            print(f"{chave}: {numero}")
    if resultado["ocorrencias"] < 30:
        print("Aviso: poucos registros; interprete as taxas com cautela.")


def analisar_hit(shoe: Shoe) -> None:
    try:
        mao = ler_cartas("Mao atual (ex.: A, 6): ")
        print(f"Valor atual: {valor_da_mao(mao)}")
        print("\nPROBABILIDADE MATEMATICA DO SHOE ATUAL")
        print(f"Cartas restantes: {shoe.total_restante}")
        print("\nProbabilidade da proxima carta:")
        mostrar_percentuais(shoe.probabilidades_proxima_carta())
        print("\nVALOR APOS EXATAMENTE UM HIT")
        mostrar_percentuais(shoe.distribuicao_apos_hit(mao))
        print(f"\nProbabilidade de bust: {shoe.probabilidade_bust(mao):.2%}")
    except ValueError as erro:
        print(f"Nao foi possivel analisar: {erro}")


def executar_menu(caminho_csv: str | Path = "dados/blackjack.csv") -> None:
    dados = carregar_dados(caminho_csv)
    shoe = Shoe(8)
    while True:
        print("""
===================================
BLACKJACK - ANALISE ESTATISTICA
===================================
1 - Resumo das partidas
2 - Consultar situacao historica
3 - Registrar cartas observadas no shoe
4 - Ver composicao atual do shoe
5 - Probabilidade da proxima carta
6 - Analisar um Hit
7 - Reiniciar shoe
8 - Executar analise completa e gerar graficos
0 - Sair
""")
        opcao = input("Opcao: ").strip()
        if opcao == "0":
            print("Programa encerrado.")
            return
        if opcao == "1":
            resumo(dados)
        elif opcao == "2":
            consulta_historica(dados)
        elif opcao == "3":
            try:
                cartas = ler_cartas("Cartas observadas, separadas por virgula: ")
                shoe.registrar_observadas(cartas)
                print(f"{len(cartas)} carta(s) registrada(s).")
                mostrar_composicao(shoe)
            except ValueError as erro:
                print(f"Nenhuma alteracao realizada: {erro}")
        elif opcao == "4":
            mostrar_composicao(shoe)
        elif opcao == "5":
            try:
                print("\nPROBABILIDADE MATEMATICA DO SHOE ATUAL")
                mostrar_percentuais(shoe.probabilidades_proxima_carta())
            except ValueError as erro:
                print(erro)
        elif opcao == "6":
            analisar_hit(shoe)
        elif opcao == "7":
            shoe.reiniciar()
            print("Shoe reiniciado com 416 cartas.")
        elif opcao == "8":
            executar_analise(caminho_csv)
        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    executar_menu()
