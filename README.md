# ChatRoom Distribuido (Front-end 2) - Pimientos Company

## Descripción del Proyecto
Sistema de chat distribuido desarrollado para Pimientos Company IS de GC que incluye:
- Autenticación de usuarios (registro/login)
- E-Lobby con lista de usuarios y chatrooms
- Chatrooms con funcionalidades para usuarios y coordinadores
- Arquitectura distribuida con balanceo de carga

## Equipo FrontEnd 2
- Diego Sebastian Montoya Rodríguez (0258630)
- Ana Maria Guzman Solis (0252231)
- Jose Bernardo Sandoval Martinez (0253019)

## Estructura del Código
```python
client/
    tcp_client.py # Manejo de conexión TCP con el backend
ui/
    Create_account.py # Ventana de creación de cuentas
    menu_principal.py # Lista de chats y creación de grupos
    registro.py # Ventana de login
    ventana_chat.py # Interfaz de chat
    app.py # Clase principal de la aplicación
    main.py # Punto de entrada
````
## Protocolos Implementados
1. **Cliente-Servidor (TCP/JSON)**
   - Mensajes JSON con campo `action`
   - Autenticación con JWT
2. **Servidor-Backend (TCP/JSON)**
   - Validación e intermediación
3. **Descubrimiento de Servicios (UDP)**
   - Heartbeats para balanceo de carga

## Requisitos
- Python 3.8
- CustomTkinter
- Conexión al servidor lógico (10.7.6.109:3000)

## Instalación
```bash
pip install customtkinter
python main.py
