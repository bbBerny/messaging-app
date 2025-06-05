# ui/ventana_chat.py
import json
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

class VentanaChat:
    def __init__(self, app, chat_id, chat_name, volver):
        self.app = app
        self.chat_id = chat_id
        self.chat_name = chat_name
        self.volver = volver
        self.last_timestamp = "2023-01-01 00:00:00"  # para filtrar mensajes nuevos

    def mostrar(self):
        ctk.set_appearance_mode("dark" if self.app.modo_oscuro else "light")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTk()
        self.window.geometry("750x600")
        self.window.title(f"Chat: {self.chat_name}")

        self.frame_mensajes = ctk.CTkScrollableFrame(self.window, height=450)
        self.frame_mensajes.pack(padx=10, pady=10, fill="both", expand=True)

        frame_entrada = ctk.CTkFrame(self.window)
        frame_entrada.pack(padx=10, pady=(0,10), fill="x")

        self.entry = ctk.CTkEntry(frame_entrada, placeholder_text="Escribe un mensaje…")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.entry.bind("<Return>", lambda e: self.enviar())

        ctk.CTkButton(frame_entrada, text="Enviar", command=self.enviar).pack(side="left", padx=5)
        ctk.CTkButton(frame_entrada, text="← Volver", command=self.salir).pack(side="left", padx=5)

        self.app.client.register_handler(self.on_server_message)

        self.obtener_mensajes_chat()
        self.recargar_historial()  # empieza recarga automática

        self.window.mainloop()

    def obtener_mensajes_chat(self):
        payload = {
            "action": 8,
            "chat_id": self.chat_id,
            "last_update_timestamp": self.last_timestamp,
            "token": self.app.token
        }
        self.app.client.send_message(json.dumps(payload))

    def recargar_historial(self):
        self.obtener_mensajes_chat()
        self.window.after(5000, self.recargar_historial)  # 5 segundos

    def agregar_mensaje_local(self, texto):
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
            return

        if not getattr(self.app, "client", None):
            messagebox.showerror("Error", "No estás conectado al servidor.")
            return
        if not getattr(self.app, "token", None):
            messagebox.showerror("Error", "Token de autenticación no disponible.")
            return

        payload = {
            "action": 6,
            "chat_id": self.chat_id,
            "sender_id": self.app.user_id,
            "content": texto,
            "message_type": "text",
            "token": self.app.token
        }

        try:
            self.app.client.send_message(json.dumps(payload))
            self.entry.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Error al enviar", f"No se pudo enviar el mensaje:\n{e}")

    def salir(self):
        self.window.destroy()
        self.volver(self.app).mostrar()

    def on_server_message(self, msg: dict):
        if msg.get("action") == 8 and "messages_array" in msg:
            for mensaje in msg["messages_array"]:
                contenido = f"{mensaje['sender_username']}: {mensaje['content']}"
                self.window.after(0, self.agregar_mensaje_local, contenido)
                # Actualizar timestamp si existe
                if "created_at" in mensaje:
                    self.last_timestamp = mensaje["created_at"]

        elif msg.get("action") == 6 and msg.get("chat_id") == self.chat_id:
            contenido = f"{msg.get('sender_username', 'usuario')}: {msg.get('content')}"
            self.window.after(0, self.agregar_mensaje_local, contenido)
