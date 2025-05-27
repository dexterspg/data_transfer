from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet import worksheet
import pandas as pd
import numpy as np
import time
import os


def nombre_formula(header: str, src_df : pd.DataFrame,  *args) -> pd.DataFrame:

    try:
        df=pd.DataFrame(columns=[header])
        df[header] = (
            src_df['Translation Type'] + " " +
            pd.to_datetime(
                src_df['Fiscal Year'].astype(str) + '-' + src_df['Fiscal Period'].astype(str)
            ).dt.strftime('%b-%Y').str.lower()
        )
        return df
    except Exception as e:
        print(e)

def descripcion_formula(header: str, src_df : pd.DataFrame,  *args) -> pd.DataFrame:
    df=pd.DataFrame(columns=[header])
    df[header] =  ('M1/' + src_df['Unit'].astype(str) + '/'  + src_df['Fiscal Year'].astype(str) + '/' + 
        src_df['Fiscal Period'].astype(str) + '/' + src_df['Contract Name'].astype(str) + '/' + 
        src_df['Vendor'].astype(str)
    )

    return df


def gl_account_split(header: str, src_df: pd.DataFrame, *args) -> pd.DataFrame:
    header_to_index = {
        "compania": 0,
        "Unidad": 1,
        "CC": 2,
        "ubicacion": 3,
        "cuenta": 4,
        "subcuenta": 5,
        "equipo": 6,
        "intercompania": 7,
    }
    
    idx = header_to_index.get(header)
    if idx is None:
        return pd.DataFrame()  # return an empty DataFrame if header not recognized
    
    splitted = src_df["GL Account"].str.split("-", expand=True)
    
    if splitted.shape[1] <= idx:
        col_data = pd.Series([None] * src_df.shape[0])
    else:
        col_data = splitted[idx]
    
    return pd.DataFrame({header: col_data})

formula_mappings = {
    "Nombre": nombre_formula,
    "divisa": lambda header, src_df, *args : pd.DataFrame({ header: src_df["Contract Currency"]}),
    "compania": gl_account_split,
    "Unidad": gl_account_split,
    "CC": gl_account_split,
    "ubicacion": gl_account_split,
    "cuenta": gl_account_split,
    "subcuenta": gl_account_split,
    "equipo": gl_account_split,
    "intercompania": gl_account_split,
    # "debito": lambda header, src_df ,*args : pd.DataFrame({header : src["Amount in Contract Currency"].astype(float) if }),
    "debito": lambda header, src_df, *args: pd.DataFrame({
    header: np.where(
        src_df["Amount in Contract Currency"].astype(float) > 0,
        src_df["Amount in Contract Currency"].astype(float),
        0
    )
}),
    "credito": lambda header, src_df, *args: pd.DataFrame({
    header: np.where(
        src_df["Amount in Contract Currency"].astype(float) < 0,
        src_df["Amount in Contract Currency"].astype(float),
        0
    )
}),
    "debito_convertido":"",
    "credito_convertido":"",
    "descripcion": descripcion_formula
}

cell_number_format = {
    "debito":'_-* #,##0.00_-;-* #,##0.00_-;_-* "-"??_-;_-@_-',
    "credito": '_-* #,##0.00_-;-* #,##0.00_-;_-* "-"??_-;_-@_-',
    "debito_convertido": '_-* #,##0.00_-;-* #,##0.00_-;_-* "-"??_-;_-@_-',
    "credito_convertido":'_-* #,##0.00_-;-* #,##0.00_-;_-* "-"??_-;_-@_-'
}


def _handle_formula(header: str, src_df,  *args) -> pd.DataFrame:
    formula_func = formula_mappings.get(header)
    
    if callable(formula_func):
        return formula_func(header, src_df, *args)  
    
    return pd.DataFrame()



def mapped_data(source_file: str, template_file: str, updated_file: str, formula_mappings: dict,
                input_header_start: int = 27, input_data_start: int =28, template_header_start: int = 1,
                template_data_start: int = 2):
    start = time.perf_counter()
    print(f"Processing source file {source_file}")
    source_file = os.path.abspath(source_file)
    template_file= os.path.abspath(template_file)
    updated_file= os.path.abspath(updated_file)

    input_df= pd.read_excel(source_file, header=input_header_start-1)
    template_df = pd.read_excel(template_file) 

    template_wb= load_workbook(template_file)
    template_ws = template_wb.worksheets[0]

    for header in template_df.columns:
        if header in formula_mappings.keys():
            result_df :pd.DataFrame = _handle_formula(header, input_df, template_df)
            if not result_df.empty:
                template_df[header] = result_df[header]

    col_index_map = {
            header: template_df.columns.get_loc(header)
            for header in template_df.columns
        }

    for r_idx, row in enumerate(template_df.itertuples(index=False), start=1):
        for header in template_df.columns:
            col_idx = col_index_map.get(header)
            if not isinstance(col_idx, int):
               raise ValueError(f"Header {header} not found in input data") 
            value = getattr(row, header)

            cell =template_ws.cell(
                row=r_idx+1,
                column=col_idx+1,
            )
            cell.value = value

            if header in cell_number_format.keys():
                cell.number_format  = cell_number_format[header]

    tc_idx = col_index_map.get("TC")
    debito_idx = col_index_map.get("debito")
    debito_conv_idx = col_index_map.get("debito_convertido")
    credito_idx = col_index_map.get("credito")
    credito_conv_idx = col_index_map.get("credito_convertido")
    
    # Validate that the necessary columns are available.
    if tc_idx is None or debito_idx is None or debito_conv_idx is None:
        raise ValueError("Required columns (TC, debito, debito_convertido) not found in template data")
    if tc_idx is None or credito_idx is None or credito_conv_idx is None:
        raise ValueError("Required columns (TC, credito, credito_convertido) not found in template data")
    
    # Cast indexes to int explicitly.
    tc_idx = int(tc_idx)
    debito_idx = int(debito_idx)
    debito_conv_idx = int(debito_conv_idx)
    credito_idx = int(credito_idx)
    credito_conv_idx = int(credito_conv_idx)
    
    tc_letter = get_column_letter(tc_idx + template_header_start)
    debito_letter = get_column_letter(debito_idx + template_header_start)
    credito_letter = get_column_letter(credito_idx + template_header_start)
    
    num_data_rows = len(template_df)
    for row_number in range(template_data_start, num_data_rows + template_data_start):
        debito_formula = (
            f"=IF(OR(ISBLANK({tc_letter}{row_number}),ISBLANK({debito_letter}{row_number})),0,{tc_letter}{row_number}*{debito_letter}{row_number})"
        )
        cell_debito = template_ws.cell(row=row_number, column=debito_conv_idx + template_header_start)
        cell_debito.value = debito_formula
        
        # Formula for credito_convertido: =IF(OR(ISBLANK(TC_row),ISBLANK(credito_row)),0,TC_row*credito_row)
        credito_formula = (
            f"=IF(OR(ISBLANK({tc_letter}{row_number}),ISBLANK({credito_letter}{row_number})),0,{tc_letter}{row_number}*{credito_letter}{row_number})"
        )
        cell_credito = template_ws.cell(row=row_number, column=credito_conv_idx + template_data_start)
        cell_credito.value = credito_formula

    # Save the updated workbook.
    template_wb.save(updated_file)
    end = time.perf_counter()

    print(f"Processing time completed: {end-start:.2f} seconds")
    print(f"Output file saved to {updated_file}")

def main():

    source_file = input("Enter the path to the source file: ")
    # source_file = "Consolidated Transaction Report.xlsx"
    template_file = "poliza_ledger_template.xlsx"
    updated_file = "poliza_ledger_output.xlsx"


    mapped_data(source_file, template_file, updated_file, formula_mappings, input_header_start=27,
                input_data_start=28, template_header_start=1, template_data_start= 2)

if __name__ == "__main__":
    main()


