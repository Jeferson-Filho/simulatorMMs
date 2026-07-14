"""
Main - Gerador de Números Pseudoaleatórios
Módulo principal com interface modularizada
"""

import sys
from gerador_aleatorio import GeradorAleatorio, exibir_resultados


def validar_entrada(semente, quantidade):
    """
    Valida os parâmetros de entrada.
    
    Args:
        semente: Valor da semente
        quantidade: Quantidade de números a gerar
    
    Returns:
        Tupla (semente_válida, quantidade_válida) ou (None, None) se inválido
    """
    try:
        semente_int = int(semente)
        quantidade_int = int(quantidade)
        
        if semente_int <= 0:
            print("Erro: Semente deve ser um número positivo!")
            return None, None
        
        if quantidade_int <= 0:
            print("Erro: Quantidade deve ser um número positivo!")
            return None, None
        
        return semente_int, quantidade_int
    
    except ValueError:
        print("Erro: Argumentos devem ser números inteiros!")
        return None, None


def gerar_numeros(semente, quantidade=10):
    """
    Gera números pseudoaleatórios para uma determinada semente.
    Descarta automaticamente os 2 primeiros números (tendenciosos).
    
    Args:
        semente: Valor da semente
        quantidade: Quantidade de números a gerar (após descartar os 2 primeiros)
    
    Returns:
        Lista de tuplas (x(i), número_pseudoaleatório)
    """
    gerador = GeradorAleatorio(semente)
    return gerador.gerar_sequencia(quantidade, desconsiderar_primeiros=2)


def salvar_resultados(semente, quantidade, caminho_arquivo):
    """
    Salva os resultados em um arquivo CSV.
    
    Args:
        semente: Valor da semente
        quantidade: Quantidade de números
        caminho_arquivo: Caminho do arquivo de saída
    """
    try:
        sequencia = gerar_numeros(semente, quantidade)
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write("iteracao,x(i),numero_aleatorio\n")
            for i, (x_i, aleatorio) in enumerate(sequencia, 1):
                f.write(f"{i},{x_i},{aleatorio:.10f}\n")
        
        print(f"\n✓ Resultados salvos em: {caminho_arquivo}")
    
    except IOError as e:
        print(f"Erro ao salvar arquivo: {e}")


def exibir_uso():
    """Exibe informações de uso do programa."""
    print("\n" + "="*70)
    print("GERADOR DE NÚMEROS PSEUDOALEATÓRIOS")
    print("="*70)
    print("\nUso: python main.py <comando> [argumentos]")
    print("\nComandos disponíveis:")
    print("  gerar <semente> [quantidade]    - Gera e exibe números")
    print("  salvar <semente> <quantidade> <arquivo>  - Salva em CSV")
    print("  comparar <seed1> <seed2> [quantidade]    - Compara dois seeds")
    print("  help                              - Exibe esta mensagem")
    print("\nExemplos:")
    print("  python main.py gerar 10")
    print("  python main.py gerar 10 5")
    print("  python main.py salvar 10 100 resultado.csv")
    print("  python main.py comparar 10 12345 5")
    print("="*70 + "\n")


def comparar_seeds(semente1, semente2, quantidade=5):
    """
    Compara as sequências de dois seeds diferentes.
    
    Args:
        semente1: Primeira semente
        semente2: Segunda semente
        quantidade: Quantidade de números a gerar
    """
    seq1 = gerar_numeros(semente1, quantidade)
    seq2 = gerar_numeros(semente2, quantidade)
    
    print("\n" + "="*70)
    print("COMPARAÇÃO DE SEEDS")
    print("="*70)
    
    print(f"\n{'Iteração':<12} {'Seed {}':<20} {'Seed {}':<20}".format(semente1, semente2))
    print("-"*70)
    
    for i, ((x1, ale1), (x2, ale2)) in enumerate(zip(seq1, seq2), 1):
        print(f"{i:<12} {ale1:<20.10f} {ale2:<20.10f}")
    
    print("\n" + "="*70 + "\n")


def executar(argumentos):
    """
    Executa o programa baseado nos argumentos fornecidos.
    
    Args:
        argumentos: Lista de argumentos do comando
    """
    if not argumentos or argumentos[0] == "help":
        exibir_uso()
        return
    
    comando = argumentos[0]
    
    if comando == "gerar":
        if len(argumentos) < 2:
            print("Erro: Comando 'gerar' requer semente")
            exibir_uso()
            return
        
        semente = argumentos[1]
        quantidade = argumentos[2] if len(argumentos) > 2 else "10"
        
        semente, quantidade = validar_entrada(semente, quantidade)
        if semente is None:
            return
        
        exibir_resultados(semente=semente, quantidade=quantidade)
    
    elif comando == "salvar":
        if len(argumentos) < 4:
            print("Erro: Comando 'salvar' requer semente, quantidade e arquivo")
            exibir_uso()
            return
        
        semente = argumentos[1]
        quantidade = argumentos[2]
        arquivo = argumentos[3]
        
        semente, quantidade = validar_entrada(semente, quantidade)
        if semente is None:
            return
        
        salvar_resultados(semente, quantidade, arquivo)
    
    elif comando == "comparar":
        if len(argumentos) < 3:
            print("Erro: Comando 'comparar' requer duas sementes")
            exibir_uso()
            return
        
        semente1 = argumentos[1]
        semente2 = argumentos[2]
        quantidade = argumentos[3] if len(argumentos) > 3 else "5"
        
        semente1, _ = validar_entrada(semente1, "10")
        semente2, quantidade = validar_entrada(semente2, quantidade)
        
        if semente1 is None or semente2 is None:
            return
        
        comparar_seeds(semente1, semente2, quantidade)
    
    else:
        print(f"Erro: Comando desconhecido '{comando}'")
        exibir_uso()


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    executar(argumentos)
