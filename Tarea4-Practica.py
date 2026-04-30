# ============================================
# SOFTWARE FJ - TRABAJO COLABORATIVO
# TAREA 4 - PRÁCTICA DE PROGRAMACIÓN 
#
# POR FAVOR DESARROLLAR LA ESTRUCTURA PROPUESTA Y COMPLETAR LOS MÓDULOS CON LAS FUNCIONALIDADES REQUERIDAS
# INCLUYENDO VALIDACIONES, MANEJO DE EXCEPCIONES Y LOGGING ADECUADO.    
#
# Miembros de equipo de trabajo: 
# 1. David Andrés Gómez Castillo - 1.122.141.463
# 2. Uvier Asdrubal Salinas Losada - 1.083.867.220
# 3. Nestor Andres Lopez Salamanca - 1.083.913.882
# ============================================

from abc import ABC, abstractmethod
import logging
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# ============================================
# CONFIGURACIÓN DEL SISTEMA Y LOGGER
# ============================================

LOG_FILE = "system.log"
STATUS_PENDING = "Pending"
STATUS_CONFIRMED = "Confirmed"
STATUS_CANCELLED = "Cancelled"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message): logging.info(message)
def log_error(message): logging.error(message)

# ============================================
# EXCEPCIONES PERSONALIZADAS
# ============================================

class SystemError(Exception):
    pass

class ValidationError(SystemError):
    pass

class ServiceError(SystemError):
    pass

class ReservationError(SystemError):
    pass


# ============================================
# VALIDADORES
# ============================================

def validate_string(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} must be a non-empty string")

def validate_positive(value, field):
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValidationError(f"{field} must be positive")
    
# ============================================
# CLASE BASE ABSTRACTA
# ============================================

class BaseEntity(ABC):
    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return self._id

# ============================================
# CLASE CLIENTE
# ============================================

class Cliente(BaseEntity):
    def __init__(self, id, name, email):
        super().__init__(id)
        self.name = name
        self.email = email

    @property
    def name(self): 
        return self._name
    
    @name.setter
    def name(self, value):
        validate_string(value, "Name")
        if len(value) < 3: raise ValidationError("Name too short")
        self._name = value

    @property
    def email(self): 
        return self._email
    
    @email.setter
    def email(self, value):
        validate_string(value, "Email")
        if "@" not in value: raise ValidationError("Invalid email format")
        self._email = value

# ============================================
# CLASE ABSTRACTA SERVICIOS
# ============================================

class Servicio(BaseEntity, ABC):
    def __init__(self, id, name, base_price):
        super().__init__(id)

        # 🔹 VALIDACIÓN AÑADIDA
        validate_string(name, "Service Name")
        validate_positive(base_price, "Base Price")

        self._name = name
        self._base_price = base_price

    @property
    def name(self):
        return self._name

    @property
    def base_price(self):
        return self._base_price

    #  SOBRECARGA 
    def calculate_total(self, duration, discount=0.0, tax=0.0):
        base = self.calculate_cost(duration)
        return base - (base * discount) + (base * tax)

    @abstractmethod
    def calculate_cost(self, duration): 
        pass

    @abstractmethod
    def describe(self): 
        pass

# ============================================
# IMPLEMENTACIONES DE SERVICIOS
# ============================================

class Sala(Servicio):
    def calculate_cost(self, hours):
        validate_positive(hours, "Hours")
        return self._base_price * hours
    
    def describe(self):
        return f"Room Service: {self._name}"

class Equipo(Servicio):
    def calculate_cost(self, days):
        validate_positive(days, "Days")
        return self._base_price * days
    
    def describe(self): 
        return f"Equipment Service: {self._name}"

class Asesoria(Servicio):
    def calculate_cost(self, sessions):
        validate_positive(sessions, "Sessions")
        return self._base_price * sessions
    def describe(self): 
        return f"Consulting Service: {self._name}"
    
    
# ============================================
# CLASE RESERVA
# ============================================

class Reserva:
    def __init__(self, id_reserva, cliente, servicio, duration):

        #  VALIDACIÓN AÑADIDA (cambiar forma,)
        validate_positive(duration, "Duration")

        self.id_reserva = id_reserva
        self._cliente = cliente
        self._servicio = servicio
        self._duration = duration
        self._status = STATUS_PENDING
        self._date = datetime.now()

    def confirm(self):
        if self._status != STATUS_PENDING:
            raise ReservationError("Invalid state transition")
        self._status = STATUS_CONFIRMED

    def cancel(self):
        if self._status == STATUS_CANCELLED:
            raise ReservationError("Already cancelled")
        self._status = STATUS_CANCELLED

    def process(self):
        try:
            #
            cost = self._servicio.calculate_total(self._duration, discount=0.1)
        except Exception as e:
            log_error(f"Error processing reservation {self.id_reserva}: {e}")
            raise ReservationError("Processing failed") from e
        else:
            return cost
        finally:
            log_info(f"Reservation {self.id_reserva} processed")

# ============================================
# INTERFAZ GRÁFICA DE USUARIO 
# ============================================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ System")
        self.root.geometry("750x500")
        
        self.clientes = []
        self.servicios = [
            Sala("1", "Meeting Room A", 50.0),
            Equipo("2", "Projector 4K", 25.0),
            Asesoria("3", "Java Specialist", 100.0)
        ]
        self.reservas = []

        self.build_main_window()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def build_main_window(self):
        self.clear_screen()
        tk.Label(self.root, text="Software FJ Management", font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Button(self.root, text="Manage Clients", width=25, command=self.manage_clients).pack(pady=10)
        tk.Button(self.root, text="Manage Services", width=25, command=self.manage_services).pack(pady=10)
        tk.Button(self.root, text="Manage Reservations", width=25, command=self.manage_reservations).pack(pady=10)

    def manage_clients(self):
        self.clear_screen()
        tk.Label(self.root, text="Client Administration", font=("Arial", 12, "bold")).pack(pady=10)
        
        form = tk.Frame(self.root)
        form.pack(pady=10)

        tk.Label(form, text="Name:").grid(row=0, column=0)
        ent_name = tk.Entry(form); ent_name.grid(row=0, column=1)
        tk.Label(form, text="Email:").grid(row=1, column=0)
        ent_email = tk.Entry(form); ent_email.grid(row=1, column=1)

        def add():
            try:
                new_id = len(self.clientes) + 1
                c = Cliente(new_id, ent_name.get(), ent_email.get())
                self.clientes.append(c)
                log_info(f"Client {c.name} registered.")
                messagebox.showinfo("Success", "Client Registered")
                self.manage_clients()
            except Exception as e:
                log_error(f"Error: {e}")
                messagebox.showerror("Validation Error", str(e))

        tk.Button(self.root, text="Register Client", command=add).pack()
        
        lb = tk.Listbox(self.root, width=50, height=5)
        lb.pack(pady=10)
        for c in self.clientes: lb.insert(tk.END, f"ID: {c.id} | {c.name} ({c.email})")

        tk.Button(self.root, text="Back", command=self.build_main_window).pack()
        
        # Optimizar aqui 


    def manage_services(self):
        self.clear_screen()
        tk.Label(self.root, text="Enabled Service Types", font=("Arial", 12, "bold")).pack(pady=10)
        
        form = tk.Frame(self.root)
        form.pack(pady=10)

        tk.Label(form, text="Name:").grid(row=0, column=0)
        ent_sname = tk.Entry(form)
        ent_sname.grid(row=0, column=1)

        tk.Label(form, text="Price:").grid(row=1, column=0)
        ent_sprice = tk.Entry(form)
        ent_sprice.grid(row=1, column=1)

        tk.Label(form, text="Type:").grid(row=2, column=0)
        cb_stype = ttk.Combobox(form, values=["Room", "Equipment", "Consulting"], state="readonly")
        cb_stype.grid(row=2, column=1)
        cb_stype.current(0)

        def add_service():
            try:
                name = ent_sname.get()
                price = float(ent_sprice.get())
                stype = cb_stype.get()
                
                validate_string(name, "Service Name")
                validate_positive(price, "Base Price")
                
                new_id = len(self.servicios) + 1
                
                if stype == "Room":
                    s = Sala(new_id, name, price)
                elif stype == "Equipment":
                    s = Equipo(new_id, name, price)
                else:
                    s = Asesoria(new_id, name, price)
                
                self.servicios.append(s)
                log_info(f"Service {name} (ID: {new_id}) added.")
                messagebox.showinfo("Success", "Service added correctly")    #optimizar 
                self.manage_services()
                
            except Exception as e:
                log_error(f"Error adding service: {e}")
                messagebox.showerror("Error", str(e))

        tk.Button(self.root, text="Add Service", command=add_service).pack(pady=5)

        tree = ttk.Treeview(self.root, columns=("ID", "Name", "Price", "Type"), show='headings', height=5)
        tree.heading("ID", text="ID")
        tree.heading("Name", text="Name")
        tree.heading("Price", text="Base price per hour")
        tree.heading("Type", text="Type")
        
        tree.column("ID", width=50)
        tree.column("Price", width=150)
        tree.pack(padx=10, pady=10)

        for s in self.servicios:
            tipo = s.__class__.__name__
            tree.insert("", tk.END, values=(s.id, s.name, f"${s.base_price}", tipo))

        tk.Button(self.root, text="Back", command=self.build_main_window).pack(pady=10)


    def manage_reservations(self):
        self.clear_screen()
        tk.Label(self.root, text="Reservation Management", font=("Arial", 12, "bold")).pack(pady=10)

        if not self.clientes:
            messagebox.showwarning("Warning", "Please register a client first!")
            return self.build_main_window()

        form = tk.Frame(self.root)
        form.pack()

        tk.Label(form, text="Client:").grid(row=0, column=0)
        cb_cli = ttk.Combobox(form, values=[c.name for c in self.clientes])
        cb_cli.grid(row=0, column=1)

        tk.Label(form, text="Service:").grid(row=1, column=0)
        cb_ser = ttk.Combobox(form, values=[s.name for s in self.servicios])
        cb_ser.grid(row=1, column=1)

        tk.Label(form, text="Duration:").grid(row=2, column=0)
        ent_dur = tk.Entry(form); ent_dur.grid(row=2, column=1)

        def make_res():
            try:
                if cb_cli.current() == -1 or cb_ser.current() == -1:
                    raise ValidationError("Select client and service")

                if not ent_dur.get():
                    raise ValidationError("Duration required")

                dur = float(ent_dur.get())
                validate_positive(dur, "Duration")

                cli = self.clientes[cb_cli.current()]
                ser = self.servicios[cb_ser.current()]

                res = Reserva(len(self.reservas)+1, cli, ser, dur)
                cost = res.process()

            except ValidationError as e:
                log_error(f"Validation error: {e}")
                messagebox.showerror("Validation Error", str(e))

            except Exception as e:
                log_error(f"Reservation failure: {e}")
                messagebox.showerror("Error", f"Could not process reservation: {str(e)}")

            else:
                self.reservas.append(res)
                messagebox.showinfo("Confirmed", f"Reservation Successful!\nTotal Cost: ${cost}")
                log_info(f"Res ID {res.id_reserva} created for {cli.name}")
                self.manage_reservations()

            finally:
                ent_dur.delete(0, tk.END)

        tk.Button(self.root, text="Create Reservation", command=make_res).pack(pady=5)
        
        lb = tk.Listbox(self.root, width=50, height=5)
        lb.pack()
        for r in self.reservas: lb.insert(tk.END, f"Res {r.id_reserva}: {r._cliente.name} - {r._servicio.name}")

        tk.Button(self.root, text="Back", command=self.build_main_window).pack(pady=5)


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

# ============================================
# EJECUCIÓN
# ============================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"Critical error: {str(e)}")
        print("Critical error. Check logs.")