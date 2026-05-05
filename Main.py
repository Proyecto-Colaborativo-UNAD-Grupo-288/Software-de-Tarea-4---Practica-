# ============================================
# SOFTWARE FJ - VERSION PRO CON HISTORIAL
# ============================================

import json
import hashlib
import uuid
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import logging

# ============================================
# ARCHIVOS
# ============================================

USERS_FILE = "users.json"
RESERVAS_FILE = "reservas.json"
LOG_FILE = "system.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# ============================================
# UTILIDADES
# ============================================

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_id():
    return str(uuid.uuid4())[:8].upper()

# ---------- USUARIOS ----------

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"admin": hash_pass("fj2026")}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------- RESERVAS ----------

def load_reservas():
    try:
        with open(RESERVAS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_reservas(reservas):
    with open(RESERVAS_FILE, "w") as f:
        json.dump(reservas, f, indent=4)

# ============================================
# MODELOS
# ============================================

class Cliente:
    def __init__(self, id, name, email):
        if len(name.strip()) < 3:
            raise ValueError("Nombre muy corto")
        if "@" not in email:
            raise ValueError("Email inválido")

        self.id = id
        self.name = name.strip()
        self.email = email.strip().lower()

class Servicio:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = float(price)

    def calcular(self, duracion):
        return self.price * float(duracion)

class Reserva:
    def __init__(self, id, cliente, servicio, duracion):
        self.id = id
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = float(duracion)
        self.fecha = datetime.now()

    def total(self):
        return self.servicio.calcular(self.duracion)

# ============================================
# APP
# ============================================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ PRO MAX")
        self.root.geometry("650x500")

        self.users = load_users()
        self.historial = load_reservas()

        self.clientes = {}
        self.servicios = {}

        self.init_services()
        self.login()

    def init_services(self):
        for s in [
            Servicio("S1","Sala",50),
            Servicio("E1","Equipo",25),
            Servicio("A1","Asesoría",100)
        ]:
            self.servicios[s.id] = s

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ============================================
    # LOGIN
    # ============================================

    def login(self):
        self.clear()

        tk.Label(self.root, text="LOGIN", font=("Arial", 16)).pack(pady=10)

        self.ent_user = tk.Entry(self.root)
        self.ent_pass = tk.Entry(self.root, show="*")

        self.ent_user.pack(pady=5)
        self.ent_pass.pack(pady=5)

        self.show_var = tk.BooleanVar()

        tk.Checkbutton(
            self.root,
            text="Mostrar contraseña",
            variable=self.show_var,
            command=self.toggle_pass
        ).pack()

        tk.Button(self.root, text="Ingresar", command=self.do_login).pack(pady=5)
        tk.Button(self.root, text="Registrar", command=self.register).pack()

    def toggle_pass(self):
        self.ent_pass.config(show="" if self.show_var.get() else "*")

    def do_login(self):
        user = self.ent_user.get().strip()
        pwd  = self.ent_pass.get().strip()

        if user in self.users and self.users[user] == hash_pass(pwd):
            logging.info(f"Login exitoso: {user}")
            self.menu()
        else:
            logging.warning(f"Login fallido: {user}")
            messagebox.showerror("Error", "Credenciales incorrectas")

    def register(self):
        user = self.ent_user.get().strip()
        pwd  = self.ent_pass.get().strip()

        if not user or not pwd:
            return messagebox.showerror("Error", "Campos vacíos")

        if user in self.users:
            return messagebox.showerror("Error", "Usuario ya existe")

        self.users[user] = hash_pass(pwd)
        save_users(self.users)

        logging.info(f"Usuario registrado: {user}")
        messagebox.showinfo("OK", "Usuario registrado")

    # ============================================
    # MENU
    # ============================================

    def menu(self):
        self.clear()

        tk.Label(self.root, text="MENU PRINCIPAL", font=("Arial", 14)).pack(pady=10)

        tk.Button(self.root, text="Clientes", command=self.view_clients).pack(pady=5)
        tk.Button(self.root, text="Reservas", command=self.view_reservas).pack(pady=5)
        tk.Button(self.root, text="Historial", command=self.view_historial).pack(pady=5)
        tk.Button(self.root, text="Salir", command=self.login).pack(pady=5)

    # ============================================
    # CLIENTES
    # ============================================

    def view_clients(self):
        self.clear()

        tk.Label(self.root, text="CLIENTES").pack()

        name = tk.Entry(self.root)
        email = tk.Entry(self.root)

        name.pack()
        email.pack()

        def add():
            try:
                c = Cliente(generate_id(), name.get(), email.get())
                self.clientes[c.id] = c
                messagebox.showinfo("OK", f"Cliente {c.id}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(self.root, text="Agregar", command=add).pack()
        tk.Button(self.root, text="Volver", command=self.menu).pack()

    # ============================================
    # RESERVAS
    # ============================================

    def view_reservas(self):
        self.clear()

        if not self.clientes:
            return messagebox.showwarning("Error","Primero crea clientes")

        cli = tk.StringVar(value=list(self.clientes.keys())[0])
        ser = tk.StringVar(value=list(self.servicios.keys())[0])

        tk.OptionMenu(self.root, cli, *self.clientes.keys()).pack()
        tk.OptionMenu(self.root, ser, *self.servicios.keys()).pack()

        dur = tk.Entry(self.root)
        dur.pack()

        def crear():
            try:
                r = Reserva(
                    generate_id(),
                    self.clientes[cli.get()],
                    self.servicios[ser.get()],
                    dur.get()
                )
                total = r.total()

                # guardar historial
                data = {
                    "id": r.id,
                    "cliente": r.cliente.name,
                    "servicio": r.servicio.name,
                    "total": total,
                    "fecha": r.fecha.strftime("%Y-%m-%d %H:%M")
                }

                self.historial.append(data)
                save_reservas(self.historial)

                logging.info(f"Reserva creada: {data}")

                messagebox.showinfo("OK", f"Total: {total}")

            except Exception as e:
                logging.error(str(e))
                messagebox.showerror("Error", str(e))

        tk.Button(self.root, text="Crear", command=crear).pack()
        tk.Button(self.root, text="Volver", command=self.menu).pack()

    # ============================================
    # HISTORIAL
    # ============================================

    def view_historial(self):
        self.clear()

        tk.Label(self.root, text="HISTORIAL DE RESERVAS").pack()

        text = tk.Text(self.root, height=20, width=70)
        text.pack()

        for r in self.historial:
            text.insert(tk.END, f"{r}\n")

        tk.Button(self.root, text="Volver", command=self.menu).pack()

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()