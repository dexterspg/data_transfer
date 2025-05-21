from nre_enums import SHEET_COLUMNS_MAPPING, LocationColumns, LocationLegalEntityColumns, SheetName
import pandas as pd

def _handle_rules_column(input_df, sheet_name: SheetName, header, mapping_config, indices) -> pd.DataFrame:

    if sheet_name is None or not header:
        return pd.DataFrame()

    if sheet_name not in SHEET_COLUMNS_MAPPING:
        return pd.DataFrame()

    columns = SHEET_COLUMNS_MAPPING[sheet_name]
    
    column = next((col for col in columns if header == col.value), None)
    if not column:
        return pd.DataFrame()

    rule_function_column = COLUMN_RULES_MAPPING.get((sheet_name, column))

    if rule_function_column:
        return rule_function_column(input_df, mapping_config, indices) if rule_function_column else pd.DataFrame()

    return pd.DataFrame()

def _handle_rules_row(input_df, sheet_name: SheetName, header, mapping_config, indices):

    if sheet_name is None or not header:
        return None

    if sheet_name not in SHEET_COLUMNS_MAPPING:
        return None 

    columns = SHEET_COLUMNS_MAPPING[sheet_name]
    
    column = next((col for col in columns if header == col.value), None)
    if not column:
        return None

    rule_function_row = ROW_RULES_MAPPING.get((sheet_name, column))

    if rule_function_row:
        return rule_function_row(input_df, mapping_config, indices) if rule_function_row else "No rule function"

    return None

def createLocationNameValue(input_df, mapping_config, indices):
    locationId_ext = input_df.at[indices[0], "Property Code 1 - Prim Prop Code"]
    value =  f"{locationId_ext}TEST"
    return value

def createLegalEntityId(input_df, mapping_config,indices):
    print("======================================================")
    locationId_ext = mapping_config[LocationColumns.LOCATIONID.value].get("external_column", "")
    # legalEnityId_ext = mapping_config[LocationLegalEntityColumns.LEGALENTITYID.value].get("external_column", "")
    lessee = input_df[['Lessee']]
    
    df = input_df.loc[indices, [locationId_ext]]
    df.columns=[LocationLegalEntityColumns.LEGALENTITYID.value]
    # print(df)
     
    
    return df
        
ROW_RULES_MAPPING = {
    (SheetName.LOCATION, LocationColumns.NAME) : createLocationNameValue,
}

COLUMN_RULES_MAPPING = {
    (SheetName.LOCATIONLEGALENTITY, LocationLegalEntityColumns.LEGALENTITYID) : createLegalEntityId 
}



