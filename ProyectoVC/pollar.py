import math

N = int(input('Ingrese un numero entero: '))
# pow = potencia
z = 2
i = 1
x_anterior = z - 1  # Inicializamos x_anterior para la primera iteración

while i < 4: 
    x = pow(z, 2) - 1
    if x > N:
        x = x % N
    print(f'Iteración {i}: x = {x}')
    
    y = pow(x, 2) - 1
    if y > N:
        y = y % N
    print(f'Iteración {i}: y = {y}')
    print(f'{y} - {x_anterior}, {N}')

    max_divisor = math.gcd(y - x_anterior, N)
    print(f'Iteración {i}: max_divisor = {max_divisor}')

    x_anterior = x  # Guardamos el valor actual de x para la próxima iteración
    z = y
    i = i + 1

# Imprimir los resultados finales
print(f'Resultado final: y = {y}, x = {x}, max_divisor = {max_divisor}')

