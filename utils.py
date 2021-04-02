"""
This module holds the utility methods and classes used in the application.
"""

if __name__ == '__main__':
    # Gently remind the user to not run utils.py themselves
    raise SystemExit("(⊙＿⊙') Wha!?... Are you trying to run utils.py?\n"
                     " You do know it's only used to store utilities; right? You should run app.py instead :)")

import pathlib
import tkinter as tk
from typing import TypeVar

from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor_cext import CMySQLCursor
from json import load


# VARS
PathLike = TypeVar("PathLike", str, pathlib.Path, None)
DB_DATA_FILE:PathLike = 'db_data.json'

root_title = "MyQueryHouse | MySQL Connector Program"
DATABASE_NAME = "myqueryhouse"

# Classes
class TkUtilWidget(tk.Tk):
    """ Holds some common utilities for widgets made for this application. """

    def destroy(self, deliberate=False):
        """
        Calls super and allows for discrimination based on context.
        :param deliberate: True when the program should continue when this function is called.
        """
        super().destroy()
        if not deliberate: raise SystemExit(f"{object.__str__(self)} wishes to stop the Tkinter application.")


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

    def _confirm(self, *args):
        # TODO Kevin: This is a pretty terrible way to populate the database, one ought to restore from a backup file instead.
        self.db_cursor.execute(f"CREATE DATABASE {self.db_name}")  # Apparently can't pass db_name as a positional argument when creating a database ¯\_(ツ)_/¯
        self.db_cursor.execute(f"USE {self.db_name}")

        self.db_cursor.execute("CREATE TABLE Location (shelf smallint UNSIGNED, space smallint UNSIGNED, locationID int PRIMARY KEY AUTO_INCREMENT)")
        self.db_cursor.execute("CREATE TABLE Item (productname varchar(50), description varchar(400), itemID int PRIMARY KEY AUTO_INCREMENT)")

        if self.populate_db.get():
            with open(DB_DATA_FILE) as json_file:
                db_data = load(json_file)
                for table_string, rows in db_data.items():
                    for row in rows:
                        self.db_cursor.execute(f"INSERT INTO {table_string} VALUES (%s,%s)", row)

        self.db_connection.commit()

        self.destroy(True)

    def __init__(self, db_name:str, db_cursor:CMySQLCursor, db_connection:MySQLConnection, screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.db_name, self.db_cursor, self.db_connection = db_name, db_cursor, db_connection

        self.title(f"Create database {db_name}")
        tk.Label(self, text=f"A database called '{db_name}' could not be found on the server,\n"
                            f"This database must be created before the program can continue.\n").pack()

        self.populate_db = tk.BooleanVar()
        self.pop_db_checkbox = tk.Checkbutton(self, text=f"Should the database be prepopulated with filler data?\nContents will be read from '{DB_DATA_FILE}'", variable=self.populate_db)
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


class MainDBView(tk.Tk):
    """ This is the main widget that will be shown when a successful connection to the database has been made. """

    # Database connection details.
    db_name: str = None
    db_cursor: CMySQLCursor = None
    db_connection: MySQLConnection = None

    rowbox: tk.Text = None

    restart_program = False

    def __init__(self, db_name:str, db_cursor:CMySQLCursor, db_connection:MySQLConnection, screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.db_name, self.db_cursor, self.db_connection = db_name, db_cursor, db_connection

        self.title(root_title)

        self.geometry("500x500")
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

        self.rowbox = tk.Text()
        tk.Text(self).grid(column=2, row=1)

    def _table_click(self, table_name: str):
        self.title(f"{root_title} | {table_name}")

        self.db_cursor.execute(f"SELECT * FROM {table_name}")
        print(tuple(i for i in self.db_cursor))

        """self.db_cursor.execute("SHOW TABLES")
        test = [i for i in self.db_cursor]
        print(test)"""

    def _delete_database(self):
        self.db_cursor.execute(f"DROP DATABASE {self.db_name}")
        self.restart_program = True
        self.destroy()

