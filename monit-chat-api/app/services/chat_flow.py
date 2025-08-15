
from pydantic import BaseModel, model_validator
from typing import List, Literal
from app.crud.database import MongoConnection

from openai import OpenAI
    
from app.models.query import SQLGeneratedResponse, SQLTableSelectionResponse, GenereateNameForChatResponse, SQLQuery
from app.models.chat import Table, ChatBotMessage, Chat, NEW_CHAT_DEFAULT_NAME

from app.crud.chat import read_chat_by_id, create_bot_reply_message, list_tables, update_chat_name
from app.crud.query import create_sql_query

import json
import sqlparse

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

    print(response.output_parsed.tables)
    
    return selected_tables

def generate_sql_query_to_answer_question(chat_history, tables: list[Table]):

    if not tables:
        return SQLGeneratedResponse()
    
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
                    Always double-quote thecolumns used.
                    Data dictonary: {json.dumps(tables)}
                """
            },
            *chat_history
        ],
        text_format=SQLGeneratedResponse
    )

    sql_generated_response = response.output_parsed
    return SQLQuery(query=sql_generated_response.query), sql_generated_response.is_a_valid_sql_question

def postprocess_sql_query(query, tables: list[Table], max_num_lines = 1000):

    # Replace the table PROMPT names with the real table names
    postprocessed_query = query
    for table in tables:

        # Try to replace column name double quoted ""
        postprocessed_query = postprocessed_query.replace(
            f'"{table.name}"',
            table.name,
        )

        # Replace the column 
        postprocessed_query = postprocessed_query.replace(
            f'{table.name}',
            f'"{table.metadata.database}"."{table.metadata.schema}"."{table.metadata.name}"'
        )

    # Apply limit
    postprocessed_query = postprocessed_query.replace(';', '')
    postprocessed_query = f'SELECT * FROM ({postprocessed_query}) AS query_limit_num_of_lines LIMIT {max_num_lines}'

    # Ident Query
    postprocessed_query = sqlparse.format(postprocessed_query, reindent=True, keyword_case='upper')

    return postprocessed_query

def check_if_query_is_read_only(query):
    all_sql_queries_tokenized = sqlparse.parse(query)

    if len(all_sql_queries_tokenized) != 1:
        # If there are more than two or any SQL statements 
        return False

    forbidden_commands = {
        "INSERT", "UPDATE", "SET", "DELETE", "MERGE", "UPSERT", "REPLACE", # DML
        "CREATE", "DROP", "ALTER", "TRUNCATE", "RENAME", # DDL
        "EXEC", "EXECUTE", "CALL"
    }

    sql_tokenized = all_sql_queries_tokenized[0]
    for token in sql_tokenized.tokens:
        if token.value in forbidden_commands:
            if str(token.ttype).startswith("Token.Keyword"):
                return False
            
    return True

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
    new_message = ChatBotMessage(
        generated_query=generated_query, 
        postprocessed_query=postprocessed_query,
        tables_used_in_query=tables,
        message="Request processed, see the results...", 
    )

    await create_bot_reply_message(chat_id, new_message)
    await create_sql_query(generated_query)
    