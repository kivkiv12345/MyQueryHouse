"""
This module holds the utility methods and classes used by MyQueryHouse.
"""

if __name__ == '__main__':
    raise SystemExit("Cannot run utils.py")

import tkinter as tk
from tkintertable import TableModel
from resources.orm import QuerySet


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
