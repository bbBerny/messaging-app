import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

def run_gui(dummy_client=None):
    grupos = []  # Lista para guardar grupos creados

    def open_chat_window(nombre, nickname, chat_name=None):
        window = tk.Tk()
        title = f"MensajeApp - Cliente de Chat ({nickname})"
        if chat_name:
            title += f" - {chat_name}"
        window.title(title)
        window.geometry("400x500")

        chat_display = scrolledtext.ScrolledText(window, wrap=tk.WORD, state="normal")
        chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        entry_message = tk.Entry(window)
        entry_message.pack(padx=10, pady=(0, 10), fill=tk.X)
        entry_message.focus()

        def send_message():
            msg = entry_message.get()
            if msg:
                chat_display.insert(tk.END, f"{nickname} ({nombre}): {msg}\n")
                entry_message.delete(0, tk.END)
                chat_display.insert(tk.END, "Servidor: (simulado) Mensaje recibido.\n")

        send_button = tk.Button(window, text="Enviar", command=send_message)
        send_button.pack(padx=10, pady=(0, 10))

        def salir_al_menu():
            window.destroy()
            open_main_menu(nombre, nickname)

        btn_salir = tk.Button(window, text="Salir al menú", command=salir_al_menu)
        btn_salir.pack(pady=(0,10))

        window.mainloop()

    def open_main_menu(nombre, nickname):
        main_win = tk.Tk()
        main_win.title(f"Bienvenido, {nickname}")
        main_win.geometry("300x400")

        tk.Label(main_win, text="Tus chats:", font=("Arial", 14)).pack(pady=10)

        chats_listbox = tk.Listbox(main_win)
        chats_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        def refresh_chats():
            chats_listbox.delete(0, tk.END)
            for grupo in grupos:
                chats_listbox.insert(tk.END, grupo)

        refresh_chats()

        def abrir_chat_seleccionado(event=None):
            selected = chats_listbox.curselection()
            if selected:
                chat_name = chats_listbox.get(selected[0])
                main_win.destroy()
                open_chat_window(nombre, nickname, chat_name=chat_name)

        chats_listbox.bind("<Double-Button-1>", abrir_chat_seleccionado)

        def crear_grupo():
            nuevo_grupo = simpledialog.askstring("Crear grupo", "Nombre del nuevo grupo:", parent=main_win)
            if nuevo_grupo:
                if nuevo_grupo not in grupos:
                    grupos.append(nuevo_grupo)
                    refresh_chats()
                else:
                    messagebox.showwarning("Grupo existente", "Ya existe un grupo con ese nombre.")

        btn_create_group = tk.Button(main_win, text="Crear grupo", command=crear_grupo)
        btn_create_group.pack(pady=10)

        main_win.mainloop()

    # Ventana de registro
    reg_window = tk.Tk()
    reg_window.title("Registro de Usuario")
    reg_window.geometry("300x150")

    tk.Label(reg_window, text="Nombre:").pack(pady=(10,0))
    entry_nombre = tk.Entry(reg_window)
    entry_nombre.pack()

    tk.Label(reg_window, text="Nickname:").pack(pady=(10,0))
    entry_nick = tk.Entry(reg_window)
    entry_nick.pack()

    def registrar():
        nombre = entry_nombre.get().strip()
        nick = entry_nick.get().strip()
        if nombre and nick:
            reg_window.destroy()
            open_main_menu(nombre, nick)
        else:
            messagebox.showwarning("Datos incompletos", "Por favor, ingresa nombre y nickname.")

    btn_registrar = tk.Button(reg_window, text="Registrar", command=registrar)
    btn_registrar.pack(pady=10)

    reg_window.mainloop()

run_gui()
