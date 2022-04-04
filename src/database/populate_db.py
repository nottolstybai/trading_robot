from datetime import datetime, timedelta
import pytz
import alpaca_trade_api as trade_api

from pymysql.connections import Connection
from alpaca_trade_api.rest import TimeFrame
from os import listdir

from pathlib import Path
from src.database import create_db
from variables import variables as vb


def populate_stock(connection: Connection, api: trade_api.rest.REST):
    print(f"STOCK TABLE POPULATION STARTING ...")
    assets = api.list_assets(status='active', asset_class='us_equity')
    asset_num_by_exchange = {str: int}
    
    cursor = connection.cursor()
    cursor.execute("SELECT `symbol` FROM `stock`")
    rows = cursor.fetchall()
    symbols = [row['symbol'] for row in rows]
    
    for asset in assets:
        try:
            if asset.tradable and asset.symbol not in symbols:
                if asset_num_by_exchange.get(asset.exchange) is not None:
                    asset_num_by_exchange[asset.exchange] += 1
                else:
                    asset_num_by_exchange[asset.exchange] = 1
                    
                query = "INSERT INTO `stock` (`symbol`, `name`, `exchange`) VALUES (%s, %s, %s);"
                cursor.execute(query, (asset.symbol, asset.name, asset.exchange))
        except Exception as e:
            print(f"Exception is {e}")

    for exchange in asset_num_by_exchange:
        print(f"Processed {exchange} exchange with {asset_num_by_exchange[exchange]} symbols")

    connection.commit()


def populate_stock_price(connection: Connection, api: trade_api.rest.REST):
    print(f"STOCK_PRICE TABLE POPULATION STARTING ...")
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
        print(f"Processing next 200 symbols")

        symbol_chunk = symbols[i: i + chunk_size]
        yesterday = (datetime.now(tz=pytz.timezone('US/Eastern')) - timedelta(days=1)).strftime("%Y-%m-%d")
        bars = api.get_bars(symbol_chunk, TimeFrame.Hour, start=yesterday, end=yesterday)
        for bar in bars:
            stock_id = stock_dict[bar.S]
            bar_time = bar.t.strftime("%Y/%m/%dT%H:%M")
            query = f'''INSERT INTO stock_price (stock_id, date, open, high, low, close, volume) VALUES ({stock_id}, 
                    "{bar_time}", {bar.o}, {bar.h}, {bar.l}, {bar.c}, {bar.v})'''
            cursor.execute(query)
    connection.commit()


def populate_strategies(connection: Connection):
    print(f"LOOKING FOR AVAILABLE STRATEGIES ...")
    cursor = connection.cursor()
    cursor.execute("SELECT `strategy` FROM `strategies`")
    rows = cursor.fetchall()
    strategies_in_db = [row['strategy'] for row in rows]
    # TODO вставить параметр strategy_path и заменить его на этот путь
    path_to_strategies = str(Path(__file__).parent.parent) + "/strategies"
    strategies = listdir(path_to_strategies)
    for strategy in strategies:
        if strategy.endswith(".py"):
            strategy = strategy.replace("_", " ")
            strategy = strategy.replace(".py", "")
            if strategy not in strategies_in_db:
                query = "INSERT INTO `strategies` (`strategy`) VALUES (%s);"
                cursor.execute(query, strategy)
                print(f"Added new strategy to database: {strategy}")
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
