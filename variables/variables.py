host = 'localhost'
user = 'root'
password = 'APOKAapoka1998'
database = 'trading_robot'
port = 3306

api_key = "PK4UF084OWP8CV1AN69Z"
secret_key = "oDwYHcrC4AenVMR3CSvm9X6J3Cp880tQqFSik88s"
base_url = "https://paper-api.alpaca.markets"

client_id = "6e41102c37fcd64ad5123d18750a783c"
client_secret = "a10e55cfb64ec06e43c1e228dc083414ec8abe49"

stock_column = {
    'name': 'stock',
    'primary_key': 'id',
    'id': 'int(11) NOT NULL AUTO_INCREMENT',
    'symbol': 'varchar(255) NOT NULL',
    'exchange': 'varchar(255) NOT NULL'}
stock_price_column = {
    'name': 'stock_price',
    'primary_key': 'id',
    'reference': [{
        'referenced_table': 'stock',
        'referenced_primary_key': 'id',
        'foreign_key': 'stock_id'},
    ],
    'id': 'int(11) NOT NULL AUTO_INCREMENT',
    'stock_id': 'int(11) NOT NULL',
    'date': 'varchar(255) NOT NULL',
    'open': 'varchar(255) NOT NULL',
    'close': 'varchar(255) NOT NULL',
    'high': 'varchar(255) NOT NULL',
    'low': 'varchar(255) NOT NULL',
    'volume': 'varchar(255) NOT NULL'
}
stock_strategy_column = {
    'name': 'stock_strategy',
    'primary_key': 'id',
    'reference': [
        {
            'referenced_table': 'stock',
            'referenced_primary_key': 'id',
            'foreign_key': 'stock_id'
        },
        {
            'referenced_table': 'strategy',
            'referenced_primary_key': 'id',
            'foreign_key': 'strategy_id'
        },
    ],
    'id': 'int(11) NOT NULL AUTO_INCREMENT',
    'strategy_id': 'int(11) NOT NULL',
    'stock_id': 'int(11) NOT NULL'
}
strategy_column = {
    'name': 'strategies',
    'primary_key': 'id',
    'strategy': 'varchar(255) NOT NULL',
    'id': 'int(11) NOT NULL AUTO_INCREMENT'
}
