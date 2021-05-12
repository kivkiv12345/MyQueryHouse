"""
Run this module to perform the preconfigured unit tests for MyQueryHouse.
"""

import unittest
from resources.exceptions import AbstractInstantiationError
from resources.orm import DBModel


class TestOrm(unittest.TestCase):

    """def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())"""

    # TODO Kevin: Find some way to populate the orm and test QuerySet exceptions,
    #  preferably done via a docker container debug database or something.

    # TODO Kevin: Check that foreignkey IDs are converted to DBModels, on a test database.

    def test_dbmodel(self):
        """ Check that instantiating DBModels raises an AbstractInstantiationError. """
        with self.assertRaises(AbstractInstantiationError): DBModel()


if __name__ == '__main__':
    unittest.main()
