import json
import os
from relationship import RELATIONSHIP_MAPPING, HIERARCHY
from configs.config import RELATIONSHIP_PATH

class RelationshipMapper:

    def __init__(self, relationships_file='relationships.json'):
        self.relationships_file =relationships_file 

    def initialize_files(self):
        # if not os.path.exists(f"{RELATIONSHIP_PATH}/{self.relationships_file}"):
        initial_relationships = { rel: {}  for rel in RELATIONSHIP_MAPPING.values()}

        with open(f"{RELATIONSHIP_PATH}/{self.relationships_file}", 'w') as f:
            json.dump(initial_relationships, f, indent=4)

    def add_relationship(self, relationship_type, parent_id, child_id):
        with open(f"{RELATIONSHIP_PATH}/{self.relationships_file}", 'r') as f:
            relationships = json.load(f)
            
        if relationship_type not in relationships:
            relationships[relationship_type] = {}
    
        if parent_id not in relationships[relationship_type]:
            relationships[relationship_type][parent_id] = []
            
        if child_id not in relationships[relationship_type][parent_id]:
            relationships[relationship_type][parent_id].append(child_id)
            
        with open(f"{RELATIONSHIP_PATH}/{self.relationships_file}", 'w') as f:
            json.dump(relationships, f, indent=4)

    def get_related_ids(self, relationship_type, parent_id):
        with open(f"{RELATIONSHIP_PATH}/{self.relationships_file}",'r') as f:
            relationships = json.load(f)

        return relationships.get(relationship_type, {}).get(parent_id, [])

    def has_field_relationship(self, parent: str,  child: str) -> bool:
        return parent in HIERARCHY  and child in HIERARCHY[parent]

    def get_parent_field(self, child: str) -> str:
        for parent, children in HIERARCHY.items():
            if child in children:
                return parent  
        return ""


