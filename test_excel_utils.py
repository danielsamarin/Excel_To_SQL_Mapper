import unittest
from unittest.mock import patch, MagicMock
from excel_utils import read_excel_columns

class TestExcelUtils(unittest.TestCase):
    @patch('pandas.read_excel')
    def test_read_excel_columns(self, mock_read_excel):
        # Mock DataFrame
        mock_df = MagicMock()
        mock_df.columns = ['Col1', 'Col2', 'Col3']
        mock_read_excel.return_value = mock_df
        columns, df = read_excel_columns('dummy.xlsx')
        self.assertEqual(columns, ['Col1', 'Col2', 'Col3'])
        self.assertEqual(df, mock_df)

if __name__ == '__main__':
    unittest.main() 