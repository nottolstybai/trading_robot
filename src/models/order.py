from typing import Optional

from pydantic import BaseModel
from alpaca_trade_api import rest


class Order(BaseModel):
    symbol: str
    order_type: str = "market"
    side: str = "buy"
    notional: Optional[float] = None
    qty: Optional[float] = None
    tif: str = "day"
    lmt_price: Optional[str] = None
    stop_price: Optional[str] = None

    def submit_order(self, api: rest.REST):
        try:
            order = api.submit_order(symbol=self.symbol,
                                     qty=self.qty,
                                     side=self.side,
                                     type=self.order_type,
                                     time_in_force=self.tif,
                                     limit_price=self.lmt_price,
                                     stop_price=self.stop_price,
                                     notional=self.notional)
            return True, order
        except Exception as e:
            print(f"Something went wrong: {e}")
            return False, None