from pydantic import BaseModel, HttpUrl

class QuizRequest(BaseModel):
    email: str
    secret: str
    url: str
