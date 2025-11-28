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

class TableIDNotFound(Exception):
    def __init__(self, id: str):
        message = f"Tabela com ID='{id}' não encontrada."
        super().__init__(message)

class QueryIDNotFound(Exception):
    def __init__(self, id: str):
        message = f"Query com ID='{id}' não encontrada."
        super().__init__(message)

class QueryCannotBeExecuted(Exception):
    def __init__(self, query_id, reason: str):
        message = f"Query com ID='{query_id}' não pôde ser executada - {reason}."
        super().__init__(message)