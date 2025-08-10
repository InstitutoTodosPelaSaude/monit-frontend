class UserAlreadyExists(Exception):
    def __init__(self, email: str):
        message = f"Usuário com o e-mail '{email}' já existe."
        super().__init__(message)