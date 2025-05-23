from nre_enums import SHEET_COLUMNS_MAPPING, LeaseColumns, LocationColumns, LocationLegalEntityColumns, PremiseColumns, SheetName, TermAmountsColumns, TermsColumns
import pandas as pd
from conversion import * 
from utils.excel_style_utils import _apply_date_format

def _handle_rules_column(input_df, sheet_name: SheetName, header, mapping_config, indices, value) -> pd.DataFrame:

    if sheet_name is None or not header:
        return pd.DataFrame()

    if sheet_name not in SHEET_COLUMNS_MAPPING:
        return pd.DataFrame()

    columns = SHEET_COLUMNS_MAPPING[sheet_name]
    
    header = next((col for col in columns if header == col.value), None)
    if not header:
        return pd.DataFrame()

    rule_function_column = COLUMN_RULES_MAPPING.get((sheet_name, header))

    if rule_function_column:
        return rule_function_column(header.value, input_df, mapping_config, indices, value) if rule_function_column else pd.DataFrame()

    return pd.DataFrame()

def _handle_rules_row(input_df, sheet_name: SheetName, header, mapping_config, indices, value):

    if sheet_name is None or not header:
        return None

    if sheet_name not in SHEET_COLUMNS_MAPPING:
        return None 

    columns = SHEET_COLUMNS_MAPPING[sheet_name]
    
    column = next((col for col in columns if header == col.value), None)
    if not column:
        return None

    rule_function_row = ROW_RULES_MAPPING.get((sheet_name, column))
    rule_function_conversion = ROW_CONVERSION_RULES_MAPPING.get((sheet_name, column))

    if rule_function_row:
        return rule_function_row(input_df, mapping_config, indices, value) if rule_function_row else "No rule function"
    elif rule_function_conversion:
        return rule_function_conversion(value) if rule_function_conversion else "No rule function"

    return None

def createLocationNameValue(input_df, mapping_config, indices, value):
    locationId_ext = input_df.at[indices[0], "Property Code 1 - Prim Prop Code"]
    value =  f"{locationId_ext}TEST"
    return value

def createLegalEntityId(column, input_df, mapping_config,indices, value):
    col_ext= mapping_config[LocationColumns.LOCATIONID.value].get("external_column", "")
    # legalEnityId_ext = mapping_config[LocationLegalEntityColumns.LEGALENTITYID.value].get("external_column", "")
    lessee = input_df[['Lessee']]
    
    df = input_df.loc[indices, [col_ext]]
    df.columns=[LocationLegalEntityColumns.LEGALENTITYID.value]
    # print(df)
     
    
    return df

def _apply_date_format_to_column(header, input_df, mapping_config,indices, value):
    date_format='%d/%m/%Y'
    col_ext = mapping_config[header].get("external_column", "")

    df = input_df.loc[indices, [col_ext]]
    df.columns=[header]
    df[header] = pd.to_datetime(df[header], errors='coerce')
    df[header] = df[header].apply(lambda x : x.strftime(date_format) if pd.notna(x) else "")
    
    return df

        
ROW_RULES_MAPPING = {
    (SheetName.LOCATION, LocationColumns.NAME) : createLocationNameValue
}

COLUMN_RULES_MAPPING = {
    (SheetName.LOCATIONLEGALENTITY, LocationLegalEntityColumns.LEGALENTITYID) : createLegalEntityId ,
    (SheetName.PREMISE, PremiseColumns.CLOSINGDATE) : _apply_date_format_to_column,
    (SheetName.PREMISE, PremiseColumns.OPENINGDATE) : _apply_date_format_to_column,
    (SheetName.PREMISE, PremiseColumns.POSSESSIONDATE) : _apply_date_format_to_column,
    (SheetName.LEASE, LeaseColumns.STARTDATE) : _apply_date_format_to_column,
    (SheetName.LEASE, LeaseColumns.ENDDATE) : _apply_date_format_to_column,
    (SheetName.TERMS, TermsColumns.STARTDATE) : _apply_date_format_to_column,
    (SheetName.TERMS, TermsColumns.ENDDATE) : _apply_date_format_to_column,
    (SheetName.TERMAMOUNTS, TermAmountsColumns.STARTDATE) : _apply_date_format_to_column,
    (SheetName.TERMAMOUNTS, TermAmountsColumns.ENDDATE) : _apply_date_format_to_column
}

ROW_CONVERSION_RULES_MAPPING = {
    (SheetName.LOCATION, LocationColumns.DEFAULTCURRENCY) : convertCurrency,
    (SheetName.LOCATION, LocationColumns.DEFAULTUNIT) : convertUnit,
    (SheetName.TERMS, TermsColumns.CURRENCYID) : convertCurrency
}



