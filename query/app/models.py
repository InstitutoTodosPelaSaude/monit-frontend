from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Literal, Optional

class QueryParameters(BaseModel):
    question: str = Field(..., description="The user's question to generate the SQL query for.")
    project: Literal["ARBO", "RESPAT"] = Field(..., description="Must be 'RESPAT' or 'ARBO'.")
    table: Literal["combined"] = Field(..., description="Must be 'combined'.")
    configs: Optional[dict] = Field(None, description="Optional configuration settings, such as 'max_lines'.")

class FormatQueryParameters(BaseModel):
    sql_raw_query: str = Field(..., description="Raw SQL query to format")
    configs: Optional[dict] = Field(None, description="Optional configuration settings, such as 'max_lines'.")
