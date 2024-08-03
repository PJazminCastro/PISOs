import math
from math import sqrt

def fermats_factorization(n):
    if n % 2 == 0:
        return n // 2, 2  # Para números pares, el factor más grande es n // 2

    k = math.ceil(math.sqrt(n))  # Ceil para  que k sea mayor o igual a la raíz cuadrada de n
    y = (k * k) - n
    d = 1

    while True:
        if y < 0:
            # Si y es negativo, no podemos continuar
            return None

        y_floor = math.floor(math.sqrt(y))
        y_sqrt = math.sqrt(y)

        if y_floor == y_sqrt:  # Si y es un cuadrado perfecto
            x = int(math.sqrt(n + y))
            y = int(y_sqrt)
            return x - y, x + y

        # Actualizar y y d para el próximo ciclo
        y += (2 * k) + d
        d += 2

        # Verificación de límite
        if y_floor >= n / 2:
            print("No se encontraron factores.")
            return None

n = int(input("Ingrese el número impar a factorizar: "))
if n <= 1:
    print("El número debe ser mayor que 1.")
else:
    result = fermats_factorization(n)
    if result:
        print(f"Los factores de {n} son: {result[0]} y {result[1]}")

        #Volver a factorizar los valores hasta que den primos