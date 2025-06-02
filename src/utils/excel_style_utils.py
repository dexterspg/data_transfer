from openpyxl import load_workbook
from openpyxl.styles import NamedStyle, Font

def _add_named_style(wb, style):
    if wb and style.name not in wb.named_styles:
        wb.add_named_style(style)

def _apply_date_format(cell, date_format):
    date_style = NamedStyle(name="custom_date_format")
    date_style.number_format = date_format
    print(f"Cell value: {cell.value}")
    # cell = sheet.cell(row=row, column=col)
    cell.style = date_style

def _check_cell_format(sheet, row, col):
    """Check the number format of a specific cell."""
    return sheet.cell(row=row, column=col).number_format

def _apply_date_format_to_df(df):
    pass

def apply_named_style_in_cols(sheet, columns, min_row, max_row, style):
    for col_idx in columns:
        for cell in sheet.iter_cols(min_col=col_idx, max_col=col_idx, min_row=min_row, max_row=max_row):
            for c in cell:
                c.style = style

def apply_missing_data_with_values_and_font_color(sheet, columns, min_row, max_row, cell_value, cell_font : Font):
    for col_idx in columns:
        for row_idx in range(min_row, max_row):  
            cell = sheet.cell(row=row_idx, column=col_idx)
            if cell.value is None or cell.value == "": 
                print(cell.value)
                cell.value = cell_value 
                cell.font = cell_font
