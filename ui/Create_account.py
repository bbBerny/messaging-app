import json
import customtkinter as ctk
from tkinter import messagebox
from client.tcp_client import TCPClient

class Create_account:
    def __init__(self, app):
        self.app = app
        self.client = None
        self.username = ""
        self.password = ""

    def mostrar(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTk()
        self.window.title("Create account")
        self.window.geometry("300x320")

        # ---- Name ----
        ctk.CTkLabel(self.window, text="Nombre:").pack(pady=(10, 0))
        self.entry_nombre = ctk.CTkEntry(self.window)
        self.entry_nombre.pack(pady=(0, 10))

        # ---- Password ----
        ctk.CTkLabel(self.window, text="Password:").pack()
        self.entry_password = ctk.CTkEntry(self.window, show="*")
        self.entry_password.pack(pady=(0, 10))

        # ---- Email ----
        ctk.CTkLabel(self.window, text="Email:").pack()
        self.entry_email = ctk.CTkEntry(self.window)
        self.entry_email.pack(pady=(0, 10))

        # ---- Buttons ----
        ctk.CTkButton(
            self.window,
            text="Crear cuenta",
            command=self.CrearCuenta
        ).pack(pady=10)

        ctk.CTkButton(
            self.window,
            text="Back",
            command=self.GoBack
        ).pack(pady=10)

        self.window.mainloop()

    def CrearCuenta(self):
        from ui.registro import RegistroVentana

        username = self.entry_nombre.get().strip()
        password = self.entry_password.get().strip()
        email = self.entry_email.get().strip()

        if not (username and password and email):
            messagebox.showwarning("Datos incompletos", "Por favor, llena todos los campos.")
            return

        try:
            self.client = TCPClient(host="10.7.11.159", port=3000)
            self.client.register_handler(self.manejar_respuesta_servidor)
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor: {e}")
            return

        self.username = username
        self.password = password

        payload = {
            "action": 2,
            "username": username,
            "password": password,
            "email": email
        }

        self.client.send_message(json.dumps(payload))

    def manejar_respuesta_servidor(self, mensaje):
        print("📨 Mensaje recibido del servidor:", json.dumps(mensaje, indent=2))

        code = mensaje.get("response_code")
        text = mensaje.get("response_text", "")
        token = mensaje.get("token")

        if code == 200 and token:
            # Registro exitoso + login automático
            self.app.set_token(token)
            self.app.set_usuario(self.username)
            self.app.client = self.client

            self.window.destroy()
            from ui.registro import RegistroVentana
            RegistroVentana(self.app).mostrar()

        elif code == 200:
            # Registro exitoso pero sin token → hacer login
            payload_login = {
                "action": 0,
                "username": self.username,
                "password": self.password
            }
            self.client.send_message(json.dumps(payload_login))

        else:
            messagebox.showerror("Error", f"{text}")

    def GoBack(self):
        from ui.registro import RegistroVentana
        self.window.destroy()
        RegistroVentana(self.app).mostrar()
