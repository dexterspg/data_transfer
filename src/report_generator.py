import pandas as pd
import json
import re
from openpyxl import load_workbook
from openpyxl.styles import Font
from id_generator import IdGenerator
from utils import SheetUtils, LoggingUtil, RegexUtils
from sheet_model import Sheet

mandatory_font= Font(color="00FF9B9B")
logger = LoggingUtil.setup_logger('ExcelProcessor')

class ExcelProcessor:

    def __init__(self, input_file, template_file, output_file, config_file, template_header_row=1, input_header_row=1, data_row_start=None) :
        self.input_file =input_file 
        self.output_file =output_file
        self.template_wb= load_workbook(template_file)
        self._load_config(config_file)
        self.template_header_row = template_header_row
        self.input_header_row = input_header_row
        self.data_row_start= self.template_header_row+1 if data_row_start is None else data_row_start
        self.limitRows = None
        self.number_of_rows_to_skip=0

    def _load_config(self, config_file):
        """Load the configuration from JSON file"""
        with open(config_file, 'r') as f:
            self.config = json.load(f)

    def _save_workbook(self):
        self.template_wb.save(self.output_file)
        print(f"Processing complete. Output saved to {self.output_file}")

    def set_data_row_start(self, data_row_start):
        self.data_row_start = data_row_start

    def set_limit_rows(self, limitRows):
        self.limitRows= limitRows

    def valid_header_mapping(self, header : str, input_df : pd.DataFrame) -> bool:
        sheet_name = self.config['sheet_name']
        if header in self.config['mappings'].keys():
            in_header_props: dict = self.config['mappings'][header]

            if not in_header_props:
                logger.error(f"Warning: no input mapping found for '{header}' for Sheet '{sheet_name}'") 

            default_val: str= in_header_props['default']
            output_col : str = in_header_props['external_column']

            if not default_val and not output_col:
                logger.error(f"Warning: no mapping found for '{header}' for Sheet '{sheet_name}'")
                return False 

            if output_col and output_col not in input_df.columns:
                logger.warning(f"Warning: no input field found for '{header}' for Sheet '{sheet_name}'")

            return True
        return False 


    def autogenerate_cell_ids(self,template_sheet, prefix_dict, data_row_range):
        for header, prefix in prefix_dict.items():
            id_generator=IdGenerator(prefix) if prefix else IdGenerator()
            for r_idx in range(data_row_range):
                value=id_generator.generate_id()
                cell =template_sheet.cell(row=r_idx+self.data_row_start, column=template_sheet.get_col_idx(header), value=value)
                cell.font=mandatory_font
    
    def set_number_of_last_rows_to_drop(self, number_of_rows_to_skip):
        self.number_of_rows_to_skip=number_of_rows_to_skip

    def process(self):
        """Process the input file according to the template and mappings"""
        input_df = pd.read_excel(self.input_file, header =self.input_header_row, nrows=self.limitRows, skipfooter=self.number_of_rows_to_skip)
        print(len(input_df))

        sheet_name = self.config['sheet_name']
        if sheet_name not in self.template_wb.sheetnames:
            logger.error(f"Warning: Sheet '{sheet_name}' not found in template")
            return

        template_sheet : Sheet= Sheet(self.template_wb[sheet_name], self.template_header_row, self.data_row_start)
        mandatory_fields = self.config['mandatory_fields']

        header_to_autogenerate_id={}
        input_df.columns=input_df.columns.str.replace(' ', '_').str.replace("/","_").str.replace(".","_").str.replace('-','_')

        print(template_sheet.get_headers())
        header_to_autogenerate_id={}
        processed_rows=[{} for _ in range(len(input_df))]  
        for header in template_sheet.get_headers():
            if not self.valid_header_mapping(header, input_df):
                continue

            in_header_props: dict= self.config['mappings'][header]

            print(f"{header}") 

            default_val : str = in_header_props['default']
            output_col : str  = in_header_props['external_column']
            prefix :str = in_header_props.get('prefix',"")


            if default_val and default_val=="autogenerate" and prefix !="":
                header_to_autogenerate_id[header]=prefix 

            normalized_col= output_col.replace(" ", "_").replace("/", "_").replace(".", "_").replace('-', '_')
            is_map_in_input_col : bool=  True if normalized_col and normalized_col in input_df.columns else False
            is_regex_exists : bool='regex' in in_header_props and in_header_props['regex'] != ""

            row_start=template_sheet.get_data_row_start()
            for r_idx, row in enumerate(input_df.itertuples(index=False), start =row_start ):
                value=None
                if is_map_in_input_col:
                    text = getattr(row, normalized_col,None)
                    if text is not None and not pd.isna(text):
                        value =  RegexUtils._extract_with_regex(text, in_header_props['regex']) if is_regex_exists else text

                processed_rows[r_idx-row_start][header] = value

        template_df = pd.DataFrame(processed_rows) 
        logger.info(f"Removing duplicates for colummn {template_sheet.sheet_name()}")
        template_df = template_df.drop_duplicates()

        col_index_map = {
            header: template_sheet.get_col_idx(header)
            for header in template_df.columns
        }

        for r_idx, row in enumerate(template_df.itertuples(index=False), start=self.data_row_start):
            for header in template_df.columns:
                col_idx=col_index_map[header]
                in_header_props: dict= self.config['mappings'][header]
                default_val : str = in_header_props['default']
                isMandatory : bool = header in mandatory_fields
                value=getattr(row, header)
                if value:
                    cell = template_sheet.cell(
                        row=r_idx, 
                        column=col_idx, 
                        value=value
                    )
                elif default_val and default_val !=  "autogenerate":
                    cell = template_sheet.cell(
                        row=r_idx, 
                        column=col_idx, 
                        value=default_val 
                    )
                    if isMandatory:
                        cell.font = mandatory_font
                elif isMandatory and not default_val:
                    raise Exception(f"Error: mandatory field '{header}' has missing value")

        self.autogenerate_cell_ids(template_sheet, header_to_autogenerate_id, len(template_df))
        
