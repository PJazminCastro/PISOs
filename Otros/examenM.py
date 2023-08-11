def euler_modificado(f, y0, t0, t_final, h):
    t = t0
    y = y0
    while t < t_final:
        y_pred = y + h * f(t, y)
        y = y + h * (f(t, y) + f(t + h, y_pred)) / 2
        t += h
    return y

def runge_kutta(f, y0, t0, t_final, h):
    t = t0
    y = y0
    while t < t_final:
        k1 = h * f(t, y)
        k2 = h * f(t + h/2, y + k1/2)
        k3 = h * f(t + h/2, y + k2/2)
        k4 = h * f(t + h, y + k3)
        
        y = y + (k1 + 2*k2 + 2*k3 + k4) / 6
        t += h
    return y

def main():
    # Solicitar al usuario que elija el método
    metodo = input("Elige el método (Euler Modificado / Runge-Kutta): ").lower()

    if metodo != "euler modificado" and metodo != "runge-kutta":
        print("Método no válido. Por favor, elige 'Euler Modificado' o 'Runge-Kutta'.")
        return

    # Solicitar al usuario que ingrese la ecuación diferencial
    ecuacion = input("Ingresa la ecuación diferencial en términos de 't' y 'y': ")
    exec(f"def f(t, y): return {ecuacion}")

    # Solicitar otros valores
    y0 = float(input("Ingresa el valor inicial de y: "))
    t0 = float(input("Ingresa el tiempo inicial: "))
    t_final = float(input("Ingresa el tiempo final: "))
    h = float(input("Ingresa el valor de h (paso): "))

    # Resolver la ecuación según el método seleccionado
    if metodo == "euler modificado":
        resultado = euler_modificado(f, y0, t0, t_final, h)
    else:
        resultado = runge_kutta(f, y0, t0, t_final, h)

    print("Resultado:", resultado)

if __name__ == "__main__":
    main()
