from app.models.chat import Chat
from app.crud.database import MongoConnection
from app.crud.exceptions import ChatIDNotFound, TableAlreadyExists


def trigger_chatbot_response_flow(
    chat_id,
    user_question
):
    
    pass