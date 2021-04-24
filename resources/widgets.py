""" This file contains user defined widgets, that are to be situated inside tk instances. """

if __name__ == '__main__':
    raise SystemExit("...and let it be known through revelation; that those who make attempts to run 'widgets.py directly'"
                     "must be thought a fool, for trying run run a file which is obviously only used to store widgets...")

import tkinter as tk
from typing import Type


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
