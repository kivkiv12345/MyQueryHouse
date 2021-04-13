"""
This module holds the utility methods and classes used by MyQueryHouse.
"""

if __name__ == '__main__':
    # Gently remind the user to not run utils.py themselves
    raise SystemExit("(⊙＿⊙') Wha!?... Are you trying to run utils.py?\n"
                     " You do know it's only used to store utilities; right? You should run app.py instead :)")

import tkinter as tk
from pathlib import Path
from typing import TypeVar, Set, Dict, Tuple
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor_cext import CMySQLCursor
from subprocess import DEVNULL, call
from tkintertable import TableCanvas, TableModel
from frozendict import frozendict
from copy import deepcopy
from mysql.connector import ProgrammingError
from orm import TABLE_EXCLUSION, TABLE_KEYS
from datetime import datetime
from tkinter.messagebox import askyesno


# VARS
PathLike = TypeVar("PathLike", str, Path, None)
DB_DATA_FILE: PathLike = 'db_data.json'

root_title = "MyQueryHouse | MySQL Connector Program"
DATABASE_NAME = "myqueryhouse"  # Must match the name of the database restoration file!


# Classes
class TkUtilWidget(tk.Tk):
    """ Holds some common utilities for widgets made for this application. """

    def destroy(self, deliberate=False):
        """
        Calls super and allows the program to continue to its next phase, based on context.
        :param deliberate: True when the program should continue when this function is called.
        """
        super().destroy()
        if not deliberate: raise SystemExit(f"{self}, wishes to stop the Tkinter application.")

    def __str__(self):
        """ Prevent Tkinter from displaying the name as . """
        return object.__str__(self)


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

            self.db_cursor.execute(f"USE {self.db_name}")

            if self.populate_db.get():
                # Run a command which will load the contents of a .sql file into an existing database.
                # This seems to be the best we can do for now; ideally we would create it as well.
                call(["mysql", "-u", "root", f"--password={self.db_password}", DATABASE_NAME], stdin=open(f"{DATABASE_NAME}.sql"), stdout=DEVNULL, stderr=DEVNULL)
            else:
                # TODO Kevin: Perhaps automate creation of needed tables?
                # Create the tables needed by the program.
                self.db_cursor.execute("""CREATE TABLE Items (
                                            productname varchar(50) NOT NULL, 
                                            description varchar(400), 
                                            itemID int PRIMARY KEY AUTO_INCREMENT NOT NULL
                                        )""")
                self.db_cursor.execute("""CREATE TABLE Locations (
                                            shelf smallint UNSIGNED NOT NULL, 
                                            space smallint UNSIGNED NOT NULL, 
                                            locationID int PRIMARY KEY AUTO_INCREMENT NOT NULL,
                                            itemID INT,
                                            FOREIGN KEY (itemID) 
                                                REFERENCES Items(itemID)
                                                ON DELETE SET NULL
                                        )""")
                # TODO Kevin: commit may be needed.
                #self.db_connection.commit()
        except ProgrammingError as e:
            print(f"Failed to restore database from {DATABASE_NAME}.sql; stating: '{e}',\ndoes the file exist?")

        self.destroy(True)

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


class VerticalScrolledFrame(tk.Frame):  # Shamelessly stolen from: https://stackoverflow.com/questions/31762698/dynamic-button-with-scrollbar-in-tkinter-python
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


class MainDBView(TkUtilWidget):
    """ This is the main widget that will be shown when a successful connection to the database has been made. """

    # Database connection details.
    db_name: str = None
    db_cursor: CMySQLCursor = None
    db_connection: MySQLConnection = None

    rowframe: tk.Frame = None
    rowtable: TableCanvas = None

    table_name: str = None  # Currently selected table is stored here for ease of access

    primary_keys: Set[int] = None  # Used to calculate the deleted rows in the shown table.
    initial_data = None  # Used to compare which rows needs to be updated in the database.

    def __init__(self, db_name:str, db_cursor:CMySQLCursor, db_connection:MySQLConnection, screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.db_name, self.db_cursor, self.db_connection = db_name, db_cursor, db_connection

        self.title(root_title)

        self.geometry("1000x500")
        #self.configure(bg="gray")

        db_scrollview = VerticalScrolledFrame(self)
        tk.Label(self, text="Tables").grid(column=0)
        db_scrollview.grid(column=0)

        db_cursor.execute("SHOW TABLES")

        db_names = (db[0] for db in db_cursor)
        for table_name in db_names:
            btn = tk.Button(db_scrollview.interior, height=1, width=20, relief=tk.FLAT,
                            bg="gray99", fg="black", text=table_name,
                            command=lambda name=table_name: self._table_click(name))
            btn.pack(padx=10, pady=5, side=tk.TOP)

        tk.Button(self, text=f"Delete {self.db_name}", command=self._delete_database).grid(column=0)
        tk.Button(self, text=f"Commit to {self.db_name}", command=self._save).grid(column=0)
        tk.Button(self, text=f"Log out", command=self._log_out).grid(column=0)

        self.tablemodel = TableModel()

        self.rowframe = tk.Frame(self)
        self.rowframe.grid(column=2, row=1)
        self.rowtable = TableCanvas(self.rowframe)
        self.rowtable.show()

    def _table_click(self, table_name: str):
        """ Runs when clicking any table button. """
        self.title(f"{root_title} | {table_name}")
        self.table_name = table_name
        self.db_cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columnnames = [columntuple[0] for columntuple in self.db_cursor]

        self.db_cursor.execute(f"SELECT * FROM {table_name}")

        # TODO Kevin: data breaks with empty database.
        #data = {f"row{i}": {name: value for name, value in zip(columnnames, data) if name not in TABLE_EXCLUSION[self.table_name]} for i, data in enumerate(self.db_cursor)}
        data = {
            next(fieldlist[index] for index, name in enumerate(columnnames) if name == TABLE_KEYS[self.table_name]):
                {name: value for name, value in zip(columnnames, fieldlist) if name not in TABLE_EXCLUSION[self.table_name]}
            for fieldlist in self.db_cursor
        }
        #data = {dict(zip(columnnames, fieldlist))[TABLE_KEYS[self.table_name]]: dict(zip(columnnames, fieldlist)) for fieldlist in self.db_cursor}
        """
        data will be in the same format as this example taken from the tkinter docs.
        {
            'rec1': {'col1': 99.88, 'col2': 108.79, 'label': 'rec1'},
            'rec2': {'col1': 99.88, 'col2': 108.79, 'label': 'rec2'}
        }
        """

        self.rowtable.destroy()  # Reinstating the table seems to work best.
        self.rowtable = TableCanvas(self.rowframe, data=data)
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

        # Read how the rows in the table have changed, and use the corresponding queries further on.
        deleted_rows = self.primary_keys.difference(set(model.reclist))
        new_rows: Tuple[Dict[str, str], ...] = *(row for pk, row in model.data.items() if pk not in self.primary_keys),
        update_rows = {pk: {column: value for column, value in data.items() if value != self.initial_data[pk][column]} for pk, data in model.data.items() if pk in self.primary_keys and data != self.initial_data[pk]}

        # TODO Kevin: Simultaneous deletions and additions override each others primary keys.
        if deleted_rows:  # Perform a single query which drops all the desired rows.
            self.db_cursor.execute(f"DELETE FROM {self.table_name} WHERE {TABLE_KEYS[self.table_name]} IN ({', '.join(str(i) for i in deleted_rows)})")
        if new_rows:  # Perform a single query which inserts all the desired rows.
            columnnames = list(new_rows[0].keys())  # Column names should be the same for all rows.
            values = ', '.join("('" + "', '".join(row.values()) + "')" for row in new_rows)
            self.db_cursor.execute(f"INSERT INTO {self.table_name}({', '.join(columnnames)}) VALUES {values}")
        if update_rows:
            for pk, data in update_rows.items():
                values = str(tuple(f"{column} = |||{value}|||" for column, value in data.items()))[1:-2].replace(r"'", '').replace('|||', r"'")
                self.db_cursor.execute(f"UPDATE {self.table_name} SET {values} WHERE {TABLE_KEYS[self.table_name]} = {pk}")

        self.db_connection.commit()
        changecount = len(deleted_rows) + len(new_rows) + len(update_rows)
        print(f"committed {changecount} change{'s' if changecount != 1 else ''} to {self.db_name}, at {datetime.now()}.")
        self._table_click(self.table_name)  # Temporary solution to reset stored primary keys.

    def _log_out(self):
        """ Creates a window which prompts the user as to if they want to log out. """
        if askyesno(title='Log out?', message='Are you sure you want to log out?'): self.destroy(True)

    def __str__(self): return f"Table of {self.table_name}"


