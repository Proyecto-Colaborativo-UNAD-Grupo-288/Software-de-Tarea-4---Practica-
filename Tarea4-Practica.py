# ============================================
# SOFTWARE FJ - TRABAJO COLABORATIVO
# TAREA 4 - PRÁCTICA DE PROGRAMACIÓN
#
# Miembros de equipo de trabajo:
# 1. David Andrés Gómez Castillo - 1.122.141.463
# 2. Uvier Asdrubal Salinas Losada - 1.083.867.220
# 3. Nestor Andres Lopez Salamanca - 1.083.913.882
# ============================================

from abc import ABC, abstractmethod
import logging
import re
import hashlib
import uuid
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# ============================================
# CONFIGURACIÓN DEL SISTEMA Y LOGGER
# ============================================

LOG_FILE = "system.log"
STATUS_PENDING   = "Pending"
STATUS_CONFIRMED = "Confirmed"
STATUS_CANCELLED = "Cancelled"

_LOGIN_USER = "admin"
_PASS_HASH  = hashlib.sha256("fj2026".encode()).hexdigest()


MAX_DURATION = 10_000.0

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message):    logging.info(message)
def log_error(message):   logging.error(message)
def log_warning(message): logging.warning(message)

# ============================================
# EXCEPCIONES PERSONALIZADAS
# ============================================

class SistemaError(Exception):
    """Excepción base del sistema."""
    pass

class ValidationError(SistemaError):
    pass

class ServiceError(SistemaError):
    pass

class ReservationError(SistemaError):
    pass

# ============================================
# VALIDADORES
# ============================================


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate_string(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} must be a non-empty string")

def validate_email(value):
    validate_string(value, "Email")
    if not _EMAIL_RE.match(value):
        raise ValidationError("Invalid email format (expected: user@domain.tld)")

def validate_positive(value, field):
    
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a number")
    if value <= 0:
        raise ValidationError(f"{field} must be positive (got {value})")
    if value > MAX_DURATION:
        raise ValidationError(f"{field} exceeds maximum allowed value ({MAX_DURATION})")
    return value

# ============================================
# GENERADOR DE IDs ÚNICOS
# ============================================


def generate_id():
    return str(uuid.uuid4())[:8].upper()

# ============================================
# CLASE BASE ABSTRACTA
# ============================================

class BaseEntity(ABC):
    def __init__(self, id):
        if id is None:
            raise ValidationError("ID cannot be None")
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
        self.name  = name
        self.email = email

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        validate_string(value, "Name")
        if len(value.strip()) < 3:
            raise ValidationError("Name must be at least 3 characters")
        self._name = value.strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        
        validate_email(value)
        self._email = value.strip().lower()

# ============================================
# CLASE ABSTRACTA SERVICIOS
# ============================================

class Servicio(BaseEntity, ABC):
    def __init__(self, id, name, base_price):
        super().__init__(id)
        validate_string(name, "Service Name")
        base_price = validate_positive(base_price, "Base Price")
        self._name       = name
        self._base_price = base_price

    @property
    def name(self):
        return self._name

    @property
    def base_price(self):
        return self._base_price

    def calculate_total(self, duration, discount=0.0, tax=0.0):
       
        if not (0.0 <= discount <= 1.0):
            raise ValidationError("Discount must be between 0.0 and 1.0")
        if not (0.0 <= tax <= 1.0):
            raise ValidationError("Tax must be between 0.0 and 1.0")
        base = self.calculate_cost(duration)
        discounted = base * (1.0 - discount)
        total = discounted * (1.0 + tax)
        return round(total, 2)

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
        hours = validate_positive(hours, "Hours")
        return round(self._base_price * hours, 2)

    def describe(self):
        return f"Room Service: {self._name} (${self._base_price:.2f}/hr)"


class Equipo(Servicio):
    def calculate_cost(self, days):
        days = validate_positive(days, "Days")
        return round(self._base_price * days, 2)

    def describe(self):
        return f"Equipment Service: {self._name} (${self._base_price:.2f}/day)"


class Asesoria(Servicio):
    def calculate_cost(self, sessions):
        sessions = validate_positive(sessions, "Sessions")
        return round(self._base_price * sessions, 2)

    def describe(self):
        return f"Consulting Service: {self._name} (${self._base_price:.2f}/session)"

# ============================================
# CLASE RESERVA
# ============================================

class Reserva:
    def __init__(self, id_reserva, cliente, servicio, duration,
                 discount=0.0, tax=0.0):
       
        if not isinstance(cliente, Cliente):
            raise ValidationError("Invalid client")
        if not isinstance(servicio, Servicio):
            raise ValidationError("Invalid service")

        duration = validate_positive(duration, "Duration")
        if not (0.0 <= discount <= 1.0):
            raise ValidationError("Discount must be between 0.0 and 1.0")
        if not (0.0 <= tax <= 1.0):
            raise ValidationError("Tax must be between 0.0 and 1.0")

        self.id_reserva = id_reserva
        self._cliente   = cliente
        self._servicio  = servicio
        self._duration  = duration
        self._discount  = discount
        self._tax       = tax
        self._status    = STATUS_PENDING
        self._date      = datetime.now()

    @property
    def date(self):
        return self._date

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def status(self):
        return self._status

    @property
    def discount(self):
        return self._discount

    @property
    def tax(self):
        return self._tax

    def confirm(self):
        if self._status != STATUS_PENDING:
            raise ReservationError(
                f"Cannot confirm: current status is '{self._status}'"
            )
        self._status = STATUS_CONFIRMED
        log_info(f"Reservation {self.id_reserva} confirmed")

    def cancel(self):
        if self._status == STATUS_CANCELLED:
            log_warning(f"Reservation {self.id_reserva} was already cancelled")
            raise ReservationError("Already cancelled")
        self._status = STATUS_CANCELLED
        log_warning(f"Reservation {self.id_reserva} cancelled (was {self._status})")

    def process(self):
        try:
            if self._status == STATUS_CANCELLED:
                raise ReservationError("Cannot process a cancelled reservation")
            if self._status == STATUS_CONFIRMED:
                raise ReservationError("Reservation already processed")

            self.confirm()
            cost = self._servicio.calculate_total(
                self._duration,
                discount=self._discount,
                tax=self._tax
            )

        except ValidationError as e:
            log_error(f"Validation error in reservation {self.id_reserva}: {e}")
            raise

        except ReservationError as e:
            log_error(f"Reservation error in {self.id_reserva}: {e}")
            raise

        except Exception as e:
            log_error(f"Unexpected error in reservation {self.id_reserva}: {e}")
            raise ReservationError("Processing failed") from e

        else:
            log_info(f"Reservation {self.id_reserva} successful. Cost: {cost}")
            return cost

        finally:
            log_info(f"Reservation {self.id_reserva} processing attempt finished")

# ============================================
# INTERFAZ GRÁFICA DE USUARIO (DG180 G.U.I v2.0)
# ============================================

COLORS = {
    "bg":       "#0F1117",
    "surface":  "#1A1D27",
    "surface2": "#22263A",
    "accent":   "#4F8EF7",
    "accent2":  "#6C63FF",
    "success":  "#2DD4A0",
    "warning":  "#F7B731",
    "danger":   "#F75F5F",
    "text":     "#E8EAF6",
    "text_dim": "#7A8099",
    "border":   "#2E3350",
    "input_bg": "#13162A",
}

FONTS = {
    "title":      ("Segoe UI", 22, "bold"),
    "subtitle":   ("Segoe UI", 13, "bold"),
    "label":      ("Segoe UI", 10),
    "label_bold": ("Segoe UI", 10, "bold"),
    "button":     ("Segoe UI", 10, "bold"),
    "small":      ("Segoe UI", 9),
    "mono":       ("Consolas", 9),
}
class ResilienceTester:
    def __init__(self, logger):
        self.logger = logger
        self.report = []

    def run_simulation(self, is_authenticated):
        # Punto 1 de David: Validación de seguridad
        if not is_authenticated:
            raise PermissionError("Access Denied: Authentication required for stress tests.")

        # Tus 10 casos originales (Punto 6: Mensajes en Inglés)
        casos = [
            ("Uvier", "uvier@unad.edu.co", "5", "Sala"),
            ("Pepito", "pepito_sin_arroba.com", "10", "Asesoria"),
            ("Dani", "dani@gmail.com", "-2", "Equipo"),
            ("Pancracio", "pancracio@gmail.com", "8", "Sala"),
            ("Nestor", "nestor@unad.edu.co", "abc", "Equipo"),
            ("David", "david@unad.edu.co", "12", "Asesoria"),
            ("", "anonimo@test.com", "2", "Sala"),
            ("Luciana", "luciana@bio.com", "7", "Equipo"),
            ("Cliente X", "x@mail.com", "0", "Sala"),
            ("Final UNAD", "final@unad.edu.co", "1", "Asesoria")
        ]

        exitos = 0
        fallos = 0

        for i, (nom, em, dur, tip) in enumerate(casos, 1):
            try:
                # Punto 2: Uso de clases reales (Cliente) y Punto 3: Logs
                self.logger.info(f"Processing operation {i}...")
                
                # REGLA 1: Nombre (Punto 5: Validaciones robustas)
                if not nom: raise ValueError("Client name is required.")
                
                # REGLA 2: Email
                if "@" not in em: raise ValueError(f"Invalid email: {em}")
                
                # REGLA 3: Duración (Punto 5: Manejo de ValueError para 'abc')
                val_dur = float(dur)
                if val_dur <= 0: raise ValueError(f"Duration must be positive: {dur}")
                
                exitos += 1
                self.report.append(f"Case {i}: [OK] - {nom} processed.")

            except (ValueError, Exception) as e:
                fallos += 1
                error_msg = f"Case {i}: [ERROR] - {str(e)}"
                self.logger.error(error_msg) # Registro obligatorio en system.log
                self.report.append(error_msg)

        return self.report, exitos, fallos

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ System")
        self.root.geometry("860x600")
        self.root.minsize(800, 550)
        self.root.configure(bg=COLORS["bg"])

        self._apply_styles()

        self.clientes = []
        self.servicios = [
            Sala("S001",    "Meeting Room A",   50.0),
            Equipo("E001",  "Projector 4K",     25.0),
            Asesoria("A001","Java Specialist", 100.0),
        ]
        self.current_user = None
        self.reservas = []

        self._login_binding = None

        self.build_login()

    # ------------------------------------------------------------------
    # ESTILOS
    # ------------------------------------------------------------------

    def _apply_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("Custom.Treeview",
            background=COLORS["surface"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["surface"],
            rowheight=32,
            borderwidth=0,
            relief="flat",
            font=FONTS["small"],
        )
        style.configure("Custom.Treeview.Heading",
            background=COLORS["surface2"],
            foreground=COLORS["accent"],
            font=FONTS["label_bold"],
            relief="flat",
            borderwidth=0,
        )
        style.map("Custom.Treeview",
            background=[("selected", COLORS["accent2"])],
            foreground=[("selected", COLORS["text"])],
        )
        style.configure("Custom.TCombobox",
            fieldbackground=COLORS["input_bg"],
            background=COLORS["surface2"],
            foreground=COLORS["text"],
            selectbackground=COLORS["accent"],
            selectforeground=COLORS["text"],
            borderwidth=1,
            relief="flat",
        )
        style.map("Custom.TCombobox",
            fieldbackground=[("readonly", COLORS["input_bg"])],
            foreground=[("readonly", COLORS["text"])],
        )
        style.configure("Custom.Vertical.TScrollbar",
            background=COLORS["surface2"],
            troughcolor=COLORS["surface"],
            borderwidth=0,
            arrowcolor=COLORS["text_dim"],
        )

    # ------------------------------------------------------------------
    # HELPERS / WIDGETS REUTILIZABLES
    # ------------------------------------------------------------------

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def get_cliente_by_id(self, cid):
        client = next((c for c in self.clientes if c.id == cid), None)
        if client is None:
            raise ValidationError(f"Client ID '{cid}' not found")
        return client

    def get_servicio_by_id(self, sid):
        service = next((s for s in self.servicios if s.id == sid), None)
        if service is None:
            raise ValidationError(f"Service ID '{sid}' not found")
        return service

    def _make_header(self, parent, title, subtitle=None):
        header = tk.Frame(parent, bg=COLORS["surface"], pady=14)
        header.pack(fill="x")
        inner = tk.Frame(header, bg=COLORS["surface"])
        inner.pack(padx=28)
        tk.Label(inner, text=title, font=FONTS["title"],
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
        if subtitle:
            tk.Label(inner, text=subtitle, font=FONTS["small"],
                     bg=COLORS["surface"], fg=COLORS["text_dim"]).pack(anchor="w")
        tk.Frame(parent, bg=COLORS["accent"], height=2).pack(fill="x")

    def _make_card(self, parent, padx=24, pady=16):
        return tk.Frame(parent, bg=COLORS["surface"], padx=padx, pady=pady)

    def _make_entry(self, parent, label_text, row, show=None):
        tk.Label(parent, text=label_text, font=FONTS["label_bold"],
                 bg=COLORS["surface"], fg=COLORS["text_dim"]).grid(
                     row=row, column=0, sticky="w", padx=(0, 14), pady=6)
        entry = tk.Entry(parent,
                         font=FONTS["label"],
                         bg=COLORS["input_bg"],
                         fg=COLORS["text"],
                         insertbackground=COLORS["accent"],
                         relief="flat", bd=0,
                         highlightthickness=1,
                         highlightcolor=COLORS["accent"],
                         highlightbackground=COLORS["border"],
                         width=28)
        if show:
            entry.config(show=show)
        entry.grid(row=row, column=1, sticky="ew", pady=6, ipady=5)
        return entry

    def _make_combobox(self, parent, label_text, row, values):
        tk.Label(parent, text=label_text, font=FONTS["label_bold"],
                 bg=COLORS["surface"], fg=COLORS["text_dim"]).grid(
                     row=row, column=0, sticky="w", padx=(0, 14), pady=6)
        cb = ttk.Combobox(parent, values=values, state="readonly",
                          style="Custom.TCombobox", font=FONTS["label"])
        cb.grid(row=row, column=1, sticky="ew", pady=6, ipady=4)
        if values:
            cb.current(0)
        return cb

    def _make_button(self, parent, text, command, style="primary", width=20):
        colors_map = {
            "primary":   (COLORS["accent"],   COLORS["bg"],       COLORS["accent2"]),
            "secondary": (COLORS["surface2"], COLORS["text_dim"], COLORS["border"]),
            "danger":    (COLORS["danger"],    COLORS["bg"],       "#c0392b"),
            "success":   (COLORS["success"],   COLORS["bg"],       "#1aab80"),
        }
        bg, fg, hover = colors_map.get(style, colors_map["primary"])
        btn = tk.Button(parent, text=text, command=command,
                        font=FONTS["button"],
                        bg=bg, fg=fg,
                        activebackground=hover,
                        activeforeground=COLORS["text"],
                        relief="flat", bd=0,
                        padx=18, pady=8,
                        cursor="hand2",
                        width=width)
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    def _make_listbox(self, parent, height=6):
        frame = tk.Frame(parent, bg=COLORS["border"], bd=1)
        sb = ttk.Scrollbar(frame, style="Custom.Vertical.TScrollbar")
        lb = tk.Listbox(frame,
                        font=FONTS["mono"],
                        bg=COLORS["surface"],
                        fg=COLORS["text"],
                        selectbackground=COLORS["accent2"],
                        selectforeground=COLORS["text"],
                        activestyle="none",
                        relief="flat", bd=0,
                        height=height,
                        highlightthickness=0,
                        yscrollcommand=sb.set)
        sb.config(command=lb.yview)
        sb.pack(side="right", fill="y")
        lb.pack(side="left", fill="both", expand=True)
        return frame, lb

    def _make_treeview(self, parent, columns, col_labels, col_widths, height=6):
        frame = tk.Frame(parent, bg=COLORS["surface"])
        sb = ttk.Scrollbar(frame, style="Custom.Vertical.TScrollbar")
        tree = ttk.Treeview(frame,
                            columns=columns,
                            show="headings",
                            height=height,
                            style="Custom.Treeview",
                            yscrollcommand=sb.set)
        sb.config(command=tree.yview)
        for col, label, width in zip(columns, col_labels, col_widths):
            tree.heading(col, text=label)
            tree.column(col, width=width, anchor="center")
        sb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        tree.tag_configure("odd",  background=COLORS["surface"])
        tree.tag_configure("even", background=COLORS["surface2"])
        return frame, tree

    def _status_badge(self, parent, count, label):
        f = tk.Frame(parent, bg=COLORS["surface2"], padx=12, pady=6)
        tk.Label(f, text=str(count), font=("Segoe UI", 18, "bold"),
                 bg=COLORS["surface2"], fg=COLORS["accent"]).pack()
        tk.Label(f, text=label, font=FONTS["small"],
                 bg=COLORS["surface2"], fg=COLORS["text_dim"]).pack()
        return f

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------

    def build_login(self):
        self.clear_screen()
        self._make_header(self.root, "🔐  Software FJ",
                          "System access — Input your credentials")

        card = tk.Frame(self.root, bg=COLORS["surface"], padx=36, pady=30)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="INICIAR SESIÓN", font=("Segoe UI", 8, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text_dim"]).grid(
                     row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        ent_user = self._make_entry(card, "Usuario",    row=1)
        ent_pass = self._make_entry(card, "Contraseña", row=2, show="•")

        lbl_error = tk.Label(card, text="", font=FONTS["small"],
                             bg=COLORS["surface"], fg=COLORS["danger"])
        lbl_error.grid(row=3, column=0, columnspan=2, pady=(6, 0))

        def login():
            input_hash = hashlib.sha256(ent_pass.get().encode()).hexdigest()
            if ent_user.get() == _LOGIN_USER and input_hash == _PASS_HASH:
                log_info("Login exitoso.")
                self.current_user = "admin"
                self.root.unbind("<Return>")
                self.build_main_window()
            else:
                log_warning("Intento de login fallido.")
                lbl_error.config(text="⚠  Usuario o contraseña incorrectos")
                ent_pass.delete(0, tk.END)
                ent_pass.focus()

        if self._login_binding:
            self.root.unbind("<Return>", self._login_binding)
        self._login_binding = self.root.bind("<Return>", lambda e: login())

        self._make_button(card, "Ingresar →", login, style="primary", width=22).grid(
            row=4, column=0, columnspan=2, pady=(16, 0), sticky="ew")

        tk.Label(self.root, text="Sistema de gestión — Software FJ v2.0",
                 font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["text_dim"]).place(
                     relx=0.5, rely=0.96, anchor="center")

    # ------------------------------------------------------------------
    # VENTANA PRINCIPAL
    # ------------------------------------------------------------------

    def build_main_window(self):
        self.clear_screen()

        self._make_header(self.root,
                          "Software FJ  ·  Management System Pro max T-3000",
                          "Collaborative Work Platform — Tarea 4")

        stats = tk.Frame(self.root, bg=COLORS["bg"], pady=20)
        stats.pack(fill="x", padx=32)

        for count, label in [
            (len(self.clientes),  "Clients"),
            (len(self.servicios), "Services"),
            (len(self.reservas),  "Reservations"),
        ]:
            self._status_badge(stats, count, label).pack(side="left", padx=10)

        tk.Label(self.root, text="QUICK ACCESS", font=("Segoe UI", 8, "bold"),
                 bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(anchor="w", padx=34, pady=(10, 4))
        # --- APORTE DE UVIER: ACCESO A PRUEBAS DE INGENIERÍA ---
        # Contenedor alineado con el diseño actual del software
        test_frame = tk.Frame(self.root, bg=COLORS["bg"], pady=10)
        test_frame.pack(fill="x", padx=34)

        # Este botón dispara la lógica de resiliencia (Método en la línea 926)
        # El texto está en inglés para mantener la consistencia con la UI original
        self._make_button(
            test_frame, 
            "🛠️ Run Resilience Test (Robust System)", 
            self.test_system_resilience,
            style="secondary", 
            width=40
        ).pack(side="left")
        
        # ---- Tarjetas de navegación ----# revisar tabla de iconos, coincidir... (NO TOCAR OJO!!!!!!!!!!!!!!!!!!!) O LEER BIEN SI TOCAR, OOGA-BOOGA o bugs por todo lado
        nav = tk.Frame(self.root, bg=COLORS["bg"])
        nav.pack(fill="x", padx=28)

        nav_items = [
            ("👤  Manage Clients",      "Register and view your clients",    self.manage_clients,      "primary"),
            ("🛠  Manage Services",      "Add and browse available services", self.manage_services,     "primary"),
            ("📋  Manage Reservations", "Create and track reservations",     self.manage_reservations, "success"),
        ]

        for title, desc, cmd, sty in nav_items:
            card = tk.Frame(nav, bg=COLORS["surface"], padx=22, pady=16,
                            highlightthickness=1, highlightbackground=COLORS["border"])
            card.pack(side="left", expand=True, fill="both", padx=8, pady=4)
            tk.Label(card, text=title, font=FONTS["subtitle"],
                     bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
            tk.Label(card, text=desc, font=FONTS["small"],
                     bg=COLORS["surface"], fg=COLORS["text_dim"]).pack(anchor="w", pady=(2, 10))
            self._make_button(card, "Open →", cmd, style=sty, width=14).pack(anchor="w")

        res_card = tk.Frame(nav, bg=COLORS["surface"], padx=22, pady=16,
                            highlightthickness=1, highlightbackground=COLORS["border"])
        res_card.pack(side="left", expand=True, fill="both", padx=8, pady=4)
        tk.Label(res_card, text="🧪  Resilience Test", font=FONTS["subtitle"],
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(res_card, text="Simulate 10 ops", font=FONTS["small"],
                 bg=COLORS["surface"], fg=COLORS["text_dim"]).pack(anchor="w", pady=(2, 10))
        btn_row = tk.Frame(res_card, bg=COLORS["surface"])
        btn_row.pack(anchor="w")
        self._make_button(btn_row, "▶ Run", self.test_system_resilience,
                          style="secondary", width=9).pack(side="left", padx=(0, 6))
        self._make_button(btn_row, "📊 Report", self.show_resilience_report,
                          style="secondary", width=10).pack(side="left")

        footer = tk.Frame(self.root, bg=COLORS["bg"])
        footer.pack(side="bottom", fill="x", padx=32, pady=12)
        tk.Label(footer, text="© Software FJ  ·  Programación, grupo 288.",
                 font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(side="right")

    # ------------------------------------------------------------------
    # CLIENTES
    # ------------------------------------------------------------------

    def manage_clients(self):
        self.clear_screen()
        self._make_header(self.root, "👤  Client Administration",
                          "Register new clients and view existing records")

        body = tk.Frame(self.root, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=28, pady=16)

        form_card = self._make_card(body)
        form_card.pack(side="left", fill="y", padx=(0, 12))

        tk.Label(form_card, text="NEW CLIENT", font=("Segoe UI", 8, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text_dim"]).grid(
                     row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ent_name  = self._make_entry(form_card, "Full Name",     row=1)
        ent_email = self._make_entry(form_card, "Email Address", row=2)
        form_card.columnconfigure(1, weight=1)

        def add():
            try:
                new_id = generate_id()
                c = Cliente(new_id, ent_name.get(), ent_email.get())
                self.clientes.append(c)
                log_info(f"Client {c.name} registered (ID: {c.id}).")
                messagebox.showinfo("Success", f"Client '{c.name}' registered.\nID: {c.id}")
                ent_name.delete(0, tk.END)
                ent_email.delete(0, tk.END)
                self.manage_clients()
            except Exception as e:
                log_error(f"Error registering client: {e}")
                messagebox.showerror("Validation Error", str(e))

        self._make_button(form_card, "Register Client", add, style="primary", width=22).grid(
            row=3, column=0, columnspan=2, pady=(14, 0), sticky="ew")

        list_card = tk.Frame(body, bg=COLORS["surface"], padx=16, pady=16)
        list_card.pack(side="left", fill="both", expand=True)

        tk.Label(list_card, text=f"REGISTERED CLIENTS  ({len(self.clientes)})",
                 font=("Segoe UI", 8, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text_dim"]).pack(anchor="w", pady=(0, 8))

        cols = ("ID", "Name", "Email")
        tree_frame, tree = self._make_treeview(
            list_card, cols, cols, [80, 180, 260], height=10)
        tree_frame.pack(fill="both", expand=True)

        for i, c in enumerate(self.clientes):
            tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", tk.END, values=(c.id, c.name, c.email), tags=(tag,))

        bottom = tk.Frame(self.root, bg=COLORS["bg"], pady=10)
        bottom.pack(fill="x", padx=28)
        self._make_button(bottom, "← Back to Menu", self.build_main_window,
                          style="secondary", width=18).pack(side="left")

    # ------------------------------------------------------------------
    # SERVICIOS
    # ------------------------------------------------------------------

    def manage_services(self):
        self.clear_screen()
        self._make_header(self.root, "🛠  Service Management",
                          "Add, edit or remove services from the active catalogue")

        body = tk.Frame(self.root, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=28, pady=16)

        if not hasattr(self, '_editing_id'):
            self._editing_id = None

        form_card = self._make_card(body)
        form_card.pack(side="left", fill="y", padx=(0, 12))

        lbl_form = tk.Label(form_card, text="SERVICE DETAILS", font=("Segoe UI", 8, "bold"),
                          bg=COLORS["surface"], fg=COLORS["text_dim"])
        lbl_form.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ent_sname  = self._make_entry(form_card,   "Service Name", row=1)
        ent_sprice = self._make_entry(form_card,   "Base Price ($)", row=2)
        cb_stype   = self._make_combobox(form_card, "Type", row=3,
                                         values=["Room", "Equipment", "Consulting"])

        form_card.columnconfigure(1, weight=1)

        def save_service():
            try:
                name = ent_sname.get()
                price = validate_positive(ent_sprice.get(), "Base Price")
                stype = cb_stype.get()
                
                if self._editing_id is None:
                    max_id = 0
                    if self.servicios:
                        max_id = max(int(s.id) for s in self.servicios)
                    
                    new_id = str(max_id + 1)
                    type_map = {"Room": Sala, "Equipment": Equipo, "Consulting": Asesoria}
                    s = type_map[stype](new_id, name, price)
                    self.servicios.append(s)
                    log_info(f"Service {name} created with ID {new_id}.")
                else:
                    for i, s in enumerate(self.servicios):
                        if str(s.id) == self._editing_id:
                            type_map = {"Room": Sala, "Equipment": Equipo, "Consulting": Asesoria}
                            self.servicios[i] = type_map[stype](s.id, name, price)
                            break
                    log_info(f"Service ID {self._editing_id} updated.")
                    self._editing_id = None
                
                messagebox.showinfo("Success", "Operation completed successfully.")
                self.manage_services()
                
            except Exception as e:
                log_error(f"Service operation failed: {e}")
                messagebox.showerror("Error", str(e))

        def delete_service():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Selection", "Please select a service to delete.")
                return
            
            item = tree.item(selected)
            s_id = str(item['values'][0])
            
            if messagebox.askyesno("Confirm", f"Delete service ID {s_id}?"):
                self.servicios = [s for s in self.servicios if str(s.id) != s_id]
                log_info(f"Service ID {s_id} deleted.")
                self._editing_id = None
                self.manage_services()

        def on_select(event):
            selected = tree.selection()
            if not selected: return
            
            item = tree.item(selected)
            self._editing_id = str(item['values'][0])
            
            ent_sname.delete(0, tk.END)
            ent_sname.insert(0, item['values'][1])
            ent_sprice.delete(0, tk.END)
            ent_sprice.insert(0, str(item['values'][2]).replace('$', ''))
            
            raw_type = item['values'][3].split()[-1] 
            cb_stype.set(raw_type)
            
            btn_save.config(text="Update Service", bg=COLORS["accent2"])
            lbl_form.config(text=f"EDITING ID: {self._editing_id}", fg=COLORS["accent"])

        btn_save = self._make_button(form_card, "Add Service", save_service, style="primary", width=22)
        btn_save.grid(row=4, column=0, columnspan=2, pady=(14, 0), sticky="ew")

        self._make_button(form_card, "Delete Selected", delete_service, style="danger", width=22).grid(
            row=5, column=0, columnspan=2, pady=(8, 0), sticky="ew")

        list_card = tk.Frame(body, bg=COLORS["surface"], padx=16, pady=16)
        list_card.pack(side="left", fill="both", expand=True)

        tk.Label(list_card, text=f"SERVICE CATALOGUE  ({len(self.servicios)})",
                 font=("Segoe UI", 8, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text_dim"]).pack(anchor="w", pady=(0, 8))

        type_icons = {"Sala": "🏢 Room", "Equipo": "🖥 Equipment", "Asesoria": "💼 Consulting"}

        cols   = ("ID", "Name", "Base Price", "Type")
        labels = ("ID", "Name", "Base Price / Unit", "Type")
        tree_frame, tree = self._make_treeview(list_card, cols, labels, [40, 190, 140, 130], height=10)
        tree_frame.pack(fill="both", expand=True)

        tree.bind("<<TreeviewSelect>>", on_select)

        for i, s in enumerate(self.servicios):
            tag = "even" if i % 2 == 0 else "odd"
            tipo = type_icons.get(s.__class__.__name__, s.__class__.__name__)
            tree.insert("", tk.END, values=(s.id, s.name, f"${s.base_price:.2f}", tipo), tags=(tag,))

        bottom = tk.Frame(self.root, bg=COLORS["bg"], pady=10)
        bottom.pack(fill="x", padx=28)
        self._make_button(bottom, "← Back to Menu", self.build_main_window,
                          style="secondary", width=18).pack(side="left")

    # ------------------------------------------------------------------
    # RESERVAS
    # ------------------------------------------------------------------

    def manage_reservations(self):
        self.clear_screen()
        
        self._make_header(self.root, "📋  Panel de Control de Reservas", "Software FJ v2.0 — Gestión de Ingeniería")

        if not self.clientes or not self.servicios:
            messagebox.showwarning("Aviso", "Registre clientes y servicios antes de gestionar reservas.")
            return self.build_main_window()

        
        stats_frame = tk.Frame(self.root, bg=COLORS["bg"], pady=10)
        stats_frame.pack(fill="x", padx=32)

        total_money = sum((r.servicio.base_price * r._duration) * (1 - r.discount) for r in self.reservas)
        pendientes = len([r for r in self.reservas if r.status == "Pending"])
        completas = len([r for r in self.reservas if r.status == "Completed"])

        self._status_badge(stats_frame, len(self.reservas), "Total Reservas").pack(side="left", padx=5)
        self._status_badge(stats_frame, pendientes, "Pendientes").pack(side="left", padx=5)
        self._status_badge(stats_frame, completas, "Completadas").pack(side="left", padx=5)
        self._status_badge(stats_frame, f"${total_money:,.2f}", "Total Ganado").pack(side="left", padx=5)

        
        actions_bar = tk.Frame(self.root, bg=COLORS["bg"], pady=15)
        actions_bar.pack(fill="x", padx=32)

        
        self._make_button(actions_bar, "➕ Nueva Reserva", self.open_reserva_modal, style="success", width=18).pack(side="left")

       
        tk.Label(actions_bar, text="🔍 Buscar:", font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(side="left", padx=(20, 5))
        self.search_var = tk.StringVar()
        ent_search = tk.Entry(actions_bar, textvariable=self.search_var, font=FONTS["small"], bg=COLORS["input_bg"], fg=COLORS["text"], relief="flat", width=25)
        ent_search.pack(side="left", padx=5, ipady=4)
        self.search_var.trace_add("write", lambda *args: self.refresh_reserva_table())

        list_card = tk.Frame(self.root, bg=COLORS["surface"], padx=15, pady=15)
        list_card.pack(fill="both", expand=True, padx=32, pady=(0, 20))

        cols = ("ID", "Cliente", "Servicio", "Fecha", "Hora", "Dur", "Subtotal", "Total", "Status", "Acciones")
        widths = [60, 110, 110, 90, 60, 40, 80, 80, 90, 60]
        tree_frame, self.res_tree = self._make_treeview(list_card, cols, cols, widths, height=12)
        tree_frame.pack(fill="both", expand=True)

        
        self.res_tree.bind("<Button-1>", self.handle_table_click)
        self.refresh_reserva_table()

        bottom = tk.Frame(self.root, bg=COLORS["bg"], pady=10)
        bottom.pack(fill="x", padx=32)
        self._make_button(bottom, "← Volver al Menú", self.build_main_window, style="secondary", width=16).pack(side="left")

    def refresh_reserva_table(self):
        for item in self.res_tree.get_children():
            self.res_tree.delete(item)
        
        search_query = self.search_var.get().lower()
        
        for i, r in enumerate(self.reservas):
            if search_query and search_query not in r.cliente.name.lower() and search_query not in r.servicio.name.lower():
                continue

            subtotal = r.servicio.base_price * r._duration
            total_final = subtotal * (1 - r.discount)
            tag = "even" if i % 2 == 0 else "odd"
            
            self.res_tree.insert("", tk.END, values=(
                r.id_reserva, r.cliente.name, r.servicio.name,
                r.date.strftime("%Y-%m-%d"), r.date.strftime("%H:%M"), 
                r._duration, f"${subtotal:,.2f}", f"${total_final:,.2f}", r.status, "⋮"
            ), tags=(tag,))

    def handle_table_click(self, event):
        item_id = self.res_tree.identify_row(event.y)
        column = self.res_tree.identify_column(event.x)
        
        if item_id and column == "#10": # Columna Acciones
            res_id = self.res_tree.item(item_id)['values'][0]
            res_obj = next((r for r in self.reservas if r.id_reserva == res_id), None)
            
            menu = tk.Menu(self.root, tearoff=0, bg=COLORS["surface2"], fg=COLORS["text"])
            # 5. Llamar ventana de editar con datos cargados
            menu.add_command(label="✏️ Actualizar", command=lambda: self.open_reserva_modal(res_obj))
            # 6. Confirmación de eliminación
            menu.add_command(label="🗑️ Eliminar", command=lambda: self.confirm_deletion(res_obj))
            menu.post(event.x_root, event.y_root)

    def confirm_deletion(self, res_obj):
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la reserva {res_obj.id_reserva}?"):
            self.reservas.remove(res_obj)
            log_warning(f"Reserva {res_obj.id_reserva} eliminada.")
            self.manage_reservations()

    
    def open_reserva_modal(self, edit_obj=None):
        modal = tk.Toplevel(self.root)
        modal.title("Reserva - Software FJ" if not edit_obj else "Editar Reserva")
        modal.geometry("450x600")
        modal.configure(bg=COLORS["bg"])
        modal.transient(self.root)
        modal.grab_set()

        self._make_header(modal, "📝 Formulario Reserva")
        container = tk.Frame(modal, bg=COLORS["surface"], padx=20, pady=20)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        cli_labels = [f"{c.name} ({c.id})" for c in self.clientes]
        ser_labels = [f"{s.name} ({s.id})" for s in self.servicios]

        cb_cli = self._make_combobox(container, "Cliente", 0, cli_labels)
        cb_ser = self._make_combobox(container, "Servicio", 1, ser_labels)
        ent_dur = self._make_entry(container, "Duración (Horas)", 2)
        
        # 2. Campos de Fecha y Hora
        ent_date = self._make_entry(container, "Fecha (AAAA-MM-DD)", 3)
        ent_time = self._make_entry(container, "Hora (HH:MM)", 4)
        
        discount_map = {"No descuento 0%": 0.0, "Frecuente 5%": 0.05, "Empresa 12%": 0.12, "Cortesia 100%": 1.0}
        cb_dis = self._make_combobox(container, "Descuento", 5, list(discount_map.keys()))
        
        status_opts = ["Pending", "Confirmed", "Cancelled", "Completed"]
        cb_stat = self._make_combobox(container, "Estatus", 6, status_opts)

       
        if edit_obj:
            ent_dur.insert(0, str(edit_obj._duration))
            ent_date.insert(0, edit_obj.date.strftime("%Y-%m-%d"))
            ent_time.insert(0, edit_obj.date.strftime("%H:%M"))
            cb_stat.set(edit_obj.status)
            for i, label in enumerate(cli_labels):
                if f"({edit_obj.cliente.id})" in label: cb_cli.current(i)
            for i, label in enumerate(ser_labels):
                if f"({edit_obj.servicio.id})" in label: cb_ser.current(i)

        def save():
            try:
                dur = float(ent_dur.get())
                cli_id = cb_cli.get().split("(")[-1].strip(")")
                ser_id = cb_ser.get().split("(")[-1].strip(")")
                cli = self.get_cliente_by_id(cli_id)
                ser = self.get_servicio_by_id(ser_id)
                
                if edit_obj:
                    edit_obj._cliente = cli
                    edit_obj._servicio = ser
                    edit_obj._duration = dur
                    edit_obj._discount = discount_map[cb_dis.get()]
                    edit_obj._status = cb_stat.get()
                else:
                    res = Reserva(generate_id(), cli, ser, dur, discount=discount_map[cb_dis.get()])
                    res._status = cb_stat.get()
                    self.reservas.append(res)
                
                modal.destroy()
                self.manage_reservations()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        self._make_button(container, "Confirmar Registro", save, style="success").grid(row=7, column=0, columnspan=2, pady=20)


#############

    def test_system_resilience(self):
        """Aporte de Uvier: Valida la robustez del sistema y el control de acceso."""
        
        # 1. VERIFICACIÓN DE SEGURIDAD (VERSIÓN SILENCIOSA)
        # En lugar de mostrar un cuadro de error, simplemente retornamos si no hay login.
        # Esto evita interrumpir al usuario antes de que ingrese sus credenciales.
        if not hasattr(self, 'current_user') or self.current_user is None:
            return

        try:
            # 2. CONEXIÓN CON EL MÓDULO DE LÓGICA (Clase de la línea 277)
            # Se crea el objeto tester y se le pasa el logger para el archivo 'system.log'
            tester = ResilienceTester(logging.getLogger())
            
            # Ejecutamos la simulación de los 10 casos (Uvier, Nestor, Pepito, etc.)
            # report: lista de textos | ok: éxitos | fails: fallos
            report, ok, fails = tester.run_simulation(True)
            
            # 3. GENERACIÓN DEL REPORTE VISUAL
            # Resumen amigable con el conteo final de operaciones (en inglés para la UI)
            resumen = f"Resilience Simulation Finished.\n\nSuccess: {ok}\nControlled Failures: {fails}"
            
            # Mostramos el reporte detallado y el resumen final
            # Título genérico para mantener la unidad del software de grupo
            messagebox.showinfo("Engineering System Report", 
                                f"{'\n'.join(report)}\n\n{resumen}")

        except Exception as e:
            # MANEJO DE ERRORES CRÍTICOS
            # Registro obligatorio en el archivo log si algo falla en la interfaz
            logging.error(f"Error crítico en el módulo de resiliencia: {e}")
            messagebox.showerror("System Error", "An unexpected failure occurred. Please check system.log.")
            
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
    finally:
        logging.shutdown()