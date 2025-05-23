import json
import os
import pandas as pd
from datetime import datetime

class IDGenerator:
    def __init__(self):
        self.sequence_file = 'id_sequences.json'
        self.relationships_file = 'relationships.json'
        self.excel_file = 'property_data.xlsx'
        self.initialize_files()

    def initialize_files(self):
        # Initialize sequence file if it doesn't exist
        if not os.path.exists(self.sequence_file):
            initial_sequences = {
                'LOC': 0,  # Location ID sequence
                'P': 0,    # Premise ID sequence
                'L': 0,    # Lease ID sequence
                'T': 0     # Term ID sequence
            }
            with open(self.sequence_file, 'w') as f:
                json.dump(initial_sequences, f, indent=4)

        # Initialize relationships file if it doesn't exist
        if not os.path.exists(self.relationships_file):
            initial_relationships = {
                'location_premise': {},  # Location to Premise mapping
                'premise_lease': {},     # Premise to Lease mapping
                'lease_term': {}         # Lease to Term mapping
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

    def process_excel_file(self):
        # Read all sheets
        locations_df = pd.read_excel(self.excel_file, sheet_name='Locations')
        premises_df = pd.read_excel(self.excel_file, sheet_name='Premises')
        leases_df = pd.read_excel(self.excel_file, sheet_name='Leases')
        terms_df = pd.read_excel(self.excel_file, sheet_name='Terms')

        # Process Locations
        if 'LocationId' not in locations_df.columns:
            locations_df['LocationId'] = [self.get_next_id('LOC') for _ in range(len(locations_df))]

        # Process Premises
        if 'PremiseId' not in premises_df.columns:
            premises_df['PremiseId'] = [self.get_next_id('P') for _ in range(len(premises_df))]
        
        # Add location-premise relationships
        for _, row in premises_df.iterrows():
            self.add_relationship('location_premise', row['LocationId'], row['PremiseId'])

        # Process Leases
        if 'LeaseId' not in leases_df.columns:
            leases_df['LeaseId'] = [self.get_next_id('L') for _ in range(len(leases_df))]
        
        # Add premise-lease relationships
        for _, row in leases_df.iterrows():
            self.add_relationship('premise_lease', row['PremiseId'], row['LeaseId'])

        # Process Terms
        if 'TermId' not in terms_df.columns:
            terms_df['TermId'] = [self.get_next_id('T') for _ in range(len(terms_df))]
        
        # Add lease-term relationships
        for _, row in terms_df.iterrows():
            self.add_relationship('lease_term', row['LeaseId'], row['TermId'])

        # Save processed data back to Excel
        with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
            locations_df.to_excel(writer, sheet_name='Locations', index=False)
            premises_df.to_excel(writer, sheet_name='Premises', index=False)
            leases_df.to_excel(writer, sheet_name='Leases', index=False)
            terms_df.to_excel(writer, sheet_name='Terms', index=False)

def main():
    generator = IDGenerator()
    generator.process_excel_file()

if __name__ == "__main__":
    main() 
