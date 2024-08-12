import math
import random
import time

# Máximo común divisor
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# Verifica si un número es primo
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

def pollards_rho(n):
    if n % 2 == 0:
        return 2
    x = random.randint(2, n - 1)
    y = x
    c = random.randint(1, n - 1)
    d = 1
    
    f = lambda x: (x * x + c) % n
    
    while d == 1:
        x = f(x)
        y = f(f(y))
        d = gcd(abs(x - y), n)
        
        if d == n:
            return pollards_rho(n)
    
    return d

def factorize(n):
    if n <= 1:
        return []
    if is_prime(n):
        return [n]
    
    factor = pollards_rho(n)
    return factorize(factor) + factorize(n // factor)

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
