class UserAlreadyExists(Exception):
    def __init__(self, email: str):
        message = f"Usuário com o e-mail '{email}' já existe."
        super().__init__(message)

class UserIDNotFound(Exception):
    def __init__(self, id: str):
        message = f"Usuário com ID='{id}' não encontrado."
        super().__init__(message)

class UserIDNotFoundOrInvalidPassword(Exception):
    def __init__(self, id: str):
        message = f"Usuário com ID='{id}' não encontrado."
        super().__init__(message)

class ChatIDNotFound(Exception):
    def __init__(self, id: str):
        message = f"Chat com ID='{id}' não encontrado."
        super().__init__(message)

class TableAlreadyExists(Exception):
    def __init__(self, table: str):
        message = f"Tabela com nome='{table}' já existe."
        super().__init__(message)
    