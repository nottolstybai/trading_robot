from pydantic import BaseModel


class Symbol(BaseModel):
    symbol_name: str
