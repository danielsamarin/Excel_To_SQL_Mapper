from typing import List, Dict
import pandas as pd

def generate_insert_scripts(table: str, target_columns: List[str], source_columns: List[str], df: pd.DataFrame, mapping: Dict[str, str]) -> List[str]:
    """
    Generates SQL INSERT scripts for each row in the DataFrame using the mapping.
    Args:
        table (str): Target table name.
        target_columns (List[str]): List of target table columns.
        source_columns (List[str]): List of source (Excel) columns.
        df (pd.DataFrame): DataFrame containing Excel data.
        mapping (Dict[str, str]): Mapping from target column to source column.
    Returns:
        List[str]: List of SQL INSERT statements.
    """
    scripts = []
    for _, row in df.iterrows():
        values = []
        for tgt_col in target_columns:
            src_col = mapping.get(tgt_col)
            val = row[src_col] if src_col in row else None
            if val is None or pd.isna(val):
                values.append("NULL")
            elif isinstance(val, str):
                values.append(f"'" + val.replace("'", "''") + "'")
            else:
                values.append(str(val))
        col_str = ", ".join(target_columns)
        val_str = ", ".join(values)
        scripts.append(f"INSERT INTO {table} ({col_str}) VALUES ({val_str})")
    return scripts 