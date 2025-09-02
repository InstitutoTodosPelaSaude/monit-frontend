
from pydantic import BaseModel, model_validator
from typing import List, Literal
from app.crud.database import MongoConnection

from openai import OpenAI
    
from app.models.query import SQLGeneratedResponse, SQLTableSelectionResponse, GenereateNameForChatResponse, SQLQuery
from app.models.chat import Table, ChatBotMessage, Chat, NEW_CHAT_DEFAULT_NAME

from app.crud.chat import read_chat_by_id, create_bot_reply_message, list_tables, update_chat_name
from app.crud.query import create_sql_query
from app.services.query_utils import postprocess_sql_query, check_if_query_is_read_only, identate_query
from app.services.query_execution import trigger_query_execution_flow

import json
from datetime import datetime

client = OpenAI()

async def select_tables_to_answer_question(chat_history) -> List[Table]:

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

    print(response.output_parsed.tables)
    
    return selected_tables

def generate_sql_query_to_answer_question(chat_history, tables: List[Table]):

    if not tables:
        return SQLQuery(query="<INVALID>"), False
    
    tables = [ table.json_data_dictionary for table in tables ]
    response = client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system", 
                "content": f"""
                    Your purpose is to write Postgres SQL queries to respond user questions. 
                    Based on the data dictionary provided and the chat history, create a new SQL query to respond the user's request.
                    Give a name to the query based on its goal.
                    If the user doesn't make a valid question, mark is_a_valid_sql_question with false.
                    Always double-quote the columns used. Never use LIKE to compare dates.
                    If the user references dates (ex. last week, current year), this is the current date: {datetime.now().strftime('%Y-%m-%d')}.
                    Data dictonary: {json.dumps(tables)}
                """
            },
            *chat_history
        ],
        text_format=SQLGeneratedResponse
    )

    sql_generated_response = response.output_parsed
    return SQLQuery(query=sql_generated_response.query, name=sql_generated_response.name), sql_generated_response.is_a_valid_sql_question

async def create_new_chat_name(chat_id: str):

    chat = await read_chat_by_id(chat_id)
    if chat.name != NEW_CHAT_DEFAULT_NAME:
        return
    
    response = client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system", 
                "content": "Give a short name to this chat based on the user's question."
            },
            *chat.format_to_openai_chat_completion_input()
        ],
        text_format=GenereateNameForChatResponse
    )

    new_name = response.output_parsed.name
    await update_chat_name(chat.id, new_name)

async def trigger_chatbot_response_flow(
    chat_id
):
    
    chat = await read_chat_by_id(chat_id)
    chat_history = chat.format_to_openai_chat_completion_input()

    tables = await select_tables_to_answer_question(chat_history)
    generated_query, is_a_valid_sql_question = generate_sql_query_to_answer_question(chat_history, tables)

    if not is_a_valid_sql_question:
        new_message = ChatBotMessage(
            generated_query=generated_query, 
            message="Unable to found tables in the database that can answer this request.", 
        )
        await create_bot_reply_message(chat_id, new_message)
        return 
    
    if not check_if_query_is_read_only(generated_query.query):
        new_message = ChatBotMessage(
            generated_query=generated_query, 
            message="Ops! Request denied, I can only READ from tables.", 
        )
        await create_bot_reply_message(chat_id, new_message)
        return 

    await create_new_chat_name(chat_id)

    postprocessed_query = postprocess_sql_query(generated_query.query, tables)
    generated_query.query = identate_query(generated_query.query)
    new_message = ChatBotMessage(
        generated_query=generated_query, 
        postprocessed_query=postprocessed_query,
        tables_used_in_query=tables,
        message="Request processed, see the results...", 
    )

    await create_bot_reply_message(chat_id, new_message)
    await create_sql_query(generated_query)

    try:
        await trigger_query_execution_flow(generated_query.id)
    except Exception as e:
        pass