#
# Ejercicio 1: Sistema de Vehículos Inteligentes
# Autor: David Andrés Gómez Castillo
#
# Descripción:
# Simulación de un sistema de vehículos utilizando Programación Orientada a Objetos (POO),
# aplicando herencia, polimorfismo y sobrecarga de métodos.
#
# ==============================================================================

import tkinter as tk
from tkinter import ttk

# commit 
# ──────────────────────────────
# Clase base: Vehiculo
# ──────────────────────────────
class Vehiculo:
    """
    Representa un vehículo genérico

    Esta clase define atributos y comportamientos comunes para todos los tipos
    de vehículos dentro del sistema.
    """

    def __init__(self, marca, modelo):
        # Inicializa las propiedades básicas del vehículo
        self.marca = marca
        self.modelo = modelo
        self.velocidad_actual = 0  # Velocidad inicial 

    def acelerar(self, *args):
        """
        Incrementa la velocidad del vehículo.

        Soporta sobrecarga mediante argumentos variables:
        - Sin argumentos: aceleración base.
        - 1 argumento (bool): activa modo turbo.
        - 2 argumentos (bool, str): turbo + tipo de terreno.
        """
        incremento = 10
        mensaje = ""

        if len(args) == 0:
            self.velocidad_actual += incremento
            mensaje = f"{self.marca} {self.modelo} accelerates +{incremento} km/h"

        elif len(args) == 1:
            turbo = args[0]
            if turbo:
                incremento *= 2
            self.velocidad_actual += incremento
            mensaje = f"{self.marca} {self.modelo} uses turbo +{incremento} km/h"

        elif len(args) == 2:
            turbo, terreno = args

            if turbo:
                incremento *= 2

            # Ajuste dinámico según el entorno
            if terreno == "montaña":
                incremento -= 5
            elif terreno == "arena":
                incremento -= 7
            elif terreno == "ciudad":
                incremento += 2

            # Garantiza que no se apliquen incrementos negativos
            self.velocidad_actual += max(incremento, 0)
            mensaje = f"{self.marca} {self.modelo} on {terreno} +{incremento} km/h"

        return mensaje

    def detener(self):
        """
        Detiene completamente el vehículo.
        """
        self.velocidad_actual = 0
        return f"{self.marca} {self.modelo} stopped"

    def obtener_informacion(self):
        """
        Retorna el estado actual del vehículo en formato legible.
        """
        return f"{self.marca} {self.modelo} | Speed: {self.velocidad_actual} km/h"


# ──────────────────────────────
# Clase derivada: AutoElectrico
# ──────────────────────────────
class AutoElectrico(Vehiculo):
    """
    Representa un vehículo eléctrico.

    Extiende la clase Vehiculo incorporando el manejo de batería
    y redefiniendo el comportamiento de aceleración.
    """

    def __init__(self, marca, modelo, bateria):
        super().__init__(marca, modelo)
        self.bateria = bateria  # Nivel de batería (%)

    def acelerar(self, *args):
        """
        Sobrescribe el método acelerar para incluir consumo de batería
        y comportamiento adaptado a vehículos eléctricos.
        """
        if self.bateria <= 0:
            return f"{self.marca} {self.modelo} no battery"

        incremento = 8
#cambio prueba 
        if len(args) == 1 and args[0]:
            incremento *= 1.5
# elf 
        elif len(args) == 2:
            turbo, terreno = args
            if turbo:
                incremento *= 1.5
            if terreno == "montaña":
                incremento -= 3

        self.velocidad_actual += incremento
        self.bateria -= 5  # Consumo por aceleración

        return f"{self.marca} {self.modelo} (electric) +{incremento} km/h | Battery: {self.bateria}%"

    def detener(self):
        """
        Implementa frenado regenerativo.
        """
        self.velocidad_actual = 0
        return f"{self.marca} {self.modelo} regenerative braking"


# ──────────────────────────────
# Clase derivada: Moto
# ──────────────────────────────
class Moto(Vehiculo):
    """
    Representa una motocicleta.

    Se caracteriza por mayor aceleración inicial y menor estabilidad al frenar.
    """

    def acelerar(self, *args):
        incremento = 15

        if len(args) == 1 and args[0]:
            incremento += 10

        elif len(args) == 2:
            turbo, terreno = args
            if turbo:
                incremento += 10
            if terreno == "arena":
                incremento -= 8

        self.velocidad_actual += incremento
        return f"{self.marca} {self.modelo} (motorcycle) +{incremento} km/h"

    def detener(self):
        """
        Simula frenado menos estable.
        """
        self.velocidad_actual = 0
        return f"{self.marca} {self.modelo} unstable braking"


# ──────────────────────────────
# Clase derivada: Camion
# ──────────────────────────────
class Camion(Vehiculo):
    """
    Representa un camión de carga.

    Tiene menor aceleración debido a su peso y mayor distancia de frenado.
    """

    def acelerar(self, *args):
        incremento = 5

        if len(args) == 1 and args[0]:
            incremento += 3

        elif len(args) == 2:
            turbo, terreno = args
            if turbo:
                incremento += 3
            if terreno == "montaña":
                incremento -= 2

        self.velocidad_actual += max(incremento, 0)
        return f"{self.marca} {self.modelo} (truck) +{incremento} km/h"

    def detener(self):
        """
        Simula frenado prolongado.
        """
        self.velocidad_actual = 0
        return f"{self.marca} {self.modelo} needs more distance to stop"


# ──────────────────────────────
# Lógica de interfaz gráfica
# ──────────────────────────────

contador_simulaciones = 0


def actualizar_monitor(vehiculos):
    """
    Actualiza la lista visual con el estado actual de los vehículos.
    """
    lista_monitor.delete(0, tk.END)
    for v in vehiculos:
        lista_monitor.insert(tk.END, v.obtener_informacion())


def ejecutar_simulacion(limpiar=True):
    """
    Ejecuta la simulación completa.

    Parámetros:
    limpiar (bool): Indica si se debe limpiar la consola antes de ejecutar.
    """
    global contador_simulaciones

    if limpiar:
        salida_texto.delete("1.0", tk.END)

    contador_simulaciones += 1
    label_contador.config(text=f"Runs: {contador_simulaciones}")

    # Instanciación de objetos
    vehiculo1 = AutoElectrico("Tesla", "Model X", 100)
    vehiculo2 = Moto("Yamaha", "R6")
    vehiculo3 = Camion("Volvo", "FH16")

    lista_vehiculos = [vehiculo1, vehiculo2, vehiculo3]

    salida_texto.insert(tk.END, f"\n--- SIMULATION #{contador_simulaciones} ---\n\n")

    for v in lista_vehiculos:
        label_estado.config(text=f"Processing: {v.marca} {v.modelo}")

        salida_texto.insert(tk.END, v.obtener_informacion() + "\n")
        salida_texto.insert(tk.END, v.acelerar() + "\n")
        salida_texto.insert(tk.END, v.acelerar(True) + "\n")
        salida_texto.insert(tk.END, v.acelerar(True, "montaña") + "\n")

        actualizar_monitor(lista_vehiculos)

        salida_texto.insert(tk.END, v.obtener_informacion() + "\n")
        salida_texto.insert(tk.END, v.detener() + "\n")
        salida_texto.insert(tk.END, "-" * 40 + "\n")

        ventana.update_idletasks()

    label_estado.config(text="Simulation finished")


def repetir_simulacion():
    """
    Ejecuta la simulación sin limpiar resultados previos.
    """
    ejecutar_simulacion(limpiar=False)


def limpiar_salida():
    """
    Limpia la consola de salida.
    """
    salida_texto.delete("1.0", tk.END)


# ──────────────────────────────
# Configuración de la ventana
# ──────────────────────────────

ventana = tk.Tk()
ventana.title("Smart Vehicle System")
ventana.geometry("850x550")
ventana.configure(bg="#1e1e1e")

tk.Label(ventana, text="Smart Vehicle Simulation",
         font=("Arial", 18, "bold"),
         bg="#1e1e1e", fg="white").pack(pady=10)

frame_botones = tk.Frame(ventana, bg="#1e1e1e")
frame_botones.pack()

tk.Button(frame_botones, text="Run Simulation",
          command=ejecutar_simulacion,
          bg="#4CAF50", fg="white").grid(row=0, column=0, padx=5)

tk.Button(frame_botones, text="Repeat Simulation",
          command=repetir_simulacion,
          bg="#2196F3", fg="white").grid(row=0, column=1, padx=5)

tk.Button(frame_botones, text="Clear Output",
          command=limpiar_salida,
          bg="#f44336", fg="white").grid(row=0, column=2, padx=5)

label_estado = tk.Label(ventana, text="Status: Idle",
                        bg="#1e1e1e", fg="#00ffcc")
label_estado.pack(pady=5)

label_contador = tk.Label(ventana, text="Runs: 0",
                          bg="#1e1e1e", fg="white")
label_contador.pack()

frame_main = tk.Frame(ventana, bg="#1e1e1e")
frame_main.pack(fill="both", expand=True)

lista_monitor = tk.Listbox(frame_main, bg="#2d2d2d",
                           fg="white", width=35)
lista_monitor.pack(side="left", fill="y", padx=10, pady=10)

salida_texto = tk.Text(frame_main,
                       wrap="word",
                       bg="#2d2d2d",
                       fg="white",
                       font=("Consolas", 10))
salida_texto.pack(side="right", expand=True, fill="both", padx=10, pady=10)

ventana.mainloop()


# Copyright (c) 2026 David Andrés Gómez Castillo.
