import pandas as pd
import uuid

def main():
    input_file = "input_prolease_398.xlsx"

# print(uuid.uuid4())
    df =pd.read_excel(io=input_file, header=3, nrows=15)

    print(df.columns[df.columns.str.contains('Lessee')].tolist())


    print(df[['Lessee', 'Lease Code 1 - Prim Lease Code']])

    location_id = df[['Lease Code 1 - Prim Lease Code']].drop_duplicates()
                                                        # .reset_index(drop=True)
    print(location_id)


if __name__ == "__main__":
    main()

