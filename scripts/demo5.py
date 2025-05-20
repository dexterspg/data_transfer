import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import numbers
from openpyxl.worksheet.worksheet import Worksheet
from datetime import datetime
from typing import cast

# Sample DataFrame
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [30, 25, 35],
    "Birthday": [datetime(1993, 5, 17), datetime(1998, 8, 21), datetime(1989, 12, 5)],
    "IsActive": [True, False, True],
    "Score": [85.6, 92.1, 78.3]
})

# Create workbook and cast active sheet to Worksheet (safe for Pyright)
wb = Workbook()
ws = cast(Worksheet, wb.active)  # ✅ This silences the Pyright error

ws.title = "People"

# Write headers
ws.append(list(df.columns))

# Write data rows with proper types
for _, row in df.iterrows():
    excel_row = []
    for value in row:
        if pd.isna(value):
            excel_row.append(None)
        elif isinstance(value, (int, float, bool, datetime)):
            excel_row.append(value)
        else:
            excel_row.append(str(value))
    ws.append(excel_row)

# Format the Birthday column as a date (column index 3)
for col in ws.iter_cols(min_row=2, min_col=3, max_col=3):
    for cell in col:
        cell.number_format = numbers.FORMAT_DATE_YYYYMMDD2

# Save Excel file
wb.save("typed_output.xlsx")

