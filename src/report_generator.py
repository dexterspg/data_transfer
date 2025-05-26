import logging
from datetime import datetime
from configs.config import NRE_SHEETS_DIR
from configs.config import PREFIX_FILE
from domain import Prefix, IdObj
from nre_enums import *
import pandas as pd
import json
from typing import List, Dict
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, NamedStyle
from id_generator import IdGenerator
from utils import  LoggingUtil, SheetUtils
from utils.regex_utils import _extract_with_regex
from utils.excel_style_utils import _apply_date_format
from sheet_model import Sheet
from rules import _handle_rules_column, _handle_rules_row
from nre_enums import LocationLegalEntityColumns, get_sheet_enum
from create_documents import save_document_indices, retrieve_document_indices

mandatory_font= Font(color="00FF9B9B")
logger = LoggingUtil.setup_logger('ExcelProcessor', console_level=logging.DEBUG)

class ExcelProcessor:

    def __init__(self, input_file, template_file, output_file, config_file, template_header_row=1, input_header_row=1, data_row_start=None) :
        self.id_container = {}
        self.input_file =input_file 
        self.output_file =output_file
        self.template_header_row = template_header_row
        self.input_header_row = input_header_row
        self.data_row_start= self.template_header_row+1 if data_row_start is None else data_row_start
        self.limitRows = None
        self.number_of_rows_to_skip=0
        self.initialize_files(template_file, config_file)

    def initialize_files(self, template_file, config_file):
        self.template_wb= load_workbook(template_file)
        self._load_config(config_file)
        self.prefix_obj = Prefix(PREFIX_FILE)

    def _load_config(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)

    def _save_workbook(self):
        self.template_wb.save(self.output_file)
        logger.info(f"Processing complete. Output saved to {self.output_file}")

    def set_data_row_start(self, data_row_start):
        self.data_row_start = data_row_start

    def set_limit_rows(self, limitRows):
        self.limitRows= limitRows

    def valid_header_mapping(self, header : str) -> bool:
        sheet_name = self.config['sheet_name']
        if header in self.config['mappings'].keys():
            in_header_props: dict = self.config['mappings'][header]

            if not in_header_props:
                logger.warning(f"Warning: no input mapping found for '{header}' for Sheet '{sheet_name}'") 

            default_val: str= in_header_props.get('default', None)
            output_col : str = in_header_props.get('external_column',None)

            if not default_val and not output_col:
                logger.error(f"Warning: no mapping found for '{header}' for Sheet '{sheet_name}'")
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

    def migrate_data(self, sheet_name, input_df , template_sheet):
        header_to_autogenerate_id={}
        # original_input_columns = input_df.columns.copy()

        input_df.columns=input_df.columns.str.replace(' ', '_').str.replace("/","_").str.replace('-','_').str.replace('(','_').str.replace(')','_').str.replace('#','_')

       # print(template_sheet.get_headers())
        header_to_autogenerate_id={}
        processed_rows=[{} for _ in range(len(input_df))]  
        for header in template_sheet.get_headers():
            logger.info(f"Processing {header} of sheet {sheet_name}")
            if not self.valid_header_mapping(header):
                continue

            in_header_props: dict= self.config['mappings'][header]

            default_val:str = in_header_props.get('default',"")
            output_col :str = in_header_props.get('external_column',"")
            prefix :str = in_header_props.get('prefix',"")

            if default_val=="autogenerate" and prefix !="":
                header_to_autogenerate_id[header]=prefix 

            normalized_col= output_col.replace(" ", "_").replace("/", "_").replace('-', '_').replace('(','_').replace(')','_').replace('#','_')
            is_map_in_input_col : bool=  True if normalized_col and normalized_col in input_df.columns else False
            is_regex_exists : bool='regex' in in_header_props and in_header_props['regex'] != ""

            # if sheet_name == "Premise":
                # print(input_df.loc[:, input_df.columns.str.contains('RE_Tax')])
        # print(template_sheet.get_headers())
            row_start=template_sheet.get_data_row_start()
            for r_idx, row in enumerate(input_df.itertuples(index=False), start =row_start ):
                value=None
                if is_map_in_input_col:
                    text = getattr(row, normalized_col,None)
                    # if header == "DefaultJurisdictionId":
                        # print(input_df.loc[:, input_df.columns.str.contains('RE_Tax')])
                        # if r_idx==row_start:
                            # print(row)
                        # print(text)
                    if text is not None and not pd.isna(text):
                        value =  _extract_with_regex(text, in_header_props['regex']) if is_regex_exists else str(text)

                processed_rows[r_idx-row_start][header] = value

        # input_df.columns=original_input_columns
        template_df = pd.DataFrame(processed_rows) 

        return template_df


    # def autogenerate_cell_ids(self,template_sheet, prefix_dict, data_row_range):
    #     for header, prefix in prefix_dict.items():
    #         # id_generator=IdGenerator(prefix) if prefix else IdGenerator()
    #         for r_idx in range(data_row_range):
    #             value=id_generator.generate_id()
    #             cell =template_sheet.cell(row=r_idx+self.data_row_start, column=template_sheet.get_col_idx(header), value=value)
    #             c_ell.font=mandatory_font
    #             cell.alignment = Alignment(wrap_text=True)
    #             
    def autogenerate_cell_ids_df(self, template_df, input_df) -> pd.DataFrame:
        id_fields : str = self.config.get("id_fields","")
        if not id_fields:
            return pd.DataFrame()
    
        indices = []
        ref_header = None
        ref_col = None
        reference_id_fields: Dict[str, str] = self.config.get("reference_id_fields",{})
        if reference_id_fields:
            ref_header = next(iter(reference_id_fields.values()), None)
            ref_obj_list : List[IdObj] = self.id_container.get(ref_header, [])
            for ref_obj in ref_obj_list:
                indices.append(ref_obj.get_position())
            
            # for sheet_name in reference_id_fields.keys():
            #     prefix : str = self.prefix_obj.get_prefix(reference_id_fields[sheet_name])
            #     sheet : Sheet= Sheet(self.template_wb[sheet_name], self.template_header_row, self.data_row_start)
            #     ref_header  = reference_id_fields[sheet_name]
            #     df_list = sheet.get_col_values_for_header_remove_prefix(ref_header, prefix)
            #     # sheet_df = sheet.to_dataframe_remove_prefix(header, prefix)
            #     print("EXTERNAL CONFIG LOADING.....")
            #     ext_config = SheetUtils._load_other_config(sheet.title())
            #     ref_col = ext_config['mappings'][ref_header]['external_column']
            #     indices = SheetUtils.get_first_matched_indices(input_df, df_list, ref_col)  
            #     # print(sheet_df[reference_id_fields[sheet_name]].tolist())
            #
        if ref_header:
            duplicated_mask=template_df.duplicated(keep=False)
            template_df = template_df[~duplicated_mask | template_df.index.isin(indices)]
        print("======================================================================")
        print("======================================================================")
        print("======================================================================")
        print(indices)
        print(template_df)

        prefix : str = self.prefix_obj.get_prefix(id_fields)
        id_generator=IdGenerator(prefix)
        logger.info(f"Processing {id_fields} with prefix {prefix if prefix else 'not found.'}") 

        # if self.config["mappings"][id_fields].get("external_column", "") !="":
        #     print(f"Use id mapping defined for {id_fields}")
        #     for row in template_df.itertuples(index=True):
        #         value = getattr(row, id_fields)
        #         value = prefix + str(value) if pd.notna(value) else value
        #         if not value:
        #             value=id_generator.generate_id(id_fields, prefix)
        #         template_df.at[row.Index, id_fields] = value
        #
        #     id_generator.write_ids_for_header(template_df, id_fields)
        # else:
        #     print("generate auto id") 
        #     template_df[id_fields]=[id_generator.generate_id(id_fields, prefix) for _ in range(len(template_df))]

        ext_col = self.config['mappings'][id_fields].get("external_column", "")
        isIdDefined = bool(ext_col !="")

        obj_list : List[IdObj] = []
        for row in template_df.itertuples(index=True):
            raw = None
            if isIdDefined:
                value = getattr(row, id_fields)
                raw = value
                value = prefix + str(value) if pd.notna(value) else value
                if not value:
                    value = id_generator.generate_id(id_fields, prefix)
                template_df.at[row.Index, id_fields] = value
            else:
                template_df.at[row.Index, id_fields] = id_generator.generate_id(id_fields, prefix)
                raw = id_generator.get_current_raw_id()

            if ref_header:
                print(row.Index)
                value= next(
    (id_obj.get_value() for id_obj in self.id_container[ref_header] if id_obj.get_position() == row.Index), None)
                if(id_fields == "PremiseId"):
                    print(row.Index)
                    print(value)
                if value:
                    template_df.at[row.Index, ref_header]  = value
                else:
                    ref_list_ids  = self.id_container.get(ref_header, [])
                    first_entry = ref_list_ids[0]
                    other_type =  first_entry.get_other_type() if ref_list_ids != [] else ""
                    ref_prefix = first_entry.get_prefix()
                    value = ref_prefix + str(input_df.at[row.Index, other_type]) if other_type else None
                    if(id_fields == "PremiseId"):
                        print(first_entry)
                        print(row.Index)
                        print(value)
                    template_df.at[row.Index, ref_header] = value

            id_obj = IdObj(raw, prefix, row.Index, id_fields, ext_col)
            obj_list.append(id_obj)
            
            # if ref_header == "LocationId" and id_fields == "PremiseId":
                # value =input_df.at[row.Index, ext_col]
                # id_generator.add_relationship("location_premise", value, inpu ) if isIdDefined: id_generator.write_ids_for_header(template_df, id_fields)
        self.id_container[id_fields] =  obj_list 
        print("ID CONTAINER ===============================================================")
        print(self.id_container.get(ref_header, []))
        if not isIdDefined:
            id_generator.write_ids_for_header(template_df, id_fields)
        return template_df

    def process(self):
        """Process the input file according to the template and mappings"""
        input_df = pd.read_excel(io=self.input_file, header=self.input_header_row, nrows=self.limitRows, skipfooter=self.number_of_rows_to_skip)
        sheet_name = self.config['sheet_name']
        reference : str = self.config.get('has_reference', None)
        if sheet_name not in self.template_wb.sheetnames:
            logger.error(f"Warning: Sheet '{sheet_name}' not found in template")
            return

        template_sheet : Sheet= Sheet(self.template_wb[sheet_name], self.template_header_row, self.data_row_start)
        mandatory_fields = self.config['mandatory_fields']
        reference_sheets = self.config.get('references',[])

        if reference_sheets:
            logger.info(f"{sheet_name} reference sheet {reference_sheets}")
        
        template_df = self.migrate_data(sheet_name, input_df.copy(), template_sheet)
        print("BEFORE")
        print(template_df)
        logger.info(f"Removing duplicates for colummn {template_sheet.sheet_name()}")

        # if reference_id_fields:
        #     for sheet_name in reference_id_fields.keys():
        #         sheet : Sheet= Sheet(self.template_wb[sheet_name], self.template_header_row, self.data_row_start)
        #         sheet_df = sheet.to_dataframe(reference_id_fields[sheet_name])
        #         print(sheet_df)
        #
        reference_id_fields: Dict[str, str] = self.config.get("reference_id_fields",None)
        # if reference_id_fields:
            # indices = retrieve_document_indices(str(next(iter(reference_id_fields))))
            # duplicated_mask=template_df.duplicated(keep=False)
            # template_df = template_df[~duplicated_mask | template_df.index.isin(indices)]
        # else:
            # template_df = template_df.drop_duplicates().dropna(how="all")
        print("drop duplicate")
        template_df = template_df.drop_duplicates().dropna(how="all")
        template_df_indices= template_df.index.tolist()
        print(template_df)
        # save_document_indices(sheet_name, template_df_indices)

        header_rules = self.config.get('has_rules')
        if header_rules:
            for header in header_rules:
                found_rule= _handle_rules_column(input_df, get_sheet_enum(sheet_name), header, self.config['mappings'], template_df_indices, None)
                if not found_rule.empty:
                    template_df[header] = found_rule[header]

        template_df = self.autogenerate_cell_ids_df(template_df, input_df)
        print("AFTER")
        print(template_df)
        col_index_map = {
            header: template_sheet.get_col_idx(header)
            for header in template_df.columns
        }

        # # get_rule=[]
        for r_idx, row in enumerate(template_df.itertuples(index=False), start=self.data_row_start):
            for header in template_df.columns:
                col_idx=col_index_map[header]
                in_header_props: dict= self.config['mappings'][header]
                default_val : str = in_header_props.get('default',"")
                prefix :str = in_header_props.get('prefix',"")
                # format :str = in_header_props.get('format',"")
                isMandatory : bool = header in mandatory_fields
                rules = in_header_props.get('rules')
                value=getattr(row, header)
                cell=None
                if value:
                    if rules and rules=="row":
                        # indices=[]
                        # indices.append(template_df_indices[r_idx-self.data_row_start])
                        indices= template_df.index.to_list()
                        found_rule= _handle_rules_row(input_df, get_sheet_enum(sheet_name), header, self.config['mappings'],indices, value )
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
                        found_rule= _handle_rules_row(input_df, get_sheet_enum(sheet_name), header, self.config['mappings'],indices, value )
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
