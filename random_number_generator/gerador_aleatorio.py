"""
Gerador de Números Pseudoaleatórios
Parâmetros: x(n) = 16807 * x(n-1) mod(2^31 - 1)
"""

class GeradorAleatorio:    
    def __init__(self, semente):
        self.a = 16807
        self.m = 2**31 - 1
        self.x_atual = semente
        self.contador = 0
    
    def proximo(self):
        self.x_atual = (self.a * self.x_atual) % self.m
        self.contador += 1
        numero_aleatorio = self.x_atual / self.m
        return self.x_atual, numero_aleatorio
    
    def gerar_sequencia(self, quantidade, desconsiderar_primeiros=0):
        # Descarta os primeiros números (tendenciosos)
        for _ in range(desconsiderar_primeiros):
            self.proximo()
        
        sequencia = []
        for _ in range(quantidade):
            x_i, aleatorio = self.proximo()
            sequencia.append((x_i, aleatorio))
        
        return sequencia


def exibir_resultados(semente, quantidade=10):
    gerador = GeradorAleatorio(semente)
    sequencia = gerador.gerar_sequencia(quantidade, desconsiderar_primeiros=0)
    
    print(f"\n{'='*70}")
    print(f"Gerador de Números Pseudoaleatórios (LCG)")
    print(f"{'='*70}")
    print(f"Semente: {semente}")
    print(f"Parâmetros: a = 16807, m = 2^31 - 1 = 2.147.483.647")
    print(f"{'='*70}\n")
    
    print(f"{'i':<5} {'x(i)':<15} {'x(i)/m':<20} {'Notação Científica':<20}")
    print(f"{'-'*70}")
    
    # Exibir semente (i=0)
    numero_aleatorio_semente = semente / gerador.m
    print(f"{'0':<5} {semente:<15} {numero_aleatorio_semente:<20.10f} {numero_aleatorio_semente:.3e}")
    
    # Exibir números gerados (i=1, 2, 3, ...)
    for i, (x_i, aleatorio) in enumerate(sequencia, 1):
        print(f"{i:<5} {x_i:<15} {aleatorio:<20.10f} {aleatorio:.3e}")
    
    print(f"\n{'='*70}")
    print("   IMPORTANTE: Os DOIS primeiros números (i=0 e i=1)")
    print("   devem ser desconsiderados porque são tendenciosos.")
    print("   Use apenas a partir de i=2 em diante para simulações.")
    print(f"{'='*70}\n")
