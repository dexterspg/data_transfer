from nre_enums import SHEET_COLUMNS_MAPPING, LocationColumns, SheetName

def _handle_rules(input_df, sheet_name: SheetName, header, mapping_config, idx):

    if sheet_name is None or not header:
        return None

    if sheet_name not in SHEET_COLUMNS_MAPPING:
        return None 

    columns = SHEET_COLUMNS_MAPPING[sheet_name]
    
    column = next((col for col in columns if header == col.value), None)
    if not column:
        return None

    rule_function = RULES_MAPPING.get((sheet_name, column))

    if rule_function:
        return rule_function(input_df, mapping_config, idx) if rule_function else "No rule function"
    return None


def createNameValue(input_df, mapping_config,r_idx):
    locationId_ext = input_df.at[r_idx, "Property Code 1 - Prim Prop Code"]
    value =  f"RULE{locationId_ext}"
    return value

        
RULES_MAPPING = {
    (SheetName.LOCATION, LocationColumns.NAME) : createNameValue


}



