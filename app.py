class ChatApp:
    def __init__(self):
        self.nombre = ""
        self.nickname = ""
        self.token = None
        self.client = None
        self.grupos = []
        self.modo_oscuro = True 

    def set_token(self, tok: str):
        self.token = tok

    def set_usuario(self, nombre, nickname):
        self.nombre = nombre
        self.nickname = nickname

    def set_client(self, client):
        self.client = client
