# tcp_client.py
import socket
import threading
import json

class TCPClient:
    def __init__(self, host='10.7.3.231', port=3001):
        """
        host: address of the load-balancer front end
        port: its TCP port (3001 by default)
        """
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        # for dispatching parsed JSON messages
        self.handlers = []

        # buffer for partial reads
        self._recv_buffer = ""

        self.running = True
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def send_message(self, msg: str):
        """
        msg: a JSON-string ending in '\n'
        """
        try:
            self.sock.sendall(msg.encode())
        except Exception as e:
            print(f"❌ Error sending message: {e}")

    def register_handler(self, handler):
        """
        handler: a callable taking one argument (the parsed JSON dict)
        """
        self.handlers.append(handler)

    def _receive_loop(self):
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    # connection closed
                    self.running = False
                    break

                # accumulate into buffer
                self._recv_buffer += data.decode()

                # process any full lines
                while "\n" in self._recv_buffer:
                    line, self._recv_buffer = self._recv_buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        print(f"⚠️  Malformed JSON received: {line}")
                        continue

                    # dispatch to all handlers
                    for h in self.handlers:
                        try:
                            h(msg)
                        except Exception as e:
                            print(f"⚠️  Handler error: {e}")

            except Exception as e:
                print(f"❌ Error receiving data: {e}")
                self.running = False
                break

    def close(self):
        self.running = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass
