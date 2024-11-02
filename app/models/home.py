from pydantic import BaseModel



class SearchAgents(BaseModel):
    query: str