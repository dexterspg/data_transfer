
import pandas as pd

# Sample Large DataFrame (~15,000 rows)
data = {
    "LocationID": [1, 2, 3, 3, 4, 4],
    "Address": ["123 Main St", "456 Elm St", "789 Oak St", "789 Oak St", "123 Main St", "123 Main St"],
    "City": ["New York", "Los Angeles", "Chicago", "Chicago", "New York", "New York"],
    "PremiseType": ["Retail", "Office", "Warehouse", "Industrial", "Retail", "Office"],
    "LeaseStart": ["2023-01-01", "2023-05-01", "2022-07-01", "2023-08-01", "2023-03-01", "2024-06-01"],
    "LeaseEnd": ["2025-01-01", "2025-05-01", "2024-07-01", "2025-08-01", "2026-03-01", "2027-06-01"],
    "TermStart": ["2023-01-01", "2024-02-01", "2022-07-01", "2023-08-01", "2023-03-01", "2025-01-01"],
    "TermEnd": ["2024-01-01", "2025-01-01", "2023-07-01", "2024-08-01", "2024-06-01", "2026-01-01"],
    "Rent": [2000, 2500, 1800, 2200, 2400, 2600]
}

df = pd.DataFrame(data)

# ✅ Optimize Memory Usage for Large Data
df["City"] = df["City"].astype("category")
df["PremiseType"] = df["PremiseType"].astype("category")

# ✅ Step 1: Extract Location DataFrame (Unique Locations)
location_df = df[["LocationID", "Address", "City"]].drop_duplicates().set_index("LocationID")  # Indexing for fast joins
print("\n✅ Location DataFrame:\n", location_df)

# ✅ Step 2: Extract Premises DataFrame (Replacing Address with LocationID)
premises_df = df[["LocationID", "PremiseType"]].drop_duplicates()
premises_df["PremiseID"] = range(101, 101 + len(premises_df))  # Assign unique PremiseIDs
premises_df.set_index("PremiseID", inplace=True)  # Index for efficient merging
print("\n✅ Premises DataFrame:\n", premises_df)

# ✅ Step 3: Extract Lease DataFrame (Removing Address)
lease_df = df[["PremiseType", "LeaseStart", "LeaseEnd"]].drop_duplicates()
lease_df["LeaseID"] = range(201, 201 + len(lease_df))

# Link to PremiseID
lease_df = lease_df.merge(premises_df[["LocationID"]], left_on="PremiseType", right_on="PremiseType", how="left")
lease_df.set_index("LeaseID", inplace=True)
print("\n✅ Lease DataFrame:\n", lease_df)

# ✅ Step 4: Extract Term DataFrame (Removing LeaseStart & LeaseEnd)
term_df = df[["TermStart", "TermEnd", "Rent"]].drop_duplicates()
term_df["TermID"] = range(301, 301 + len(term_df))

# Link to LeaseID
term_df = term_df.merge(lease_df[["LeaseID"]], left_on=["TermStart", "TermEnd"], right_on=["LeaseStart", "LeaseEnd"], how="left")
term_df.set_index("TermID", inplace=True)
print("\n✅ Term DataFrame:\n", term_df)

# ✅ Final Memory Optimizations for Large Data
print("\n🚀 Memory Usage Summary:")
print("Location:", location_df.memory_usage(deep=True).sum(), "bytes")
print("Premises:", premises_df.memory_usage(deep=True).sum(), "bytes")
print("Lease:", lease_df.memory_usage(deep=True).sum(), "bytes")
print("Term:", term_df.memory_usage(deep=True).sum(), "bytes")
