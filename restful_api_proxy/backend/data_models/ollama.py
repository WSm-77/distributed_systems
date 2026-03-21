from pydantic import BaseModel, ConfigDict


class OllamaResponseMessage(BaseModel):
    model_config = ConfigDict(extra="allow")

    content: str

class OllamaResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str
    message: OllamaResponseMessage
