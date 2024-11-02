from pydantic import BaseModel



class PesonaID(BaseModel):
    persona_id: str


class AgentReport(BaseModel):
    persona_id: str
    conversation_id: str 
    report_message: str = ""



class CurrentStatus(BaseModel):
    
    feeling: str
    status: str = ""
