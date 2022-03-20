import alpaca_trade_api as trade_api
import datetime as dt
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import create_db
from models import schemas
from variables import variables as vb

app = FastAPI()

app.mount("/static", StaticFiles(directory="web/static"), name="static")
app.mount("/scripts", StaticFiles(directory="web/scripts"), name="scripts")
templates = Jinja2Templates(directory="web")


@app.get("/stocks")
async def get_stocks(request: Request):
    exchanges_filter = request.query_params.get('exchanges', False)

    connection = create_db.connect(vb.host, vb.user, vb.password, vb.database, vb.port)
    cursor = connection.cursor()

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
    connection = create_db.connect(vb.host, vb.user, vb.password, vb.database, vb.port)
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM stock WHERE symbol='{symbol}'")
    stock = cursor.fetchone()
    cursor.execute(f"SELECT * FROM `stock_price` WHERE `stock_id` = '{stock['id']}'")
    prices = cursor.fetchall()
    cursor.execute(f"SELECT * FROM `strategies`")
    strategy = cursor.fetchall()
    return templates.TemplateResponse("price.html",
                                      {"request": request, "stock": stock, "prices": prices, "strategies": strategy})


@app.post("/api/strategies")
async def apply_strategy(strategy_symbol: schemas.Strategy):
    connection = create_db.connect(vb.host, vb.user, vb.password, vb.database, vb.port)
    cursor = connection.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM stock_strategy WHERE stock_id='{strategy_symbol.stock_id}'")
    quantity = cursor.fetchone()
    if quantity['COUNT(*)'] == 0:
        cursor.execute(f"INSERT INTO `stock_strategy` (`strategy_id`, `stock_id`) VALUES "
                       f"({strategy_symbol.strategy_id}, {strategy_symbol.stock_id});")
        connection.commit()
        status = "Symbol has been added to the queue"
    else:
        status = "Symbol is already in the queue"
    return status


@app.get("/strategies")
async def get_stocks(request: Request):
    strategy_filter = request.query_params.get('strategy', False)
    connection = create_db.connect(vb.host, vb.user, vb.password, vb.database, vb.port)
    cursor = connection.cursor()
    if strategy_filter != "":
        cursor.execute(f"SELECT id, strategy FROM strategies WHERE id={strategy_filter} ORDER BY id")
        strategy = cursor.fetchone()
        print(strategy)
        cursor.execute(f"SELECT symbol, name FROM stock JOIN stock_strategy ON stock_strategy.stock_id=stock.id WHERE "
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
    api = trade_api.REST(vb.api_key, vb.secret_key, vb.base_url)
    order_list = api.list_orders()
    my_order_list = []

    portfolio_history = api.get_portfolio_history()
    portfolio_list = []
    for i in range(len(portfolio_history.equity)):
        timestamp = dt.datetime.utcfromtimestamp(portfolio_history.timestamp[i]).strftime("%Y-%m-%d")
        print(timestamp)
        portfolio = {'equity': portfolio_history.equity[i], 'profit_loss': portfolio_history.profit_loss[i],
                     'timestamp': timestamp}
        portfolio_list.append(portfolio)

    for order in order_list:
        order_info = {'symbol': order.symbol, 'info': order.type + " " + order.side + " " + str(order.submitted_at),
                      'order_qty': order.qty, 'filled_qty': order.filled_qty, 'status': order.status,
                      'price': "$" + order.filled_avg_price if order.filled_avg_price is not None else ""}
        my_order_list.append(order_info)
    return templates.TemplateResponse("orders.html",
                                      {"request": request, "orders": my_order_list, "portfolio_list": portfolio_list,
                                       "portfolio_len": len(portfolio_history.equity) - 1})
