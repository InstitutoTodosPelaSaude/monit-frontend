from app.crud.database import MongoConnection
from app.models.query import SQLQuery
from app.crud.exceptions import QueryIDNotFound
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