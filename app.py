""" This module handles the main program loop, as in; it determines when certain windows and widgets appear. """

import sys
import os
if os.name == 'nt':
    # Windows is a bloated piece of broken garbage code,
    # which can't detect installed packages when running from command line!
    # So we must tell it where to find them... *sigh*
    conf_path = os.getcwd()
    sys.path.append(conf_path)
    sys.path.append(conf_path + r'\env\Lib\site-packages')
    # Appending the packages like this; means we assume the program is running from a virtual environment called 'env'.

try:
    import traceback
    import tkinter as tk
    from tkinter.messagebox import askyesno
    from tkinter.scrolledtext import ScrolledText
    from typing import Callable
    from frozendict import frozendict
    from mysql.connector import ProgrammingError, DatabaseError
    from resources.enums import KeyModes, SysArgs, DatabaseLocations
    from multiprocessing import Process
    from mysql import connector
    from resources.program import DATABASE_NAME, LoginBox, CreateDatabaseMessage, VerticalScrolledFrame, MainDBView
    from resources import orm
except ModuleNotFoundError as e:
    traceback.print_exc()
    raise SystemExit(f"""
    ٩(^‿^)۶ Hey there, some imports failed; stating: '{e}'.\n
    This most likely happened due to missing dependencies.
    Assuming you're located in the directory of app.py,
    this can easily be fixed by running:
    'pip3 install -r requirements.txt'.\n
    You might want to do this in virtual environment though, which can be made with:
    'python3 -m venv env',\n
    You must now activate it by typing:
    (on Linux)   'source env/bin/activate'
    (on Windows) 'env/Scripts/activate' :)
    """)


def m1click(event, mode:KeyModes=None):
    print(f"Clicked mouse1 using {mode} as mode.")


def m2click(event):
    pass


def bind_modifiers(widget, event:Callable, button='Button-1',
                   modes=frozendict({'Shift': KeyModes.SHIFT, 'Control': KeyModes.CONTROL, 'Alt': KeyModes.ALT, })):
    """ Creates modifier bindings (ALT, CONTROL & SHIFT, by default) for the provided widget. """
    widget.bind(button, event)
    for modifier, keymode in modes.items():
        # We must provide 'keymode' as a default argument in the lambda expression (as method parameters are
        # only evaluated once), otherwise it will end up referencing the last value in the modes dictionary.
        widget.bind(f"<{modifier}-{button}>", lambda bind_event, mode=keymode: event(bind_event, mode))


if __name__ == '__main__':

    # Check for invalid arguments passed to the program.
    if invalid_args := set(sys.argv[1:]).difference({enum.value for enum in SysArgs}):
        raise EnvironmentError(f"Invalid arguments passed to app.py: {invalid_args}")

    while True:  # Loop the entire program.

        login = LoginBox()
        while True:  # Login screen loop.
            login.mainloop()
            try: # Use the login details stored in our login widget for the MySQL connection.
                orm.CONNECTION = connector.connect(**login.logindeets)
                break
            except (ProgrammingError, DatabaseError) as e:
                login = LoginBox(e.msg)

        orm.CURSOR = orm.CONNECTION.cursor()

        try:  # Prompt the user to create the database, should it be absent.
            orm.CURSOR.execute(f"USE {DATABASE_NAME}")
        except ProgrammingError:  # Assume the database to not exist, if we cannot use it.
            newdbmsg = CreateDatabaseMessage(login.logindeets, orm.CURSOR, orm.CONNECTION)
            newdbmsg.mainloop()

        # Override methods for __len__ and __str__ in created DBModels
        def dbmodel_len(self): return len(str(self.pk))
        def dbmodel_str(self): return str(self.pk)

        orm.init_orm({
            '__len__': dbmodel_len,
            '__str__': dbmodel_str,
        })

        root = MainDBView(login.logindeets, orm.CURSOR, orm.CONNECTION)

        root.mainloop()

#root.bind("<Button 1>", m1click)
#root.bind("<Button 3>", m2click)

# Bind some event modifiers, these alter the behavior when clicking the mouse.
#bind_modifiers(root, m1click)
