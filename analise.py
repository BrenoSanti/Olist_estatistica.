"""Analise exploratoria das partidas simuladas de Blackjack."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


COLUNAS_OBRIGATORIAS = {
    "round", "player_initial_value", "dealer_upcard", "player_first_action",
    "player_final_value", "dealer_final_value", "player_cards", "dealer_cards",
    "hits", "actions", "player_blackjack", "player_bust", "dealer_bust",
    "double_down", "result", "profit", "initial_hand",
}
NUMERICAS = [
    "player_initial_value", "player_final_value", "dealer_final_value",
    "player_cards", "dealer_cards", "hits", "actions", "profit",
]
ORDEM_DEALER = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


def carregar_dados(caminho: str | Path = "dados/blackjack.csv") -> pd.DataFrame:
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"CSV nao encontrado: {caminho}")
    dados = pd.read_csv(caminho)
    faltantes = COLUNAS_OBRIGATORIAS.difference(dados.columns)
    if faltantes:
        raise ValueError(f"Colunas obrigatorias ausentes: {sorted(faltantes)}")
    return dados


def validar_dados(dados: pd.DataFrame) -> dict[str, object]:
    inconsistencias: list[str] = []
    if not dados["round"].is_unique:
        inconsistencias.append("A coluna round possui identificadores repetidos.")
    if (~dados["result"].isin(["vitoria", "derrota", "empate"])).any():
        inconsistencias.append("Ha resultados fora de vitoria/derrota/empate.")
    if (~dados["player_first_action"].isin(["H", "S", "D", "BLACKJACK", "SEM_ACAO"])).any():
        inconsistencias.append("Ha primeiras acoes desconhecidas.")
    blackjack_mal_rotulado = dados["player_first_action"].eq("BLACKJACK") & ~dados["player_blackjack"]
    if blackjack_mal_rotulado.any():
        inconsistencias.append(
            f"{int(blackjack_mal_rotulado.sum())} linhas usam BLACKJACK como primeira acao "
            "sem blackjack do jogador; sao rodadas encerradas antes de uma decisao."
        )
    for coluna in ["player_cards", "dealer_cards"]:
        if (dados[coluna] < 2).any():
            inconsistencias.append(f"{coluna} possui valor menor que 2.")
    for coluna in ["hits", "actions"]:
        if (dados[coluna] < 0).any():
            inconsistencias.append(f"{coluna} possui valor negativo.")
    if not (dados.loc[dados["player_blackjack"], "player_final_value"] == 21).all():
        inconsistencias.append("Ha blackjack do jogador com valor final diferente de 21.")
    if not (dados.loc[dados["player_bust"], "player_final_value"] > 21).all():
        inconsistencias.append("Ha player_bust com valor final menor ou igual a 21.")
    if not (dados.loc[dados["dealer_bust"], "dealer_final_value"] > 21).all():
        inconsistencias.append("Ha dealer_bust com valor final menor ou igual a 21.")
    return {
        "shape": dados.shape,
        "linhas": len(dados),
        "colunas": len(dados.columns),
        "nomes_colunas": dados.columns.tolist(),
        "tipos": dados.dtypes.astype(str).to_dict(),
        "nulos": dados.isna().sum().to_dict(),
        "duplicados_completos": int(dados.duplicated().sum()),
        "duplicados_sem_round": int(dados.drop(columns="round").duplicated().sum()),
        "valores_unicos": {
            coluna: sorted(dados[coluna].dropna().unique().tolist(), key=str)
            for coluna in ["result", "player_first_action", "dealer_upcard"]
        },
        "inconsistencias": inconsistencias,
    }


def estatisticas_descritivas(dados: pd.DataFrame) -> pd.DataFrame:
    linhas = {}
    for coluna in NUMERICAS:
        serie = dados[coluna].dropna()
        moda = serie.mode()
        linhas[coluna] = {
            "media": serie.mean(), "mediana": serie.median(),
            "moda": moda.iloc[0] if not moda.empty else np.nan,
            "variancia": serie.var(ddof=1), "desvio_padrao": serie.std(ddof=1),
            "minimo": serie.min(), "maximo": serie.max(),
            "amplitude": serie.max() - serie.min(), "Q1": serie.quantile(.25),
            "Q2": serie.quantile(.50), "Q3": serie.quantile(.75),
            "IQR": serie.quantile(.75) - serie.quantile(.25),
            "P5": serie.quantile(.05), "P10": serie.quantile(.10),
            "P90": serie.quantile(.90), "P95": serie.quantile(.95),
        }
    return pd.DataFrame.from_dict(linhas, orient="index")


def tabela_frequencias(dados: pd.DataFrame) -> pd.DataFrame:
    categorias = {
        "vitoria": dados["result"].eq("vitoria"),
        "derrota": dados["result"].eq("derrota"),
        "empate": dados["result"].eq("empate"),
        "blackjack": dados["player_blackjack"],
        "player_bust": dados["player_bust"],
        "dealer_bust": dados["dealer_bust"],
        "Hit": dados["player_first_action"].eq("H"),
        "Stand": dados["player_first_action"].eq("S"),
        "Double": dados["player_first_action"].eq("D"),
    }
    return pd.DataFrame({
        "frequencia": {nome: int(mascara.sum()) for nome, mascara in categorias.items()},
        "percentual": {nome: float(mascara.mean() * 100) for nome, mascara in categorias.items()},
    })


def _agrupar_taxas(dados: pd.DataFrame, coluna: str, incluir_bust_dealer: bool = False) -> pd.DataFrame:
    base = dados.assign(
        vitoria=dados.result.eq("vitoria"), derrota=dados.result.eq("derrota"),
        empate=dados.result.eq("empate"), bust=dados.player_bust,
    )
    agregacoes = {
        "partidas": ("round", "size"), "vitorias": ("vitoria", "sum"),
        "derrotas": ("derrota", "sum"), "empates": ("empate", "sum"),
        "busts": ("bust", "sum"), "taxa_vitoria": ("vitoria", "mean"),
        "taxa_derrota": ("derrota", "mean"), "taxa_empate": ("empate", "mean"),
        "taxa_bust": ("bust", "mean"),
    }
    if incluir_bust_dealer:
        agregacoes["taxa_dealer_bust"] = ("dealer_bust", "mean")
    return base.groupby(coluna).agg(**agregacoes).sort_index()


def analise_valor_inicial(dados: pd.DataFrame) -> pd.DataFrame:
    return _agrupar_taxas(dados, "player_initial_value")


def analise_dealer(dados: pd.DataFrame) -> pd.DataFrame:
    return _agrupar_taxas(dados, "dealer_upcard", incluir_bust_dealer=True)


def analise_acoes_contextual(dados: pd.DataFrame) -> pd.DataFrame:
    # Somente H/S/D representam decisoes comparaveis.
    base = dados[dados.player_first_action.isin(["H", "S", "D"])].copy().assign(
        vitoria=dados.result.eq("vitoria"), derrota=dados.result.eq("derrota"),
        empate=dados.result.eq("empate"), bust=dados.player_bust,
    )
    return (base.groupby(["player_initial_value", "dealer_upcard", "player_first_action"])
            .agg(partidas=("round", "size"), taxa_vitoria=("vitoria", "mean"),
                 taxa_derrota=("derrota", "mean"), taxa_empate=("empate", "mean"),
                 taxa_bust=("bust", "mean"))
            .sort_index())


def consultar_situacao(dados: pd.DataFrame, valor: int, dealer: int) -> dict[str, float | int]:
    filtro = dados[(dados.player_initial_value == valor) & (dados.dealer_upcard == dealer)]
    total = len(filtro)
    if not total:
        return {"ocorrencias": 0}
    return {
        "ocorrencias": total,
        "vitorias": int(filtro.result.eq("vitoria").sum()),
        "derrotas": int(filtro.result.eq("derrota").sum()),
        "empates": int(filtro.result.eq("empate").sum()),
        "taxa_vitoria": float(filtro.result.eq("vitoria").mean()),
        "taxa_derrota": float(filtro.result.eq("derrota").mean()),
        "taxa_empate": float(filtro.result.eq("empate").mean()),
        "taxa_bust": float(filtro.player_bust.mean()),
    }


def correlacoes_numericas(dados: pd.DataFrame) -> pd.DataFrame:
    # Pearson e aplicado apenas a contagens/valores numericos, nao a categorias codificadas.
    return dados[NUMERICAS].corr(method="pearson")


def conclusoes_hipoteses(dados: pd.DataFrame) -> list[str]:
    inicial = analise_valor_inicial(dados)
    corr = inicial.index.to_series().corr(inicial["taxa_vitoria"], method="spearman")
    dealer = analise_dealer(dados)
    taxa_456 = dealer.loc[dealer.index.isin([4, 5, 6]), "taxa_vitoria"].mean()
    taxa_outros = dealer.loc[~dealer.index.isin([4, 5, 6]), "taxa_vitoria"].mean()
    contextos = analise_acoes_contextual(dados).reset_index()
    contextos_multiacao = contextos.groupby(["player_initial_value", "dealer_upcard"]).size().gt(1).sum()
    if contextos_multiacao:
        texto_h3 = (
            f"H3: existem {contextos_multiacao} contextos valor inicial x dealer com mais de uma "
            "acao observada. Compare as taxas dentro desses contextos, nao apenas globalmente."
        )
    else:
        texto_h3 = (
            "H3: nao ha contexto valor inicial x dealer com mais de uma acao H/S/D observada. "
            "A estrategia simulada determina a acao pelo contexto, portanto estes dados nao "
            "permitem comparar acoes alternativas dentro da mesma situacao."
        )
    return [
        f"H1: associacao monotona (Spearman) entre valor inicial e taxa de vitoria = {corr:.3f}. O sinal e a magnitude descrevem os dados, sem provar causalidade.",
        f"H2: taxa media por grupo de dealer 4/5/6 = {taxa_456:.2%}; demais cartas = {taxa_outros:.2%}. A tabela completa deve orientar a conclusao.",
        texto_h3,
    ]


def _salvar(fig: plt.Figure, destino: Path, nome: str) -> None:
    fig.tight_layout()
    fig.savefig(destino / nome, dpi=160, bbox_inches="tight")
    plt.close(fig)


def gerar_graficos(dados: pd.DataFrame, diretorio: str | Path = "graficos") -> list[Path]:
    destino = Path(diretorio)
    destino.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    criados: list[Path] = []

    def registrar(fig: plt.Figure, nome: str) -> None:
        _salvar(fig, destino, nome)
        criados.append(destino / nome)

    contagens = dados.result.value_counts().reindex(["vitoria", "derrota", "empate"])
    fig, ax = plt.subplots(figsize=(8, 5)); sns.barplot(x=contagens.index, y=contagens.values, ax=ax)
    ax.set(title="Frequencia dos resultados", xlabel="Resultado", ylabel="Partidas"); registrar(fig, "01_frequencia_resultados.png")

    for coluna, titulo, nome in [
        ("player_initial_value", "Distribuicao do valor inicial do jogador", "02_distribuicao_valor_inicial.png"),
        ("player_final_value", "Distribuicao do valor final do jogador", "03_distribuicao_valor_final.png")]:
        fig, ax = plt.subplots(figsize=(9, 5)); sns.histplot(dados[coluna], discrete=True, ax=ax)
        ax.set(title=titulo, xlabel="Valor da mao", ylabel="Partidas"); registrar(fig, nome)

    inicial = analise_valor_inicial(dados)
    fig, ax = plt.subplots(figsize=(9, 5)); sns.lineplot(x=inicial.index, y=inicial.taxa_vitoria * 100, marker="o", ax=ax)
    ax.set(title="Taxa de vitoria por valor inicial", xlabel="Valor inicial", ylabel="Taxa de vitoria (%)"); registrar(fig, "04_taxa_vitoria_valor_inicial.png")

    dealer = analise_dealer(dados).reindex(ORDEM_DEALER)
    fig, ax = plt.subplots(figsize=(9, 5)); sns.barplot(x=[str(x) if x != 11 else "A" for x in dealer.index], y=dealer.taxa_vitoria * 100, ax=ax)
    ax.set(title="Taxa de vitoria por carta visivel do dealer", xlabel="Carta do dealer", ylabel="Taxa de vitoria (%)"); registrar(fig, "05_taxa_vitoria_dealer.png")

    fig, ax = plt.subplots(figsize=(9, 5)); sns.lineplot(x=inicial.index, y=inicial.taxa_bust * 100, marker="o", ax=ax)
    ax.set(title="Taxa de bust por valor inicial", xlabel="Valor inicial", ylabel="Taxa de bust (%)"); registrar(fig, "06_taxa_bust_valor_inicial.png")

    fig, ax = plt.subplots(figsize=(11, 6)); sns.boxplot(data=dados[["player_initial_value", "player_final_value", "dealer_final_value", "player_cards", "dealer_cards", "hits", "actions"]], ax=ax)
    ax.set(title="Boxplots das variaveis numericas", xlabel="Variavel", ylabel="Valor"); ax.tick_params(axis="x", rotation=30); registrar(fig, "07_boxplots_variaveis_numericas.png")

    heat = dados.assign(vitoria=dados.result.eq("vitoria")).pivot_table(index="player_initial_value", columns="dealer_upcard", values="vitoria", aggfunc="mean") * 100
    heat = heat.reindex(columns=ORDEM_DEALER).rename(columns={11: "A"})
    fig, ax = plt.subplots(figsize=(11, 8)); sns.heatmap(heat, cmap="YlGnBu", ax=ax, cbar_kws={"label": "Taxa de vitoria (%)"})
    ax.set(title="Taxa de vitoria: mao inicial x carta do dealer", xlabel="Carta visivel do dealer", ylabel="Valor inicial"); registrar(fig, "08_heatmap_mao_dealer.png")
    return criados


def executar_analise(caminho: str | Path = "dados/blackjack.csv", graficos: str | Path = "graficos") -> None:
    dados = carregar_dados(caminho)
    validacao = validar_dados(dados)
    print("\n=== VALIDACAO DO DATASET ===")
    print(f"Shape: {validacao['shape']} ({validacao['linhas']:,} linhas, {validacao['colunas']} colunas)")
    print("Colunas:", ", ".join(validacao["nomes_colunas"]))
    print("\nTipos:\n", pd.Series(validacao["tipos"]).to_string())
    print("\nPrimeiras linhas:\n", dados.head().to_string(index=False))
    print("\nNulos:\n", pd.Series(validacao["nulos"]).to_string())
    print(f"\nDuplicados completos: {validacao['duplicados_completos']}")
    print(f"Duplicados desconsiderando round: {validacao['duplicados_sem_round']}")
    print("Valores unicos relevantes:", validacao["valores_unicos"])
    print("Inconsistencias:", validacao["inconsistencias"] or "nenhuma encontrada")
    print("\n=== ESTATISTICA DESCRITIVA ===\n", estatisticas_descritivas(dados).round(3).to_string())
    print("\n=== FREQUENCIAS ===\n", tabela_frequencias(dados).round(3).to_string())
    print("\n=== INVESTIGACAO 1: VALOR INICIAL ===\n", analise_valor_inicial(dados).round(4).to_string())
    print("\n=== INVESTIGACAO 2: CARTA DO DEALER ===\n", analise_dealer(dados).round(4).to_string())
    print("\n=== INVESTIGACAO 3: ACOES POR CONTEXTO ===\n", analise_acoes_contextual(dados).round(4).to_string())
    print("\n=== CORRELACOES NUMERICAS (PEARSON) ===\n", correlacoes_numericas(dados).round(3).to_string())
    print("\n=== HIPOTESES ===")
    for conclusao in conclusoes_hipoteses(dados):
        print("-", conclusao)
    criados = gerar_graficos(dados, graficos)
    print(f"\n{len(criados)} graficos salvos em {Path(graficos).resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analise exploratoria do Blackjack")
    parser.add_argument("--csv", default="dados/blackjack.csv")
    parser.add_argument("--graficos", default="graficos")
    argumentos = parser.parse_args()
    executar_analise(argumentos.csv, argumentos.graficos)
