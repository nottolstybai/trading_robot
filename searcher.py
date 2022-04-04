import datetime
import time

from pymysql import Connection

from src.database import create_db
from variables import variables as vb
from src.strategies import scalp_algo_strategy


def check_db(connection: Connection):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM stock_strategy")
    stock_strategy = cursor.fetchone()
    if stock_strategy is not None:
        print(stock_strategy)
        cursor.execute(f"DELETE FROM stock_strategy WHERE id={stock_strategy['id']};")
        connection.commit()

        cursor.execute(f"SELECT symbol FROM stock WHERE id='{stock_strategy['stock_id']}'")
        symbol = cursor.fetchone()

        scalp_algo_strategy.main([symbol], 100)
    else:
        print("No strategies are applied")


def schedule_api():
    connection = create_db.connect(vb.host, vb.user, vb.password, vb.database, vb.port)
    while datetime.datetime.now().minute % 1 != 0:
        time.sleep(1)
    check_db(connection)
    while True:
        time.sleep(60)
        check_db(connection)
