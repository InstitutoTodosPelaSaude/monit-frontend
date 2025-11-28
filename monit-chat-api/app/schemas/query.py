from pydantic import BaseModel
from app.models.query import QueryResult

class QueryUpdateResult(BaseModel):
    id: str
    query_result: QueryResult