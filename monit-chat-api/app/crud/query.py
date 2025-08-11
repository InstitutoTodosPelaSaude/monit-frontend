from pydantic import BaseModel, model_validator
from typing import List, Literal
from app.crud.database import MongoConnection

from openai import OpenAI


class SQLGeneratedResponse(BaseModel):
    query: str = "<INVALID>"
    is_a_valid_sql_question: bool = False

    @model_validator(mode='after')
    def check_valid_sql_question(self):
        if not self.is_a_valid_sql_question:
           self.query = "<INVALID>" 
        return self
    
class SQLTableSelectionResponse(BaseModel):
    tables: list[str]


client = OpenAI()

def select_tables_that_can_answer_this_question(question):

    db = MongoConnection.get_client()
    db_collection = db.chat

    tables = list(
        db_collection
        .find(
            {'type': 'TABLE'},
            {'name':1, 'description': 1}
        )
    )

    tables_prompt = "\n".join( [ f"Name: {table['name']} Description: {table['description']}" for table in tables ] )
    tables_prompt = f"\n{tables_prompt}"

    response = client.responses.parse(
        model="gpt-4o",
        input=[
            {
                "role": "system", 
                "content": f"Based on the table's descriptions, select a list of tables that can be used to answer the user's question with a SQL query. If no table suits the task, return a empty list. {tables_prompt}"
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        text_format=SQLTableSelectionResponse
    )

    selected_tables = [
        table for table in tables
        if table['name'] in response.output_parsed.tables
    ]

    return selected_tables

def generate_sql_query_to_answer_question(question):

    selected_tables = select_tables_that_can_answer_this_question(question)
    print(selected_tables)
    if not selected_tables:
        return SQLGeneratedResponse()

    response = client.responses.parse(
        model="gpt-4o",
        input=[
            {"role": "system", "content": "Respond this SQL question. If it is not a valid question, mark is_a_valid_sql_question with false."},
            {
                "role": "user",
                "content": question,
            },
        ],
        text_format=SQLGeneratedResponse
    )

    return response.output_parsed
    