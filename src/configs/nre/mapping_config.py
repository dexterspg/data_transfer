import json
import copy
from typing import Dict, List
from enum import Enum
from configs.config import NRE_SHEETS_DIR

class MappingEnum(Enum):
    SHEET_NAME = 'sheet_name'
    MAPPINGS = 'mappings'
    EXTERNAL_COLUMN = 'external_column'
    MANDATORY_FIELDS = 'mandatory_fields' 
    ID_FIELDS = 'id_fields'
    DEFAULT ='default'
    REFERENCE_ID_FIELD = 'reference_id_fields'
    PREFIX = 'prefix'
    COLUMN_RULES = 'has_rules'
    ROW_RULES= 'rules'

class MappingConfig:

    def __init__(self, config_path: str):
        self.config = {}  # Initialize as a dictionary
        self.config_path : str = "" 
        self._load_config(config_path)

    def _load_config(self, config_path: str):
        if config_path == '':
            return
        self.config_path = config_path
        print(f" Loading config from {config_path}")
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def copy(self):
        return copy.deepcopy(self)

    def get_config_for_sheet_name(self, sheet_name: str):
        current_path = self.config_path
        self._load_config(f'{NRE_SHEETS_DIR}/{sheet_name}.json')
        entity = self.copy()
        self._load_config(current_path)
        return entity

    def get_config_path(self):
        return self.config_path

    def get_sheet_name(self)-> str:
        return self.config.get(MappingEnum.SHEET_NAME.value, '')

    def get_mandatory_fields(self)-> List[str]:
        return self.config.get(MappingEnum.MANDATORY_FIELDS.value, [])

    def get_column_rules(self)-> List[str]:
        return self.config.get(MappingEnum.COLUMN_RULES.value, [])

    def get_id_field(self) -> str :
        return self.config.get(MappingEnum.ID_FIELDS.value, '')

    def get_reference_dict(self)-> Dict[str, str]:
        return self.config.get(MappingEnum.REFERENCE_ID_FIELD.value, {})

    def get_reference_header_name(self)-> str:
        if not self.get_reference_dict():
            return ''
        return next(iter(self.get_reference_dict().keys()), '')

    def get_reference_header_value(self)-> str:
        if not self.get_reference_dict():
            return ''
        return next(iter(self.get_reference_dict().values()))

    def get_mappings(self) -> Dict[str, Dict]:
        return self.config.get(MappingEnum.MAPPINGS.value, {})  

    def get_df_fields(self) -> List[str]:
        mappings = self.get_mappings()
        return list(mappings.keys()) if mappings else []


    def get_df_fields_for_sheet_name(self, sheet_name : str) -> List[str]:
        current_path = self.config_path
        self._load_config(f'{NRE_SHEETS_DIR}/{sheet_name}.json')
        df_fields = self.get_df_fields() 
        self._load_config(current_path)
        return df_fields 

    def get_header_props(self, header: str) -> Dict[str, str]:
        return self.get_mappings().get(header, {})  

    def get_external_column_of_header(self, header: str) -> str:
        return self.get_header_props(header).get(MappingEnum.EXTERNAL_COLUMN.value, '')

    def get_external_column_of_header_on_sheet(self, sheet_name : str,  header: str) -> str:
        current_path = self.config_path
        self._load_config(f'{NRE_SHEETS_DIR}/{sheet_name}.json')
        header = self.get_external_column_of_header(header) 
        self._load_config(current_path)
        return header

    def get_external_column_fields(self) -> List[str]:
        df_fields : List[str] = self.get_df_fields()
        return list(set(column for df in df_fields if (column:=self.get_external_column_of_header(df))))

    def get_external_column_fields_on_sheet(self, sheet_name :str) -> List[str]:
        current_path = self.config_path
        self._load_config(f'{NRE_SHEETS_DIR}/{sheet_name}.json')
        ext_fields = self.get_external_column_fields()
        self._load_config(current_path)
        return ext_fields

    def get_df_fields_for_sheet_name_with_ext(self, config, sheet_name :str="") -> List[str]:
        current_path = self.config_path
        self._load_config(f'{NRE_SHEETS_DIR}/{sheet_name}.json')
        src_fields : List[str] = self.get_df_fields()
        src_fields_with_ext_col = [
            src
            for src in src_fields
            if self.get_external_column_of_header(src)
        ]
        self._load_config(current_path)
        return src_fields_with_ext_col 

    def get_default_value(self, header: str) -> str:
        return self.get_header_props(header).get(MappingEnum.DEFAULT.value, '')

    def get_prefix(self, header: str) -> str:
        return self.get_header_props(header).get(MappingEnum.PREFIX.value, '')

    def get_row_rules(self, header: str) -> str:
        return self.get_header_props(header).get(MappingEnum.ROW_RULES.value, '')
