from app.crud.database import MongoConnection
from app.models.query import SQLQuery

async def create_sql_query( query: SQLQuery ) -> SQLQuery:
    db = MongoConnection.get_client()
    db_collection = db.chat

    db_collection.insert_one(query.dict())
    return query
