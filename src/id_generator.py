import uuid
from configs.config import ENTITIES_PATH, PREFIX_FILE
from utils import  LoggingUtil
import logging
from domain import Prefix
import json
import os
import numpy as np

logger = LoggingUtil.setup_logger('IdGenerator', console_level=logging.DEBUG)

class IdGenerator:
    def __init__(self, prefix='ID_', start=100000000, end=999999999):
        self.prefix = prefix
        self.start = start
        self.end = end
        self.current_id = start -1
        self.sequence_file = 'id_sequences.json'

    def set_header(self, header):
        self.header =header
    
    def update_sequence(self, prefix, existing_ids):
        if not existing_ids:
            return
        max_num = max(int(id_str[len(prefix):]) for id_str in existing_ids)
        with open(self.sequence_file, 'r') as f:
            sequences = json.load(f)
        sequences[prefix] = max_num + 1
        with open(self.sequence_file, 'w') as f:
            json.dump(sequences, f, indent=4)

    def get_current_raw_id(self):
        return self.current_id

    def generate_id(self, header,  prefix):
        with open(f"{ENTITIES_PATH}/{header}.json", 'r+') as f:
            data = json.load(f)

            if prefix not in data:
                data[prefix] = {
                "number_range_start": self.start,
                "number_range_end": self.end,
                "last_id_generated": self.current_id
                    }

            sequence = data[prefix]

            if  sequence["last_id_generated"] < sequence["number_range_end"]:
                sequence["last_id_generated"]+=1
                self.current_id = sequence["last_id_generated"]
            else:
                raise ValueError("ID limit reached")

            new_id = f"{self.prefix}{sequence["last_id_generated"]}"

            ids_list = data.get(header, [])
            ids_list.append(new_id)
            data[header] = ids_list
            f.seek(0)
            json.dump(data, f, indent = 4)
            f.truncate()
            return new_id

    # @staticmethod
    # def dump_ids(df, header):
        # df[header].to_json("output.json", orient="records", indent=4)


    def write_ids_for_header(self, df, header, output=None):
        if not output:
            output = f"{ENTITIES_PATH}/{header}.json"
        try:
            with open(output, "r+") as f:
                data = json.load(f)
                ids_list = data.get(header, [])

                new_ids = df[header].to_list()
                combined_ids = list(dict.fromkeys(ids_list + new_ids))

                data[header] = combined_ids
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {output} not found")
        except IOError:
            raise IOError(f"Error writing to file {output}")

    def read_ids_for_header(self, header, output=None):
        if not output:
            output = f"{ENTITIES_PATH}/{header}.json"
        try:
            with open(output, "r") as f:
                curr_data = json.load(f)
                return curr_data.get(header, [])
        except Exception as e:
            logger.error(e)

    @staticmethod
    def dump_df_for_col_list(df, output="df_output_col_list.json"):
        data = {col: np.array(df[col]).tolist() for col in df.columns}
        with open(output, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def dump_df_for_rows(df, output_file="df_rows_output.json"):
        data = df.to_dict(orient="records")  
    
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())

