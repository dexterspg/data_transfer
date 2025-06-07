import logging
from create_duckdb_table import *
import duckdb
from datetime import datetime
from os import waitpid
from configs.config import DATE_STYLE, MANDATORY_FONT_STYLE, NRE_SHEETS_DIR, PREFIX_FILE
from domain import Prefix, IdObj
from nre_enums import *
import pandas as pd
import json
from typing import List, Dict
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, NamedStyle
from id_generator import IdGenerator
from relationship import RELATIONSHIP_MAPPING
import relationship_mapper
from utils import  LoggingUtil, SheetUtils
from utils.regex_utils import _extract_with_regex
from utils.excel_style_utils import _apply_date_format, _add_named_style, apply_named_style_in_cols, apply_missing_data_with_values_and_font_color
from sheet_model import Sheet
from rules import COLUMN_RULES_MAPPING, _handle_rules_column, _handle_rules_row
from nre_enums import SheetName
from create_documents import save_document_indices, retrieve_document_indices
from relationship_mapper import RelationshipMapper
from configs.nre.mapping_config import MappingConfig

mandatory_font= Font(color="00FF9B9B")
logger = LoggingUtil.setup_logger('ExcelProcessor', console_level=logging.DEBUG)

class ExcelProcessor:

    def __init__(self, input_file, template_file, output_file, config_file, template_header_row=1, input_header_row=1, data_row_start=None) :
        self.id_container = {}
        self.df_map : Dict [str, pd.DataFrame]={}
        self.input_file =input_file
        self.input_df = pd.DataFrame()
        self.output_file =output_file
        self.template_header_row = template_header_row
        self.input_header_row = input_header_row
        self.data_row_start= self.template_header_row+1 if data_row_start is None else data_row_start
        self.limitRows = None
        self.number_of_rows_to_skip=0
        self.initialize_files(template_file, config_file)

    def initialize_input_df(self):
        self.input_df = pd.read_excel(io=self.input_file, header=self.input_header_row, nrows=self.limitRows, 
                                 skipfooter=self.number_of_rows_to_skip)

        print(self.input_df[['Property Code 1 - Prim Prop Code', 'Lease Code 1 - Prim Lease Code']].drop_duplicates())
        self.input_df['row_index'] = self.input_df.index 
        self.conn = duckdb.connect(":memory:")
        self.conn.register("raw_data", self.input_df)
        # create_duck_tables(self.conn, self.config)

    def initialize_files(self,template_file, config_file):
        self.template_wb= load_workbook(template_file)
        _add_named_style(self.template_wb, DATE_STYLE)
        self.config = MappingConfig(config_file) 
        self.prefix_obj = Prefix(PREFIX_FILE)
        relMapper = RelationshipMapper()
        relMapper.initialize_files()


    def _load_config(self, config_file):
        self.config._load_config(config_file)

    def _save_workbook(self):
        self.template_wb.save(self.output_file)
        logger.info(f"Processing complete. Output saved to {self.output_file}")

    def set_data_row_start(self, data_row_start):
        self.data_row_start = data_row_start

    def set_limit_rows(self, limitRows):
        self.limitRows= limitRows

    def valid_header_mapping(self, header : str) -> bool:
        sheet_name = self.config.get_sheet_name()
        if header in  self.config.get_df_fields():
            in_header_props: dict =  self.config.get_header_props(header)

            if not in_header_props:
                print()
                # logger.warning(f"Warning: no input mapping found for '{header}' for Sheet '{sheet_name}'") 

            default_val: str= self.config.get_default_value(header)
            output_col : str =  self.config.get_external_column_of_header(header)

            if not default_val and not output_col:
                # logger.error(f"Warning: no mapping found for '{header}' for Sheet '{sheet_name}'")
                return False 

            return True
        return False 

    def set_number_of_last_rows_to_drop(self, number_of_rows_to_skip):
        self.number_of_rows_to_skip=number_of_rows_to_skip

    def _delete_work_sheet_not_in_list(self, sheetnames):
        for sheet in self.template_wb.sheetnames:
            if sheet not in sheetnames:
                ws=self.template_wb[sheet]
                self.template_wb.remove(ws)

    def migrate_data(self, sheet_name : str, src_df :pd.DataFrame , dest_columns : List[str]) -> pd.DataFrame:

        mapping : Dict[str, str] = {
            header : self.config.get_external_column_of_header(header)
            for header in dest_columns
        }

        dest_df : pd.DataFrame = pd.DataFrame(columns = dest_columns)

        for header in dest_columns:
            # logger.info(f"Processing {header} of sheet {sheet_name}")
            if not self.valid_header_mapping(header):
                continue

            if mapping[header]!= "":
                dest_df[header] = src_df[mapping[header]]
        
        # print(dest_df.info())

        return dest_df

    def save_entities(self, df : pd.DataFrame, primary_id_field, ref_header,  prefix : str ) -> None:
        if not primary_id_field:
            return

        id_generator=IdGenerator(prefix)
        ext_col = self.config.get_external_column_of_header(primary_id_field) 
        isIdDefinedByExtCol = bool(ext_col !="")

        ref_obj_map={}
        if ref_header:
            ref_obj_list : List[IdObj] = self.id_container.get(ref_header, [])
            for ref_obj in ref_obj_list:
                ref_obj_map[ref_obj.get_position()]  = ref_obj.get_value()

        obj_list : List[IdObj] = []

        for row in df.itertuples(index=True):
            raw = None
            if isIdDefinedByExtCol:
                value = getattr(row, primary_id_field)
                raw = value
                value = prefix + str(value) if pd.notna(value) else id_generator.generate_id(primary_id_field, prefix)
                df.at[row.Index, primary_id_field] = value
            else:
                df.at[row.Index, primary_id_field] = id_generator.generate_id(primary_id_field, prefix)
                raw = id_generator.get_current_raw_id()

            prev : str =""
            if ref_obj_map.get(row.Index, "") != "": 
                prev = ref_obj_map[int(row.Index)]

            print(prev)
            id_obj = IdObj(raw, prefix, int(row.Index), primary_id_field, ext_col, prev=prev)
            obj_list.append(id_obj)

        self.id_container[primary_id_field] =  obj_list 
        print("ID CONTAINER ===============================================================")
        id_generator.write_ids_for_header(df, primary_id_field)

        relMapper = RelationshipMapper()
        if ref_header:
            relationshipType = RELATIONSHIP_MAPPING.get((ref_header, primary_id_field))
            df.apply(lambda x: relMapper.add_relationship(relationshipType, x[ref_header], x[primary_id_field]), axis=1)

    def get_filtered_df_by_ref_header(self, src_df, df, ref_header) -> pd.DataFrame:
        print(f" iget {self.config.get_config_path()}")
        relMapper = RelationshipMapper()
        ref_obj_map={}
        ref_obj_list : List[IdObj] = self.id_container.get(ref_header, [])

        indices=[]
        for ref_obj in ref_obj_list:
            indices.append(ref_obj.get_position())
            ref_obj_map[ref_obj.get_raw()]  = ref_obj.get_value()

        if len(indices) == 0:
            return df

        duplicated_mask=df.duplicated(keep='first')
        filtered_df = df[~duplicated_mask | df.index.isin(indices)]
        # src_df[index_to_be_populated, ]

        if ref_obj_list[0].get_other_type():
            print(filtered_df.index.to_list())
            positions = [filtered_df.index.get_loc(idx) for idx in filtered_df.index]
            print(positions)  # List of positional indices
            filtered_indices =  filtered_df.index.to_list()
            filtered_df.loc[filtered_indices , ref_header] = src_df.loc[ filtered_indices, ref_obj_list[0].get_other_type()]
        else:
            curr_config = self.config.get_config_path()
            print(f"curr config  {curr_config} is {type(curr_config)}")
            # index_to_be_populated = list(set(filtered_df.index.to_list()) - set(indices))
            parent  = relMapper.get_parent_field(ref_header)
            print(f"Parent: {parent} of {ref_header} is {parent} and its type is {type(parent)}") if parent else print(parent)
            temp_sheet_name = self.config.get_reference_header_name()
            print(temp_sheet_name)
            self.config._load_config(f"{NRE_SHEETS_DIR}/{temp_sheet_name}.json")
            print(self.config.get_config_path())
            ext_col = self.config.get_external_column_of_header(parent)
            print(f" {ext_col} is {type(ext_col)}") if ext_col else print(ext_col)
            self.config._load_config(curr_config)
            print(self.config.get_config_path())
            raw_values = [ obj.get_raw() for obj in ref_obj_list ]
            pos_values = [ obj.get_position() for obj in ref_obj_list ]
            new_src_df = pd.Series(raw_values, index=pos_values)
            filtered_df.loc[:,ref_header] = new_src_df

        filtered_df.loc[:, ref_header] = filtered_df[ref_header].map(ref_obj_map)

        return filtered_df

    def migrate_date_with_duck(self, conn):
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
        FROM raw_data
        """).fetchdf()


        return df

    
    def process(self):
        """Process the input file according to the template and mappings"""
        sheet_name = self.config.get_sheet_name()

        if sheet_name not in self.template_wb.sheetnames:
            logger.error(f"Warning: Sheet '{sheet_name}' not found in template")
            return

        template_sheet : Sheet= Sheet(self.template_wb[sheet_name], self.template_header_row, self.data_row_start)
        mandatory_fields = self.config.get_mandatory_fields()

        dest_columns = SHEET_COLUMNS_MAPPING[SheetName.get_enum(sheet_name)].get_values()
        # template_df = self.migrate_data(sheet_name, input_df.copy(), dest_columns)
        if sheet_name == 'Location':
            create_location(self.config, self.conn)
            # location_df = self.conn.execute("SELECT * FROM Location").fetchdf()
            # print(location_df)
        # elif sheet_name == 'Premise':
            # create_premise(self.config, self.conn)
            # premise_df= self.conn.execute("SELECT * FROM Premise").fetchdf()
            # print(premise_df)
        # elif sheet_name == "Lease":
            # create_lease(self.config, self.conn)
            # lease_df = self.conn.execute("SELECT * FROM Lease").fetchdf()
            # print(lease_df)
        # else:

            # return

        return
            
        template_df = self.migrate_date_with_duck(self.conn)
        self.df_map[sheet_name]  = template_df
        self.conn.register(sheet_name, template_df)
        print("BEFORE")
        print(self.df_map.get(sheet_name, {}))

        id_field : str = self.config.get_id_field()
        ref_header = self.config.get_reference_header_value()
        print(ref_header)


        return
        # if sheet_name == 'Premise':
            # print("ref_df ===================000000000000000000000000000")

                         

            # dest_column_fields = self.config.get_df_fields()   

            # query_fields = [
                # f'"{self.config.get_external_column_of_header(col)}" AS "{col}"'
                # if self.config.get_external_column_of_header(col)
                # else f"'NA' AS {col}"



            # location  = self.conn.execute("SELECT * FROM Location").fetchdf()
            # query_fields.append(f'"{self.config.get_external_column_of_header("LocationId")}" AS LocationId')
            # print(query_fields)
            #
            # # location  = self.conn.execute("SELECT * FROM Location").fetchdf()
            # # premise = self.conn.execute("SELECT * FROM Premise").fetchdf()
            # print("duckdb1")
            # # print(location)
            # # print(premise)
            # print("duckdb1")
            # query_string = ",\n " .join(query_fields)
            #
            # merge_df = self.conn.execute(f"""
            # SELECT DISTINCT
            # {query_string}
            # FROM input_data
            # """).fetchdf()
            #
            # print(merge_df)
            #

        logger.info(f"Removing duplicates for colummn {template_sheet.sheet_name()}")
        print(self.config.get_config_path())
        if id_field and ref_header:
            template_df=self.get_filtered_df_by_ref_header(input_df, template_df, ref_header)
        else:
            template_df = template_df.drop_duplicates().dropna(how="all")

        # template_df = template_df.drop_duplicates().dropna(how="all")
        template_df_indices= template_df.index.tolist()
        print(template_df)
        # save_document_indices(sheet_name, template_df_indices)

        header_rules = self.config.get_column_rules() 
        if header_rules:
            for header in header_rules:
                found_rule= _handle_rules_column(template_df, input_df, sheet_name, header, self.config.get_mappings(), template_df_indices, None)
                if not found_rule.empty:
                    template_df[header] = found_rule[header]

        # template_df = self.save_entities(template_df, input_df)

        if id_field:
            prefix : str = self.prefix_obj.get_prefix(id_field)
            self.save_entities(template_df, id_field, ref_header,  prefix)

        print("AFTER")
        print(template_df)

        col_index_map = {
            header: template_sheet.get_col_idx(header)
            for header in template_df.columns
        }

        # for r_idx, row in enumerate(template_df.itertuples(index=False), start=self.data_row_start):
            # template_sheet.get_sheet().append(row)

# def apply_missing_data_with_values_and_font_color(sheet, columns, min_row, max_row, cell_value, cell_font):

        # print(mandatory_fields)
        # mandatory_fields_indices = [ template_df.columns.get_loc(col) + 1 for col in mandatory_fields if col in template_df.columns]
        # print(mandatory_fields_indices)

        # apply_missing_data_with_values_and_font_color(template_sheet.get_sheet(), mandatory_fields_indices, min_row=self.data_row_start+1, max_row=template_sheet.get_sheet().max_row + 1, cell_value="EMPTY", cell_font=MANDATORY_FONT_STYLE)         
        
        # # get_rule=[]
        for r_idx, row in enumerate(template_df.itertuples(index=False), start=self.data_row_start):
            for header in template_df.columns:
                col_idx=col_index_map[header]
                default_val : str =  self.config.get_default_value(header) 
                if header == "State":
                    print(f" {default_val} is {type(default_val)}")
                prefix :str = self.config.get_prefix(header) 
                isMandatory : bool = header in mandatory_fields
                rules = self.config.get_row_rules(header)
                value=getattr(row, header)
                cell=None
                if value and not pd.isna(value):
                    if rules and rules=="row":
                        # indices=[]
                        # indices.append(template_df_indices[r_idx-self.data_row_start])
                        indices= template_df.index.to_list()
                        found_rule= _handle_rules_row(input_df, sheet_name, header, self.config.get_mappings(),indices, value )
                        if found_rule:
                            value = found_rule
                        else:
                            value = value

                    # if default_val != "autogenerate" and prefix != "":
                        # value = prefix + str(value)

                    cell = template_sheet.cell(
                        row=r_idx, 
                        column=col_idx, 
                        value=value
                    )
                    
                    cell.alignment = Alignment(wrap_text=True)
                elif default_val and default_val !=  "autogenerate":
                    value = default_val

                    if rules and rules=="row":
                        indices=[]
                        indices.append(template_df_indices[r_idx-self.data_row_start])
                        found_rule= _handle_rules_row(input_df, sheet_name, header, self.config.get_mappings(),indices, value )
                        if found_rule:
                            value = found_rule
                        else:
                            value = default_val
        #                     # get_rule.append(value)
        #
                    cell = template_sheet.cell(
                        row=r_idx, 
                        column=col_idx, 
                        value=value
                    )
                    if isMandatory:
                        cell.font = mandatory_font
                    cell.alignment = Alignment(wrap_text=True)
                elif isMandatory and not default_val:
                    raise Exception(f"Error: mandatory field '{header}' has missing value")
        #
        # # if get_rule:
        #     # print(get_rule)
        #
        # self.autogenerate_cell_ids(template_sheet, header_to_autogenerate_id, len(template_df))
        # 
