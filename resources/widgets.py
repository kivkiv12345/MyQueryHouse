""" This file contains user defined widgets, that are to be situated inside tk instances. """
from resources.orm import DATABASE_NAME

if __name__ == '__main__':
    raise SystemExit("...and let it be known through revelation; that those who make attempts to run 'widgets.py directly'"
                     "must be thought a fool, for trying run run a file which is obviously only used to store widgets...")

import traceback
import tkinter as tk
from typing import Tuple, Union
from resources import orm
from frozendict import frozendict
from resources.enums import ViewModes, DatabaseLocations
from resources.utils import NotReadOnlyWidget, TkUtilWidget, CreateToolTip


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

    def show_mode(self, mode:ViewModes) -> Tuple[str, ...]:
        """
        Removes existing buttons in the table/view list, and adds those corresponding to the specified mode.
        :return: A tuple of queried table/view names.
        """
        for button in tuple(self.interior.children.values()):
            button.destroy()

        orm.CURSOR.execute(f"SHOW FULL TABLES WHERE Table_type = '{mode.value}'")
        table_names = *(db[0] for db in orm.CURSOR),

        for table_name in table_names:
            btn = tk.Button(self.interior, height=1, width=20, relief=tk.FLAT,
                            bg="gray99", fg="black", text=table_name,
                            command=lambda name=table_name: self.master._table_click(name, mode))
            btn.pack(padx=10, pady=5, side=tk.TOP)

        try:
            self.master._table_click(table_name, mode)
        except IndexError:
            self.master.outlog.insert(f"Found no {mode.value}s in the database.")

        return table_names


class SwitchViewModeButton(tk.Button):
    modes = frozendict(tables='views', views='tables')
    next_mode = 'views'
    table_view: VerticalScrolledFrame = None

    def __init__(self, table_view:VerticalScrolledFrame, master=None, cnf={}, **kw):
        super().__init__(master, cnf,
                         text=kw.pop('text', f"Show {self.next_mode}"),
                         command=kw.pop('command', self.switch_mode), **kw)
        self.table_view = table_view

    def switch_mode(self) -> None:
        """ Changes the linked table_view to its next mode. """
        try:
            mode = ViewModes.TABLE if self.next_mode == 'tables' else ViewModes.VIEW
            self.table_view.show_mode(mode)

        except Exception:
            traceback.print_exc() # Stop exceptions in table button list from preventing mode switching on this button.
        self.next_mode = self.modes[self.next_mode]
        self.config(text=f"Show {self.next_mode}")


class OutputLogOptionMenu(tk.Menu):
    """ Right-click context menu used by OutputLog. """

    def __init__(self, master:tk.Text=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.add_command(label='Clear log', command=lambda: master.delete('1.0', tk.END))


class OutputLog(tk.Text):
    """ A text log which may be cleared by use of an included right-click context menu. """
    options: OutputLogOptionMenu = None

    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, state=kw.pop('state', tk.DISABLED), **kw)
        self.options = OutputLogOptionMenu(self)

        self.bind('<Button 3>', self.show_options)

    def show_options(self, event):
        """ Shows a popup with the included option at the position of the provided event. """
        self.options.tk_popup(event.x_root, event.y_root)

    def insert(self, chars, index=tk.END, to_console=True, newline=True, *args):
        """ Inserting into the output log, should automatically crete newlines (and print to console). """
        with NotReadOnlyWidget(self): super().insert(index, chars + ('\n' if newline else ''), *args)
        if to_console: print(chars)


class MessageRoot(TkUtilWidget):
    txtbox: tk.Text = None
    answerframe: tk.Frame = None

    def __init__(self, message: str, initial_txt='', screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)

        tk.Label(self, text=message).pack()
        self.txtbox = tk.Text(self, width=50, wrap=tk.WORD)
        self.txtbox.insert(tk.INSERT, initial_txt)
        self.txtbox.pack()

        # Adjust the height of the textbox to fit the SQL.
        newheigt = self.txtbox.tk.call((self.txtbox._w, "count", "-update", "-displaylines", "1.0", "end"))
        self.txtbox.configure(height=min(20, newheigt+3))

        self.answerframe = tk.Frame(self)

        tk.Button(self.answerframe, text='Yes', command=lambda _=None: self.destroy(True)).grid(column=0, row=0)
        tk.Button(self.answerframe, text='No', command=lambda _=None: self.destroy(True)).grid(column=1, row=0)

        self.answerframe.pack()

        self.bind('<Return>', self._check_enter)  # ENTER should confirm the user input.

    def _check_enter(self, event):
        """ Only simulates clicking yes, if the text widget is not in focus. """
        if self.focus_get() is not self.txtbox: self.destroy(True)


class LoginModeWidget(tk.Frame):
    """
    Collects the widgets used to connect to either a normal or dockerized database into a single frame.
    __init__ parameter allows for switching between modes.
    """

    # Local database widgets
    host_input: tk.Entry = None
    user_input: tk.Entry = None

    password_input: tk.Entry = None

    # Docker database widgets
    name_input: tk.Entry = None
    port_input: tk.Entry = None

    def __init__(self, mode:DatabaseLocations, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)

        if mode is DatabaseLocations.DOCKER:
            tk.Label(self, text="Connecting to a dockerized database.").pack()

            # Setup of a container name Entry widget.
            (namedefault := tk.StringVar()).set(f"{DATABASE_NAME}_db")
            tk.Label(self, text="Container name").pack()
            self.name_input = tk.Entry(self, text=namedefault); self.name_input.pack()
            CreateToolTip(self.name_input, "Determines the name of the created container.")

            # Setup of a password Entry widget.
            (passworddefault := tk.StringVar()).set("Test1234!")
            tk.Label(self, text="Database password").pack()
            self.password_input = tk.Entry(self, text=passworddefault); self.password_input.pack()
            CreateToolTip(self.password_input,
                          "Determines the password which will be used to connect to the dockerized database.")

            # Setup of a port Entry widget.
            (portdefault := tk.StringVar()).set("5506")
            tk.Label(self, text="Container port").pack()
            self.port_input = tk.Entry(self, text=portdefault); self.port_input.pack()  # TODO Kevin: Make input number only.
            CreateToolTip(self.port_input, "Determines which port should be forwarded to the docker container.")

        elif mode is DatabaseLocations.LOCAL:  # Runs when the user wants to connect to a local database.
            tk.Label(self, text="Connecting to a normal database.").pack()

            # Setup of an Entry widget for the database server IP.
            (hostdefault := tk.StringVar()).set("localhost")
            tk.Label(self, text="Connection server").pack()
            self.host_input = tk.Entry(self, text=hostdefault)
            self.host_input.pack()

            # Setup of an Entry widget for the database user widget.
            (userdefault := tk.StringVar()).set("root")
            tk.Label(self, text="Connection user").pack()
            self.user_input = tk.Entry(self, text=userdefault)
            self.user_input.pack()

            # Setup of an Entry widget for the database password widget.
            tk.Label(self, text="Connection password").pack()
            self.password_input = tk.Entry(self, show="*"); self.password_input.pack()
            self.password_input.focus_set()

        else:
            raise ValueError("Invalid mode provided to LoginModeWidget.")


def ask_text_answer(message: str, initial_txt='') -> Union[str, None]:
    """
    Prompts the user for a yes/no answer, while also allowing them to edit the returned text answer.
    :return: None when cancelled, text when accepted.
    """

    msgbox = MessageRoot(message, initial_txt)

    msgbox.mainloop()

    return msgbox.txtbox.get("1.0", "end-1c")