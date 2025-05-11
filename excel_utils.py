import pandas as pd
from typing import List, Tuple

def read_excel_columns(file_path: str) -> Tuple[List[str], pd.DataFrame]:
    """
    Reads the first sheet of an Excel file and returns the column names and the DataFrame.
    Args:
        file_path (str): Path to the Excel file.
    Returns:
        Tuple[List[str], pd.DataFrame]: List of column names and the DataFrame.
    Raises:
        RuntimeError: If the file cannot be read.
    """
    try:
        df = pd.read_excel(file_path)
        return list(df.columns), df
    except Exception as e:
        raise RuntimeError(f"Failed to read Excel file: {e}") 