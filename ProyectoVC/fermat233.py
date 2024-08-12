import math
import time

def fermats_factorization(n):
    if n % 2 == 0:
        return n // 2, 2  # Para números pares, el factor más grande es n // 2

    k = math.ceil(math.sqrt(n))  # Ceil para que k sea mayor o igual a la raíz cuadrada de n
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

def factorize(n):
    factors = []
    stack = [n]
    while stack:
        current = stack.pop()
        if current <= 1:
            continue
        if is_prime(current):
            factors.append(current)
        else:
            factor1, factor2 = fermats_factorization(current)
            stack.append(factor1)
            stack.append(factor2)
    return sorted(factors)

def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def main():
    n = int(input("Ingrese el número a factorizar: "))
    if n <= 1:
        print("El número debe ser mayor que 1.")
        return
    
    start_time = time.time()
    factors = factorize(n)
    end_time = time.time()

    # Calcular tiempo en milisegundos
    elapsed_time_ms = (end_time - start_time) * 1000

    print(f"Los factores de {n} son: {factors}")
    print(f"Tiempo de factorización: {elapsed_time_ms:.2f} ms")

if __name__ == "__main__":
    main()
