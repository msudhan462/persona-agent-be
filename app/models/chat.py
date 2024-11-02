from pydantic import BaseModel
from typing import List


# Shared properties for the item
class Convsersation(BaseModel):
    prompt: str
    persona_id: str
    conversation_id: str

class Report(BaseModel):
    message_id: str
    report_message: str = ""
    persona_id: str
    conversation_id: str

class PostReaction(BaseModel):
    message_id: str
    reaction: str
    persona_id: str
    conversation_id: str


class GetReaction(BaseModel):
    persona_id: str
    conversation_id: str

class PostLike(BaseModel):
    message_id: str
    persona_id: str
    conversation_id: str

class PostDislike(BaseModel):
    message_id: str
    persona_id: str
    conversation_id: str

class GetLikesAndDislike(BaseModel):
    persona_id: str
    conversation_id: str

class GetAgents(BaseModel):
    persona_id: str
