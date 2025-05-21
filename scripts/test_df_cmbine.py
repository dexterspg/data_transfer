import pandas as pd
import uuid

class IdGenerator:
    def __init__(self, prefix="ID_", start=100000000, end=999999999):
        self.prefix = prefix
        self.start = start
        self.end = end
        self.current_id = start - 1

    def generate_id(self):
        if self.current_id < self.end:
            self.current_id += 1
            return f"{self.prefix}{self.current_id}"
        else:
            raise ValueError("ID limit reached")

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())


def main():
    # Load Excel file
    df = pd.read_excel("input_prolease_398.xlsx", header=3, nrows=100)

    # LOCATION DATAFRAME
    location = df[['Lease Code 1 - Prim Lease Code']].drop_duplicates()
    location['idx'] = location.index.tolist()

    # BUSINESS UNIT ID GENERATION (Optimized)
    business_id_gen = IdGenerator("BU")
    business = df[['Lease Primary Use - Calculated Field']].copy()
    business['idx'] = business.index.tolist()

    location_to_business = location.merge(business, on="idx", how="left")
    location_to_business["BusinessUnitId"] = [
        business_id_gen.generate_id() for _ in range(len(location))
    ]

    print("Business Unit Mapping:")
    print(location_to_business)

    # LEGAL ENTITY ID GENERATION (Optimized)
    legal_id_gen = IdGenerator("")
    legal_entity = df[['Lessee']].copy()
    legal_entity['idx'] = legal_entity.index.tolist()

    location_to_legalentity = location.merge(legal_entity, on="idx", how="left")

    # Remove duplicates before generating LegalEntityId
    unique_lessees = location_to_legalentity[['Lessee']].drop_duplicates().dropna()

    # Efficiently generate unique IDs for each Lessee
    legal_entity_df = pd.DataFrame(
        unique_lessees["Lessee"].apply(lambda x: (x, legal_id_gen.generate_id())).tolist(),
        columns=["Lessee", "LegalEntityId"]
    )

    print(legal_entity_df)

    # Merge the generated IDs into the main DataFrame
    location_to_legalentity = location_to_legalentity.merge(legal_entity_df, on="Lessee", how="left")

    print("Legal Entity Mapping:")
    print(location_to_legalentity)

    
    premise_id_gen = IdGenerator("P")
    premise= df[['Lease Code 1 - Prim Lease Code', 'Subspace Primary Use']].drop_duplicates()
    premise['idx']= premise.index.tolist()
    print(premise)

    premise_df = pd.DataFrame(
        premise["Subspace Primary Use"].apply(lambda x: (x, premise_id_gen.generate_id())).tolist(),
        columns=['Subspace Primary Use', 'PremiseId']
    )
    print(premise_df)
    # location_to_premise= location_to_legalentity.merge(premise_df, on="Subspace Primary Use", how="left")

    # print(location_to_premise)


if __name__ == "__main__":
    main()

