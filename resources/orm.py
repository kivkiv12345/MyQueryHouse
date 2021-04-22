"""
Stores database data and queryset models.
"""

if __name__ == '__main__':
    # Gently remind the user to not run utils.py themselves
    raise SystemExit("(⊙＿⊙') Wha!?... Are you trying to run orm.py?\n"
                     " You know this is a bad idea; right? You should run app.py instead :)")

from typing import Type, Dict, List, Any, Tuple
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor_cext import CMySQLCursor

CONNECTION: MySQLConnection = None
CURSOR: CMySQLCursor = None

DATABASE_NAME = "myqueryhouse"  # Must match the name of the database restoration file!

"""
TABLE_EXCLUSION = {
    'Items': {'itemID', },
    'Locations': {'locationID', },
}

TABLE_KEYS = {'Items': 'itemID',
              'Locations': 'locationID'}
"""

PK_IDENTIFIER = "ID"  # Should reflect how table primary keys are suffixed in the database.


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
        try: CONNECTION.consume_results()
        except Exception: pass
        current_table: str = self.model.Meta.table_name
        CURSOR.execute(f"SELECT * FROM {current_table}")
        self._raw_result = [obj for obj in CURSOR]
        self._query_result = [Models[current_table](obj) for obj in self._raw_result]
        return self

    def __iter__(self):
        for instance in self._query_result.values():
            yield instance


class ModelField:
    name: str = None
    attrs: tuple = None

    def __init__(self, column: tuple) -> None:
        super().__init__()
        self.name, *self.attrs = column

    def __str__(self) -> str:
        return self.name


class _DBModelMeta(type):
    @property
    def objects(cls) -> QuerySet:
        return QuerySet(cls)


class DBModel(metaclass=_DBModelMeta):
    """ Django'esque model class which converts table rows to Python class instances. """

    fields: Dict[str, Any] = None

    def __init__(self, **kwargs) -> None:
        """
        :param table_name: used to override the queried table name.
        """
        print(kwargs)
        super().__init__()

    @property
    def pk(self) -> int:
        return self.fields[self.Meta.pk_column]

    class Meta:
        """ Holds information about the makeup of the current class. """
        table_name: str = None
        pk_column: str = None
        fields: Tuple[ModelField, ...] = None

    def __str__(self) -> str:
        return f"Meta for {self.Meta.table_name}"


Models: Dict[str, Type[DBModel]] = {}


def init_orm():
    global Models

    CURSOR.execute(f"USE {DATABASE_NAME}")
    CURSOR.execute("SHOW TABLES")
    table_names = [table_tuple[0] for table_tuple in CURSOR]

    def get_columns(table_name:str):
        CURSOR.execute(f"SHOW COLUMNS FROM {DATABASE_NAME}.{table_name}")
        columndata = [column for column in CURSOR]
        return columndata, next(col[0] for col in columndata if col[3] == 'PRI')

    for name in table_names:
        columns, pk_column = get_columns(name)  # Get the needed column data for the current model.

        # Declare the new model, and populate it with attributes.
        # The fields dictionary will hold the values contained within an instance of the model.
        model = type(name, (DBModel,), {'fields': {column[0]: None for column in columns}})

        # We add Meta to the model after declaration, such that it may refer back to its model.
        setattr(model, 'Meta', type('Meta', (DBModel.Meta,), {'fields': tuple(ModelField(column) for column in columns), 'pk_column': pk_column, 'table_name': name}))

        # Once we're finished with the current model, we add it to the dictionary with will hold them all.
        Models[name] = model  # We use typehinting to indicate attributes that cannot be inferred from our generic type.

    test2 = Models
    test = Models['Storage'].objects
    print(test)