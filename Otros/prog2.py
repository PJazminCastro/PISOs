noVentas = int(input('Ingresa el número de ventas:'))
sum = 0
for i in range(noVentas):
    venta = float(str(input("Ingresa la venta:")))
    sum = sum + venta
    print("La suma total es de: "+str(sum))

