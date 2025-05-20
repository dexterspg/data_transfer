import pandas as pd
import uuid


def main():
    # df = pd.read_excel("output_nre.xlsx", header=2, sheet_name="Premise")
    df = pd.read_excel("input_prolease_398.xlsx", header=3, nrows=100)

    premise=df[['Property Code 1 - Prim Prop Code', 'Subspace Primary Use' ]].drop_duplicates()
    premise['PremiseId'] = [str(uuid.uuid4()) for _ in range(len(premise))] 
    
    premise_area=df[['Lease Code 1 - Prim Lease Code']].drop_duplicates()
    # subspace['PremiseId'] = [str(uuid.uuid4()) for _ in range(len(subspace))] 

     

    

    print(premise)
    print(premise_area)

    # premise=premise.merge(subspace, on="Lease Code 1 - Prim Lease Code", how="left")
    # print(premise)
   



if __name__ == "__main__":
    main()
