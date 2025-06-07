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
    loc_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("location")])

    print(loc_ext_cols_with_comma)


    locationId_ext_col = config.get_external_column_of_header_on_sheet("location", "LocationId")
    conn.execute(f"""
    CREATE TABLE Location AS
    SELECT DISTINCT ON ({loc_ext_cols_with_comma})
        -- "{locationId_ext_col}",
        {loc_ext_cols_with_comma}
    FROM raw_data 
    ORDER BY row_index;
    """)

    print("Location")
    print(conn.execute(f"SELECT * FROM Location").fetchdf())

    create_premise(config, conn)


def create_premise(config : MappingConfig, conn)-> None:
    print("================= PREMISE ==================================")

    loc_ext_df_cols_drop_row_index = conn.execute(f"SELECT * FROM Location LIMIT 0").fetchdf()
    # loc_ext_df_cols_drop_row_index.drop(columns=["row_index"], inplace=True)
    loc_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in loc_ext_df_cols_drop_row_index.columns])
    print(loc_ext_cols_with_comma)

    premise_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("premise")])
    print(premise_ext_cols_with_comma)

    locationId_ext_col = config.get_external_column_of_header_on_sheet("location", "LocationId")

    conn.execute(f"""
    CREATE TABLE Premise AS
    SELECT 
        -- "{locationId_ext_col}",
        row_number() OVER (ORDER BY row_index) + 100 AS PremiseId,
        {premise_ext_cols_with_comma},
        row_index
    FROM (
      SELECT DISTINCT ON ({loc_ext_cols_with_comma}, {premise_ext_cols_with_comma}) 
        {loc_ext_cols_with_comma}, 
        {premise_ext_cols_with_comma},
        row_index
      FROM raw_data
      ORDER BY row_index
    ) loc_premise 
    ORDER BY row_index
    """)

    print(conn.execute(f"SELECT * FROM Premise").fetchdf())

    create_lease(config, conn)

def create_lease(config : MappingConfig, conn)-> None:

    print("================= LEASE =====_=============================")

    premise_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("premise")])
    print(premise_ext_cols_with_comma)

    lease_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("lease")])
    print(lease_ext_cols_with_comma)

    premise_ext_df = conn.execute(f"SELECT * FROM Premise").fetchdf()

    on_condition = " AND ".join([
        f'premise_lease."{col}"= premise."{col}"'
        for col in config.get_external_column_fields_on_sheet("premise")
        if col and not premise_ext_df[col].isna().any()
])
    print(on_condition)
    lease_ext_cols_with_comma_premise_lease: str = ", ".join([f'premise_lease."{col}"' for col in config.get_external_column_fields_on_sheet("premise")])

    # print(premise_ext_df.info())
    # 
    # conn.execute(f"""
    #     CREATE TABLE try AS
    #     SELECT DISTINCT ON ({premise_ext_cols_with_comma}, {lease_ext_cols_with_comma}) 
    #     {premise_ext_cols_with_comma},
    #     {lease_ext_cols_with_comma}, 
    #     row_index
    #   FROM raw_data
    #   ORDER BY row_index""")
    # print(conn.execute(f"SELECT * FROM try").fetchdf().info())

    conn.execute(f"""
    CREATE TABLE Lease AS
    SELECT 
        row_number() OVER (ORDER BY premise_lease.row_index) + 200 AS LeaseId,
        premise.PremiseId,
        {lease_ext_cols_with_comma}
    FROM (
      SELECT DISTINCT ON ({premise_ext_cols_with_comma}, {lease_ext_cols_with_comma}) 
        {premise_ext_cols_with_comma},
        {lease_ext_cols_with_comma}, 
        row_index
      FROM raw_data
      ORDER BY row_index  
    ) premise_lease 
    LEFT JOIN Premise premise ON {on_condition}
    ORDER BY premise_lease.row_index
    """)

    print(conn.execute(f"SELECT * FROM Lease").fetchdf())

    create_term(config, conn)

def create_term(config : MappingConfig, conn)-> None:

    print("================= TERM=====_=============================")

    lease_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("lease")])
    print(lease_ext_cols_with_comma)

    terms_ext_cols_with_comma: str = ", ".join([f'"{col}"' for col in config.get_external_column_fields_on_sheet("terms")])
    print(terms_ext_cols_with_comma)

    lease_ext_df = conn.execute(f"SELECT * FROM lease").fetchdf()

    on_condition = " AND ".join([
        f'lease_terms."{col}"= lease."{col}"'
        for col in config.get_external_column_fields_on_sheet("lease")
        if col and not lease_ext_df[col].isna().any()
    ])
    print(on_condition)
    terms_ext_cols_with_comma_lease_terms: str = ", ".join([f'lease_terms."{col}"' for col in config.get_external_column_fields_on_sheet("lease")])

    # print(lease_ext_df.info())
    # 
    # conn.execute(f"""
    #     CREATE TABLE try AS
    #     SELECT DISTINCT ON ({lease_ext_cols_with_comma}, {terms_ext_cols_with_comma}) 
    #     {lease_ext_cols_with_comma},
    #     {terms_ext_cols_with_comma}, 
    #     row_index
    #   FROM raw_data
    #   ORDER BY row_index""")
    # print(conn.execute(f"SELECT * FROM try").fetchdf().info())

    conn.execute(f"""
    CREATE TABLE Terms AS
    SELECT 
        row_number() OVER (ORDER BY lease_terms.row_index) + 300 AS TermId,
        lease.LeaseId,
        {terms_ext_cols_with_comma}
    FROM (
      SELECT DISTINCT ON ({lease_ext_cols_with_comma}, {terms_ext_cols_with_comma}) 
        {lease_ext_cols_with_comma},
        {terms_ext_cols_with_comma}, 
        row_index
      FROM raw_data
      ORDER BY row_index  
    ) lease_terms 
    LEFT JOIN Lease lease ON {on_condition}
    ORDER BY lease_terms.row_index
    """)

    print(conn.execute(f"SELECT * FROM Terms").fetchdf())   

def on_condition(config : MappingConfig, source, target, dest_fields):
    on_cond  = [
        f'{source}."{column}" = {target}."{column}"'
        for col in dest_fields
        if (column := config.get_external_column_of_header(col)) 
    ]

    return " AND ".join(on_cond) if on_cond else ""
    


def create_duck_tables(conn, config):

    loc_dest_fields : List[str] = config.get_df_fields_for_sheet_name("Location")   
    loc_query_string : str = ", ".join(set_src_as_query_fields(config.get_config_for_sheet_name("location"), "",  loc_dest_fields))
    loc_query_string_no_quotes: str = ", ".join(set_src_as_query_fields_no_quotes(config.get_config_for_sheet_name("location"), "",  loc_dest_fields))

    print(loc_query_string)
    print(loc_query_string_no_quotes)

    pivot = 'Property Code 1 - Prim Prop Code'
    conn.execute(f"""
    CREATE TABLE Location AS
    SELECT DISTINCT ON ({loc_query_string})
        {loc_query_string},
        row_index
    FROM raw_data 
    ORDER BY row_index;
    """)

    print("Location")
    print(conn.execute(f"SELECT * FROM Location").fetchdf())

    premise_dest_fields : List[str] = config.get_df_fields_for_sheet_name("Premise")   
    premise_query_string : str = ", ".join(set_src_as_query_fields(config.get_config_for_sheet_name("premise"), "",  premise_dest_fields))

    premise_query_string_with_p : str = ", ".join(set_src_as_query_fields(config.get_config_for_sheet_name("premise"), "premise",  premise_dest_fields))
    print(premise_query_string_with_p)
    conn.execute(f"""
    CREATE TABLE PREMISE AS
    SELECT 
        row_number() OVER (ORDER BY location.row_index)  + 100 AS PremiseId,
        {premise_query_string_with_p},
    FROM Location location
    LEFT JOIN(
        SELECT DISTINCT ON ({loc_query_string}, {premise_query_string})
            {loc_query_string}, {premise_query_string},row_index
        FROM raw_data
        ORDER BY row_index
    ) premise ON location."{pivot}"= premise."{pivot}"
    ORDER BY location.row_index
    """)

    # LEFT JOIN Location location ON location."{pivot}"= premise."{pivot}"
    print("Premise")
    print(conn.execute(f"SELECT * FROM Premise").fetchdf())

    lease_dest_fields : List[str] = config.get_df_fields_for_sheet_name("Lease")   
    print(lease_dest_fields)
    lease_query_string : str = ", ".join(set_src_as_query_fields(config.get_config_for_sheet_name("lease"), "",  lease_dest_fields))

    lease_query_string_with_l : str = ", ".join(set_src_as_query_fields(config.get_config_for_sheet_name("lease"), "lease",  lease_dest_fields))

    a= conn.execute(f"""
        SELECT DISTINCT ON ({premise_query_string}, {lease_query_string})
           {premise_query_string}
           {lease_query_string}
           ,row_index
        FROM raw_data
        ORDER BY row_index
 """).fetchdf().columns
    print(a)

    b = conn.sql("SELECT * FROM Premise").fetchdf().columns
    print(conn.sql("SELECT * FROM Premise").fetchdf().columns)

    print("gwegeg")
    print(set(a).intersection(set(b)))

    lease_with_ext = config.get_external_column_fields_on_sheet("lease")
    premise_with_ext = config.get_external_column_fields_on_sheet("premise")
    location_with_ext = config.get_external_column_fields_on_sheet("location")

    print(lease_with_ext)
    print(premise_with_ext)
    print(location_with_ext)

    lease_premise_fields = list(set(a).intersection(set(b)))    
    premise_dest_fields_with_ext = config.get_df_fields_for_sheet_name("Premise")
    lease_dest_fields_with_ext = config.get_df_fields_for_sheet_name("Lease")
    print(premise_dest_fields_with_ext)
    print(lease_dest_fields_with_ext)
    print("gegewgawegae4wgw34g4")
    print(on_condition(config.get_config_for_sheet_name("premise"), "premise", "lease", premise_dest_fields_with_ext))
    conn.execute(f"""
    CREATE TABLE Lease AS
    SELECT 
        row_number() OVER (ORDER BY premise.PremiseId)  + 200 AS LeaseId,
        premise.PremiseId,
        {lease_query_string_with_l}
    FROM Premise premise 
    LEFT JOIN(
        SELECT DISTINCT ON ({premise_query_string}, {lease_query_string})
           {premise_query_string}
           {lease_query_string}
           ,row_index
        FROM raw_data
        ORDER BY row_index
    ) lease ON 
    CAST(premise."Subspace Commence Date" AS TIMESTAMP) = CAST(lease."Subspace Commence Date" AS TIMESTAMP)  
    AND CAST(premise."Subspace Expiration Date" AS TIMESTAMP) = CAST(lease."Subspace Expiration Date" AS TIMESTAMP)  
    AND CAST(premise."Move In Date" AS TIMESTAMP) = CAST(lease."Move In Date" AS TIMESTAMP)  
ORDER BY premise.PremiseId;
    """)
# {'Subspace Commence Date', 'Lease Primary Use - Calculated Field', 'Move In Date', 'Lessee', 'Active/Inactive', 'Subspace Expiration Date', 'RE Tax - (ID#)'}
     # ) lease ON {on_condition(config.get_config_for_sheet_name("premise"), "premise", "lease", premise_dest_fields_with_ext)}
    # ) lease ON premise."Lessee" = lease."Lessee"
    print("Lease")
    print(conn.execute(f"SELECT * FROM Lease").fetchdf())

    terms_dest_fields : List[str] = config.get_df_fields_for_sheet_name("Terms")   
    terms_query_string : str = ", ".join(set_src_as_query_fields(config.get_config_for_sheet_name("terms"), "",  terms_dest_fields))

    terms_query_string_with_t : str = ", ".join(set_src_as_query_fields(config.get_config_for_sheet_name("Terms"), "terms",  terms_dest_fields))

    a= conn.execute(f"""
        SELECT DISTINCT ON ({lease_query_string}, {terms_query_string})
           {lease_query_string}
           {terms_query_string}
           ,row_index
        FROM raw_data
        ORDER BY row_index
 """).fetchdf().columns
    print(a)

    b = conn.sql("SELECT * FROM Lease").fetchdf().columns
    print(conn.sql("SELECT * FROM Lease").fetchdf().columns)

    print("gwegeg")
    print(set(a).intersection(set(b)))

    conn.execute(f"""
        CREATE TABLE Terms AS
        SELECT
            row_number() OVER (ORDER BY lease.LeaseId)  + 200 AS TermId,
            lease.LeaseId,
            {terms_query_string_with_t}
        FROM Lease lease
        LEFT JOIN
        (
        SELECT DISTINCT ON ({lease_query_string}, {terms_query_string})
           {lease_query_string}
           {terms_query_string}
           ,row_index
        FROM raw_data
        ORDER BY row_index
        ) terms ON terms."Lease Commence Date"= lease."Lease Commence Date" AND terms."Lease Expiration Date"= lease."Lease Expiration Date"
        ORDER BY lease.LeaseId
        """)
    print("Terms")
    print(conn.execute(f"SELECT * FROM Terms").fetchdf())

         # LEFT JOIN Lease lease ON terms."Lease Commence Date"= lease."Lease Commence Date"
         # AND terms."Lease Expiration Date"= lease."Lease Expiration Date"


