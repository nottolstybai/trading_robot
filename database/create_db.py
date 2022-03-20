import pymysql


def connect(host, user, password, dbname, port):
    try:
        connection = pymysql.connect(host=host,
                                     user=user,
                                     password=password,
                                     database=dbname,
                                     cursorclass=pymysql.cursors.DictCursor,
                                     port=int(port))
        print("Connection successful")
        return connection
    except Exception as e:
        print(f"Connection failed: {e}")


def drop_db(host, user, password):
    connection = pymysql.connect(host=host, user=user, password=password)
    cursor = connection.cursor()
    try:
        cursor.execute("DROP DATABASE IF EXISTS trading_robot;")
        print("Dropped database: trading_robot")
    except Exception as e:
        print(f"Database dropping failed: {e}")


def create_db(host, user, password):
    connection = pymysql.connect(host=host, user=user, password=password)
    cursor = connection.cursor()
    try:
        cursor.execute("""
            CREATE DATABASE IF NOT EXISTS `trading_robot`
            CHARACTER SET utf8mb4;
            """)
        print(f"Created database: trading_robot")
    except Exception as e:
        print(f"Database creation failed: {e}")


def create_tables(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `stock` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `symbol` VARCHAR(255) UNIQUE NOT NULL,
                `name` VARCHAR(255) NOT NULL,
                `exchange` VARCHAR(255) NOT NULL,
                PRIMARY KEY (`id`)
            );
            """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `stock_price` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `stock_id` int(11) NOT NULL,
                `date` varchar(255) NOT NULL,
                `open` varchar(255) NOT NULL,
                `high` varchar(255) NOT NULL,
                `low` varchar(255) NOT NULL,
                `close` varchar(255) NOT NULL,
                `volume` varchar(255) NOT NULL,  
                PRIMARY KEY (`id`),
                FOREIGN KEY (stock_id)
                    REFERENCES stock(id)
                    ON DELETE CASCADE
            );
            """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `strategies` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `strategy` varchar(255) NOT NULL, 
                PRIMARY KEY (`id`)
            );
            """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `stock_strategy` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `strategy_id` int(11) NOT NULL,
                `stock_id` int(11) NOT NULL,
                PRIMARY KEY (`id`),
                FOREIGN KEY (stock_id)
                    REFERENCES stock(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (strategy_id)
                    REFERENCES strategies(id)
                    ON DELETE CASCADE
            );
            """)
        print(f"Created tables: stock, stock_price, strategies, stock_strategy")
    except Exception as e:
        print(f"Table creation failed: {e}")
