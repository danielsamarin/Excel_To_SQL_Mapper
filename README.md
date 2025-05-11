# Excel to SQL Mapper

A Python application with a DearPyGui interface to map Excel columns to MSSQL table columns and generate SQL insert scripts.

## Features
- Import Excel files and display columns
- Connect to MSSQL and fetch table columns
- Visually map source (Excel) columns to target (MSSQL) columns
- Generate SQL insert scripts for all Excel rows
- Modular, testable code

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure you have the ODBC Driver 17 for SQL Server installed for MSSQL connectivity.

## Usage
1. Run the application:
   ```bash
   python main.py
   ```
2. Follow the steps in the GUI:
   - Import an Excel file
   - Connect to your MSSQL server and select a table
   - Map columns between source and target
   - Generate SQL insert scripts

## Testing
Run unit tests with:
```bash
python -m unittest test_excel_utils.py
python -m unittest test_mssql_utils.py
```

## Project Structure
- `main.py` - Main GUI application
- `excel_utils.py` - Excel file utilities
- `mssql_utils.py` - MSSQL connection utilities
- `mapping_utils.py` - Mapping and SQL generation logic
- `gui_components.py` - Reusable GUI components
- `test_excel_utils.py` - Unit tests for Excel utilities
- `test_mssql_utils.py` - Unit tests for MSSQL utilities
- `requirements.txt` - Dependencies 