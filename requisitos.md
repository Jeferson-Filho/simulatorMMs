# Requisitos — Simulador de Sistema de Filas M/M/s

**Disciplina:** Modelagem e Avaliação de Desempenho
**Contexto:** Implementação de simulador de filas M/M/s baseado em distribuições exponenciais (TEC e TS), conforme metodologia e fórmulas apresentadas em aula.

---

## 1. Objetivo

Desenvolver um programa que simule um sistema de filas M/M/s, evoluindo em duas etapas obrigatórias e sequenciais:

1. **Etapa 1 — Simulação manual** (5 clientes fixos, para validação da lógica de cálculo).
2. **Etapa 2 — Simulador M/M/s** controlado por tempo simulado, com múltiplos servidores, múltiplas replicações e múltiplas rodadas.

A Etapa 1 serve exclusivamente para validar a lógica antes da Etapa 2. O relatório final usa apenas os resultados da Etapa 2.

---

## 2. Fórmulas obrigatórias (não alterar)

- **Tempo entre chegadas (TEC):**
  `TEC(i) = -ln(random(i)) / (1/2)` → distribuição exponencial, **média = 2** unidades de tempo.

- **Tempo de serviço (TS):**
  `TS(i) = -ln(random(i)) / (1/8)` → distribuição exponencial, **média = 8** unidades de tempo.

- `random(i)` deve ser um número uniforme em **(0, 1)** gerado por `random_number_generator/gerador_aleatorio.py`, parametrizado por semente (evitar valor 0 exato, que gera `ln(0)` indefinido).

---

## 3. Variáveis e colunas obrigatórias da simulação

Para cada cliente, calcular e registrar:

| Coluna | Cálculo |
|---|---|
| Cliente (i) | índice sequencial |
| TEC | tempo entre chegadas (gerado pela fórmula) |
| TS | tempo de serviço (gerado pela fórmula) |
| Tempo de chegada no relógio | chegada(i-1) + TEC(i) |
| Tempo início serviço | máx(chegada no relógio, fim do serviço do servidor escolhido) |
| Tempo fim serviço | início do serviço + TS |
| Tempo na fila | início do serviço − chegada no relógio |
| Tempo no sistema | tempo na fila + TS |
| Tempo ocioso do servidor | chegada no relógio − fim do serviço anterior (se > 0; senão 0) |

---

## 4. Etapa 1 — Simulação manual (5 clientes)

**Requisitos:**
- **Não usar** a fórmula TEC/TS nesta etapa. Usar os valores fixos abaixo:

  | Cliente | TEC (bruto) | TS (bruto) |
  |---|---|---|
  | 1 |  2 | 2 |
  | 2 |  5 | 4 |
  | 3 |  1 | 6 |
  | 4 |  2 | 3 |
  | 5 | 12 | 2 |

- Simular exatamente **5 clientes** com 1 servidor.
- Exibir tabela com todas as colunas da seção 3.

**Critério de aceite:** a tabela deve reproduzir, linha a linha, os cálculos do exemplo do slide 17 (lógica de chegada, início/fim de serviço, fila, sistema e ociosidade).

---

## 5. Etapa 2 — Simulador M/M/s

### 5.1 Funcionamento básico

- Gerar clientes com TEC e TS pelas fórmulas da seção 2.
- O loop encerra quando `tempo de chegada no relógio > TEMPO_SIMULACAO`; o cliente que ultrapassar é descartado.
- **s servidores em paralelo** (`NUM_CAIXAS` ∈ {1, 2, 3, 4}): o cliente é atendido pelo primeiro servidor livre; se todos estiverem ocupados, entra na fila (disciplina FIFO).
- Cada servidor tem seu próprio controle de tempo ocioso e `fim_servico`.
- Com `NUM_CAIXAS = 1`, o comportamento é idêntico ao M/M/1 (critério de regressão).

### 5.2 Cenários

O simulador é executado para todos os quatro cenários em uma única rodada:

- `NUM_CAIXAS` ∈ {1, 2, 3, 4}

Todos os cenários de uma mesma rodada compartilham os **mesmos pares de sementes** por índice de replicação (*common random numbers*), garantindo que as diferenças entre cenários sejam devidas ao número de servidores, não à variabilidade das entradas.

### 5.3 Replicações e rodadas

- Cada **replicação** roda a simulação completa do tempo `0` até `TEMPO_SIMULACAO` com seu próprio par de sementes `(seed_tec, seed_ts)`.
- Cada **rodada** agrupa `N_REPLICACOES = 200` replicações para um dado cenário.
- O simulador executa `N_RODADAS = 5` rodadas, cada uma com um bloco distinto de sementes.
- A partir de `n ≥ 130` replicações, o percentil t de Student converge para `t ≈ 1,96`, simplificando o IC 95%. Com 200 replicações por rodada esse limiar é satisfeito com margem.

---

## 6. Sementes (seeds) — regra dura de geração

- São necessários `N_RODADAS × N_REPLICACOES` pares `(seed_TEC, seed_TS)`.
- **Regra dura:** nenhum dos `2 × N_RODADAS × N_REPLICACOES` valores de semente pode se repetir — nem dentro do mesmo tipo, nem entre TEC e TS, nem entre replicações ou rodadas.
- As sementes são geradas de forma **determinística e reprodutível** por `gerar_seeds.py`.

**Algoritmo de geração (Opção B — tabela única extendida):**
1. Gerar a lista ordenada `[1, 2, ..., 2 × N_RODADAS × N_REPLICACOES]`.
2. Embaralhar deterministicamente com `random.Random(SEED_MESTRA).shuffle(lista)`.
3. Dividir em `N_RODADAS × N_REPLICACOES` pares consecutivos: `par[j] = (lista[2j], lista[2j+1])`.
4. A rodada `r` usa os pares de índice `(r-1) × N_REPLICACOES` até `r × N_REPLICACOES - 1`.
5. Dentro de cada rodada, o par de índice `i` define: `seed_TEC = lista[2j]`, `seed_TS = lista[2j+1]`.

A tabela é gerada **uma única vez** por `gerar_seeds.py`, persistida em `seeds.json` e reutilizada de forma idêntica em todos os cenários.

---

## 7. Métricas por replicação

Calcular sobre o conjunto de clientes de cada replicação:

a) Tempo médio de espera na fila
b) Tempo médio de serviço
c) Tempo médio no sistema (fila + serviço)
d) Tempo médio ocioso por servidor

---

## 8. Estatísticas agregadas

Para cada par (rodada, cenário) e para cada métrica da seção 7, calcular sobre as `N_REPLICACOES = 200` replicações:

- **Média das médias:**
  `x̄ = (1/n) × Σ xi`

- **Desvio padrão amostral entre replicações:**
  `s = sqrt( (1/(n-1)) × Σ (xi - x̄)² )`

- **Intervalo de confiança 95%:**
  `x̄ ± 1,96 × s / sqrt(n)`

Implementado em `calcular_estatisticas_agregadas(valores)` em `etapa2_mms.py`.

---

## 9. Gráficos

Dois tipos de gráfico são gerados automaticamente ao final da execução:

### Convergência por rodada (`results/rodada_X/convergencia.png`)
- 4 subgráficos, um por métrica.
- Cada subgráfico mostra a **média acumulada** das primeiras `k` replicações (k = 1..200) para cada cenário s ∈ {1, 2, 3, 4}.
- Permite verificar visualmente se 200 replicações são suficientes para estabilizar as estimativas.

### Comparação global entre cenários (`results/comparacao_cenarios.png`)
- 4 subgráficos, um por métrica.
- Gráfico de barras com **error bars do IC 95%**, comparando os 4 cenários lado a lado.
- Agrega todas as rodadas em pool (`N_RODADAS × N_REPLICACOES` valores por cenário).

---

## 10. Requisitos técnicos

- **Linguagem:** Python 3.10+
- **Bibliotecas:** `math`, `os`, `sys`, `json`, `random` (padrão) + `matplotlib` (gráficos).
- Funções principais em `etapa2_mms.py`:
  - `gerar_tec(gerador_tec)` / `gerar_ts(gerador_ts)`
  - `simular_mms(tempo_simulacao, NUM_CAIXAS, semente_tec, semente_ts)`
  - `calcular_metricas(dados, NUM_CAIXAS)`
  - `calcular_estatisticas_agregadas(valores)`
- Funções em `gerar_seeds.py`:
  - `gerar_tabela_sementes(n_rodadas, n_replicacoes, seed_mestra)`
  - `validar_unicidade(pares)`

---

## 11. Estrutura de arquivos

```
manual_simulator/
├── requisitos.md
├── README.md
├── etapa1_manual.py          # Validação manual — não entra no relatório
├── etapa2_mms.py             # Simulador principal M/M/s
├── gerar_seeds.py            # Gerador da tabela de sementes
├── seeds.json                # 200 pares × N_RODADAS — não regenerar após gerado
└── results/
    ├── comparacao_cenarios.png
    ├── rodada_1/
    │   ├── convergencia.png
    │   ├── resultados_caixas_1.txt
    │   ├── resultados_caixas_2.txt
    │   ├── resultados_caixas_3.txt
    │   └── resultados_caixas_4.txt
    ├── rodada_2/
    │   └── ...
    └── rodada_N/
        └── ...
```

```
Modelagem/
└── random_number_generator/
    └── gerador_aleatorio.py  # Gerador LCG parametrizado por semente
```

| Arquivo | Descrição |
|---|---|
| `etapa1_manual.py` | Simulação manual de 5 clientes com TEC/TS fixos — validação inicial da lógica. |
| `etapa2_mms.py` | Simulador M/M/s completo. Roda todos os cenários e rodadas, gera arquivos de resultado e gráficos. |
| `gerar_seeds.py` | Gera `seeds.json` via algoritmo determinístico. Executar uma única vez. |
| `seeds.json` | Tabela de pares de sementes — fonte única de aleatoriedade de todo o experimento. |
| `results/rodada_X/resultados_caixas_S.txt` | Tabela de clientes + métricas por replicação + estatísticas agregadas (média, desvio padrão, IC 95%) para o cenário `s=S` na rodada `X`. |
| `results/rodada_X/convergencia.png` | Evolução da média acumulada por métrica e cenário para a rodada `X`. |
| `results/comparacao_cenarios.png` | Comparação global entre os 4 cenários com IC 95%. |

---

## 12. Passo a passo de execução

```bash
# 1. Gerar as sementes (uma única vez)
python gerar_seeds.py

# 2. Rodar todas as rodadas e cenários
python etapa2_mms.py
```

O script `etapa2_mms.py` executa automaticamente:
- `N_RODADAS` rodadas (definidas pela tabela `seeds.json`)
- 4 cenários por rodada (`NUM_CAIXAS` ∈ {1, 2, 3, 4})
- `N_REPLICACOES` replicações por cenário
- Gera os arquivos `.txt` e os gráficos `.png` em `results/`

---

## 13. Fora do escopo

- Interface gráfica interativa.
- Distribuições diferentes da exponencial.
- Múltiplas rodadas de replicações além das `N_RODADAS` definidas em `seeds.json`.
- Animação ou visualização gráfica da fila em tempo real.
- Etapa separada de M/M/1: o caso `NUM_CAIXAS = 1` do simulador M/M/s já cobre esse cenário.
