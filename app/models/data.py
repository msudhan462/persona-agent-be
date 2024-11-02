from pydantic import BaseModel

class IngestQA(BaseModel):


    qtype: str
    question_number: int
    question: str
    answer: str

class IngestText(BaseModel):
    text: str

class GetQA(BaseModel):

    qtype: str
    question_number: str
    question: str

class DeleteFile(BaseModel):

    file_id: str
