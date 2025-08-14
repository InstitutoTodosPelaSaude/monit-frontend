from pydantic import BaseModel, model_validator
from typing import Literal, Any

from datetime import datetime
from pydantic import BaseModel, Field, model_validator, model_serializer, AliasChoices
import hashlib

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

class QueryResult(BaseModel):

    id: str = Field(
        default_factory=lambda: hashlib.sha256(datetime.now().isoformat().encode()).hexdigest(), 
        validation_alias=AliasChoices('id', '_id')
    )
    query_id: str
    last_executed_at: datetime = Field(default_factory=datetime.now)
    data: list[Any]
    columns: list[str]

class SQLQuery(BaseModel):
    id: str = Field(
        default_factory=lambda: hashlib.sha256(datetime.now().isoformat().encode()).hexdigest(), 
        validation_alias=AliasChoices('id', '_id')
    )
    query: str
    type: Literal["QUERY"] = "QUERY"
    query_result: QueryResult | None = None

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        dict_repr = dict(self)
        dict_repr['_id'] = dict_repr['id']
        del dict_repr['id']
        return dict_repr