from pydantic import BaseModel
from pymysql import connections


class Strategy(BaseModel):
    strategy_id: int
    stock_id: int
    symbol: str

    def add_strategy(self, connection: connections.Connection):
        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM stock_strategy WHERE stock_id='{self.stock_id}'")
        quantity = cursor.fetchone()
        if quantity['COUNT(*)'] == 0:
            cursor.execute(f"INSERT INTO `stock_strategy` (`strategy_id`, `stock_id`) VALUES "
                           f"({self.strategy_id}, {self.stock_id});")
            connection.commit()
            return True
        return False