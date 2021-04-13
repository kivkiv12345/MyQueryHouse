try:
    import tkinter as tk
    from tkinter.scrolledtext import ScrolledText
    from typing import Callable
    from frozendict import frozendict
    from mysql.connector import ProgrammingError
    from enums import KeyModes
    from multiprocessing import Process
    from mysql import connector
    from utils import DATABASE_NAME, LoginBox, CreateDatabaseMessage, VerticalScrolledFrame, MainDBView
    from orm import CONNECTION, CURSOR
    from multiprocessing import Process
except ModuleNotFoundError as e:
    raise SystemExit(f"٩(^‿^)۶ Hey there, some import failed; stating: '{e}'.\nThis most likely happened because you "
                     f"aren't running the program from the intended virtual environment.\n"
                     f"Please navigate to the directory of app.py and execute 'source env/bin/activate'. :)")

def m1click(event, mode:KeyModes=None):
    print(f"Clicked mouse1 using {mode} as mode.")


def m2click(event):
    pass


def runtk(tk:tk.Tk):
    """ Used to run a tkinter instance async. """
    tk.mainloop()


def bind_modifiers(widget, event:Callable, button='Button-1',
                   modes=frozendict({'Shift': KeyModes.SHIFT, 'Control': KeyModes.CONTROL, 'Alt': KeyModes.ALT, })):
    """ Creates modifier bindings (ALT, CONTROL & SHIFT, by default) for the provided widget. """
    widget.bind(button, event)
    for modifier, keymode in modes.items():
        # We must provide 'keymode' as a default argument in the lambda expression (as method parameters are
        # only evaluated once), otherwise it will end up referencing the last value in the modes dictionary.
        widget.bind(f"<{modifier}-{button}>", lambda bind_event, mode=keymode: event(bind_event, mode))


if __name__ == '__main__':

    while True:
        # Login screen loop.
        login = LoginBox()
        while True:
            login.mainloop()
            try:
                # Use the login details stored in our login widget for the MySQL connection.
                CONNECTION = connector.connect(**login.logindeets)
                break
            except ProgrammingError as e:
                login = LoginBox(e.msg)

        CURSOR = CONNECTION.cursor()

        try:  # Prompt the user to create the database, should it be absent.
            CURSOR.execute(f"USE {DATABASE_NAME}")
        except ProgrammingError:  # Assume the database to not exist, if we cannot use it.
            newdbmsg = CreateDatabaseMessage(DATABASE_NAME, CURSOR, CONNECTION, login.logindeets["passwd"])
            newdbmsg.mainloop()

        root = MainDBView(DATABASE_NAME, CURSOR, CONNECTION)

        #root.bind("<Button 1>", m1click)
        #root.bind("<Button 3>", m2click)

        # Bind some event modifiers, these alter the behavior when clicking the mouse.
        #bind_modifiers(root, m1click)

        root.mainloop()

    #root2 = tk.Tk()
    #root2.title("hahahtest")

    #root2.mainloop()

    #p1 = Process(target=runtk, args=(root,))
    #p2 = Process(target=runtk, args=(root2,))

