# tcp_client.py
import socket
import threading
import json
from client.cesar_cipher import cesar_encrypt, cesar_decrypt  # Importar funciones de cifrado

class TCPClient:
    def __init__(self, host='10.7.6.109', port=3000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        self.handlers = []
        self._recv_buffer = ""
        self.running = True

        threading.Thread(target=self._receive_loop, daemon=True).start()

    def send_message(self, msg: str):
        """
        Envía un mensaje JSON (como string), aplicando cifrado César antes de enviarlo.
        """
        try:
            encrypted = cesar_encrypt(msg + "\n")  # Agrega salto de línea y cifra
            self.sock.sendall(encrypted.encode())
        except Exception as e:
            print(f"❌ Error sending message: {e}")

    def register_handler(self, handler):
        """
        Permite registrar funciones para manejar mensajes del servidor.
        """
        self.handlers.append(handler)

    def _receive_loop(self):
        """
        Hilo que escucha mensajes del servidor, aplicando descifrado y decodificación JSON.
        """
        decoder = json.JSONDecoder()

        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    self.running = False
                    break

                decrypted = cesar_decrypt(data.decode())  # Aplicar descifrado
                self._recv_buffer += decrypted

                while self._recv_buffer:
                    try:
                        msg, index = decoder.raw_decode(self._recv_buffer)
                        self._recv_buffer = self._recv_buffer[index:].lstrip()

                        for h in self.handlers:
                            try:
                                h(msg)
                            except Exception as e:
                                print(f"⚠️ Handler error: {e}")

                    except json.JSONDecodeError:
                        # El mensaje aún no está completo
                        break

            except Exception as e:
                print(f"❌ Error receiving data: {e}")
                self.running = False
                break

    def close(self):
        """
        Cierra la conexión de forma segura.
        """
        self.running = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass
