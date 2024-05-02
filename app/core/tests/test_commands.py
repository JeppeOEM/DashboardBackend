"""
Test custom Django management commands.
"""
#simulate the db
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2OpError
#django helper function to actually call the command by name
from django.core.management import call_command
# one possible db error
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        patched_check.return_value = True
        call_command('wait_for_db')
        patched_check.assert_called_once_with(databases=['default'])

    #replace build sleep function with mock object, to overwrite the sleep behaviour so we just run the code faster
    @patch('time.sleep')
    #must be in correct order, adds decorators inside out first time.sleep then @path('core....)
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        #First to times it raises the error, then after it raises 3 operational errors
        # 6th is true and not a fail, so it returns
        patched_check.side_effect = [Psycopg2OpError] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')
        #We know how many time it will call so we check if that is correct
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])