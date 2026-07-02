# Simulador de Filas M/M/s

Simulador estocástico de sistemas de filas com múltiplos servidores (M/M/s), desenvolvido para a disciplina de **Modelagem e Avaliação de Desempenho**.

---

## Visão geral

`etapa2_mms.py` implementa a simulação de uma fila M/M/s com as seguintes características:

- Chegadas de clientes com **distribuição exponencial** de média 2 (TEC) e tempo de serviço com **distribuição exponencial** de média 8 (TS), ambas geradas por um gerador pseudoaleatório LCG parametrizado por semente.
- Suporte a **s servidores em paralelo** (s ∈ {1, 2, 3, 4}), com disciplina FIFO e atendimento pelo primeiro servidor livre.
- Critério de parada por **tempo simulado** (`TEMPO_SIMULACAO`), não por número fixo de clientes.
- Execução de múltiplas **rodadas de replicações independentes**, cada uma com seu próprio par de sementes, para suporte ao cálculo de intervalo de confiança.
- Geração automática de **gráficos de convergência** por rodada e **gráfico comparativo global** entre cenários.

---

## Como executar

### 1. Gerar as sementes (uma única vez)

```bash
python gerar_seeds.py
```

Gera o arquivo `seeds.json` com todos os pares de sementes necessários para as rodadas e replicações. **Deve ser executado apenas uma vez** — regerar altera os resultados e quebra a reprodutibilidade.

Se `seeds.json` já existir, o script avisa e não sobrescreve.

### 2. Executar a simulação

```bash
python etapa2_mms.py
```

Roda automaticamente todas as rodadas e cenários definidos nos parâmetros do script. Ao final, gera os arquivos de resultado e os gráficos em `results/`.

---

## Parâmetros configuráveis

### `gerar_seeds.py`

| Parâmetro | Valor padrão | Descrição |
|---|---|---|
| `SEED_MESTRA` | `2026` | Semente usada para embaralhar deterministicamente a lista de inteiros. Garante reprodutibilidade. |
| `N_RODADAS` | `5` | Número de rodadas de replicações a gerar sementes. |
| `N_REPLICACOES` | `200` | Número de replicações por rodada. |
| `OUTPUT_PATH` | `seeds.json` | Caminho de saída da tabela de sementes. |

### `etapa2_mms.py`

| Parâmetro | Valor padrão | Descrição |
|---|---|---|
| `TEMPO_SIMULACAO` | `200` | Tempo total de cada simulação. O loop gera clientes até que o tempo de chegada ultrapasse este valor. |
| `CENARIOS` | `[1, 2, 3, 4]` | Lista de valores de `NUM_CAIXAS` (número de servidores) a simular. |

As fórmulas de geração de TEC e TS estão fixas conforme especificação:

```
TEC(i) = -ln(u) / (1/2)   →  média = 2
TS(i)  = -ln(u) / (1/8)   →  média = 8
```

onde `u` é um número uniforme em (0, 1) gerado pelo `GeradorAleatorio` com a semente do par correspondente.

---

## Estrutura de arquivos

```
manual_simulator/
├── etapa2_mms.py           # Simulador principal M/M/s
├── gerar_seeds.py          # Gerador da tabela de sementes
├── seeds.json              # Tabela de pares (seed_tec, seed_ts) — não regenerar
├── etapa1_manual.py        # Simulação manual de validação (5 clientes fixos)
├── requisitos.md           # Documento de requisitos do projeto
├── README.md               # Este arquivo
└── results/
    ├── comparacao_cenarios.png        # Gráfico global: IC 95% por cenário e métrica
    ├── rodada_1/
    │   ├── convergencia.png           # Gráfico de média acumulada × replicações
    │   ├── resultados_caixas_1.txt    # Dados brutos + estatísticas (s=1)
    │   ├── resultados_caixas_2.txt
    │   ├── resultados_caixas_3.txt
    │   └── resultados_caixas_4.txt
    ├── rodada_2/
    │   └── ...
    └── rodada_N/
        └── ...
```

| Arquivo | Descrição |
|---|---|
| `seeds.json` | Tabela com `N_RODADAS × N_REPLICACOES` pares de sementes, todos únicos, gerados deterministicamente. |
| `results/rodada_X/resultados_caixas_S.txt` | Tabela completa de clientes + métricas por replicação + estatísticas agregadas (média, desvio padrão, IC 95%) para o cenário `s=S` na rodada `X`. |
| `results/rodada_X/convergencia.png` | Gráfico com 4 subplots (um por métrica), mostrando a evolução da média acumulada de `k=1` até `k=N_REPLICACOES` para cada cenário `s` — permite verificar a estabilização das estimativas. |
| `results/comparacao_cenarios.png` | Gráfico de barras com IC 95% comparando os 4 cenários em cada métrica, agregando todas as rodadas em pool. |

---

## Estatísticas geradas

Para cada par (rodada, cenário), são calculadas sobre as `N_REPLICACOES` replicações:

| Estatística | Fórmula |
|---|---|
| Média das médias | `x̄ = (1/n) Σ xi` |
| Desvio padrão amostral | `s = √((1/(n-1)) Σ (xi − x̄)²)` |
| Intervalo de confiança 95% | `x̄ ± 1,96 · s / √n` (aproximação t ≈ 1,96 válida para n ≥ 130) |

As métricas calculadas por replicação são:

- **Tempo médio na fila** — média do tempo que cada cliente aguardou antes de ser atendido.
- **Tempo médio de serviço** — média do tempo de atendimento de cada cliente.
- **Tempo médio no sistema** — fila + serviço.
- **Tempo médio ocioso** — média do tempo ocioso registrado por atendimento (soma dos períodos em que o servidor estava livre antes de cada chegada, dividido pelo número de clientes).

---

## Lógica de simulação: rodadas, replicações e clientes

A simulação está organizada em três níveis hierárquicos:

```
Rodada (R)
  └── Cenário (s = número de servidores)
        └── Replicação (1 a N_REPLICACOES)
              └── Clientes (gerados até tempo de chegada > TEMPO_SIMULACAO)
```

**Clientes por replicação:** o loop gera clientes sequencialmente. O tempo de chegada do cliente `i` é `chegada(i-1) + TEC(i)`. Quando esse valor ultrapassa `TEMPO_SIMULACAO`, o cliente é descartado e a replicação encerra. O número de clientes varia entre replicações.

**Replicações independentes:** cada replicação usa um par de sementes `(seed_tec, seed_ts)` exclusivo, garantindo sequências de números aleatórios distintas. As replicações de um mesmo cenário compartilham o mesmo par de sementes entre cenários diferentes (técnica de *common random numbers*), de modo que diferenças observadas entre `s=1`, `s=2`, `s=3` e `s=4` sejam atribuídas ao número de servidores, não à variabilidade das entradas.

**Rodadas independentes:** cada rodada usa um bloco diferente da tabela de sementes (sem sobreposição), garantindo independência estatística entre rodadas. As replicações de índice `i` na rodada `r` usam o par de sementes na posição `(r-1) × N_REPLICACOES + i` da tabela embaralhada.

**Geração das sementes (Opção B — tabela única extendida):**
1. Gera a lista ordenada `[1, 2, ..., 2 × N_RODADAS × N_REPLICACOES]`.
2. Embaralha deterministicamente com `random.Random(SEED_MESTRA).shuffle(lista)`.
3. Divide em pares consecutivos: o par de índice `j` é `(lista[2j], lista[2j+1])`.
4. A rodada `r` usa os pares `j = (r-1)×N_REPLICACOES` até `r×N_REPLICACOES - 1`.

Isso garante que nenhum valor de semente se repete entre rodadas, replicações ou tipos (TEC vs TS), e que o experimento é completamente reprodutível a partir de `SEED_MESTRA`.

---

## Bibliotecas utilizadas

| Biblioteca | Uso |
|---|---|
| `math` | Funções `log` e `sqrt` para TEC, TS e desvio padrão. |
| `os` | Manipulação de caminhos e criação de diretórios. |
| `sys` | Inserção do path para importar o módulo `GeradorAleatorio`. |
| `json` | Leitura de `seeds.json` em tempo de execução. |
| `random` | `random.Random(seed).shuffle()` para embaralhar a lista de sementes em `gerar_seeds.py`. |
| `matplotlib` | Geração dos gráficos de convergência e comparação entre cenários (modo `Agg` — sem display, salva em PNG). |

Todas as bibliotecas são da distribuição padrão do Python ou do ecossistema científico básico (`matplotlib`). Não há dependências de frameworks externos.
