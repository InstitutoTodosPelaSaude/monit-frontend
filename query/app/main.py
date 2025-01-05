from fastapi import FastAPI, HTTPException, Query
from openai import OpenAI

from models import QueryParameters, FormatQueryParameters
from prompt import ARBO_FIELDS, RESPAT_FIELDS
from prompt import apply_configs_to_sql_query, fill_table_name, get_prompt
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API is working"}

@app.post("/query")
def get_sql_query(params: QueryParameters):

    # IF project IS NOT RESPAT or ARBO the return error BAD REQUEST
    project  = params.project
    question = params.question
    table    = params.table
    configs = params.configs

    prompt = get_prompt(question, project, table)

    try:
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" },
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse and return the response
        response_content = json.loads(response.model_dump_json())
        message = response_content['choices'][0]['message']['content']

        sql_raw_query = json.loads(message).get("query", "No query found")

    except Exception as e:
        # RETURN 500 error
        raise HTTPException(status_code=500, detail=f"Error fetching SQL query from OpenAI: {str(e)}")
    
    sql_query = fill_table_name(sql_raw_query)
    sql_query = apply_configs_to_sql_query(sql_query, configs)

    return {
        "sql": sql_query,
        "raw_sql": sql_raw_query,
        "project": project
    }


@app.post("/process")
def get_sql_query(params: FormatQueryParameters):
    
    sql_raw_query = params.sql_raw_query
    configs = params.configs

    sql_query = fill_table_name(sql_raw_query)
    sql_query = apply_configs_to_sql_query(sql_query, configs)
    return {
        "sql": sql_query,
        "raw_sql": sql_raw_query,
    }

