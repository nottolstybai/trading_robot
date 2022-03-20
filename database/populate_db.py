from datetime import datetime, timedelta
import pytz
import alpaca_trade_api as trade_api

from pymysql.connections import Connection
from alpaca_trade_api.rest import TimeFrame
from os import listdir

from database import create_db
from variables import variables as vb


def populate_stock(connection: Connection, api: trade_api.rest.REST):
    assets = api.list_assets(status='active', asset_class='us_equity')
    cursor = connection.cursor()
    cursor.execute("SELECT `symbol` FROM `stock`")
    rows = cursor.fetchall()
    symbols = [row['symbol'] for row in rows]

    for asset in assets:
        try:
            if asset.tradable and asset.symbol not in symbols:
                query = "INSERT INTO `stock` (`symbol`, `name`, `exchange`) VALUES (%s, %s, %s);"
                cursor.execute(query, (asset.symbol, asset.name, asset.exchange))
                print(f"ADDED TO stock table: {asset.symbol}")
        except Exception as e:
            print(asset.name)
            print(e)
    connection.commit()


def populate_stock_price(connection: Connection, api: trade_api.rest.REST):
    symbols = []
    stock_dict = {}

    cursor = connection.cursor()
    cursor.execute("SELECT `id`, `symbol`, `name` FROM `stock`")
    rows = cursor.fetchall()

    for row in rows:
        symbol = row['symbol']
        symbols.append(symbol)
        stock_dict[symbol] = row['id']

    chunk_size = 200
    for i in range(0, len(symbols), chunk_size):
        symbol_chunk = symbols[i: i + chunk_size]
        yesterday = (datetime.now(tz=pytz.timezone('US/Eastern')) - timedelta(days=1)).strftime("%Y-%m-%d")
        print(yesterday)

        bars = api.get_bars(symbol_chunk, TimeFrame.Hour, start=yesterday, end=yesterday)
        for bar in bars:
            print(f"Processing symbol {bar.S}")
            stock_id = stock_dict[bar.S]
            bar_time = bar.t.strftime("%Y/%m/%dT%H:%M")
            query = f'''INSERT INTO stock_price (stock_id, date, open, high, low, close, volume) VALUES ({stock_id}, 
                    "{bar_time}", {bar.o}, {bar.h}, {bar.l}, {bar.c}, {bar.v})'''
            cursor.execute(query)
    connection.commit()


def populate_strategies(connection: Connection):
    cursor = connection.cursor()
    cursor.execute("SELECT `strategy` FROM `strategies`")
    rows = cursor.fetchall()
    strategies_in_db = [row['strategy'] for row in rows]
    # TODO вставить параметр strategy_path и заменить его на этот путь
    strategies = listdir("C:/Users/Adil/PycharmProjects/TradingRobot/strategies")
    for strategy in strategies:
        if strategy.endswith(".py"):
            strategy = strategy.replace("_", " ")
            strategy = strategy.replace(".py", "")
            if strategy not in strategies_in_db:
                query = "INSERT INTO `strategies` (`strategy`) VALUES (%s);"
                cursor.execute(query, strategy)
                print(f"Added new strategy to db: {strategy}")
    connection.commit()


def populate_stock_strategy(connection: Connection, symbol, strategy):
    cursor = connection.cursor()
    cursor.execute(f"SELECT id FROM stock WHERE symbol = '{symbol}'")
    stock_id = cursor.fetchone()['id']
    cursor.execute(f"SELECT id FROM strategies WHERE strategy = '{strategy}'")
    strategy_id = cursor.fetchone()['id']

    stock_strategy_dict = {}
    cursor.execute("SELECT * FROM `stock_strategy`")
    rows = cursor.fetchall()
    for row in rows:
        stock_strategy_dict[row["strategy_id"]] = row["stock_id"]
    for key in stock_strategy_dict:
        if key == strategy_id and stock_strategy_dict[key] == stock_id:
            return
    cursor.execute("INSERT INTO `stock_strategy` (`strategy_id`, `stock_id`) VALUES (%s, %s);", (strategy_id, stock_id))
    print(f"{symbol} is added to list of assets that will be used for {strategy} strategy")

    connection.commit()


if __name__ == '__main__':
    api = trade_api.REST(vb.api_key, vb.secret_key, vb.base_url)
    connection = create_db.connect(vb.host, vb.user, vb.password, vb.database, vb.port)
    populate_stock_price(connection, api)
