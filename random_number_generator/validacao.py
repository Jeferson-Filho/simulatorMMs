"""
Executa apenas a validação do gerador com semente = 10
"""

from gerador_aleatorio import GeradorAleatorio

print("\n" + "="*70)
print("VALIDAÇÃO COM EXEMPLO (Semente = 10)")
print("="*70)

gerador = GeradorAleatorio(10)

print("\nSequência completa (incluindo os 2 primeiros a descartar):")
print(f"{'i':<5} {'x(i)':<15} {'x(i)/m':<20} {'Notação Científica':<20}")
print("-" * 70)

valores_esperados = [
    (10, 4.657e-9),
    (168070, 7.826e-5),
    (677268843, 0.3154),
    (1194115201, 0.5561),
    (1259501992, 0.5865),
    (703671065, 0.3277),
    (407145426, 0.1896),
    (1010275440, 0.4704),
    (1693606898, 0.7886),
    (1702877348, 0.3469),
]

# Verificar primeiro valor (semente)
print(f"{'0':<5} {10:<15} {10/gerador.m:<20.10e} {10/gerador.m:.3e}")

# Gerar próximos valores
for i in range(1, len(valores_esperados) + 1):
    x_i, aleatorio = gerador.proximo()
    print(f"{i:<5} {x_i:<15} {aleatorio:<20.10f} {aleatorio:.3e}")

print("\n" + "="*70)
