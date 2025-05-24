# ui/ventana_chat.py
import json
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

class VentanaChat:
    def __init__(self, app, chat_name, volver):
        self.app = app
        self.chat_name = chat_name
        self.volver = volver

    def mostrar(self):
        # Appearance
        ctk.set_appearance_mode("dark" if self.app.modo_oscuro else "light")
        ctk.set_default_color_theme("blue")

        # Main window
        self.window = ctk.CTk()
        self.window.title(f"{self.chat_name} — {self.app.nickname}")
        self.window.geometry("750x600")

        # Register so incoming chat messages land in this UI
        self.app.client.register_handler(self.on_server_message)


        # Scrollable frame for messages
        self.frame_mensajes = ctk.CTkScrollableFrame(self.window, height=450)
        self.frame_mensajes.pack(padx=10, pady=10, fill="both", expand=True)

        # Input bar
        frame_entrada = ctk.CTkFrame(self.window)
        frame_entrada.pack(padx=10, pady=(0,10), fill="x")

        self.entry = ctk.CTkEntry(frame_entrada, placeholder_text="Escribe un mensaje…")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.entry.bind("<Return>", lambda e: self.enviar())

        ctk.CTkButton(frame_entrada, text="Enviar", command=self.enviar).pack(side="left", padx=5)
        ctk.CTkButton(frame_entrada, text="← Volver", command=self.salir).pack(side="left", padx=5)

        self.window.mainloop()

    def agregar_mensaje_local(self, texto):
        """Display a local message in the scroll frame."""
        hora = datetime.now().strftime("%I:%M %p")
        label = ctk.CTkLabel(
            self.frame_mensajes,
            text=f"[{hora}] {texto}",
            wraplength=600,
            justify="left"
        )
        label.pack(anchor="w", pady=2)

    def enviar(self):
        texto = self.entry.get().strip()
        if not texto:
            return  # nothing to send

        # 1) Check we have a connected client and a valid token
        if not getattr(self.app, "client", None):
            messagebox.showerror("Error", "No estás conectado al servidor.")
            return
        if not getattr(self.app, "token", None):
            messagebox.showerror("Error", "Token de autenticación no disponible.")
            return

        # 2) Build the MSG_SEND payload (action 3)
        payload = {
            "action": 3,
            "token": self.app.token,
            "chat": self.chat_name,
            "msg": texto
        }

        # 3) Send it to the server
        try:
            # newline‐delimited JSON
            self.app.client.send_message(json.dumps(payload) + "\n")
        except Exception as e:
            messagebox.showerror("Error al enviar", f"No se pudo enviar el mensaje:\n{e}")
            return

        # 4) Display locally
        self.agregar_mensaje_local(f"{self.app.nickname}: {texto}")
        self.entry.delete(0, "end")

    def salir(self):
        self.window.destroy()
        self.volver(self.app).mostrar()


    def on_server_message(self, msg: dict):
        # only handle messages for this chat
        if msg.get("action")==3 and msg.get("chat")==self.chat_name:
            texto = f"{msg.get('from')}: {msg.get('msg')}"
            # schedule on the Tk main thread
            self.window.after(0, self.agregar_mensaje_local, texto)

