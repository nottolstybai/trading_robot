import multiprocessing

import alpaca_trade_api as trade_api
import uvicorn

import searcher
from app import get_api
from src.database import create_db, populate_db
from variables import variables as vb


def process_one():
    api = trade_api.REST(vb.api_key, vb.secret_key, vb.base_url)
    create_db.drop_db(vb.host, vb.user, vb.password)
    create_db.create_db(vb.host, vb.user, vb.password)
    connection = create_db.connect(vb.host, vb.user, vb.password, vb.database, vb.port)
    create_db.create_tables(connection)
    populate_db.populate_stock(connection, api)
    populate_db.populate_stock_price(connection, api)
    populate_db.populate_strategies(connection)
    searcher.schedule_api()


def process_two():
    app = get_api()
    uvicorn.run(app, host="localhost", port=8000)


if __name__ == '__main__':
    # p1 = multiprocessing.Process(target=process_one)
    # p2 = multiprocessing.Process(target=process_two)
    #
    # #p1.start()
    # p2.start()
    process_two()
