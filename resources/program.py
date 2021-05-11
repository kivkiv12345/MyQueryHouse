"""
This module holds the different UIs that appear while the program progresses through its main loop.
"""

if __name__ == '__main__':
    # Gently remind the user to not run program.py themselves
    raise SystemExit("(⊙＿⊙') Wha!?... Are you trying to run program.py?\n"
                     " You do know it's only used to store utilities; right? You should run app.py instead :)")

import tkinter as tk
from typing import Set, Dict, Tuple, List, Type
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor_cext import CMySQLCursor
from subprocess import DEVNULL, call
from tkintertable import TableCanvas
from frozendict import frozendict
from copy import deepcopy
from mysql.connector import ProgrammingError
from resources import orm  # Module wide import needed to specify CONNECTION and CURSOR from orm.
from resources.orm import Models, DBModel, QuerySet
from datetime import datetime
from tkinter.messagebox import askyesno
from resources.widgets import VerticalScrolledFrame, OutputLog, SwitchViewModeButton
from resources.enums import ViewModes
from resources.utils import TkUtilWidget, OrmTableModel

# VARS
root_title = "MyQueryHouse | MySQL Connector Program"
DATABASE_NAME = "myqueryhouse"  # Must match the name of the database restoration file!


# Classes
class LoginBox(TkUtilWidget):
    """
    Used to prompt the user for login details.
    Provided information may be retrieved in the 'logindeets' dictionary.
    """
    logindeets: dict = None

    host_input: tk.Entry = None
    user_input: tk.Entry = None
    password_input: tk.Entry = None

    def _confirm(self, *args):
        self.logindeets = {
            'host': self.host_input.get(),
            'user': self.user_input.get(),
            'passwd': self.password_input.get()
        }

        self.destroy(True)

    def __init__(self, failed_connection:str=False, screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.title("Login")
        self.logindeets = {'host': None, 'user': None, 'passwd': None, }

        if failed_connection:
            tk.Label(self, text=f"Connection to server failed, stating: \n{failed_connection},\nPlease try again.").pack()

        hostdefault = tk.StringVar(); hostdefault.set("localhost")
        tk.Label(self, text="Connection server").pack()
        self.host_input = tk.Entry(self, text=hostdefault)
        self.host_input.pack()

        userdefault = tk.StringVar(); userdefault.set("root")
        tk.Label(self, text="Connection user").pack()
        self.user_input = tk.Entry(self, text=userdefault)
        self.user_input.pack()

        tk.Label(self, text="Connection password").pack()
        self.password_input = tk.Entry(self, show="*")
        self.password_input.pack()
        self.password_input.focus_set()

        tk.Button(self, text='Confirm settings', command=self._confirm).pack()

        self.bind('<Return>', self._confirm)  # ENTER should confirm the user input.


class CreateDatabaseMessage(TkUtilWidget):
    """
    Will be initialized if the project database couldn't be found on the desired MySQL server.
    Asks the user if the want the database to be automatically created and populated with data.
    """
    pop_db_checkbox: tk.Checkbutton = None
    populate_db: tk.BooleanVar = None

    # We store the MySQL connection details in this class, such that the database may be created here as well.
    db_name: str = None
    db_cursor: CMySQLCursor = None
    db_connection: MySQLConnection = None
    db_password:str = None

    def _confirm(self, *args):
        try:
            try: self.db_cursor.execute(f"CREATE DATABASE {self.db_name}")  # Apparently can't pass db_name as a positional argument when creating a database ¯\_(ツ)_/¯
            except ProgrammingError: pass  # The database probably already exists, which is fine by us (unless we want to wipe it first).

            # Run a command which will load the contents of a .sql file into an existing database.
            # This seems to be the best we can do for now; ideally we would create it as well.
            with open(f"database_backups/{DATABASE_NAME}{'(empty)' if not self.populate_db.get() else ''}.sql") as db_file:
                call(["mysql", "-u", "root", f"--password={self.db_password}", DATABASE_NAME], stdin=db_file, stdout=DEVNULL, stderr=DEVNULL)
        except ProgrammingError as e:
            print(f"Failed to restore database from {DATABASE_NAME}.sql; stating: '{e}',\ndoes the file exist?")

        self.db_cursor.execute(f"USE {self.db_name}")  # Use the database, regardless of how it was created.

        self.destroy(True)  # Destroy this widget, and progress to the next.

    def __init__(self, db_name:str, db_cursor:CMySQLCursor, db_connection:MySQLConnection, db_password:str, screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.db_name, self.db_cursor, self.db_connection, self.db_password = db_name, db_cursor, db_connection, db_password

        self.title(f"Create database {db_name}")
        tk.Label(self, text=f"A database called '{db_name}' could not be found on the server,\n"
                            f"This database must be created before the program can continue.\n").pack()

        self.populate_db = tk.BooleanVar()
        self.pop_db_checkbox = tk.Checkbutton(self, text=f"Should the database be prepopulated with filler data?\nContents will be read from '{db_name}.sql'", variable=self.populate_db)
        self.pop_db_checkbox.select()
        self.pop_db_checkbox.pack()

        tk.Button(self, text='Create database', command=self._confirm).pack()


class MainDBView(TkUtilWidget):
    """ This is the main widget that will be shown when a successful connection to the database has been made. """

    # Database connection details.
    db_name: str = None
    db_cursor: CMySQLCursor = None
    db_connection: MySQLConnection = None
    password: str = None

    # Widget details
    db_scrollview: VerticalScrolledFrame = None
    rowframe: tk.Frame = None
    rowtable: TableCanvas = None
    outlog: tk.Text = None
    actionframe: tk.Frame = None
    commitbutton: tk.Button = None

    model: Type[DBModel] = None  # Currently applicable model

    primary_keys: Set[int] = None  # Used to calculate the deleted rows in the shown table.
    initial_data = None  # Used to compare which rows needs to be updated in the database.
    queryset: List[DBModel] = None

    def __init__(self, db_name:str, db_cursor:CMySQLCursor, db_connection:MySQLConnection, password:str, screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)

        # Make some assignments from provided or default variables.
        self.db_name, self.db_cursor, self.db_connection, self.password = db_name, db_cursor, db_connection, password
        self.tablemodel, self.queryset = OrmTableModel(), []

        self.title(root_title)

        #self.geometry("1000x500")
        #self.configure(bg="gray")

        self.db_scrollview = VerticalScrolledFrame(self, highlightbackground="black", highlightthickness=1)
        tk.Label(self, text="Tables").grid(column=0)
        self.db_scrollview.grid(column=0)

        tk.Label(self, text="Rows").grid(column=2, row=0)

        # The primary widget (namely; the table), which shows the rows in the database.
        self.rowframe = tk.Frame(self)
        self.rowframe.grid(column=2, row=1)
        self.rowtable = TableCanvas(self.rowframe, model=self.tablemodel)
        self.rowtable.show()

        tk.Label(self, text="Actions").grid(column=0, row=2)

        # A frame to hold action buttons for the program.
        self.actionframe = tk.Frame(self, highlightbackground="black", highlightthickness=1)
        self.actionframe.grid(column=0, row=3)

        # Buttons for the actions frame.
        SwitchViewModeButton(self.db_scrollview, self.actionframe, width=20).grid(column=0)
        tk.Button(self.actionframe, width=20, text=f"Delete {self.db_name}", command=self._delete_database).grid(column=0)
        self.commitbutton = tk.Button(self.actionframe, width=20, text=f"Commit to {self.db_name}", command=self._save)
        self.commitbutton.grid(column=0)
        tk.Button(self.actionframe, width=20, text=f"Backup of {self.db_name}", command=self._backup_database).grid(column=0)
        tk.Button(self.actionframe, width=20, text=f"Restore from backup", command=self._restore_database).grid(column=0)
        tk.Button(self.actionframe, width=20, text=f"Log out", command=self._log_out).grid(column=0)

        self.db_scrollview.show_mode(ViewModes.TABLE)

        tk.Label(self, text="Output Log").grid(column=2, row=2)

        # A simple output log, which, amongst other things, shows executed statements.
        self.outlog = OutputLog(self, height=10, width=70)
        self.outlog.grid(column=2, row=3)

    def _table_click(self, table_name: str, mode:ViewModes=ViewModes.TABLE):
        """ Runs when clicking any table button. """
        self.title(f"{root_title} | {table_name}")

        if mode is ViewModes.VIEW:
            self.model = self.queryset = None  # Remove outdated values from last mode.
            self.tablemodel.createEmptyModel()  # Remove existing content from the model.
            self.db_cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columnnames = *(names[0] for names in self.db_cursor),
            self.db_cursor.execute(f"SELECT * FROM {table_name}")
            # Absolutely terrible! It would appear that tkintertables can't handle decimal values.
            data = {i: dict(zip(columnnames, (str(n) if n is not None else n for n in values))) for i, values in enumerate(self.db_cursor)}
            self.tablemodel.importDict(data)
            self.commitbutton.config(state=tk.DISABLED)  # Disables the commit function when showing view results.
        else:
            self.model = Models[table_name]
            self.queryset: QuerySet = self.model.objects
            self.tablemodel.change_queryset(self.queryset)
            self.commitbutton.config(state=tk.NORMAL)  # Re-enable commit functionality when showing tables.

        self.rowtable.destroy()  # Reinstating the table seems to work best.
        self.rowtable = TableCanvas(self.rowframe, model=self.tablemodel)
        self.rowtable.show()
        self.rowtable.autoResizeColumns()
        model = self.rowtable.getModel()
        self.primary_keys = set(model.reclist)
        self.initial_data = frozendict(deepcopy(model.data))

    def _delete_database(self):
        """ Runs when clicking the delete database button. """
        if askyesno(f"delete '{self.db_name}'?", f"Are you sure you want to delete '{self.db_name}' from the server?"):
            self.db_cursor.execute(f"DROP DATABASE {self.db_name}")
            self.destroy(True)

    def _save(self):
        """ Writes written changes to the database. """
        model = self.rowtable.getModel()

        # TODO Kevin: Reordering columns for inserted rows leads to incorrect SQL.

        # Read how the rows in the table have changed, and use the corresponding queries further on.
        deleted_rows = self.primary_keys.difference(set(model.reclist))
        new_rows: Tuple[Dict[str, str], ...] = *(row for pk, row in model.data.items() if pk not in self.primary_keys),
        update_rows = {instance.pk: {column: value for column, value in instance.values.items() if value != instance._initial_values[column]} for instance in self.queryset if instance.values != instance._initial_values}

        statements: List[str] = []

        table_name, pk_column = self.model.Meta.table_name, self.model.Meta.pk_column  # Shorten Meta names.

        if deleted_rows:  # Perform a single query which drops all the desired rows.
            statements.append(f"DELETE FROM {table_name} WHERE {pk_column} IN ({', '.join(str(i) for i in deleted_rows)})")
        if new_rows:  # Perform a single query which inserts all the desired rows.
            columnnames = list(new_rows[0].keys())  # Column names should be the same for all rows.
            values = ', '.join("('" + "', '".join(row.values()) + "')" for row in new_rows)
            statements.append(f"INSERT INTO {DATABASE_NAME}.{table_name}({', '.join(columnnames)}) VALUES {values}")
        if update_rows:
            for pk, data in update_rows.items():
                values = str(tuple(f"{column} = |||{value}|||" for column, value in data.items()))[1:-2].replace(r"'", '').replace('|||', r"'")
                statements.append(f"UPDATE {table_name} SET {values} WHERE {pk_column} = {pk}")

        _sql = ";\n".join(statements)  # F-strings can't include escape sequences.

        # TODO Kevin: Allow the user to edit the executed SQL.
        #_sql = ask_text_answer("Do you want the following SQL to be executed on the database?:", _sql)

        if not statements:
            self.outlog.insert('Canceled attempt to commit: Nothing to commit!')
        elif askyesno("Confirm statements", f"Do you want the following SQL to be executed on the database?:\n\n{_sql}"):
            #self.db_cursor.execute("; ".join(statements))
            for command in statements:
                self.db_cursor.execute(command)
            self.db_connection.commit()
            changecount = len(deleted_rows) + len(new_rows) + len(update_rows)
            self.outlog.insert(f"committed {changecount} change{'s' if changecount != 1 else ''} to {self.db_name}, at {datetime.now()}.")
            self.outlog.insert(_sql)
            self._table_click(table_name)  # Temporary solution to reset stored primary keys.

    def destroy(self, deliberate=False):
        """ Resets the database connection before calling super. """
        orm.CURSOR.close(); orm.CONNECTION.close()
        orm.CONNECTION = orm.CURSOR = None  # Reset the MySQL connection.
        super().destroy(deliberate)

    def _log_out(self):
        """ Creates a window which prompts the user as to if they want to log out. """
        if askyesno(title='Log out?', message='Are you sure you want to log out?'): self.destroy(True)

    def __str__(self): return f"Table of {self.model.Meta.table_name}"

    def _backup_database(self):
        """ Writes the current contents of the database to a corresponding file in the 'database_backups' directory. """
        with open(f"database_backups/{DATABASE_NAME}.sql", 'w+') as db_file:
            call(["mysqldump", "-u", "root", f"--password={self.password}", DATABASE_NAME], stdin=DEVNULL, stdout=db_file, stderr=DEVNULL)

    def _restore_database(self):
        """
        Restores the contents of the current database from a corresponding file in the 'database_backups' directory.
        """
        with open(f"database_backups/{DATABASE_NAME}.sql", 'r+') as db_file:
            call(["mysql", "-u", "root", f"--password={self.password}", DATABASE_NAME], stdin=db_file, stdout=db_file, stderr=DEVNULL)
