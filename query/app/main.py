from fastapi import FastAPI, HTTPException, Query
from openai import OpenAI

from models import QueryParameters
from prompt import ARBO_FIELDS, RESPAT_FIELDS
from prompt import fill_table_name, get_prompt
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

    return {
        "sql": sql_query,
        "raw_sql": sql_raw_query,
        "project": project
    }