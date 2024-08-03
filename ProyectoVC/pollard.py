import math
import random
import time

# Maximo comun divisor; si b ! a 0, intercambia entre a y b valores
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# Descartas multiplos de 2 y 3, verifica si es divisible hasta llegar a
# la raiz cuadrada
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
    #X, Y, puntos de inicio y C constante
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

    print(f"Los factores de {n} son: {factors}")
    print(f"Tiempo de factorización: {end_time - start_time} segundos")

if __name__ == "__main__":
    main()
