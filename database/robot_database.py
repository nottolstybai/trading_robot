import pymysql
import variables.variables as vb
from pymysql.connections import Connection


class RobotDatabase:

    def __init__(self, host, user, password, database, port):
        self.__host = host
        self.__user = user
        self.__password = password
        self.__database = database
        self.__port = port
        self.__connection = pymysql.connect(host=self.__host,
                                            user=self.__user,
                                            password=self.__password,
                                            database=self.__database,
                                            cursorclass=pymysql.cursors.DictCursor,
                                            port=int(self.__port))

    def __del__(self):
        pass

    def create_db(self, database_name):
        cursor = self.__connection.cursor()
        try:
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {database_name}
                CHARACTER SET utf8mb4
                );
                """)
            print(f"Created database: {database_name}")
        except Exception as e:
            print(f"Database creation failed: {e}")

    def drop_db(self, database_name):
        cursor = self.__connection.cursor()
        try:
            cursor.execute(f"DROP DATABASE IF EXISTS {database_name});")
            print(f"Dropped database: {database_name}")
        except Exception as e:
            print(f"Database dropping failed: {e}")

    @staticmethod
    def get_query(columns: dict, method: str):
        if method == "CREATE":
            query = f"CREATE TABLE IF NOT EXISTS {columns['name']} ( \n"
            for key in columns:
                if key not in ['name', 'reference', 'primary_key']:
                    query = query + f'{key}' + ' ' + columns[key] + ',\n'
            query = query + f"PRIMARY KEY ({columns['primary_key']})," + '\n'
            for key in columns:
                if key == 'reference':
                    for field in columns[key]:
                        query = query + f"FOREIGN KEY ({field['foreign_key']})\n" + \
                                f"\tREFERENCES {field['referenced_table']}({field['referenced_primary_key']})" + \
                                '\n \tON DELETE CASCADE,\n'
            query = query[:-2] + ')'
            return query
        if method == "INSERT":
            query = f"INSERT INTO {0} ("
            var = "("
            for key in columns:
                if key not in ['name', 'reference', 'primary_key', 'id']:
                    query = query + key
                    var += "%s,"
            var = var[:-1] + ")"
            query = query[:-1] + f') VALUES {var}'
            return query

    def create_table(self, columns: dict):
        print(" creating {} table...".format(columns['name']))
        query = self.get_query(columns, "CREATE")
        cursor = self.__connection.cursor()
        cursor.execute(query)

    def insert_data(self, columns, variables: list):
        print(" inserting data into {} table...".format(columns['name']))
        query = self.get_query(columns, "INSERT")
        cursor = self.__connection.cursor()
        cursor.execute(query, variables)
    # TODO ПОТОМ ЗАКОНЧИТЬ КЛАСС БД ДЛЯ УДОБНОГО ПОЛЬЗОВАНИЯ


print(RobotDatabase.get_query(vb.stock_strategy_column, "INSERT"))