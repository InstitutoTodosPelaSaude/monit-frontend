from pydantic import BaseModel, model_validator
from typing import List, Literal

from openai import OpenAI


class SQLGeneratedResponse(BaseModel):
    query: str
    is_a_valid_sql_question: bool

    @model_validator(mode='after')
    def check_valid_sql_question(self):
        if not self.is_a_valid_sql_question:
           self.query = "<INVALID>" 
        return self


def generate_sql_query_to_answer_question(question):
    client = OpenAI()

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
    