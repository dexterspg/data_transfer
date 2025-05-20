import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "Los Angeles", "Chicago"]
})

# Iterate using enumerate() and itertuples()
for r_idx, row in enumerate(df.itertuples(index=False), start=1):  # Start index from 1
    name = getattr(row, "Name")  # Access 'Name' column
    age = getattr(row, "Age")    # Access 'Age' column
    city = getattr(row, "City")  # Access 'City' column

    print(f"Row {r_idx}: Name={name}, Age={age}, City={city}")

