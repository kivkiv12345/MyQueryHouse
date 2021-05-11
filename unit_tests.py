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

    def test_dbmodel(self):
        # check that instantiating DBModels raises an AbstractInstantiationError.
        with self.assertRaises(AbstractInstantiationError): DBModel()


if __name__ == '__main__':
    unittest.main()
