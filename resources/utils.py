"""
This module holds the utility methods and classes used by MyQueryHouse.
"""

if __name__ == '__main__':
    raise SystemExit("Cannot run utils.py")

import os
import tkinter as tk
from time import sleep
from resources import orm
from subprocess import run, DEVNULL
from tkintertable import TableModel
from mysql.connector import ProgrammingError
from docker.errors import APIError, NotFound
from resources.enums import DatabaseLocations
from resources.orm import QuerySet, DATABASE_NAME
from docker.models.containers import Container


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


class NotReadOnlyWidget:
    """ Provides a clean way to temporarily edit read-only widgets using the 'with' statement. """

    widget: tk.Widget = None
    initial_state: str = None

    def __init__(self, widget: tk.Widget) -> None:
        """ :param widget: The widget which should be opened for editing. """
        super().__init__()
        self.widget = widget
        try: self.initial_state = widget['state']  # Attempt to retrieve and store the initial state of the widget.
        except (TypeError, AttributeError): pass  # Use a default value later on, if this fails.

    def __enter__(self):
        """ Open the widget for editing while inside 'with' statement. """
        self.widget.config(state=tk.NORMAL)

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        """Restore the widget to its initial state (or disabled state, if the original state could not be retrieved)."""
        self.widget.config(state=self.initial_state or tk.DISABLED)
        del self


class OrmTableModel(TableModel):
    """ May delete rows in supplied QuerySet, while also deleting in the connected table. """
    _queryset: QuerySet = ()  # Initialise as an empty iterable value.

    def change_queryset(self, queryset:QuerySet) -> None:
        """
        Changes the queryset to the one provided, while also altering columns to match the provided model.
        :param queryset: The new queryset to use.
        """
        # Empty the model first.
        self.createEmptyModel()
        self._queryset = queryset

        # Use the values from the queryset when possible; otherwise, create an empty row to indicate column names.
        # TODO Kevin: Ensure no errors occur for odd data types.
        data = {instance.pk: instance.values for instance in queryset} or \
               {None: {colname: None for colname in queryset.model.Meta.fieldnames if colname != queryset.model.Meta.pk_column}}

        """
        data will be in the same format as this example taken from the tkinter docs.
        {
            'rec1': {'col1': 99.88, 'col2': 108.79, 'label': 'rec1'},
            'rec2': {'col1': 99.88, 'col2': 108.79, 'label': 'rec2'}
        }
        """

        # Import this data into the model.
        self.importDict(data)


class CreateToolTip(object):  # Taken from: https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
    """
    create a tooltip for a given widget.

    gives a Tkinter widget a tooltip as the mouse is above the widget
    tested with Python27 and Python34  by  vegaseat  09sep2014
    www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter

    Modified to include a delay time by Victor Zaccardo, 25mar16
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()


class TempDockerContainer:
    """ Temporarily keeps a Docker running, and ensures its deleted afterwards. """

    container: Container = None

    def __init__(self, container: Container) -> None:
        """
        :param container: The Docker container to keep running inside the with statement.
        """
        super().__init__()
        self.container = container

    def __enter__(self):
        self.container.start()
        if not self.container.attrs['State']['Running']:
            print(f"Waiting for container with name: '{self.container.name}' to start.")
            sleep(15)
        return self.container

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.container.stop()
            self.container.remove()
        except (NotFound, APIError):
            pass  # Container is most likely already deleted, happens when the container has auto_remove set to True.


class MockCMySQLCursor:
    """ Used to replace the existing CMySQLCursor when its import fails. Otherwise does nothing. """


def fixpath(string:str) -> str:
    """ Ensures that backslashes are used for Windows paths, and forward slashes for UNIX/Linux. """
    return string.replace(*(('/', '\\') if os.name == 'nt' else ('\\', '/')))


def restore_database(logindeets:dict, filename=DATABASE_NAME + '.sql', container_name:str = None) -> None:
    """
    Looks for a file in 'database_backups/', and uses it to restore the database on the server.

    :param logindeets: Dictionary of login details, used to connect to the database server.
    :param filename: The name of the .sql file in 'database_backups/' to use.
    :param container_name: The name of the container the database is located in, only applicable when using Docker.
    """

    restore_db_args = () if orm.database_location is DatabaseLocations.DOCKER else ('-h', logindeets['host'])

    try:
        with open(fixpath(f"database_backups/{filename}")) as db_file:
            # The following command populates the database according to the opened .sql file.
            command = ["mysql", DATABASE_NAME, "-u", "root", f"--password={logindeets['passwd']}", *restore_db_args]
            if orm.database_location is DatabaseLocations.DOCKER:  # Execute inside the docker container, if applicable.
                assert container_name, "Container name must be specified when using Docker"
                command = ["docker", "exec", "-i", container_name] + command
            run(command, stdin=db_file, stdout=DEVNULL, stderr=DEVNULL)

            try:  # The above command currently fails on Linux, and this one requires that MySQL-client is installed.
                command = ["mysql", DATABASE_NAME, "-u", "root", f"--password={logindeets['passwd']}", "-h", "127.0.0.1", "-P", str(logindeets['port'])]
                run(command, stdin=db_file, stdout=DEVNULL, stderr=DEVNULL)
            except Exception:  # Fails when the MySQL-client is not installed.
                pass

    except ProgrammingError as e:
        print(f"Failed to restore database from {filename}; stating: '{e}',\ndoes the file exist?")
