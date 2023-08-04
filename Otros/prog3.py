numero = float(input('Ingresa un numero mayor o igual a 0: '))
while numero < 0:
    print('El número debe ser mayor o igual a cero')
    numero = float(input('Ingresa un numero mayor o igual a 0: '))
print('El número intoducido es: '+str(numero))