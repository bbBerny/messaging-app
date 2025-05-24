import json
import customtkinter as ctk
from tkinter import messagebox
from ui.menu_principal import MenuPrincipal
from client.tcp_client import TCPClient

class RegistroVentana:
    def __init__(self, app):
        self.app = app
        # we’ll hold the TCPClient here so later windows can reuse it
        self.client = None

    def mostrar(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTk()
        self.window.title("Registro de Usuario")
        self.window.geometry("300x240")

        # ---- Name / Nickname ----
        ctk.CTkLabel(self.window, text="Nombre:").pack(pady=(10, 0))
        self.entry_nombre = ctk.CTkEntry(self.window)
        self.entry_nombre.pack(pady=(0, 10))

        ctk.CTkLabel(self.window, text="Nickname:").pack()
        self.entry_nick = ctk.CTkEntry(self.window)
        self.entry_nick.pack(pady=(0, 10))

        # ---- Password ----
        ctk.CTkLabel(self.window, text="Password:").pack()
        self.entry_password = ctk.CTkEntry(self.window, show="*")
        self.entry_password.pack(pady=(0, 10))

        ctk.CTkButton(
            self.window,
            text="Registrar",
            command=self.registrar
        ).pack(pady=10)

        self.window.mainloop()

    def registrar(self):
        nombre   = self.entry_nombre.get().strip()
        nick     = self.entry_nick.get().strip()
        password = self.entry_password.get().strip()

        if not (nombre and nick and password):
            messagebox.showwarning(
                "Datos incompletos",
                "Por favor, ingresa nombre, nickname y password."
            )
            return

        # 1) Open connection to the load-balancer front end
        try:
            self.client = TCPClient(host="10.7.3.231", port=3001)
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor: {e}")
            return

        # 2) Build & send REGISTER payload
        #    See backend ACTIONS enum: REGISTER = 2 :contentReference[oaicite:1]{index=1}
        register_payload = {
            "action": 2,
            "username": nick,
            "password": password
        }
        # newline-delimited JSON
        self.client.send_message(json.dumps(register_payload) + "\n")

        # 3) Wait synchronously for response
        resp_raw = self.client.sock.recv(1024).decode().strip()
        try:
            resp = json.loads(resp_raw)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Respuesta inválida del servidor al registrar.")
            return

        if not resp.get("success", False):
            messagebox.showerror("Registro fallido", resp.get("error", "Error desconocido"))
            return

        # 4) On register success, immediately LOGIN
        login_payload = {
            "action": 0,
            "username": nick,
            "password": password
        }
        self.client.send_message(json.dumps(login_payload) + "\n")

        resp_raw = self.client.sock.recv(1024).decode().strip()
        try:
            resp = json.loads(resp_raw)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Respuesta inválida del servidor al iniciar sesión.")
            return

        if not resp.get("success", False):
            messagebox.showerror("Login fallido", resp.get("error", "Credenciales inválidas"))
            return

        # 5) Store token and user info in app state
        token = resp.get("token")
        self.app.set_token(token)
        self.app.set_usuario(nombre, nick)

        # 6) Hand off the same TCPClient to the rest of the app
        self.app.client = self.client

        # 7) Close registration and open main menu
        self.window.destroy()
        MenuPrincipal(self.app).mostrar()
