from app.crud.query import read_query_by_id, update_query_result
from app.models.query import SQLQuery, QueryResult
from app.schemas.query import QueryUpdateResult
from app.crud.chat import list_tables
from app.services.query_utils import postprocess_sql_query, check_if_query_is_read_only
from app.crud.exceptions import QueryCannotBeExecuted

from app.crud.database import PostgresConnection
from pprint import pprint

async def execute_query(sql_query: str, query_id: str) -> QueryResult:

    columns, result = PostgresConnection().execute_query(sql_query)

    if not columns or not result:
        raise QueryCannotBeExecuted(query_id=query_id, reason="Problema executando consulta")

    query_result = QueryResult(
        query_id=query_id,
        data=result,
        columns=columns
    )

    return query_result

async def trigger_query_execution_flow(
    query_id: SQLQuery
):
    query = await read_query_by_id(query_id)
    generated_query = query.query
    if not check_if_query_is_read_only(generated_query):
        raise QueryCannotBeExecuted(query_id=query_id, reason="A Query precisa ser somente-leitura.")
    
    tables = await list_tables()
    postprocessed_query = postprocess_sql_query(generated_query, tables)
    query_result = await execute_query(postprocessed_query, query_id)

    await update_query_result(
        QueryUpdateResult(
            id=query.id,
            query_result=query_result
        )
    )

    return query_result