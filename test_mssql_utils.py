import unittest
from unittest.mock import patch, MagicMock
from mssql_utils import get_mssql_table_columns

class TestMSSQLUtils(unittest.TestCase):
    @patch('pyodbc.connect')
    def test_get_mssql_table_columns(self, mock_connect):
        # Mock cursor and connection
        mock_cursor = MagicMock()
        mock_cursor.description = [('id',), ('name',), ('age',)]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn
        columns = get_mssql_table_columns('server', 'db', 'user', 'pass', 'table')
        self.assertEqual(columns, ['id', 'name', 'age'])

if __name__ == '__main__':
    unittest.main() 