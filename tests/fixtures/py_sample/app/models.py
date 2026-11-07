from pydantic import BaseModel


class Order(BaseModel):
    id: str
    status: str = "open"
