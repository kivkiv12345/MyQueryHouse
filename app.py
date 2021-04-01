import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from typing import Callable

from frozendict import frozendict

from keymodes import KeyModes
from multiprocessing import Process
from mysql import connector
from utils import *

root_title = "MyQueryHouse | MySQL Connector Program"

def m1click(event, mode:KeyModes=None):
    print(f"Clicked mouse1 using {mode} as mode.")


def m2click(event):
    pass


def runtk(tk:tk.Tk):
    """ Used to run a tkinter instance async. """
    tk.mainloop()


def db_click(db_name: str):
    """ Runs when clicking a database in the object explorer. """
    root.title(root_title + f" | {db_name}")
    db_cursor.execute(f"USE {db_name}")

    """db_cursor.execute("SHOW TABLES")
    test = [i for i in db_cursor]
    print(test)"""


def bind_modifiers(widget, event:Callable, button='Button-1',
                   modes=frozendict({'Shift': KeyModes.SHIFT, 'Control': KeyModes.CONTROL, 'Alt': KeyModes.ALT, })):
    """ Creates modifier bindings (ALT, CONTROL & SHIFT, by default) for the provided widget. """
    widget.bind(button, event)
    for modifier, keymode in modes.items():
        # We must provide 'keymode' as a default argument in the lambda expression (as method parameters are
        # only evaluated once), otherwise it will end up referencing the last value in the modes dictionary.
        widget.bind(f"<{modifier}-{button}>", lambda bind_event, mode=keymode: event(bind_event, mode))


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("500x500")
    root.configure(bg="gray")
    root.title(root_title)

    #root.bind("<Button 1>", m1click)
    root.bind("<Button 3>", m2click)

    # Bind some event modifiers, these alter the behavior when clicking the mouse.
    #root.bind('<Shift-Button-1>', lambda event: m1click(event, KeyModes.SHIFT))
    #root.bind('<Control-Button-1>', lambda event: m1click(event, KeyModes.CONTROL))
    #root.bind('<Alt-Button-1>', lambda event: m1click(event, KeyModes.ALT))

    bind_modifiers(root, m1click)

    # TODO Kevin: Create a login screen
    db_connection = connector.connect(host="localhost", user="root", passwd="Test1234!")

    db_cursor = db_connection.cursor()
    db_cursor.execute("SHOW DATABASES")

    db_scrollview = VerticalScrolledFrame(root)
    db_scrollview.grid(column=0)

    db_names = (db[0] for db in db_cursor)
    for name in db_names:
        btn = tk.Button(db_scrollview.interior, height=1, width=20, relief=tk.FLAT,
                        bg="gray99", fg="black", text=name,
                        command=lambda db_name=name: db_click(db_name))
        btn.pack(padx=10, pady=5, side=tk.TOP)

    root.mainloop()

    #root2 = tk.Tk()
    #root2.title("hahahtest")

    #root2.mainloop()

    #p1 = Process(target=runtk, args=(root,))
    #p2 = Process(target=runtk, args=(root2,))

