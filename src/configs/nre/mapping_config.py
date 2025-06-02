import json
from typing import Dict, List
from enum import Enum

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

    def get_src_fields(self) -> List[str]:
        mappings = self.get_mappings()
        return list(mappings.keys()) if mappings else []

    def get_header_props(self, header: str) -> Dict[str, str]:
        return self.get_mappings().get(header, {})  

    def get_external_column_of_header(self, header: str) -> str:
        return self.get_header_props(header).get(MappingEnum.EXTERNAL_COLUMN.value, '')

    def get_external_column_fields(self) -> List[str]:
        src_fields : List[str] = self.get_src_fields()
        return list(set(self.get_external_column_of_header(src) for src in src_fields))

    def get_default_value(self, header: str) -> str:
        return self.get_header_props(header).get(MappingEnum.DEFAULT.value, '')

    def get_prefix(self, header: str) -> str:
        return self.get_header_props(header).get(MappingEnum.PREFIX.value, '')

    def get_row_rules(self, header: str) -> str:
        return self.get_header_props(header).get(MappingEnum.ROW_RULES.value, '')
