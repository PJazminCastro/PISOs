import math

#función para calcular x=(x^2 - 1)%N
def calculate_x(x, N):
    x = (pow(x, 2) - 1) % N
    return x

#función para calcular el MCD de dos números
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def pollards_p_method(N):
    z = 2
    i = 0
    x_anterior = calculate_x(2, N)  #se inicia x_anterior para la primera iteración

    #arreglos en donde se guardan los valores de x y y
    x_values = []
    y_values = []

    while True:  #el ciclo se detendrá cuando encontremos un divisor no trivial / primo
        x = calculate_x(z, N)
        x_values.append(x)  #se guarda x en la lista
        print(f'Iteración {i}: x = {x}') 
        
        #condicional que guarda unicamente aquellos valores de x cuando sean par
        y = x_values[2 + (i - 1)] if 2 + (i - 1) < len(x_values) else calculate_x(x, N)
        y_values.append(y)  #se guarda 'y' en la lista
        print(f'Iteración {i}: y = {y}')
        print(f'MCD = {y} - {x_anterior}, {N}')

        max_divisor = gcd(abs(y - x_anterior), N)
        print(f'Iteración {i}: max_divisor = {max_divisor}')

        if 1 < max_divisor < N:
            print(f'Factor no trivial encontrado: {max_divisor}')
            break

        #se guarda el valor actual de x para la próxima iteración
        x_anterior = x
        z = y
        i += 1
        #separacion entre cada ciclo ejecutado
        print(f' ')

    #imprime los valores de arreglos de 'x' y 'y'
    print(f'Valores de x: {x_values}')
    print(f'Valores de y: {y_values}')

    #imprime los resultados finales
    print(f'Resultado final: y = {y}, x = {x}, max_divisor = {max_divisor}')
    return max_divisor

#solicita un numero entero
N = int(input('Ingrese un número entero: '))
#llama nuestra funcion pollard para ejecutarla de acuerdo a N
factor = pollards_p_method(N)

#aun falta arreglar la asignación de y, ya que en (y2 aun no me toma el valor correspondiente)
