class AbstractInstantiationError(Exception):
    """ Applicable when illegally trying to instantiate an abstract class. """


class RetryError(Exception):
    """ Applicable when a given action should be retried. """
