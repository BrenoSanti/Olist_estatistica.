import csv
import random
import argparse


# ============================================================
# CONFIGURAÇÕES DO BLACKJACK
# ============================================================

HIT = "H"
STAND = "S"
DOUBLE = "D"


# Estratégia básica simplificada para mãos hard.
# A decisão depende do valor do jogador e da carta visível do dealer.
def decidir_acao(valor_jogador, dealer_up, pode_dobrar):
    # 17 ou mais -> parar
    if valor_jogador >= 17:
        return STAND

    # 13 a 16 -> parar contra dealer 2-6
    if 13 <= valor_jogador <= 16:
        if 2 <= dealer_up <= 6:
            return STAND
        return HIT

    # 12 -> parar contra dealer 4-6
    if valor_jogador == 12:
        if 4 <= dealer_up <= 6:
            return STAND
        return HIT

    # 11 -> dobrar quando possível
    if valor_jogador == 11 and pode_dobrar:
        return DOUBLE

    # 10 -> dobrar contra 2-9
    if valor_jogador == 10 and 2 <= dealer_up <= 9 and pode_dobrar:
        return DOUBLE

    # 9 -> dobrar contra 3-6
    if valor_jogador == 9 and 3 <= dealer_up <= 6 and pode_dobrar:
        return DOUBLE

    return HIT


# ============================================================
# BARALHO
# ============================================================

def criar_baralho(numero_decks=8):
    """
    Cria um shoe de Blackjack.

    Ás = 11
    2-9 = valores normais
    10/J/Q/K = 10
    """

    cartas = [
        2, 3, 4, 5, 6, 7, 8, 9,
        10, 10, 10, 10,
        11
    ]

    baralho = cartas * 4 * numero_decks

    random.shuffle(baralho)

    return baralho


def comprar_carta(baralho):
    return baralho.pop()


# ============================================================
# CÁLCULO DAS MÃOS
# ============================================================

def calcular_valor(mao):
    valor = sum(mao)

    ases = mao.count(11)

    while valor > 21 and ases > 0:
        valor -= 10
        ases -= 1

    return valor


def possui_as_flexivel(mao):
    valor = sum(mao)
    ases = mao.count(11)

    while valor > 21 and ases > 0:
        valor -= 10
        ases -= 1

    return ases > 0


def blackjack(mao):
    return len(mao) == 2 and calcular_valor(mao) == 21


# ============================================================
# JOGADA DO DEALER
# ============================================================

def jogar_dealer(mao_dealer, baralho):

    while True:

        valor = calcular_valor(mao_dealer)

        # Dealer compra em soft 17
        if valor < 17:
            mao_dealer.append(comprar_carta(baralho))

        elif valor == 17 and possui_as_flexivel(mao_dealer):
            mao_dealer.append(comprar_carta(baralho))

        else:
            break

    return mao_dealer


# ============================================================
# UMA PARTIDA
# ============================================================

def jogar_partida(baralho):

    jogador = [
        comprar_carta(baralho),
        comprar_carta(baralho)
    ]

    dealer = [
        comprar_carta(baralho),
        comprar_carta(baralho)
    ]

    # Dados iniciais
    valor_inicial = calcular_valor(jogador)
    dealer_up = dealer[0]

    mao_inicial = jogador.copy()

    quantidade_hits = 0
    quantidade_acoes = 0

    primeira_acao = None
    dobrou = False

    # --------------------------------------------------------
    # BLACKJACK NATURAL
    # --------------------------------------------------------

    jogador_blackjack = blackjack(jogador)
    dealer_blackjack = blackjack(dealer)

    if not jogador_blackjack and not dealer_blackjack:

        # ----------------------------------------------------
        # JOGADA DO JOGADOR
        # ----------------------------------------------------

        while calcular_valor(jogador) < 21:

            pode_dobrar = len(jogador) == 2

            acao = decidir_acao(
                calcular_valor(jogador),
                dealer_up,
                pode_dobrar
            )

            if primeira_acao is None:
                primeira_acao = acao

            quantidade_acoes += 1

            if acao == STAND:
                break

            elif acao == HIT:

                jogador.append(
                    comprar_carta(baralho)
                )

                quantidade_hits += 1

            elif acao == DOUBLE:

                jogador.append(
                    comprar_carta(baralho)
                )

                dobrou = True
                break

    # --------------------------------------------------------
    # DEALER JOGA
    # --------------------------------------------------------

    if calcular_valor(jogador) <= 21 and not dealer_blackjack:
        dealer = jogar_dealer(
            dealer,
            baralho
        )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    valor_final_jogador = calcular_valor(jogador)
    valor_final_dealer = calcular_valor(dealer)

    jogador_estourou = valor_final_jogador > 21
    dealer_estourou = valor_final_dealer > 21

    if jogador_blackjack and dealer_blackjack:

        resultado = "empate"
        lucro = 0

    elif jogador_blackjack:

        resultado = "vitoria"
        lucro = 1.5

    elif dealer_blackjack:

        resultado = "derrota"
        lucro = -1

    elif jogador_estourou:

        resultado = "derrota"
        lucro = -2 if dobrou else -1

    elif dealer_estourou:

        resultado = "vitoria"
        lucro = 2 if dobrou else 1

    elif valor_final_jogador > valor_final_dealer:

        resultado = "vitoria"
        lucro = 2 if dobrou else 1

    elif valor_final_jogador < valor_final_dealer:

        resultado = "derrota"
        lucro = -2 if dobrou else -1

    else:

        resultado = "empate"
        lucro = 0

    # --------------------------------------------------------
    # RETORNA OS DADOS DA PARTIDA
    # --------------------------------------------------------

    return {
        "player_initial_value": valor_inicial,

        "dealer_upcard": dealer_up,

        "player_first_action":
            primeira_acao if primeira_acao else "BLACKJACK",

        "player_final_value": valor_final_jogador,

        "dealer_final_value": valor_final_dealer,

        "player_cards": len(jogador),

        "dealer_cards": len(dealer),

        "hits": quantidade_hits,

        "actions": quantidade_acoes,

        "player_blackjack": jogador_blackjack,

        "player_bust": jogador_estourou,

        "dealer_bust": dealer_estourou,

        "double_down": dobrou,

        "result": resultado,

        "profit": lucro,

        "initial_hand":
            "-".join(map(str, mao_inicial))
    }


# ============================================================
# SIMULAÇÃO
# ============================================================

def executar_simulacao(numero_partidas, arquivo_saida):

    colunas = [
        "round",
        "player_initial_value",
        "dealer_upcard",
        "player_first_action",
        "player_final_value",
        "dealer_final_value",
        "player_cards",
        "dealer_cards",
        "hits",
        "actions",
        "player_blackjack",
        "player_bust",
        "dealer_bust",
        "double_down",
        "result",
        "profit",
        "initial_hand"
    ]

    # cria o CSV
    with open(
        arquivo_saida,
        "w",
        newline="",
        encoding="utf-8"
    ) as arquivo:

        writer = csv.DictWriter(
            arquivo,
            fieldnames=colunas
        )

        writer.writeheader()

        baralho = criar_baralho()

        for rodada in range(
            1,
            numero_partidas + 1
        ):

            # cria novo shoe quando restarem poucas cartas
            if len(baralho) < 60:
                baralho = criar_baralho()

            resultado = jogar_partida(baralho)

            resultado["round"] = rodada

            writer.writerow(resultado)

            # mostra progresso
            if rodada % 10000 == 0:
                print(
                    f"{rodada:,} partidas simuladas..."
                )

    print()
    print("==============================")
    print("SIMULAÇÃO FINALIZADA")
    print("==============================")
    print(f"Partidas: {numero_partidas:,}")
    print(f"Arquivo: {arquivo_saida}")


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="Simulador de Blackjack para análise estatística"
    )

    parser.add_argument(
        "--hands",
        type=int,
        default=100000,
        help="Quantidade de partidas"
    )

    parser.add_argument(
        "--output",
        default="dados/blackjack.csv",
        help="Arquivo CSV de saída"
    )

    args = parser.parse_args()

    executar_simulacao(
        args.hands,
        args.output
    )


if __name__ == "__main__":
    main()