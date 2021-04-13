"""
Stores database data and queryset models.
"""

if __name__ == '__main__':
    # Gently remind the user to not run utils.py themselves
    raise SystemExit("(⊙＿⊙') Wha!?... Are you trying to run orm.py?\n"
                     " You know this is a bad idea; right? You should run app.py instead :)")

from typing import Type, Dict
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor_cext import CMySQLCursor

CONNECTION: MySQLConnection = None
CURSOR: CMySQLCursor = None

TABLE_EXCLUSION = {
    'Items': {'itemID', },
    'Locations': {'locationID', },
}

TABLE_KEYS = {'Items': 'itemID',
              'Locations': 'locationID'}


class QuerySet:
    """
    Django'esque queryet class which allows for retrieving a list of models from the database.
    Currently only able to retrieve all rows of a table.
    """
    model = None
    _evaluated = False
    _raw_result: Dict[str, Dict[str, str]] = None
    _query_result: Dict[str, Type[object]] = None

    def __init__(self, model) -> None:
        """
        :param model: Hints at to which table should be queried.
        """
        super().__init__()
        self.model: Type[DBModel] = model
        self._raw_result = {}
        self._query_result: Dict[str, Type[DBModel]] = {}

        self.evaluate()  # TODO Kevin: Remember that queries are to be lazy.

    def evaluate(self):
        """ Performs the query """
        CURSOR.execute(f"SELECT * FROM {self.model.table_name}")
        self._raw_result = [obj for obj in CURSOR]
        raise NotImplementedError()


class DBModel:
    """ Django'esque model class which converts table rows to Python class instances. """
    table_name:str = None

    def __init__(self, table_name:str=None) -> None:
        """
        :param table_name: used to override the queried table name.
        """
        super().__init__()
        self.table_name = table_name or self.__name__

    @property
    def objects(self) -> QuerySet:
        return QuerySet(self.__class__)