from app.crud.database import MongoConnection
from app.models.query import SQLQuery
from app.crud.exceptions import QueryIDNotFound
from app.crud.users import read_user_by_id
from app.schemas.query import QueryUpdateResult
from pprint import pprint

async def create_sql_query( query: SQLQuery ) -> SQLQuery:
    db = MongoConnection.get_client()
    db_collection = db.chat

    db_collection.insert_one(query.dict())
    return query

async def read_query_by_id(query_id: str) -> SQLQuery:
    
    db = MongoConnection.get_client()
    db_collection = db.chat

    query_result = db_collection.find_one(
        {
            "_id": query_id,
            "type": "QUERY"
        },
    )

    if not query_result:
        raise QueryIDNotFound(query_id)
    
    query = SQLQuery(
        **query_result
    )

    return query

async def read_user_queries(user_id: str) -> list[SQLQuery]:
    
    db = MongoConnection.get_client()
    db_collection = db.chat

    user = await read_user_by_id(user_id)
    queries_ids = user.favorite_queries_ids

    query_result = db_collection.find(
        {
            "type": "QUERY",
            #"_id": {"$in": queries_ids}
        },
    )

    queries = [
        SQLQuery(**query) for query in query_result
    ]

    return queries

async def favorite_query(user_id: str, query_id: str) -> dict:
    """
    Adiciona uma query aos favoritos do usuário.
    """
    # garante que a query existe
    await read_query_by_id(query_id)

    db = MongoConnection.get_client()
    db_collection = db.users  # ajuste o nome da coleção de usuários se for diferente

    result = db_collection.update_one(
        {"_id": user_id},
        {"$addToSet": {"favorite_queries_ids": query_id}}
    )

    if result.modified_count == 0:
        return {"message": f"Query {query_id} já estava nos favoritos."}

    return {"message": f"Query {query_id} adicionada aos favoritos com sucesso."}

async def remove_favorite_query(user_id: str, query_id: str) -> dict:
    """
    Remove uma query dos favoritos do usuário.
    """
    db = MongoConnection.get_client()
    db_collection = db.users

    result = db_collection.update_one(
        {"_id": user_id},
        {"$pull": {"favorite_queries_ids": query_id}}
    )

    if result.modified_count == 0:
        return {"message": f"Query {query_id} não estava nos favoritos."}

    return {"message": f"Query {query_id} removida dos favoritos com sucesso."}

async def update_query_result(query_update: QueryUpdateResult):
    db = MongoConnection.get_client()
    db_collection = db.chat

    query_id = query_update.id
    query = await read_query_by_id(query_id)

    result = db_collection.update_one(
        {"_id": query_id},
        {"$set": {"query_result": query_update.query_result.dict()}}
    )

    if result.modified_count == 0:
        return query

    updated_query = await read_query_by_id(query_id)
    return updated_query