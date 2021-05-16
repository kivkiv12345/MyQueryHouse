"""
Run this module to perform the preconfigured unit tests for MyQueryHouse.
"""
from typing import Type

import unittest
from resources import orm
from docker.errors import NotFound
from subprocess import call, DEVNULL
from mysql.connector import connect
from resources.utils import TempDockerContainer
from resources.orm import DBModel, DATABASE_NAME, init_orm
from resources.exceptions import AbstractInstantiationError
from test_resources.test_subclass import MoreTestCases


class TestOrm(MoreTestCases):

    """def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())"""

    def test_docker(self):
        """ Instantiates a MySQL Docker container mock database, to run unit tests against. """

        # TODO Kevin: Some refactoring may be in order here. Destruction of unit test resources raises ResourceWarning;
        #   stating: unclosed socket. This may hint at needed changes to an __exit__ method somewhere.

        client = docker.from_env()
        client.images.pull('mysql')  # Ensure that the image is pulled.

        CONTAINER_NAME = DATABASE_NAME + '_test_db'
        PASSWORD = "Test1234!"
        PORT = 53063

        try:  # Attempt to retrieve an existing testing container.
            container = client.containers.get(CONTAINER_NAME)
        except NotFound:  # Create one for our use case.
            container = client.containers.run(
                'mysql',
                name=CONTAINER_NAME,
                environment=[f"MYSQL_ROOT_PASSWORD={PASSWORD}"],
                ports={"3306/tcp": PORT},
                detach=True,
                auto_remove=True
            )

        with TempDockerContainer(container):
            with open(f"database_backups/{DATABASE_NAME}(test).sql") as db_file:
                # The following command populates the database according to the opened .sql file.
                call(["mysql", "-u", "root", f"--password={PASSWORD}", DATABASE_NAME, '-h', '127.0.0.1', '-P', str(PORT)],
                    stdin=db_file, stdout=DEVNULL, stderr=DEVNULL)

            with connect(
                host='127.0.0.1',
                user='root',
                password=PASSWORD,
            ) as connection:
                with connection.cursor() as cursor:
                    orm.CONNECTION, orm.CURSOR = connection, cursor
                    models = init_orm()

                    Category, Storage = models['Category'], models['Storage']
                    category: Type[DBModel] = Category.objects.get(CategoryID=1)

                    # We put the actual test cases here, after all the setup.
                    #self.assertTrue(isinstance(category, Category.model))

                    # Checks that the related row is lazily queried and deserialized correctly.
                    self.assertEqual(category.values['storageid'], Storage.objects.get(StorageID=6))

    def test_dbmodel(self):
        """ Check that instantiating DBModels raises an AbstractInstantiationError. """
        with self.assertRaises(AbstractInstantiationError): DBModel()


if __name__ == '__main__':
    unittest.main()
