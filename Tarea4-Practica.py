# ============================================
# SOFTWARE FJ - TRABAJO COLABORATIVO
# TAREA 4 - PRÁCTICA DE PROGRAMACIÓN 
#
#git 
# POR FAVOR DESARROLLAR LA ESTRUCTURA PROPUESTA Y COMPLETAR LOS MÓDULOS CON LAS FUNCIONALIDADES REQUERIDAS
# INCLUYENDO VALIDACIONES, MANEJO DE EXCEPCIONES Y LOGGING ADECUADO.    
# 
# Miembros de equipo de trabajo: 
# 1. David Andrés Gómez Castillo - 1.122.141.463
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
    # TODO (Equipo): agregar validaciones más estrictas (correo válido, longitud, etc.)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} must be a non-empty string")

def validate_positive(value, field):
    """Validar que un valor sea positivo"""
    # TODO (Equipo): ampliar validaciones si es necesario
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
# CLASE CLIENTE
# ============================================

class Cliente(BaseEntity):
    """
    Representa un cliente del sistema

    TODO (Equipo):
    - Agregar más atributos (telefono, edad, etc.)
    - Implementar validaciones más estrictas
    - Aplicar encapsulación completa
    """

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
# CLASE ABSTRACTA SERVICIO
# ============================================

class Servicio(BaseEntity, ABC):
    """
    Clase abstracta que representa un servicio

    TODO (Equipo):
    - Definir atributos comunes adicionales
    - Mejorar encapsulación
    - Validar parámetros de entrada
    """

    def __init__(self, id, name, base_price):
        super().__init__(id)
        self._name = name
        self._base_price = base_price

    @abstractmethod
    def calculate_cost(self, duration):
        """Calcular costo del servicio"""
        pass

    @abstractmethod
    def describe(self):
        """Describir servicio"""
        pass

# ============================================
# IMPLEMENTACIONES DE SERVICIOS
# ============================================

class Sala(Servicio):
    """Servicio de reserva de salas"""

    def calculate_cost(self, hours):
        validate_positive(hours, "Hours")
        # TODO (Equipo): extender lógica de cálculo
        return self._base_price * hours

    def describe(self):
        return f"Room Service: {self._name}"

class Equipo(Servicio):
    """Servicio de alquiler de equipos"""

    def calculate_cost(self, days):
        validate_positive(days, "Days")
        # TODO (Equipo): extender lógica de cálculo
        return self._base_price * days

    def describe(self):
        return f"Equipment Service: {self._name}"

class Asesoria(Servicio):
    """Servicio de asesoría"""

    def calculate_cost(self, sessions):
        validate_positive(sessions, "Sessions")
        # TODO (Equipo): extender lógica de cálculo
        return self._base_price * sessions

    def describe(self):
        return f"Consulting Service: {self._name}"

# ============================================
# CLASE RESERVA
# ============================================

class Reserva:
    """
    Representa una reserva en el sistema

    TODO (Equipo):
    - Validar transiciones de estado
    - Integrar logs en cada operación
    - Manejar excepciones avanzadas
    """

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
    """
    Interfaz gráfica principal del sistema

    TODO (Equipo):
    - Implementar formulario de creación de clientes
    - Implementar gestión de servicios
    - Implementar creación y gestión de reservas
    - Mostrar resultados y errores en la interfaz
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ System")

        self.build_main_window()

    def build_main_window(self):
        """Construcción de la ventana principal"""

        title = tk.Label(self.root, text="Software FJ Management System", font=("Arial", 16))
        title.pack(pady=10)

        btn_client = tk.Button(self.root, text="Manage Clients", command=self.manage_clients)
        btn_client.pack(pady=5)

        btn_services = tk.Button(self.root, text="Manage Services", command=self.manage_services)
        btn_services.pack(pady=5)

        btn_reservations = tk.Button(self.root, text="Manage Reservations", command=self.manage_reservations)
        btn_reservations.pack(pady=5)

    def manage_clients(self):
        # TODO (Equipo): desarrollar módulo de clientes
        messagebox.showinfo("Info", "Clients module not implemented yet")

    def manage_services(self):
        # TODO (Equipo): desarrollar módulo de servicios
        messagebox.showinfo("Info", "Services module not implemented yet")

    def manage_reservations(self):
        # TODO (Equipo): desarrollar módulo de reservas
        messagebox.showinfo("Info", "Reservations module not implemented yet")

# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """
    Punto de entrada del sistema

    TODO (Equipo):
    - Implementar mínimo 10 operaciones (válidas e inválidas)
    - Garantizar continuidad del sistema ante errores
    - Integrar logging en toda la ejecución
    """

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