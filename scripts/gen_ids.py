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

    def update_sequence(self, prefix, existing_ids):
        """Update sequence file with highest existing ID"""
        if not existing_ids:
            return
        
        max_num = max(int(id_str[len(prefix):]) for id_str in existing_ids)
        with open(self.sequence_file, 'r') as f:
            sequences = json.load(f)
        sequences[prefix] = max_num + 1
        with open(self.sequence_file, 'w') as f:
            json.dump(sequences, f, indent=4)

    def process_excel_file_location(self):
        """Process only the Locations sheet"""
        print("Processing Locations sheet...")
        try:
            # Read Locations sheet
            locations_df = pd.read_excel(self.excel_file, sheet_name='Locations')
            
            # Process Location IDs
            if 'LocationId' not in locations_df.columns:
                locations_df['LocationId'] = [self.get_next_id('LOC') for _ in range(len(locations_df))]
            else:
                self.update_sequence('LOC', locations_df['LocationId'])

            # Save only the Locations sheet back to Excel
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                locations_df.to_excel(writer, sheet_name='Locations', index=False)
            
            print("Locations sheet processed successfully!")
            return True
        except Exception as e:
            print(f"Error processing Locations sheet: {str(e)}")
            return False

    def process_excel_file_premises(self):
        """Process the Premises sheet using existing Location IDs"""
        print("Processing Premises sheet...")
        try:
            # Read both sheets
            locations_df = pd.read_excel(self.excel_file, sheet_name='Locations')
            premises_df = pd.read_excel(self.excel_file, sheet_name='Premises')

            # Validate Location IDs
            valid_location_ids = set(locations_df['LocationId'])
            invalid_locations = premises_df[~premises_df['LocationId'].isin(valid_location_ids)]
            if not invalid_locations.empty:
                raise ValueError(f"Invalid LocationIds found in Premises sheet: {invalid_locations['LocationId'].tolist()}")

            # Process Premise IDs
            if 'PremiseId' not in premises_df.columns:
                premises_df['PremiseId'] = [self.get_next_id('P') for _ in range(len(premises_df))]
            else:
                self.update_sequence('P', premises_df['PremiseId'])

            # Add relationships
            for _, row in premises_df.iterrows():
                self.add_relationship('location_premise', row['LocationId'], row['PremiseId'])

            # Save both sheets back to Excel
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                locations_df.to_excel(writer, sheet_name='Locations', index=False)
                premises_df.to_excel(writer, sheet_name='Premises', index=False)

            print("Premises sheet processed successfully!")
            return True
        except Exception as e:
            print(f"Error processing Premises sheet: {str(e)}")
            return False

    def process_excel_file_leases(self):
        """Process the Leases sheet using existing Premise IDs"""
        print("Processing Leases sheet...")
        try:
            # Read all relevant sheets
            premises_df = pd.read_excel(self.excel_file, sheet_name='Premises')
            leases_df = pd.read_excel(self.excel_file, sheet_name='Leases')

            # Validate Premise IDs
            valid_premise_ids = set(premises_df['PremiseId'])
            invalid_premises = leases_df[~leases_df['PremiseId'].isin(valid_premise_ids)]
            if not invalid_premises.empty:
                raise ValueError(f"Invalid PremiseIds found in Leases sheet: {invalid_premises['PremiseId'].tolist()}")

            # Process Lease IDs
            if 'LeaseId' not in leases_df.columns:
                leases_df['LeaseId'] = [self.get_next_id('L') for _ in range(len(leases_df))]
            else:
                self.update_sequence('L', leases_df['LeaseId'])

            # Add relationships
            for _, row in leases_df.iterrows():
                self.add_relationship('premise_lease', row['PremiseId'], row['LeaseId'])

            # Save all sheets back to Excel
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                pd.read_excel(self.excel_file, sheet_name='Locations').to_excel(writer, sheet_name='Locations', index=False)
                premises_df.to_excel(writer, sheet_name='Premises', index=False)
                leases_df.to_excel(writer, sheet_name='Leases', index=False)

            print("Leases sheet processed successfully!")
            return True
        except Exception as e:
            print(f"Error processing Leases sheet: {str(e)}")
            return False

    def process_excel_file_terms(self):
        """Process the Terms sheet using existing Lease IDs"""
        print("Processing Terms sheet...")
        try:
            # Read all relevant sheets
            leases_df = pd.read_excel(self.excel_file, sheet_name='Leases')
            terms_df = pd.read_excel(self.excel_file, sheet_name='Terms')

            # Validate Lease IDs
            valid_lease_ids = set(leases_df['LeaseId'])
            invalid_leases = terms_df[~terms_df['LeaseId'].isin(valid_lease_ids)]
            if not invalid_leases.empty:
                raise ValueError(f"Invalid LeaseIds found in Terms sheet: {invalid_leases['LeaseId'].tolist()}")

            # Process Term IDs
            if 'TermId' not in terms_df.columns:
                terms_df['TermId'] = [self.get_next_id('T') for _ in range(len(terms_df))]
            else:
                self.update_sequence('T', terms_df['TermId'])

            # Add relationships
            for _, row in terms_df.iterrows():
                self.add_relationship('lease_term', row['LeaseId'], row['TermId'])

            # Save all sheets back to Excel
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                pd.read_excel(self.excel_file, sheet_name='Locations').to_excel(writer, sheet_name='Locations', index=False)
                pd.read_excel(self.excel_file, sheet_name='Premises').to_excel(writer, sheet_name='Premises', index=False)
                leases_df.to_excel(writer, sheet_name='Leases', index=False)
                terms_df.to_excel(writer, sheet_name='Terms', index=False)

            print("Terms sheet processed successfully!")
            return True
        except Exception as e:
            print(f"Error processing Terms sheet: {str(e)}")
            return False

def main():
    generator = IDGenerator()
    
    # Process each sheet in sequence
    if generator.process_excel_file_location():
        if generator.process_excel_file_premises():
            if generator.process_excel_file_leases():
                if generator.process_excel_file_terms():
                    print("All sheets processed successfully!")
                else:
                    print("Failed to process Terms sheet")
            else:
                print("Failed to process Leases sheet")
        else:
            print("Failed to process Premises sheet")
    else:
        print("Failed to process Locations sheet")

if __name__ == "__main__":
    main() 
