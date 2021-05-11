"""
Stores database data and queryset models.
"""

if __name__ == '__main__':
    # Gently remind the user to not run program.py themselves
    raise SystemExit("(⊙＿⊙') Wha!?... Are you trying to run orm.py?\n"
                     " You know this is a bad idea; right? You should run app.py instead :)")

from typing import Type, Dict, List, Any, Tuple, Union, Set
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor_cext import CMySQLCursor
from copy import copy
from resources.enums import FieldTypes
from resources.exceptions import AbstractInstantiationError

CONNECTION: MySQLConnection = None
CURSOR: CMySQLCursor = None

DATABASE_NAME = "myqueryhouse"  # Must match the name of the database restoration file!


class QuerySet:
    """
    Django'esque queryet class which allows for retrieving a list of models from the database.
    Currently only able to retrieve all rows of a table.
    """
    model = None
    _evaluated = False
    _query_result: list = None

    def __init__(self, model) -> None:
        """
        :param model: Hints at to which table should be queried.
        """
        super().__init__()
        self.model: Type[DBModel] = model
        self._query_result: List[DBModel] = []

        self.evaluate()  # TODO Kevin: Remember that queries are to be lazy.

    def evaluate(self):
        """ Performs the query and caches the result. """
        try: CONNECTION.consume_results()
        except Exception: pass
        current_table: str = self.model.Meta.table_name
        CURSOR.execute(f"SELECT * FROM {DATABASE_NAME}.{current_table}")
        self._query_result = [Models[current_table](obj) for obj in CURSOR]
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
        missing_required = next((field.name for field in self.model.Meta.fields if field.attrs[1] == 'NO' and field.type != 'PRI' and field.name not in kwargs.keys()), None)
        if missing_required: raise AttributeError(f"Cannot create {self.model} object without a value for {missing_required}")

        instance = self.model(**kwargs)  # Create the instance before we save it.
        instance.save()  # TODO Kevin: Get the primary key from the database when done.

    def __str__(self) -> str:
        return f"{self.__class__.__name__} object of {self.model.__name__}"


class ModelField:
    """ Represents metadata for a column in the database, holds its name and other attributes. """
    name: str = None
    byte_type: bytes = None  # Holds something about the byte type of this field.
    no: str = None  # No idea what this means as of yet.
    type: str = None  # Describes whether this field is a foreignkey, primary key or neither.
    attrs: tuple = None  # A tuple of additional metadata.

    def __init__(self, column: tuple) -> None:
        super().__init__()
        self.name, self.byte_type, self.no, self.type, *self.attrs = column

    def __str__(self) -> str: return self.name


class _DBModelMeta(type):
    """
    Black magic metaclass; which in our case allows us to specify properties,
    that are provided classes instead of instances when called on classes themselves.
    """
    @property
    def objects(cls) -> QuerySet:
        """ :return: A lazy queryset which may be altered before eventually being evaluated when iterated over (for example). """
        # Metaclassing somehow makes the subclass itself be passed as an argument,
        # which we forward to the queryset constructor.
        return QuerySet(cls)


class DBModel(metaclass=_DBModelMeta):
    """ Django'esque model class which converts table rows to Python class instances. """

    model = None
    values: Dict[str, Any] = None  # Holds the values of the instances.
    _initial_values: Dict[str, Any] = None  # Holds the initial values for comparison when saving.

    # NOTE Encapsulation: __getting is private (hidden), and cannot be reached from outside its class.
    __getting = [False, ]  # True when the overloaded __getattribute__ methods should be ignored, used to prevent recursion.

    def __init__(self, *args, zipped_data: zip = None, **kwargs) -> None:
        """ Accepts multiple ways to pass model instance data. """
        if type(self) is DBModel:  # NOTE Abstraction: This exceptions prevents creation of instances of the base class.
            raise AbstractInstantiationError("Cannot instantiate instances of DBModel itself, use subclasses instead.")

        # Allow a more readable way to access the class itself from its instances.
        self.model: Type[DBModel] = self.__class__

        # We allow several different ways to pass data to the constructor of the model instance
        if kwargs:
            invalid_field = next((field for field in kwargs.keys() if field not in {metafield.name for metafield in self.Meta.fields}), None)
            if invalid_field: raise AttributeError(f"{invalid_field} is not a valid field for {self.model}")
            self.values = kwargs
        else:
            # Zip the data correctly, such that we pair column names with their values.
            data = zipped_data or zip(self.Meta.fieldnames, *args) or {field: None for field in self.Meta.fieldnames}
            # Convert the result to a dictionary.
            datadict = {fieldname: value for fieldname, value in data}

            # Take care that we don't set invalid fields for the instance.
            invalid_fields = set(datadict.keys()).difference(set(self.Meta.fieldnames))
            if invalid_fields: raise AttributeError(f"{invalid_fields} are not valid fields for {self.model}")

            # Merge the values into the class.
            self.values = datadict

        # We run these assignments sequentially,
        # to ensure that the primary key is removed from the dictionary, before it is copied.
        self._initial_values = copy(self.values)

        super().__init__()

    @property
    def pk(self) -> int:
        """ Returns the value of the current instance's primary key. """
        return self.values.get(self.Meta.pk_column, None)

    def save(self) -> None:  # TODO Kevin: Test save.
        """ Saves or updates the current instance in the database. """
        raise NotImplementedError("Save method is currently not finished.")
        diff = {column: value for column, value in self.values if (value or self._initial_values[column])}
        if self.pk:
            values = str(tuple(f"{column} = |||{value}|||" for column, value in diff.items()))[1:-2].replace(r"'",'').replace('|||', r"'")
            CURSOR.execute(f"UPDATE {self.Meta.table_name} SET {values} WHERE {self.Meta.pk_column} = {self.pk}")
        else:
            columns, values = diff.items()
            CURSOR.execute(f"INSERT INTO {self.Meta.table_name}({columns}) VALUES {values}")

    def delete(self): raise NotImplementedError("Cannot delete yet!")

    class Meta:
        """ Holds information about the makeup of the current class. """
        _col_hint = Union[str, None]

        table_name: str = None
        pk_column: str = None
        fields: Tuple[ModelField, ...] = None
        fieldnames: Tuple[str] = ()
        column_data: Tuple[Tuple[_col_hint, bytes, _col_hint, _col_hint, _col_hint, _col_hint], ...]

        def __str__(self) -> str:
            return f"Meta for {self.table_name}"

    def __str__(self) -> str:
        """ :return: The class name paired with its primary key, when referring to an instance. Otherwise returns super. """
        return f"{self.__class__.__name__} object ({self.pk})" if self.pk else super(DBModel, self).__str__()

    def __getattribute__(self, name: str, getting=__getting) -> Any:
        return super().__getattribute__(name)
        """ Lazily queries related foreignkey rows. """
        if not getting[0]:  # TODO Kevin: Perhaps find a less impactful way to accomplish this than overriding __getattribute__.
            with IndexChangedTo(getting, True):
                if name in self.values and type(self.values[name]) is int and next((field for field in self.Meta.fields if field.type is FieldTypes.FOREIGN_KEY and field.name == name), None):
                    pass  # TODO Kevin: Query the related table for the related row.
                return getattr(self, name)
        else:
            return super().__getattribute__(name)


Models: Dict[str, Type[DBModel]] = {}


def init_orm() -> Dict[str, Type[DBModel]]:
    """
    Populates the global Models dictionary with models matching tables in the database.
    Ought to only ever be run once during the app startup.
    :return: The populated Models dictionary.
    """
    global Models  # Make a reference to the global Models dictionary.

    CURSOR.execute(f"USE {DATABASE_NAME}")
    CURSOR.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
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
        model = type(name, (DBModel,), {})

        # We add Meta to the model after declaration, such that it may refer back to its model.
        metadata = {
            'fields': tuple(ModelField(column) for column in columns),
            'fieldnames': tuple(column[0] for column in columns),
            'pk_column': pk_column,
            'table_name': name,
            'column_data': columns,
        }

        model.Meta = type('Meta', (DBModel.Meta,), metadata)

        # Once we're finished with the current model, we add it to the dictionary with will hold them all.
        Models[name] = model  # We use typehinting to indicate attributes that cannot be inferred from our generic type.

    return Models