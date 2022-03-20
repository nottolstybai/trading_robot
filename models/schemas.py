from pydantic import BaseModel


class Strategy(BaseModel):
    strategy_id: int
    stock_id: int
    symbol: str
