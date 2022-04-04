import datetime as dt
import time

import alpaca_trade_api as trade_api
import pytz
from alpaca_trade_api import TimeFrame
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.database import create_db
from src.models import order
from src.models import strategy
from src.models import symbol
from variables import variables as vb


def get_api():
    print("Starting ... ")
    time.sleep(10)

    connection = create_db.connect(vb.host, vb.user, vb.password, vb.database, vb.port)
    cursor = connection.cursor()

    app = FastAPI()

    app.mount("/static", StaticFiles(directory="web/static"), name="static")
    app.mount("/scripts", StaticFiles(directory="web/scripts"), name="scripts")
    templates = Jinja2Templates(directory="web")

    @app.get("/stocks")
    async def get_stocks(request: Request):
        exchanges_filter = request.query_params.get('exchanges', False)
        if exchanges_filter != '':
            cursor.execute(f"SELECT * FROM stock WHERE exchange='{exchanges_filter}' ORDER BY symbol ASC")
            stocks = cursor.fetchall()
        else:
            cursor.execute("SELECT * FROM stock ORDER BY symbol ASC")
            stocks = cursor.fetchall()
        cursor.execute("SELECT DISTINCT exchange FROM stock")
        exchanges = cursor.fetchall()
        return templates.TemplateResponse("index.html", {"request": request, "stocks": stocks, "exchanges": exchanges})

    @app.get("/stocks/{symbol}")
    async def get_price(request: Request, symbol: str):
        cursor.execute(f"SELECT * FROM stock WHERE symbol='{symbol}'")
        stock = cursor.fetchone()
        cursor.execute(f"SELECT * FROM `stock_price` WHERE `stock_id` = '{stock['id']}'")
        prices = cursor.fetchall()
        cursor.execute(f"SELECT * FROM `strategies`")
        strategy = cursor.fetchall()
        return templates.TemplateResponse("price.html",
                                          {"request": request, "stock": stock, "prices": prices,
                                           "strategies": strategy})

    @app.get("/strategies")
    async def get_stocks(request: Request):
        strategy_filter = request.query_params.get('strategy', False)
        if strategy_filter != "":
            cursor.execute(f"SELECT id, strategy FROM strategies WHERE id={strategy_filter} ORDER BY id")
            strategy = cursor.fetchone()
            cursor.execute(
                f"SELECT symbol, name FROM stock JOIN stock_strategy ON stock_strategy.stock_id=stock.id WHERE "
                f"strategy_id={strategy_filter}")
            stocks = cursor.fetchall()
        # TODO FIX ELSE STATEMENT
        else:
            cursor.execute(f"SELECT id, strategy FROM strategies ORDER BY id")
            strategy = cursor.fetchone()
            cursor.execute(f"SELECT symbol, name FROM stock JOIN stock_strategy ON stock_strategy.stock_id")
            stocks = cursor.fetchall()
        cursor.execute("SELECT id, strategy FROM strategies")
        strategies = cursor.fetchall()

        return templates.TemplateResponse("strategy.html", {"request": request, "stocks": stocks, "strategy": strategy,
                                                            "strategies": strategies})

    @app.get("/orders")
    async def get_orders(request: Request):

        def get_history_by_timeframe(history):
            history_list_len = 0
            history_list = []
            for i in range(len(history.equity)):
                if history.equity[i] is not None:
                    portfolio = {'equity': history.equity[i],
                                 'profit_loss': history.profit_loss[i],
                                 'timestamp': history.timestamp[i]}

                    history_list.append(portfolio)
                    history_list_len += 1
                else:
                    continue
            return history_list

        api = trade_api.REST(vb.api_key, vb.secret_key, vb.base_url)

        order_list = api.list_orders(status="all")
        my_order_list = []
        for order in order_list:
            order_info = {'symbol': order.symbol, 'info': order.type + " " + order.side + " " + str(order.submitted_at),
                          'order_qty': order.qty, 'filled_qty': order.filled_qty, 'status': order.status,
                          'price': "$" + order.filled_avg_price if order.filled_avg_price is not None else ""}
            my_order_list.append(order_info)

        day_history = api.get_portfolio_history(period="1D", timeframe="5Min")
        day_history_list = get_history_by_timeframe(day_history)

        month_history = api.get_portfolio_history(period="1M", timeframe="1D")
        month_history_list = get_history_by_timeframe(month_history)

        return templates.TemplateResponse("orders.html",
                                          {"request": request,
                                           "orders": my_order_list,
                                           "day_history_list": day_history_list,
                                           "month_history_list": month_history_list,
                                           "day_history_len": len(day_history_list)})

    @app.post("/api/v1/strategy")
    async def apply_strategy(strategy_symbol: strategy.Strategy):
        is_added = strategy_symbol.add_strategy(connection)
        if is_added:
            status = "Symbol has been added to the queue"
        else:
            status = "Symbol is already in the queue"
        return status

    @app.post("/api/v1/symbol")
    async def check_symbol_existence(symbol: symbol.Symbol):
        api = trade_api.REST(vb.api_key, vb.secret_key, vb.base_url)
        yesterday = (dt.datetime.now(tz=pytz.timezone('US/Eastern')) - dt.timedelta(days=1)).strftime("%Y-%m-%d")
        bars = api.get_bars(symbol.symbol_name, TimeFrame.Day, yesterday, yesterday)
        if len(bars) > 0:
            yesterday_price = bars[0].l
            return yesterday_price
        return

    @app.post("/api/v1/order")
    async def send_order(order: order.Order):
        api = trade_api.REST(vb.api_key, vb.secret_key, vb.base_url)
        is_submitted, order = order.submit_order(api)
        if is_submitted:
            status = "Order placed"
        else:
            status = "Something went wrong"
        return status

    return app
