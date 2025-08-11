
from pydantic import BaseModel, model_validator
from typing import List, Literal
from app.crud.database import MongoConnection

from openai import OpenAI
    
from app.models.query import SQLGeneratedResponse, SQLTableSelectionResponse

client = OpenAI()    

def select_tables_to_answer_question(question):

    db = MongoConnection.get_client()
    db_collection = db.chat

    tables = list(
        db_collection
        .find({'type': 'TABLE'})
    )

    tables_prompt = "\n".join( [ f"Name: {table['name']} Description: {table['description']}" for table in tables ] )
    tables_prompt = f"\n{tables_prompt}"

    response = client.responses.parse(
        model="gpt-4o-mini",
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

    selected_tables = select_tables_to_answer_question(question)
    if not selected_tables:
        return SQLGeneratedResponse()

    response = client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": "Based on the table's descriptions, respond this SQL question. If it is not a valid question, mark is_a_valid_sql_question with false."},
            {
                "role": "user",
                "content": question,
            },
        ],
        text_format=SQLGeneratedResponse
    )

    return response.output_parsed
    
