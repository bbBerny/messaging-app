
import json
import customtkinter as ctk
from tkinter import simpledialog, messagebox
from ui.ventana_chat import VentanaChat

class MenuPrincipal:
    def __init__(self, app):
        self.app = app

    def mostrar(self):
        # 1. Mostrar ventana inmediatamente
        ctk.set_appearance_mode("dark" if self.app.modo_oscuro else "light")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTk()
        self.window.title("Menú Principal")
        self.window.geometry("350x450")

        ctk.CTkLabel(self.window, text="Tus chats", font=("Arial", 18)).pack(pady=15)

        self.chats_listbox = ctk.CTkScrollableFrame(self.window, height=250)
        self.chats_listbox.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        self.actualizar_chats()

        ctk.CTkButton(self.window, text="Crear Grupo", command=self.crear_grupo).pack(pady=10)
        ctk.CTkButton(self.window, text="Modo Claro/Oscuro", command=self.toggle_modo).pack(pady=10)

        # 2. Después de abrir la ventana, solicitar chats
        def solicitar_chats():
            print("🔁 Solicitando chats con user_id:", self.app.user_id)

            getchats_payload = {
                "action": 7,
                "user_id": self.app.user_id,
                "last_update_timestamp": None,
                "token": self.app.token
            }

            def handler_en_main(mensaje):
                print("📩 Handler ejecutado (desde hilo principal)")
                self.window.after(0, lambda: self.manejar_respuesta_lista_chats(mensaje))

            try:
                self.app.client.register_handler(handler_en_main)
                self.app.client.send_message(json.dumps(getchats_payload))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo solicitar la lista de chats:\n{e}")

        self.window.after(100, solicitar_chats)

        # 3. Iniciar ventana
        self.window.mainloop()

    def manejar_respuesta_lista_chats(self, resp):
        print("📥 Respuesta del servidor:", json.dumps(resp, indent=2))

        if isinstance(resp, list):
            self.app.grupos = [
                {"chat_id": c["chat_id"], "chat_name": c["chat_name"]}
                for c in resp
            ]
        elif isinstance(resp, dict) and "chats_array" in resp:
            self.app.grupos = [
                {"chat_id": c["chat_id"], "chat_name": c["chat_name"]}
                for c in resp["chats_array"]
            ]
        else:
            messagebox.showerror("Error", "Formato de respuesta no reconocido.")
            return

        self.actualizar_chats()

    def actualizar_chats(self):
        for widget in self.chats_listbox.winfo_children():
            widget.destroy()

        for grupo in self.app.grupos:
            btn = ctk.CTkButton(
                self.chats_listbox,
                text=grupo["chat_name"],
                command=lambda g=grupo: self.abrir_chat(g["chat_id"], g["chat_name"])
            )
            btn.pack(fill="x", padx=5, pady=5)

    def crear_grupo(self):
        chat_name = simpledialog.askstring("Crear grupo", "Nombre del nuevo grupo:")
        if not chat_name:
            return

        participantes_str = simpledialog.askstring(
            "Participantes",
            "Lista de user_id (separados por comas), ej: 17,23,42:",
            parent=self.window
        )
        if not participantes_str:
            return

        try:
            participant_ids = [int(x.strip()) for x in participantes_str.split(",") if x.strip()]
        except:
            messagebox.showerror("Error", "IDs inválidos. Deben ser números separados por comas.")
            return

        if self.app.user_id not in participant_ids:
            participant_ids.insert(0, self.app.user_id)

        # Registrar handler para respuesta del servidor
        def handler_en_main(mensaje):
            print("📩 Handler respuesta creación:", json.dumps(mensaje, indent=2))
            self.window.after(0, lambda: self.manejar_respuesta_crear_grupo(mensaje))

        self.app.client.register_handler(handler_en_main)

        create_payload = {
            "action": 4,
            "is_group": True,
            "chat_name": chat_name,
            "created_by": self.app.user_id,
            "participant_ids": participant_ids,
            "token": self.app.token
        }

        self.chat_name_temp = chat_name
        self.app.client.send_message(json.dumps(create_payload))

    def manejar_respuesta_crear_grupo(self, mensaje):
        print("📨 Respuesta acción 4:", json.dumps(mensaje, indent=2))

        if mensaje.get("response_code") != 200:
            messagebox.showerror("Error", mensaje.get("response_text", "No se pudo crear el grupo."))
            return

        # Agregar grupo a la UI aunque no se reciba chat_id
        self.app.grupos.append({
            "chat_id": -1,
            "chat_name": self.chat_name_temp
        })

        self.actualizar_chats()
        messagebox.showinfo("Éxito", f"Grupo '{self.chat_name_temp}' creado exitosamente.")

    def abrir_chat(self, chat_id, chat_name):
        if not getattr(self.app, "client", None):
            messagebox.showerror("Error", "No hay conexión al servidor. Vuelve a iniciar sesión.")
            return

        self.window.destroy()
        VentanaChat(self.app, chat_id, chat_name, volver=MenuPrincipal).mostrar()

    def toggle_modo(self):
        self.app.modo_oscuro = not self.app.modo_oscuro
        self.window.destroy()
        self.mostrar()

