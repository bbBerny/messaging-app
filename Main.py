##from client.tcp_client import TCPClient
from app import ChatApp
from ui.registro import RegistroVentana


if __name__ == "__main__":  
     ## client = TCPClient()
    app = ChatApp()
    RegistroVentana(app).mostrar()
