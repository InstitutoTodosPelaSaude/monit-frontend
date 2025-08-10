import os
import pymongo

MONGO_APP_DB = os.getenv("MONGO_APP_DB", "appdb")

class MongoConnection:
    _client = None

    @classmethod
    def get_client(cls):
        """
        Mongo singleton connection creation
        """
        mongo_app_db = os.getenv("MONGO_APP_DB", "appdb")
        
        if cls._client is None:
            mongo_port = os.getenv("MONGO_PORT", "27018")
            mongo_app_user = os.getenv("MONGO_APP_USER", "appuser")
            mongo_app_pass = os.getenv("MONGO_APP_PASS", "password")

            mongo_uri = os.getenv(
                "MONGO_URI",
                f"mongodb://{mongo_app_user}:{mongo_app_pass}@mongodb:{mongo_port}/{mongo_app_db}?authSource={mongo_app_db}"
            )

            cls._client = pymongo.MongoClient(mongo_uri)
        
        return cls._client[mongo_app_db]

