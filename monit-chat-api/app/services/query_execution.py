from app.crud.query import read_query_by_id, update_query_result
from app.models.query import SQLQuery, QueryResult
from app.schemas.query import QueryUpdateResult
from app.crud.chat import list_tables
from app.services.chat_flow import postprocess_sql_query, check_if_query_is_read_only
from app.crud.exceptions import QueryCannotBeExecuted

async def execute_query(sql_query: str, query_id: str) -> QueryResult:

    # [WIP] Query execution in the real database
    query_result = QueryResult(
        query_id=query_id,
        data=[(1,2,3,4,5), (1,2,3,4,5)],
        columns=["c1","c2","c3","c4","c5"]
    )

    return query_result

async def trigger_query_execution_flow(
    query_id: SQLQuery
):
    query = await read_query_by_id(query_id)
    generated_query = query.query
    if not check_if_query_is_read_only(generated_query):
        raise QueryCannotBeExecuted("A Query precisa ser somente-leitura.")
    
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