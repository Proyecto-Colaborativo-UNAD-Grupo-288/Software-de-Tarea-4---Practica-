# ============================================
# SOFTWARE FJ - TRABAJO COLABORATIVO
# TAREA 4 - PRÁCTICA DE PROGRAMACIÓN 
#
#
# POR FAVOR DESARROLLAR LA ESTRUCTURA PROPUESTA Y COMPLETAR LOS MÓDULOS CON LAS FUNCIONALIDADES REQUERIDAS
# INCLUYENDO VALIDACIONES, MANEJO DE EXCEPCIONES Y LOGGING ADECUADO.    
# 
# Miembros de equipo de trabajo: 
# 1. David Andrés Gómez Castillo - 1.122.141.463
# 2. Uvier Asdrubal Salinas Losada - 1.083.867.220
# ============================================

from abc import ABC, abstractmethod
import logging
import tkinter as tk
from tkinter import messagebox

# ============================================
# CONFIGURACIÓN DEL SISTEMA
# ============================================

LOG_FILE = "system.log"

STATUS_PENDING = "Pending"
STATUS_CONFIRMED = "Confirmed"
STATUS_CANCELLED = "Cancelled"

# ============================================
# CONFIGURACIÓN DEL LOGGER
# ============================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

# ============================================
# EXCEPCIONES PERSONALIZADAS
# ============================================

class SystemError(Exception):
    """Excepción base del sistema"""
    pass

class ValidationError(SystemError):
    """Errores relacionados con validación de datos"""
    pass

class ServiceError(SystemError):
    """Errores relacionados con servicios"""
    pass

class ReservationError(SystemError):
    """Errores relacionados con reservas"""
    pass

# ============================================
# VALIDADORES
# ============================================

def validate_string(value, field):
    """Validar que un campo sea string no vacío"""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} must be a non-empty string")

def validate_positive(value, field):
    """Validar que un valor sea positivo"""
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValidationError(f"{field} must be positive")

# ============================================
# CLASE BASE ABSTRACTA
# ============================================

class BaseEntity(ABC):
    """Clase base para todas las entidades del sistema"""

    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return self._id

# ============================================
# CLASE CLIENTE  (W.I.P David Gómez)
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
        self._name = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        validate_string(value, "Email")
        self._email = value

# ============================================
# GESTIÓN DE CLIENTES
# ============================================

clientes = []

def find_client_by_id(client_id):
    """Buscar cliente por ID"""
    for c in clientes:
        if c.id == client_id:
            return c
    return None


def list_clients():
    """Retornar lista de clientes"""
    return clientes


def register_client(id, name, email):
    try:
        if find_client_by_id(id):
            raise ValidationError("Client ID already exists")

        cliente = Cliente(id, name, email)
        clientes.append(cliente)

        log_info(f"Client registered: {name}")
        return cliente

    except ValidationError as e:
        log_error(f"Validation error: {str(e)}")
        raise

    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        raise

# ============================================
# CLASE ABSTRACTA SERVICIO
# ============================================

class Servicio(BaseEntity, ABC):
    def __init__(self, id, name, base_price):
        super().__init__(id)
        self._name = name
        self._base_price = base_price

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
    def __init__(self, cliente, servicio, duration):
        self._cliente = cliente
        self._servicio = servicio
        self._duration = duration
        self._status = STATUS_PENDING

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
            cost = self._servicio.calculate_cost(self._duration)
        except Exception as e:
            raise ReservationError("Processing failed") from e
        return cost

# ============================================
# INTERFAZ GRÁFICA (TKINTER)
# ============================================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ System")

        self.build_main_window()

    def build_main_window(self):
        title = tk.Label(self.root, text="Software FJ Management System", font=("Arial", 16))
        title.pack(pady=10)

        btn_client = tk.Button(self.root, text="Manage Clients", command=self.manage_clients)
        btn_client.pack(pady=5)

        btn_services = tk.Button(self.root, text="Manage Services", command=self.manage_services)
        btn_services.pack(pady=5)

        btn_reservations = tk.Button(self.root, text="Manage Reservations", command=self.manage_reservations)
        btn_reservations.pack(pady=5)

    def manage_clients(self):
        try:
            cliente = register_client(len(clientes)+1, f"User {len(clientes)+1}", "mail@test.com")

            all_clients = "\n".join([f"{c.id} - {c.name}" for c in list_clients()])

            messagebox.showinfo("Clients", f"Client created:\n{cliente.name}\n\nAll clients:\n{all_clients}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def manage_services(self):
        messagebox.showinfo("Info", "Services module not implemented yet")

    def manage_reservations(self):
        messagebox.showinfo("Info", "Reservations module not implemented yet")

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