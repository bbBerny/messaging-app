import json
import customtkinter as ctk
from tkinter import messagebox
from client.tcp_client import TCPClient
from ui.menu_principal import MenuPrincipal

class RegistroVentana:
    def __init__(self, app):
        self.app = app
        self.client = None
        self.usuario_ingresado = ""

    def mostrar(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTk()
        self.window.title("Iniciar Sesión")
        self.window.geometry("300x260")

        # ---- Username / Email ----
        ctk.CTkLabel(self.window, text="Usuario o Email:").pack(pady=(10, 0))
        self.entry_usuario = ctk.CTkEntry(self.window)
        self.entry_usuario.pack(pady=(0, 10))

        # ---- Password ----
        ctk.CTkLabel(self.window, text="Contraseña:").pack()
        self.entry_password = ctk.CTkEntry(self.window, show="*")
        self.entry_password.pack(pady=(0, 10))

        ctk.CTkButton(
            self.window,
            text="Login",
            command=self.iniciar_sesion
        ).pack(pady=(5, 5))

        ctk.CTkLabel(self.window, text="¿No tienes una cuenta?").pack()
        ctk.CTkButton(
            self.window,
            text="Crear cuenta",
            command=self.enviar_a_crear_cuenta
        ).pack(pady=(0, 10))

        self.window.mainloop()

    def iniciar_sesion(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()

        if not (usuario and password):
            messagebox.showwarning("Datos incompletos", "Por favor, ingresa usuario/email y contraseña.")
            return

        try:
            self.client = TCPClient(host="10.7.11.159", port=3000)
            self.client.register_handler(self.manejar_respuesta_servidor)
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor: {e}")
            return

        self.usuario_ingresado = usuario
        payload = {
            "action": 0,
            "key": usuario,
            "password": password
        }

        self.client.send_message(json.dumps(payload))

    def manejar_respuesta_servidor(self, mensaje):
        print("📨 Mensaje recibido del servidor:", json.dumps(mensaje, indent=2))

        code = mensaje.get("response_code", 0)
        if code != 200:
            messagebox.showerror("Login fallido", mensaje.get("response_text", "Error desconocido."))
            return

        token = mensaje.get("token")
        user_id = mensaje.get("user_id")

        if not token or user_id is None:
            messagebox.showerror("Login fallido", "Faltan datos del servidor (token o user_id).")
            return

        # Guardar datos en la aplicación
        self.app.set_token(token)
        self.app.set_user_id(user_id)
        self.app.set_usuario(self.usuario_ingresado)
        self.app.set_client(self.client)

        # Transición segura al menú principal
        self.window.after(0, self.ir_a_menu_principal)

    def ir_a_menu_principal(self):
        self.window.destroy()
        MenuPrincipal(self.app).mostrar()


    def enviar_a_crear_cuenta(self):
        from ui.Create_account import Create_account
        self.window.destroy()
        Create_account(self.app).mostrar()
