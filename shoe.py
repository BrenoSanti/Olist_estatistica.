"""Modelo probabilistico de um shoe de Blackjack.

Este modulo nao usa o CSV de simulacoes: todas as probabilidades sao
calculadas exclusivamente a partir das cartas que ainda restam no shoe.
"""

from collections import Counter, defaultdict
from typing import Iterable


VALORES = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10")


def normalizar_carta(carta: object) -> str:
    texto = str(carta).strip().upper()
    if texto in {"J", "Q", "K"}:
        return "10"
    if texto == "11":
        return "A"
    if texto not in VALORES:
        raise ValueError(f"Carta invalida: {carta!r}. Use A, 2-10, J, Q ou K.")
    return texto


def valor_da_mao(cartas: Iterable[object]) -> int:
    normalizadas = [normalizar_carta(carta) for carta in cartas]
    valor = sum(11 if carta == "A" else int(carta) for carta in normalizadas)
    ases = normalizadas.count("A")
    while valor > 21 and ases:
        valor -= 10
        ases -= 1
    return valor


class Shoe:
    def __init__(self, numero_decks: int = 8) -> None:
        if numero_decks <= 0:
            raise ValueError("O numero de decks deve ser positivo.")
        self.numero_decks = numero_decks
        self._inicial = {valor: 4 * numero_decks for valor in VALORES}
        self._inicial["10"] = 16 * numero_decks
        self.restantes: dict[str, int] = {}
        self.observadas: Counter[str] = Counter()
        self.reiniciar()

    @property
    def total_inicial(self) -> int:
        return 52 * self.numero_decks

    @property
    def total_restante(self) -> int:
        return sum(self.restantes.values())

    @property
    def total_utilizado(self) -> int:
        return self.total_inicial - self.total_restante

    @property
    def percentual_utilizado(self) -> float:
        return 100 * self.total_utilizado / self.total_inicial

    def reiniciar(self) -> None:
        self.restantes = self._inicial.copy()
        self.observadas = Counter()

    def registrar_observadas(self, cartas: Iterable[object]) -> None:
        normalizadas = [normalizar_carta(carta) for carta in cartas]
        solicitadas = Counter(normalizadas)
        excedentes = {
            carta: quantidade
            for carta, quantidade in solicitadas.items()
            if quantidade > self.restantes[carta]
        }
        if excedentes:
            detalhes = ", ".join(
                f"{carta}: pediu {qtd}, restam {self.restantes[carta]}"
                for carta, qtd in excedentes.items()
            )
            raise ValueError(f"Nao ha cartas suficientes no shoe ({detalhes}).")
        for carta, quantidade in solicitadas.items():
            self.restantes[carta] -= quantidade
            self.observadas[carta] += quantidade

    def probabilidades_proxima_carta(self) -> dict[str, float]:
        if self.total_restante == 0:
            raise ValueError("O shoe esta vazio; nao e possivel calcular probabilidades.")
        return {
            carta: quantidade / self.total_restante
            for carta, quantidade in self.restantes.items()
        }

    def distribuicao_apos_hit(self, mao: Iterable[object]) -> dict[object, float]:
        cartas_mao = [normalizar_carta(carta) for carta in mao]
        if not cartas_mao:
            raise ValueError("Informe ao menos uma carta na mao.")
        probabilidades = self.probabilidades_proxima_carta()
        distribuicao: defaultdict[object, float] = defaultdict(float)
        for proxima, probabilidade in probabilidades.items():
            novo_valor = valor_da_mao([*cartas_mao, proxima])
            destino: object = "Bust" if novo_valor > 21 else novo_valor
            distribuicao[destino] += probabilidade
        numericos = sorted(chave for chave in distribuicao if isinstance(chave, int))
        resultado = {chave: distribuicao[chave] for chave in numericos}
        if "Bust" in distribuicao:
            resultado["Bust"] = distribuicao["Bust"]
        return resultado

    def probabilidade_bust(self, mao: Iterable[object]) -> float:
        return self.distribuicao_apos_hit(mao).get("Bust", 0.0)
