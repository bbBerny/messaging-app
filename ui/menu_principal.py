# menu_principal.py
import json
import customtkinter as ctk
from tkinter import simpledialog, messagebox
from ui.ventana_chat import VentanaChat

class MenuPrincipal:
    def __init__(self, app):
        self.app = app

    def mostrar(self):
        ctk.set_appearance_mode("dark" if self.app.modo_oscuro else "light")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTk()
        self.window.title(f"Bienvenido, {self.app.nickname}")
        self.window.geometry("350x450")

        ctk.CTkLabel(self.window, text="Tus chats", font=("Arial", 18)).pack(pady=15)

        self.chats_listbox = ctk.CTkScrollableFrame(self.window, height=250)
        self.chats_listbox.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        self.actualizar_chats()

        ctk.CTkButton(self.window, text="Crear Grupo", command=self.crear_grupo).pack(pady=10)
        ctk.CTkButton(self.window, text="Modo Claro/Oscuro", command=self.toggle_modo).pack(pady=10)

        self.window.mainloop()

    def actualizar_chats(self):
        for widget in self.chats_listbox.winfo_children():
            widget.destroy()

        for grupo in self.app.grupos:
            btn = ctk.CTkButton(
                self.chats_listbox,
                text=grupo,
                command=lambda g=grupo: self.abrir_chat(g)
            )
            btn.pack(fill="x", padx=5, pady=5)

    def crear_grupo(self):
        nuevo_grupo = simpledialog.askstring("Crear grupo", "Nombre del nuevo grupo:")
        if nuevo_grupo:
            if nuevo_grupo not in self.app.grupos:
                self.app.grupos.append(nuevo_grupo)
                self.actualizar_chats()
            else:
                messagebox.showwarning("Ya existe", "Ese grupo ya existe.")

    def abrir_chat(self, grupo):
        # 1) Sanity check: ensure we have an open client and a token
        if not hasattr(self.app, "client") or self.app.client is None:
            messagebox.showerror("Error", "No hay conexión al servidor. Vuelve a iniciar sesión.")
            return
        if not hasattr(self.app, "token") or not self.app.token:
            messagebox.showerror("Error", "Token de autenticación faltante.")
            return

        # 2) Build the JOIN-CHAT payload (action 5)
        join_req = {
            "action": 5,
            "token": self.app.token,
            "chat": grupo
        }
        try:
            self.app.client.send_message(json.dumps(join_req) + "\n")
        except Exception as e:
            messagebox.showerror("Error de envío", f"No se pudo enviar la solicitud: {e}")
            return

        # 3) Read and parse the server's response
        try:
            raw = self.app.client.sock.recv(4096).decode().strip()
            resp = json.loads(raw)
        except Exception:
            messagebox.showerror("Error", "Respuesta inválida al unir al chat.")
            return

        # 4) Handle failure
        if not resp.get("success", False):
            messagebox.showerror("Unión fallida", resp.get("error", "No se pudo unir al chat"))
            return

        # 5) Success! Open the chat window
        self.window.destroy()
        VentanaChat(self.app, grupo, volver=MenuPrincipal).mostrar()

    def toggle_modo(self):
        self.app.modo_oscuro = not self.app.modo_oscuro
        self.window.destroy()
        self.mostrar()
