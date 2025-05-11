import pyodbc
from typing import List

def get_mssql_table_columns(server: str, database: str, username: str, password: str, table: str) -> List[str]:
    """
    Connects to MSSQL and fetches column names for the specified table.
    Args:
        server (str): MSSQL server address.
        database (str): Database name.
        username (str): Username for authentication.
        password (str): Password for authentication.
        table (str): Table name to fetch columns from.
    Returns:
        List[str]: List of column names.
    Raises:
        RuntimeError: If connection or query fails.
    """
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT TOP 0 * FROM {table}")
            return [column[0] for column in cursor.description]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch table columns: {e}") 