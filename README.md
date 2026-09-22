# Analise Estatistica Exploratória de Blackjack

Este projeto analisa 100.000 partidas produzidas pelo simulador de Blackjack e,
separadamente, calcula probabilidades matematicas para um shoe atual de oito
decks. Cada linha de `dados/blackjack.csv` representa uma partida simulada.

## Objetivo e metodologia

O estudo investiga como o valor inicial da mao, a carta visivel do dealer e a
primeira acao do jogador estao associados aos resultados. O programa valida o
CSV, calcula estatisticas descritivas, frequencias, taxas condicionais,
correlacoes somente entre variaveis numericas e gera graficos.

A analise das acoes e estratificada por valor inicial e carta do dealer. Assim,
uma taxa global de Hit, Stand ou Double nao e interpretada isoladamente como
evidencia de superioridade, pois as acoes ocorrem em contextos diferentes.

O modulo `shoe.py` e independente do historico. Ele parte de 416 cartas, aceita
cartas observadas e calcula a proxima carta, o valor da mao apos exatamente um
Hit e a chance de bust a partir da composicao restante. J, Q e K contam como 10;
o As vale 1 ou 11 conforme a mao.

Na base existente, algumas rodadas encerradas pelo blackjack do dealer foram
rotuladas como `BLACKJACK` em `player_first_action`, embora o jogador nao tivesse
blackjack. A validacao informa quantas sao; elas permanecem intactas no CSV e
sao excluidas somente da comparacao entre H/S/D. Para futuras simulacoes,
`main.py` passou a registrar essas rodadas como `SEM_ACAO`.

## Estrutura

- `main.py`: simulador original (preservado).
- `analise.py`: leitura, validacao, estatisticas, hipoteses e oito graficos.
- `shoe.py`: composicao e probabilidades do shoe.
- `interface.py`: menu interativo.
- `test_blackjack.py`: testes basicos automatizados.
- `dados/blackjack.csv`: base existente; nao e alterada pela analise.
- `graficos/`: criada automaticamente ao executar a analise.

## Instalacao e execucao

Requer Python 3.10 ou superior. Em um ambiente virtual:

```bash
python -m pip install -r requirements.txt
python analise.py
python interface.py
python -m unittest -v
```

`python analise.py` imprime a validacao, as tabelas e as conclusoes descritivas
das hipoteses, e salva os PNGs em `graficos/`. `python interface.py` abre as
consultas historicas e os calculos do shoe.

Para gerar uma nova simulacao apenas quando isso for realmente desejado:

```bash
python main.py --hands 100000 --output dados/blackjack_novo.csv
```

Use outro nome de saida para nao sobrescrever a base original.

## Analises e graficos

As tabelas cobrem media, mediana, moda, variancia, desvio padrao, amplitude,
minimo, maximo, quartis, IQR e percentis. Tambem apresentam frequencias e taxas
de resultados, blackjack, bust e primeiras acoes. As investigacoes incluem:

1. taxas por valor inicial da mao;
2. taxas por carta visivel do dealer;
3. taxas por acao dentro de cada contexto mao x dealer;
4. matriz de correlacao das variaveis numericas;
5. avaliacao descritiva das hipoteses H1, H2 e H3.

Sao gerados graficos de resultados, distribuicoes inicial e final, taxa de
vitoria por valor inicial e por dealer, taxa de bust, boxplots e heatmap da taxa
de vitoria por mao inicial e carta do dealer.

## Fonte e limitacoes

Os dados sao as 100.000 partidas do simulador deste projeto. Os resultados
dependem das regras e da estrategia simplificada implementadas no simulador.
Eles nao representam comportamento humano, nao demonstram causalidade e nao
garantem resultados em partidas reais. O projeto e descritivo e academico; nao
fornece recomendacoes de aposta.
