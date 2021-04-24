"""
Stores database data and queryset models.
"""
from copy import copy

if __name__ == '__main__':
    # Gently remind the user to not run utils.py themselves
    raise SystemExit("(⊙＿⊙') Wha!?... Are you trying to run orm.py?\n"
                     " You know this is a bad idea; right? You should run app.py instead :)")

from typing import Type, Dict, List, Any, Tuple, Union, Set
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
    _raw_result: Tuple[tuple, ...] = ()
    _query_result = ()

    def __init__(self, model) -> None:
        """
        :param model: Hints at to which table should be queried.
        """
        super().__init__()
        self.model: Type[DBModel] = model
        self._query_result: Tuple[DBModel] = ()

        self.evaluate()  # TODO Kevin: Remember that queries are to be lazy.

    def evaluate(self):
        """ Performs the query and caches the result. """
        try: CONNECTION.consume_results()
        except Exception: pass
        current_table: str = self.model.Meta.table_name
        CURSOR.execute(f"SELECT * FROM {current_table}")
        self._raw_result = *(obj for obj in CURSOR),
        self._query_result = *(Models[current_table](obj) for obj in self._raw_result),
        self._evaluated = True
        return self

    def __iter__(self):
        if not self._evaluated: self.evaluate()
        for instance in self._query_result:
            yield instance

    def create(self, **kwargs):
        """ Creates an instance of the specified model, saves it to the database, and returns it to the user. """
        invalid_field = next((field for field in kwargs.keys() if field not in self.model.fields), None)
        if invalid_field: raise AttributeError(f"{invalid_field} is not a valid field for {self.model}.")

        # Check for NOT NULL fields that arent specified.
        missing_required = next((field.name for field in self.model.Meta.fields if field.attrs[1] == 'NO' and field.attrs[2] != 'PRI' and field.name not in kwargs.keys()), None)
        if missing_required: raise AttributeError(f"Cannot create {self.model} object without a value for {missing_required}")

        instance = self.model(**kwargs)  # Create the instance before we save it.
        instance.save()  # TODO Kevin: Get the primary key from the database when done.

    def __str__(self) -> str:
        return f"{self.__class__.__name__} object of {self.model.__name__}"


class ModelField:
    """ Represents metadata for a column in the database, holds its name and other attributes. """
    name: str = None
    attrs: tuple = None  # A tuple of metadata; such as whether the column is a primary key.

    def __init__(self, column: tuple) -> None:
        super().__init__()
        self.name, *self.attrs = column

    def __str__(self) -> str:
        return self.name


class _DBModelMeta(type):
    @property
    def objects(cls) -> QuerySet:
        """ :return: A lazy queryset which may be altered before eventually being evaluated when iterated over (for example). """
        # Metaclassing somehow has to subclass itself be passed as an argument,
        # which we forward to the queryset constructor.
        return QuerySet(cls)


class DBModel(metaclass=_DBModelMeta):
    """ Django'esque model class which converts table rows to Python class instances. """

    model = None
    values: Dict[str, Any] = None  # Holds the values of the instances.
    _initial_values: Dict[str, Any] = None  # Holds the initial values for comparison when saving.

    def __init__(self, *args, zipped_data: zip = None, **kwargs) -> None:
        """
        :param table_name: used to override the queried table name.
        """
        # Allow a more readable way to access the class itself from its instances.
        self.model: Type[DBModel] = self.__class__

        if kwargs:
            invalid_field = next((field for field in kwargs.keys() if field not in {metafield.name for metafield in self.Meta.fields}), None)
            if invalid_field: raise AttributeError(f"{invalid_field} is not a valid field for {self.model}")
            self.values = kwargs
            self._initial_values = copy(self.values)
        else:
            # Zip the data correctly, such that we pair column names with their values.
            data = zipped_data or zip(self.Meta.fieldnames, *args)
            # Convert the result to a dictionary.
            datadict = {fieldname: value for fieldname, value in data}

            # Take care that we don't set invalid fields for the instance.
            invalid_fields = set(datadict.keys()).difference(self.Meta.fieldnames)
            if invalid_fields: raise AttributeError(f"{invalid_fields} are not valid fields for {self.model}")

            # Merge the values into the class.
            self.values = datadict
            self._initial_values = copy(self.values)

        super().__init__()

    @property
    def pk(self) -> int:
        """ Returns the value of the current instance's primary key. """
        return self.values[self.Meta.pk_column]

    def save(self) -> None:  # TODO Kevin: Test save.
        """ Saves or updates the current instance in the database. """
        diff = {column: value for column, value in self.values if (value or self._initial_values[column])}
        if self.pk:
            values = str(tuple(f"{column} = |||{value}|||" for column, value in diff.items()))[1:-2].replace(r"'",'').replace('|||', r"'")
            CURSOR.execute(f"UPDATE {self.Meta.table_name} SET {values} WHERE {self.Meta.pk_column} = {self.pk}")
        else:
            columns, values = diff.items()
            CURSOR.execute(f"INSERT INTO {self.Meta.table_name}({columns}) VALUES {values}")

    def delete(self):
        raise NotImplementedError("Cannot delete yet!")

    class Meta:
        """ Holds information about the makeup of the current class. """
        _col_hint = Union[str, None]

        table_name: str = None
        pk_column: str = None
        fields: Tuple[ModelField, ...] = None
        fieldnames: Set[str] = None
        column_data: Tuple[Tuple[_col_hint, bytes, _col_hint, _col_hint, _col_hint, _col_hint], ...]

        def __str__(self) -> str:
            return f"Meta for {self.table_name}"

    def __str__(self) -> str:
        """ :return: The class name paired with its primary key, when referring to an instance. Otherwise returns super. """
        return f"{self.__class__.__name__} object ({self.pk})" if self.pk else super(DBModel, self).__str__()


Models: Dict[str, Type[DBModel]] = {}


def init_orm():
    global Models

    CURSOR.execute(f"USE {DATABASE_NAME}")
    CURSOR.execute("SHOW TABLES")
    table_names = [table_tuple[0] for table_tuple in CURSOR]

    def get_columns(table_name:str):
        CURSOR.execute(f"SHOW COLUMNS FROM {DATABASE_NAME}.{table_name}")
        columndata = *(column for column in CURSOR),
        # Returns a tuple of the things we need (All metadata for columns, and the primary key column).
        return columndata, next(col[0] for col in columndata if col[3] == 'PRI')

    for name in table_names:
        columns, pk_column = get_columns(name)  # Get the needed column data for the current model.

        # Declare the new model, and populate it with attributes.
        # The fields dictionary will hold the values contained within an instance of the model.
        model = type(name, (DBModel,), {'fields': {column[0]: None for column in columns}})

        # We add Meta to the model after declaration, such that it may refer back to its model.
        metadata = {
            'fields': tuple(ModelField(column) for column in columns),
            'fieldnames': frozenset(column[0] for column in columns),
            'pk_column': pk_column,
            'table_name': name,
            'column_data': columns,
        }

        setattr(model, 'Meta', type('Meta', (DBModel.Meta,), metadata))

        # Once we're finished with the current model, we add it to the dictionary with will hold them all.
        Models[name] = model  # We use typehinting to indicate attributes that cannot be inferred from our generic type.

    test2 = Models
    test = Models['Storage'].objects
    print([str(i) for i in test])
    print(test)