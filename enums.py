if __name__ == '__main__':
    # Gently remind the user to not run enums.py themselves
    raise SystemExit("Hiya (ʘ‿ʘ)╯, it appears you're trying to enums.py instead of app.py. This, sadly, will not work :(")

from enum import Enum

class KeyModes(Enum):
    """ Enum to hold keystroke modifiers. """
    SHIFT   = 1
    CONTROL = 2
    ALT     = 3
