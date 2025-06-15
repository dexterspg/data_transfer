from typing import List
import pandas as pd
from configs.nre.mapping_config import MappingConfig


def print_sel(conn, query : str =""):
    print(conn.execute({query}).fetchdf())


def create_sheet_table(self, conn):
    dest_column_fields = self.config.get_df_fields()   

    query_fields = [
        f'"{self.config.get_external_column_of_header(col)}" AS "{col}"'
        if self.config.get_external_column_of_header(col)
        else f"'NA' AS \"{col}\""
        for col in dest_column_fields
    ]

    query_string = ",\n " .join(query_fields)

    df = conn.execute(f"""
    SELECT DISTINCT
    {query_string}
    FROM input_data
    """)


    return df

def create_src_table_with_row_number(config, conn, sheet_name, dest_column_fields, filter=None):
    filter = set(filter) if filter else set()
    src_query_fields= [
        f'"{config.get_external_column_of_header(col)}"'
        for col in dest_column_fields
        if config.get_external_column_of_header(col) and col not in filter
    ]
    
    table_name = f"src_{sheet_name.lower()}_with_row_number"
    conn.execute(f"""
        CREATE TABLE {table_name} AS
        SELECT DISTINCT
            ROW_NUMBER() OVER() AS row_number,
             {',\n '.join(src_query_fields)}
            FROM raw_data
            ORDER BY row_number
    """)
    print(conn.execute(f"SELECT * FROM {table_name}").fetchdf())


def set_src_as_query_fields(config, sheet_name :str="", dest_column_fields: List[str]=[] ):
    return {
        f'{sheet_name.lower()}."{column}"' if sheet_name else f'"{column}"'
        for col in dest_column_fields  
        if (column :=config.get_external_column_of_header(col)) 
    }

def set_src_as_query_fields_no_quotes(config, sheet_name :str="", dest_column_fields: List[str]=[] ):
    return {
        f'{sheet_name.lower()}.{config.get_external_column_of_header(col)}' if sheet_name else f'{config.get_external_column_of_header(col)}'
        for col in dest_column_fields  
        if config.get_external_column_of_header(col) 
    }

def create_location(config : MappingConfig, conn)-> None:
    loc_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("Location")])

    locationId_ext_col = config.get_external_column_of_header_on_sheet("Location", "LocationId")
    conn.execute(f"""
    CREATE TABLE Location AS
    SELECT DISTINCT ON ({loc_ext_cols_with_comma})
        'LO' || "{locationId_ext_col}" AS "LocationId",
        {loc_ext_cols_with_comma},
        row_index
    FROM raw_data 
    ORDER BY row_index;
    """)

    # create_location_group(config, conn)
    # create_premise(config, conn)

def create_location_group(config : MappingConfig, conn)-> None:
    print("================= Location Group ==================================")

    loc_ext_df_cols_drop_row_index = conn.execute(f"SELECT * FROM Location LIMIT 0").fetchdf()
    # loc_ext_df_cols_drop_row_index.drop(columns=["row_index"], inplace=True)
    loc_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in loc_ext_df_cols_drop_row_index.columns])
    print(loc_ext_cols_with_comma)

    locationgroup_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("LocationGroup")])
    print(locationgroup_ext_cols_with_comma)

    locationId_ext_col = config.get_external_column_of_header_on_sheet("Location", "LocationId")

    conn.execute(f"""
    CREATE TABLE LocationGroup AS
    SELECT 
        "{locationId_ext_col}",
       -- {locationgroup_ext_cols_with_comma},
        row_index
    FROM (
      SELECT DISTINCT ON ({loc_ext_cols_with_comma}, {locationgroup_ext_cols_with_comma}) 
        {loc_ext_cols_with_comma},
        -- {locationgroup_ext_cols_with_comma},
        row_index
      FROM raw_data
      ORDER BY row_index
    ) loc_locationgroup 
    ORDER BY row_index
    """)

    print(conn.execute(f"SELECT * FROM LocationGroup").fetchdf())


def select_from_raw_table(column_names: str):
    print(column_names)
    return f"""   
    SELECT DISTINCT ON ({column_names})
        {column_names}, 
        row_index
      FROM raw_data
      ORDER BY row_index
      """

def create_join_table(config : MappingConfig, conn, left_table , right_table, prefix: str='')-> None:
    print("================= JOIN TABLE ==================================")

    left_ext_cols_comma_separated: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet(f"{left_table}")])
    right_ext_cols_comma_separated: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet(f"{right_table}")])

    left_ext_df = conn.execute(f"SELECT * FROM {left_table}").fetchdf()

    on_condition = " AND ".join([
        f'{left_table.lower()}_{right_table.lower()}."{col}"= {left_table.lower()}."{col}"'
        for col in config.get_external_column_fields_on_sheet(f"{left_table}")
        if col and not left_ext_df[col].isna().any()
    ])

    merge_table = f"{left_table.lower()}_{right_table.lower()}"

    right_ext_cols_with_comma_and_prefix : str = ", ".join([f'{merge_table}."{col}"' for col in config.get_external_column_fields_on_sheet(f"{right_table}")])

    conn.execute(f"""
    CREATE TABLE {right_table} AS
    SELECT 
      {left_table.lower()}.{left_table}Id,
      CONCAT('{prefix}', LPAD(row_number() OVER (ORDER BY {left_table.lower()}.row_index)::TEXT, 7, '0')) AS {right_table}Id,
      {right_ext_cols_with_comma_and_prefix},
      {left_table.lower()}.row_index
    FROM (
      {select_from_raw_table(",".join([left_ext_cols_comma_separated, right_ext_cols_comma_separated]))}
    ) {merge_table}
    LEFT JOIN {left_table} {left_table.lower()}  ON {on_condition}
    ORDER BY {left_table.lower()}.row_index
    """)

def create_premise(config : MappingConfig, conn)-> None:
    print("================= PREMISE ==================================")

    # loc_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("Location")])
    #
    # premise_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("Premise")])
    #
    # location_ext_df = conn.execute(f"SELECT * FROM Location").fetchdf()
    #
    # on_condition = " AND ".join([
    #     f'loc_premise."{col}"= location."{col}"'
    #     for col in config.get_external_column_fields_on_sheet("Location")
    #     if col and not location_ext_df[col].isna().any()
    # ])
    # print(on_condition)
    #
    # premise_ext_cols_with_comma_and_prefix: str = ", ".join([f'loc_premise."{col}"' for col in config.get_external_column_fields_on_sheet("Premise")])
    # conn.execute(f"""
    # CREATE TABLE Premise AS
    # SELECT 
    #     location.LocationId,
    #     row_number() OVER (ORDER BY row_index) + 100 AS PremiseId,
    #     {premise_ext_cols_with_comma_and_prefix},
    #     row_index
    # FROM (
    #   {select_from_raw_table(",".join([loc_ext_cols_with_comma, premise_ext_cols_with_comma]))}
    # ) loc_premise 
    # LEFT JOIN Location location  ON {on_condition}
    # ORDER BY row_index
    # """)

    create_join_table(config, conn, "Location", "Premise", 'P')

    # print(conn.execute(f"SELECT * FROM Premise").fetchdf())

    # create_lease(config, conn)

def create_lease(config : MappingConfig, conn)-> None:

    print("================= LEASE =====_=============================")

    # premise_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("Premise")])
    # lease_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("Lease")])
    #
    # premise_ext_df = conn.execute(f"SELECT * FROM Premise").fetchdf()
    # lease_ext_cols_with_comma_and_prefix: str = ", ".join([f'premise_lease."{col}"' for col in config.get_external_column_fields_on_sheet("Lease")])
    #
    # on_condition = " AND ".join([
    #     f'premise_lease."{col}"= premise."{col}"'
    #     for col in config.get_external_column_fields_on_sheet("Premise")
    #     if col and not premise_ext_df[col].isna().any()
    # ])
    # print(on_condition)
    #
    # conn.execute(f"""
    # CREATE TABLE Lease AS
    # SELECT 
    #     row_number() OVER (ORDER BY premise.PremiseId) + 200 AS LeaseId,
    #     premise.PremiseId,
    #     {lease_ext_cols_with_comma_and_prefix}
    # FROM (
    #   {select_from_raw_table(",".join([premise_ext_cols_with_comma, lease_ext_cols_with_comma]))}
    # ) premise_lease 
    # LEFT JOIN Premise premise ON {on_condition}
    # ORDER BY premise.PremiseId
    # """)
    #
    # print(conn.execute(f"SELECT * FROM Lease").fetchdf())
    create_join_table(config, conn, "Premise", "Lease", 'L')

    # create_terms(config, conn)

def create_terms(config : MappingConfig, conn)-> None:

    print("================= TERM=====_=============================")

    # lease_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("Lease")])
    # terms_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("Terms")])
    #
    # lease_ext_df = conn.execute(f"SELECT * FROM Lease").fetchdf()
    #
    # on_condition = " AND ".join([
    #     f'lease_terms."{col}"= lease."{col}"'
    #     for col in config.get_external_column_fields_on_sheet("Lease")
    #     if col and not lease_ext_df[col].isna().any()
    # ])
    # print(on_condition)
    #
    # conn.execute(f"""
    # CREATE TABLE Terms AS
    # SELECT 
    #     row_number() OVER (ORDER BY lease.LeaseId) + 300 AS TermId,
    #     lease.LeaseId,
    #     {terms_ext_cols_with_comma}
    # FROM (
    #   {select_from_raw_table(",".join([lease_ext_cols_with_comma, terms_ext_cols_with_comma]))}
    # ) lease_terms 
    # LEFT JOIN Lease lease ON {on_condition}
    # ORDER BY lease.LeaseId
    # """)
    #
    # print(conn.execute(f"SELECT * FROM Terms").fetchdf())   
    # create_terms_amounts(config, conn)
    create_join_table(config, conn, "Lease", "Terms", 'T')

def create_terms_amounts(config : MappingConfig, conn)-> None:
    print("================= TermAmounts ==================================")

    terms_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("Terms")])
    term_amounts_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("TermAmounts")])

    terms_ext_df = conn.execute(f"SELECT * FROM Terms").fetchdf()
    on_condition = " AND ".join([
        f'terms_term_amounts."{col}"= terms."{col}"'
        for col in config.get_external_column_fields_on_sheet("Terms")
        if col and not terms_ext_df[col].isna().any()
    ])

    print(on_condition)

    terms_ext_cols_with_comma_and_prefix: str = ", ".join([f'terms_term_amounts."{col}"' for col in config.get_external_column_fields_on_sheet("TermAmounts")])

    conn.execute(f"""
    CREATE TABLE TermAmounts AS
    SELECT 
        terms.TermId,
        {terms_ext_cols_with_comma_and_prefix}
    FROM (
      {select_from_raw_table(",".join([terms_ext_cols_with_comma, term_amounts_ext_cols_with_comma]))}
    ) terms_term_amounts 
    LEFT JOIN Terms terms ON {on_condition}
    ORDER BY terms.TermId
    """)

    print(conn.execute(f"SELECT * FROM TermAmounts").fetchdf())


def on_condition(config : MappingConfig, source, target, dest_fields):
    on_cond  = [
        f'{source}."{column}" = {target}."{column}"'
        for col in dest_fields
        if (column := config.get_external_column_of_header(col)) 
    ]

    return " AND ".join(on_cond) if on_cond else ""
    





