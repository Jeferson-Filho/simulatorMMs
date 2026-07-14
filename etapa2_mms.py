"""
Simulação de fila M/M/s
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from random_number_generator.gerador_aleatorio import GeradorAleatorio

# parâmetros
TEMPO_SIMULACAO = 200


# Geradores TEC e TS
def gerar_tec(gerador_tec: GeradorAleatorio) -> float:
    """TEC = -ln(u) / (1/2)  →  média 2"""
    _, u = gerador_tec.proximo()
    return -math.log(u) / (1 / 2)


def gerar_ts(gerador_ts: GeradorAleatorio) -> float:
    """TS = -ln(u) / (1/8)  →  média 8"""
    _, u = gerador_ts.proximo()
    return -math.log(u) / (1 / 8)


# Simulação M/M/s
def simular_mms(tempo_simulacao: float, NUM_CAIXAS: int, semente_tec: int, semente_ts: int) -> list[dict]:
    """Simula fila M/M/s até tempo_simulacao."""
    gerador_tec = GeradorAleatorio(semente_tec)
    gerador_ts  = GeradorAleatorio(semente_ts)

    fim_caixas       = [0.0] * NUM_CAIXAS
    resultados       = []
    chegada_anterior = 0.0
    cliente_id       = 0

    while True:
        tec     = gerar_tec(gerador_tec)
        chegada = chegada_anterior + tec

        if chegada > tempo_simulacao:
            break

        cliente_id += 1
        ts = gerar_ts(gerador_ts)

        caixa_idx      = fim_caixas.index(min(fim_caixas))
        fim_anterior   = fim_caixas[caixa_idx]
        inicio_servico = max(chegada, fim_anterior)
        fim_servico    = inicio_servico + ts
        tempo_fila     = inicio_servico - chegada
        tempo_sistema  = tempo_fila + ts
        tempo_ocioso   = max(0.0, chegada - fim_anterior)

        fim_caixas[caixa_idx] = fim_servico
        chegada_anterior      = chegada

        resultados.append({
            "cliente":        cliente_id,
            "caixa":          caixa_idx + 1,
            "tec":            tec,
            "ts":             ts,
            "chegada":        chegada,
            "inicio_servico": inicio_servico,
            "fim_servico":    fim_servico,
            "tempo_fila":     tempo_fila,
            "tempo_sistema":  tempo_sistema,
            "tempo_ocioso":   tempo_ocioso,
        })

    return resultados


# Métricas por replicação
def calcular_metricas(dados: list[dict], NUM_CAIXAS: int) -> dict:
    n = len(dados)
    if n == 0:
        return {}

    ocioso_por_caixa: dict[int, float] = {}
    for r in dados:
        s = r["caixa"]
        ocioso_por_caixa[s] = ocioso_por_caixa.get(s, 0.0) + r["tempo_ocioso"]

    return {
        "n_clientes":         n,
        "media_fila":         sum(r["tempo_fila"]    for r in dados) / n,
        "media_ts":           sum(r["ts"]            for r in dados) / n,
        "media_sistema":      sum(r["tempo_sistema"] for r in dados) / n,
        "media_ocioso_total": sum(r["tempo_ocioso"]  for r in dados) / n,
        "ocioso_por_caixa":   [ocioso_por_caixa.get(s + 1, 0.0) for s in range(NUM_CAIXAS)],
    }


# Estatísticas agregadas
def calcular_estatisticas_agregadas(valores: list[float]) -> dict:
    """
    Recebe os valores de uma métrica por replicação e calcula
      - Média das médias
      - Desvio padrão amostral
      - IC 95%
    """
    n = len(valores)
    media = sum(valores) / n
    desvio = math.sqrt(sum((x - media) ** 2 for x in valores) / (n - 1))
    margem = 1.96 * desvio / math.sqrt(n)
    return {
        "n":           n,
        "media":       media,
        "desvio":      desvio,
        "ic_inferior": media - margem,
        "ic_superior": media + margem,
        "margem":      margem,
    }


# Impressão auxiliar
def imprimir_metricas(m: dict, file=None):
    print(f"  Clientes simulados:       {m['n_clientes']}", file=file)
    print(f"  Tempo médio na fila:      {m['media_fila']:.4f}", file=file)
    print(f"  Tempo médio de serviço:   {m['media_ts']:.4f}", file=file)
    print(f"  Tempo médio no sistema:   {m['media_sistema']:.4f}", file=file)
    print(f"  Tempo médio ocioso:       {m['media_ocioso_total']:.4f}", file=file)
    for i, v in enumerate(m["ocioso_por_caixa"]):
        print(f"    caixa {i + 1} — ocioso acum.: {v:.4f}", file=file)


def imprimir_tabela(dados: list[dict], max_linhas: int = 20, file=None):
    cabecalho = ["Cliente", "Caixa", "TEC", "TS", "Chegada", "Início Serv.", "Fim Serv.", "T. Fila", "T. Sistema", "T. Ocioso"]
    larguras  = [8, 9, 8, 8, 10, 13, 11, 9, 12, 11]

    def linha(vals):
        return " | ".join(str(v).center(larguras[i]) for i, v in enumerate(vals))

    sep = "-+-".join("-" * w for w in larguras)
    print(linha(cabecalho), file=file)
    print(sep, file=file)

    for r in dados[:max_linhas]:
        vals = [
            r["cliente"], r["caixa"],
            f"{r['tec']:.4f}", f"{r['ts']:.4f}",
            f"{r['chegada']:.4f}", f"{r['inicio_servico']:.4f}",
            f"{r['fim_servico']:.4f}", f"{r['tempo_fila']:.4f}",
            f"{r['tempo_sistema']:.4f}", f"{r['tempo_ocioso']:.4f}",
        ]
        print(linha(vals), file=file)

    if len(dados) > max_linhas:
        print(f"  ... ({len(dados) - max_linhas} linhas omitidas)", file=file)


# Main
if __name__ == "__main__":
    import json
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # parâmetros
    CENARIOS      = [1, 2, 3, 4]
    CHAVES        = ["media_fila", "media_ts", "media_sistema", "media_ocioso_total"]
    LABELS_METR   = ["Tempo médio na fila", "Tempo médio de serviço", "Tempo médio no sistema", "Tempo médio ocioso"]
    CORES_CENARIO = {1: "#1f77b4", 2: "#ff7f0e", 3: "#2ca02c", 4: "#d62728"}

    # Carrega tabela de seeds
    seeds_path = os.path.join(os.path.dirname(__file__), "seeds.json")
    with open(seeds_path, encoding="utf-8") as fj:
        tabela_seeds = json.load(fj)

    seeds_por_rodada: dict[int, list] = {}
    for entrada in tabela_seeds:
        seeds_por_rodada.setdefault(entrada["rodada"], []).append(entrada)

    n_rodadas     = len(seeds_por_rodada)
    n_replicacoes = len(next(iter(seeds_por_rodada.values())))

    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    print(f"\n=== M/M/s | T={TEMPO_SIMULACAO} | {n_rodadas} rodadas × {n_replicacoes} replicações | s={CENARIOS} ===\n")

    todos_resultados: dict[int, dict[int, list[dict]]] = {}

    # rodadas --> cenários --> replicações
    for rodada, seeds_rodada in seeds_por_rodada.items():
        rodada_dir = os.path.join(results_dir, f"rodada_{rodada}")
        os.makedirs(rodada_dir, exist_ok=True)
        todos_resultados[rodada] = {}

        print(f"\n{'='*70}")
        print(f"  RODADA {rodada}/{n_rodadas}")
        print(f"{'='*70}")

        for num_caixas in CENARIOS:
            arquivo = os.path.join(rodada_dir, f"resultados_caixas_{num_caixas}.txt")
            metricas_rep: list[dict] = []

            with open(arquivo, "w", encoding="utf-8") as arq:
                arq.write(f"=== Rodada {rodada} | s={num_caixas} | T={TEMPO_SIMULACAO} | {n_replicacoes} repl. ===\n\n")

                for entrada in seeds_rodada:
                    rep      = entrada["replicacao"]
                    seed_tec = entrada["seed_tec"]
                    seed_ts  = entrada["seed_ts"]

                    dados = simular_mms(TEMPO_SIMULACAO, num_caixas, seed_tec, seed_ts)
                    m     = calcular_metricas(dados, num_caixas)
                    metricas_rep.append(m)

                    arq.write(f"-- Rep {rep} (seed_tec={seed_tec}, seed_ts={seed_ts}) --\n")
                    imprimir_tabela(dados, max_linhas=len(dados), file=arq)
                    arq.write("\n")
                    imprimir_metricas(m, file=arq)
                    arq.write("\n")

                # Resumo por cenário no arquivo
                arq.write(f"--- Estatísticas agregadas (rodada={rodada}, s={num_caixas}) ---\n")
                for chave, label in zip(CHAVES, LABELS_METR):
                    vals  = [mr[chave] for mr in metricas_rep]
                    estat = calcular_estatisticas_agregadas(vals)
                    arq.write(f"  {label}\n")
                    arq.write(f"    Média:       {estat['media']:.4f}\n")
                    arq.write(f"    Desvio pad.: {estat['desvio']:.4f}\n")
                    arq.write(f"    IC 95%%:      [{estat['ic_inferior']:.4f}, {estat['ic_superior']:.4f}]\n")

            todos_resultados[rodada][num_caixas] = metricas_rep
            print(f"  -> s={num_caixas} concluído  ({arquivo})")

        # Grafico de convergência da rodada
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f"Convergência da média acumulada — Rodada {rodada}", fontsize=13)

        for ax, chave, label in zip(axes.flat, CHAVES, LABELS_METR):
            for s in CENARIOS:
                vals = [mr[chave] for mr in todos_resultados[rodada][s]]
                medias_acum = [sum(vals[:k]) / k for k in range(1, n_replicacoes + 1)]
                ax.plot(range(1, n_replicacoes + 1), medias_acum, label=f"s={s}", color=CORES_CENARIO[s], linewidth=1.2)
            ax.set_title(label, fontsize=10)
            ax.set_xlabel("Replicações (k)", fontsize=9)
            ax.set_ylabel("Média acumulada", fontsize=9)
            ax.legend(fontsize=8)
            ax.grid(True, linestyle="--", alpha=0.5)

        plt.tight_layout()
        grafico_rodada = os.path.join(rodada_dir, "convergencia.png")
        fig.savefig(grafico_rodada, dpi=120)
        plt.close(fig)
        print(f"  -> Gráfico de convergência: {grafico_rodada}")

    # Grafico de convergência por cenário
    CORES_RODADA = plt.get_cmap("tab10").colors

    for s in CENARIOS:
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f"Convergência da média acumulada — s={s} (todas as rodadas)", fontsize=13)

        for ax, chave, label in zip(axes.flat, CHAVES, LABELS_METR):
            for i, rodada in enumerate(todos_resultados):
                vals = [mr[chave] for mr in todos_resultados[rodada][s]]
                medias_acum = [sum(vals[:k]) / k for k in range(1, n_replicacoes + 1)]
                ax.plot(range(1, n_replicacoes + 1), medias_acum, label=f"rodada {rodada}", color=CORES_RODADA[i % len(CORES_RODADA)], linewidth=1.2)
            ax.set_title(label, fontsize=10)
            ax.set_xlabel("Replicações (k)", fontsize=9)
            ax.set_ylabel("Média acumulada", fontsize=9)
            ax.legend(fontsize=8)
            ax.grid(True, linestyle="--", alpha=0.5)

        plt.tight_layout()
        grafico_cenario = os.path.join(results_dir, f"convergencia_s{s}.png")
        fig.savefig(grafico_cenario, dpi=120)
        plt.close(fig)
        print(f"-> Gráfico de convergência (s={s}): {grafico_cenario}")

    # Grafico de comparação entre cenários
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(
        f"Comparação entre cenários — {n_rodadas} rodadas * {n_replicacoes} replicações",
        fontsize=13
    )

    x_pos  = list(range(len(CENARIOS)))
    width  = 0.55

    for ax, chave, label in zip(axes.flat, CHAVES, LABELS_METR):
        medias, margens = [], []
        for s in CENARIOS:
            vals_global = [
                mr[chave]
                for r in todos_resultados.values()
                for mr in r[s]
            ]
            estat = calcular_estatisticas_agregadas(vals_global)
            medias.append(estat["media"])
            margens.append(estat["margem"])

        bars = ax.bar(x_pos, medias, width, color=[CORES_CENARIO[s] for s in CENARIOS], alpha=0.85, zorder=2)
        ax.errorbar(x_pos, medias, yerr=margens, fmt="none", color="black", capsize=5, linewidth=1.5, zorder=3)

        ax.set_title(label, fontsize=10)
        ax.set_xticks(x_pos)
        ax.set_xticklabels([f"s={s}" for s in CENARIOS])
        ax.set_ylabel("Média (IC 95%)", fontsize=9)
        ax.grid(True, axis="y", linestyle="--", alpha=0.5)

        for bar, m, mg in zip(bars, medias, margens):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + mg + 0.2, f"{m:.2f}", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    grafico_global = os.path.join(results_dir, "comparacao_cenarios.png")
    fig.savefig(grafico_global, dpi=120)
    plt.close(fig)
    print(f"\n-> Gráfico global: {grafico_global}")
    print("\nConcluído.")
