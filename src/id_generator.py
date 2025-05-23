import uuid
import random
import json
import os
import numpy as np

class IdGenerator:
    def __init__(self, prefix="ID_", start=100000000, end=999999999):
        self.prefix = prefix
        self.start = start
        self.end = end
        self.current_id = start -1
        self.sequence_file = 'id_sequences.json'
        self.relationships_file = 'relationships.json'
        self.initialize_files()

    def generate_id(self):
        # with open(self.sequence_file, 'r') as f:
            # sequences = json.load(f)

        if self.current_id < self.end:
            self.current_id+=1
            # with open(self.sequence_file, 'w') as f:
                # json.dump(sequences, f, indent=4)
        
            return f"{self.prefix}{self.current_id}"
        else:
            raise ValueError("ID limit reached")

    def initialize_files(self):
        if not os.path.exists(self.relationships_file):
            initial_relationships = {
                'location_premise': {}, 
                'premise_lease': {},     
                'lease_term': {}         
            }
            with open(self.relationships_file, 'w') as f:
                json.dump(initial_relationships, f, indent=4)

    def get_next_id(self, prefix):
        with open(self.sequence_file, 'r') as f:
            sequences = json.load(f)
        
        if prefix not in sequences:
            sequences[prefix] = 0
        
        next_num = sequences[prefix]
        sequences[prefix] += 1
        
        with open(self.sequence_file, 'w') as f:
            json.dump(sequences, f, indent=4)
        
        return f"{prefix}{next_num:04d}"

    # @staticmethod
    # def dump_ids(df, header):
        # df[header].to_json("output.json", orient="records", indent=4)

    @staticmethod
    def dump_ids_for_header(df, header):
        data = {header: np.array(df[header]).tolist()}  
        with open("header_output.json", "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def dump_df_for_col_list(df):
        data = {col: np.array(df[col]).tolist() for col in df.columns}
        with open("df_output_col_list.json", "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def dump_df_for_rows(df, output_file="df_rows_output.json"):
        data = df.to_dict(orient="records")  
    
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)


    def add_relationship(self, relationship_type, parent_id, child_id):
        with open(self.relationships_file, 'r') as f:
            relationships = json.load(f)
        
        if relationship_type not in relationships:
            relationships[relationship_type] = {}
        
        if parent_id not in relationships[relationship_type]:
            relationships[relationship_type][parent_id] = []
        
        if child_id not in relationships[relationship_type][parent_id]:
            relationships[relationship_type][parent_id].append(child_id)
        
        with open(self.relationships_file, 'w') as f:
            json.dump(relationships, f, indent=4)

    def get_related_ids(self, relationship_type, parent_id):
        with open(self.relationships_file, 'r') as f:
            relationships = json.load(f)

        return relationships.get(relationship_type, {}).get(parent_id, [])
    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())

