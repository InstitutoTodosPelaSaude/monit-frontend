
import sqlparse
from app.models.chat import Table
from typing import List

def identate_query(query: str):
    formated_query = sqlparse.format(query, reindent=True, keyword_case='upper')
    return formated_query

def postprocess_sql_query(query, tables: List[Table], max_num_lines = 1000):

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
    postprocessed_query = identate_query(postprocessed_query)

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
