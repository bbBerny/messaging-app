class ChatApp:
    def __init__(self):
        self.nombre = ""
        self.token = None
        self.client = None
        self.user_id = None
        self.grupos = []
        self.modo_oscuro = True 

    def set_token(self, tok: str):
        self.token = tok

    def set_usuario(self, nombre):
        self.nombre = nombre

    def set_client(self, client):
        self.client = client
    
    def set_user_id(self, uid: int):  
        self.user_id = uid    
