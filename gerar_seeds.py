"""
Gerador de pares de seeds (seed_TEC, seed_TS).
O resultado é armazenado em seeds.json, onde:
    - É uma lista ordenada
    - Nenhum valor se repete entre todas as rodadas e replicações
    - A lista é embaralhada com SEED_MESTRA (Opção B — tabela única extendida)
"""

import json
import random
import os

SEED_MESTRA    = 2026
N_RODADAS      = 5
N_REPLICACOES  = 200
OUTPUT_PATH    = os.path.join(os.path.dirname(__file__), "seeds.json")


def gerar_tabela_sementes(
    n_rodadas: int     = N_RODADAS,
    n_replicacoes: int = N_REPLICACOES,
    seed_mestra: int   = SEED_MESTRA,
) -> list[dict]:
    """
    Gera n_rodadas × n_replicacoes pares (seed_tec, seed_ts) sem repetição global.

    Algoritmo (Opção B):
      1. Lista [1 .. 2 × n_rodadas × n_replicacoes]
      2. Embaralha deterministicamente com seed_mestra
      3. Divide em pares consecutivos; a rodada r usa os pares [(r-1)×n_replicacoes .. r×n_replicacoes - 1]
    """
    total_pares = n_rodadas * n_replicacoes
    lista = list(range(1, 2 * total_pares + 1))
    random.Random(seed_mestra).shuffle(lista)

    pares = []
    for r in range(n_rodadas):
        for i in range(n_replicacoes):
            idx = r * n_replicacoes + i
            pares.append({
                "rodada":     r + 1,
                "replicacao": i + 1,
                "seed_tec":   lista[2 * idx],
                "seed_ts":    lista[2 * idx + 1],
            })
    return pares


def validar_unicidade(pares: list[dict]) -> None:
    todos = [p["seed_tec"] for p in pares] + [p["seed_ts"] for p in pares]
    assert len(todos) == len(set(todos)), "Existem sementes duplicadas!"


if __name__ == "__main__":
    if os.path.exists(OUTPUT_PATH):
        print(f"AVISO: arquivo de seeds já existe, apague antes de regerar.")
    else:
        pares = gerar_tabela_sementes()
        validar_unicidade(pares)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(pares, f, indent=2, ensure_ascii=False)
        total = len(pares)
        print(f"seeds.json gerado: {N_RODADAS} rodadas × {N_REPLICACOES} replicações = {total} pares")
        print(f"Seed mestra: {SEED_MESTRA} | Seeds únicos: {2 * total}")
        print("Primeiros 3 pares:")
        for p in pares[:3]:
            print(f"  rodada={p['rodada']}  replicacao={p['replicacao']}  seed_tec={p['seed_tec']}  seed_ts={p['seed_ts']}")
