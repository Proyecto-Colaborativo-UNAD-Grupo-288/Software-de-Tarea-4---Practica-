# ============================================
# SOFTWARE FJ - VERSIÓN FINAL (SIN JSON)
# ============================================

import hashlib
import uuid
import tkinter as tk
from tkinter import messagebox
import logging
from abc import ABC, abstractmethod
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE LOGS (ÚNICO ARCHIVO PERMITIDO)
# ============================================
LOG_FILE = "system_errors.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ============================================
# EXCEPCIONES PERSONALIZADAS
# ============================================
class SoftwareFJError(Exception): pass
class ValidationError(SoftwareFJError): pass

# ============================================
# MODELOS (POO AVANZADA)
# ============================================

class EntidadBase(ABC):
    """Clase abstracta general requerida"""
    def __init__(self, id_entidad):
        self._id = id_entidad

    @property
    def id(self): return self._id

class Cliente(EntidadBase):
    """Encapsulación de datos personales con validación[cite: 1]"""
    def __init__(self, id_cli, nombre, email):
        super().__init__(id_cli)
        self.nombre = nombre
        self.email = email

    @property
    def nombre(self): return self._nombre
    @nombre.setter
    def nombre(self, v):
        if len(v.strip()) < 3: 
            raise ValidationError("Nombre muy corto (mínimo 3 caracteres)[cite: 1]")
        self._nombre = v

    @property
    def email(self): return self._email
    @email.setter
    def email(self, v):
        if "@" not in v: 
            raise ValidationError("Email inválido (falta @)[cite: 1]")
        self._email = v

class Servicio(EntidadBase, ABC):
    """Clase abstracta Servicio con polimorfismo[cite: 1]"""
    def __init__(self, id_serv, nombre, precio):
        super().__init__(id_serv)
        self.nombre = nombre
        self.precio = float(precio)

    @abstractmethod
    def calcular_costo(self, duracion): pass

class ReservaSala(Servicio):
    def calcular_costo(self, horas): 
        return self.precio * horas

class AlquilerEquipo(Servicio):
    def calcular_costo(self, dias): 
        # Lógica de descuento para demostrar polimorfismo[cite: 1]
        return (self.precio * dias) * 0.9 if dias > 3 else self.precio * dias

class Asesoria(Servicio):
    def calcular_costo(self, sesiones): 
        # Lógica con impuesto adicional[cite: 1]
        return (self.precio * sesiones) * 1.19

# ============================================
# APLICACIÓN PRINCIPAL (GESTIÓN EN MEMORIA)[cite: 1]
# ============================================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Gestión 100% Objetos[cite: 1]")
        self.root.geometry("600x500")
        
        # Gestión mediante listas y diccionarios en RAM (No JSON)[cite: 1]
        self.usuarios_sistema = {"admin": hashlib.sha256("fj2026".encode()).hexdigest()}
        self.clientes = {} 
        self.servicios = {
            "S1": ReservaSala("S1", "Sala de Juntas", 50),
            "E1": AlquilerEquipo("E1", "Equipos Computo", 25),
            "A1": Asesoria("A1", "Asesoría Técnica", 100)
        }
        self.login_view()

    def clear(self):
        for w in self.root.winfo_children(): w.destroy()

    # --- VISTAS ---
    def login_view(self):
        self.clear()
        tk.Label(self.root, text="SISTEMA SOFTWARE FJ", font=("Arial", 14, "bold")).pack(pady=20)
        tk.Label(self.root, text="Usuario:").pack()
        self.ent_user = tk.Entry(self.root); self.ent_user.pack()
        tk.Label(self.root, text="Contraseña:").pack()
        self.ent_pass = tk.Entry(self.root, show="*"); self.ent_pass.pack()
        
        tk.Button(self.root, text="Ingresar", command=self.do_login, width=15).pack(pady=10)
        tk.Button(self.root, text="Registrar Usuario", command=self.do_register).pack()

    def do_login(self):
        u = self.ent_user.get()
        p = hashlib.sha256(self.ent_pass.get().encode()).hexdigest()
        if self.usuarios_sistema.get(u) == p: 
            self.main_menu()
        else: 
            messagebox.showerror("Error", "Credenciales incorrectas")

    def do_register(self):
        u, p = self.ent_user.get(), self.ent_pass.get()
        if u and p:
            self.usuarios_sistema[u] = hashlib.sha256(p.encode()).hexdigest()
            messagebox.showinfo("Éxito", f"Usuario {u} registrado en memoria.[cite: 1]")
        else: 
            messagebox.showwarning("Aviso", "Complete los campos")

    def main_menu(self):
        self.clear()
        tk.Label(self.root, text="PANEL DE CONTROL", font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="Nuevo Cliente", command=self.view_cliente, width=20).pack(pady=5)
        tk.Button(self.root, text="Nueva Reserva", command=self.view_reserva, width=20).pack(pady=5)
        tk.Button(self.root, text="Cerrar Sesión", command=self.login_view).pack(pady=20)

    def view_cliente(self):
        self.clear()
        tk.Label(self.root, text="REGISTRO DE CLIENTE").pack(pady=10)
        tk.Label(self.root, text="Nombre:").pack()
        nom_ent = tk.Entry(self.root); nom_ent.pack()
        tk.Label(self.root, text="Email:").pack()
        ema_ent = tk.Entry(self.root); ema_ent.pack()

        def guardar():
            try:
                uid = str(uuid.uuid4())[:5].upper()
                nuevo_c = Cliente(uid, nom_ent.get(), ema_ent.get())
                self.clientes[uid] = nuevo_c
                messagebox.showinfo("Éxito", f"Cliente {nuevo_c.nombre} creado.[cite: 1]")
                self.main_menu()
            except ValidationError as e:
                logging.error(f"Error de validación: {e}") # Log obligatorio[cite: 1]
                messagebox.showerror("Error", str(e))

        tk.Button(self.root, text="Guardar", command=guardar).pack(pady=10)
        tk.Button(self.root, text="Cancelar", command=self.main_menu).pack()

    def view_reserva(self):
        if not self.clientes: 
            return messagebox.showwarning("Aviso", "No hay clientes registrados en la sesión.[cite: 1]")
        
        self.clear()
        tk.Label(self.root, text="PROCESAR RESERVA").pack(pady=10)
        
        tk.Label(self.root, text="Seleccione Cliente:").pack()
        cli_var = tk.StringVar(self.root); cli_var.set(list(self.clientes.keys())[0])
        tk.OptionMenu(self.root, cli_var, *self.clientes.keys()).pack()

        tk.Label(self.root, text="Servicio:").pack()
        ser_var = tk.StringVar(self.root); ser_var.set("S1")
        tk.OptionMenu(self.root, ser_var, *self.servicios.keys()).pack()

        tk.Label(self.root, text="Duración:").pack()
        cant_ent = tk.Entry(self.root); cant_ent.pack()

        def procesar():
            try:
                cliente = self.clientes[cli_var.get()]
                servicio = self.servicios[ser_var.get()]
                cantidad = float(cant_ent.get())
                
                if cantidad <= 0: raise ValueError("Cantidad inválida[cite: 1]")

                total = servicio.calcular_costo(cantidad)
                messagebox.showinfo("Éxito", f"Reserva para: {cliente.nombre}\nTotal: ${total:.2f}")
                self.main_menu()

            except Exception as e:
                logging.error(f"Falla en reserva: {e}") # Log obligatorio[cite: 1]
                messagebox.showerror("Error", f"Error procesando datos: {e}")

        tk.Button(self.root, text="Confirmar", command=procesar).pack(pady=10)
        tk.Button(self.root, text="Volver", command=self.main_menu).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()