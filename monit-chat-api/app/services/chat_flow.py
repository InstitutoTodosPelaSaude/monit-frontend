
from pydantic import BaseModel, model_validator
from typing import List, Literal
from app.crud.database import MongoConnection

from openai import OpenAI
    
from app.models.query import SQLGeneratedResponse, SQLTableSelectionResponse
from app.models.chat import Table, ChatBotMessage

from app.crud.chat import read_chat_by_id, create_bot_reply_message, list_tables
import json

client = OpenAI()

async def select_tables_to_answer_question(chat_history) -> list[Table]:

    db = MongoConnection.get_client()
    db_collection = db.chat

    tables = await list_tables()

    tables_prompt = "\n".join( [ f"Name: {table.name} Description: {table.description}" for table in tables ] )
    tables_prompt = f"\n{tables_prompt}"

    response = client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system", 
                "content": f"Based on the table's descriptions and the chat history, select a list of tables that can be used to answer the user's question with a SQL query. If no table suits the task, return a empty list. {tables_prompt}"
            },
            *chat_history
        ],
        text_format=SQLTableSelectionResponse
    )

    selected_tables = [
        table for table in tables
        if table.name in response.output_parsed.tables
    ]

    return selected_tables

def generate_sql_query_to_answer_question(chat_history, tables: list[Table]):
    
    tables = [ table.json_data_dictionary for table in tables ]
    response = client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system", 
                "content": f"""
                    Your purpose is to write SQL queries to respond user questions. 
                    Based on the data dictionary provided and the chat history, create a new SQL query to respond the user's request. 
                    If the user doesn't make valid question, mark is_a_valid_sql_question with false.
                    Data dictonary: {json.dumps(tables)}
                """
            },
            *chat_history
        ],
        text_format=SQLGeneratedResponse
    )

    return response.output_parsed
    
async def trigger_chatbot_response_flow(
    chat_id,
    user_question
):
    
    chat = await read_chat_by_id(chat_id)
    chat_history = chat.format_to_openai_chat_completion_input()

    tables = await select_tables_to_answer_question(chat_history)
    generated_query = generate_sql_query_to_answer_question(chat_history, tables)

    new_message = ChatBotMessage(generated_query=generated_query, message=generated_query.query)
    await create_bot_reply_message(chat_id, new_message)