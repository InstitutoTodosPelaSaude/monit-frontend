from pydantic import BaseModel, model_validator

class GenereateNameForChatResponse(BaseModel):
    name: str

class SQLTableSelectionResponse(BaseModel):
    tables: list[str]

class SQLGeneratedResponse(BaseModel):
    query: str = "<INVALID>"
    is_a_valid_sql_question: bool = False

    @model_validator(mode='after')
    def check_valid_sql_question(self):
        if not self.is_a_valid_sql_question:
           self.query = "<INVALID>" 
        return self