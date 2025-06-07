import pandas as pd
import duckdb

data = {
    "LocationID": [1, 2, 3, 3, 4, 4],
    "Address": ["123 Main St", "456 Elm St", "789 Oak St", "789 Oak St", "123 Main St", "123 Main St"],
    "City": ["New York", "Los Angeles", "Chicago", "Chicago", "New York", "New York"],
    "PremiseType": ["Retail", "Office", "Warehouse", "Industrial", "Retail", "Office"],
    "LeaseStart": ["2023-01-01", "2023-05-01", "2022-07-01", "2023-08-01", "2023-03-01", "2024-06-01"],
    "LeaseEnd":   ["2025-01-01", "2025-05-01", "2024-07-01", "2025-08-01", "2026-03-01", "2027-06-01"],
    "TermStart":  ["2023-01-01", "2024-02-01", "2022-07-01", "2023-08-01", "2023-03-01", "2025-01-01"],
    "TermEnd":    ["2024-01-01", "2025-01-01", "2023-07-01", "2024-08-01", "2024-06-01", "2026-01-01"],
    "Rent":       [2000, 2500, 1800, 2200, 2400, 2600]
}
df = pd.DataFrame(data)
# ✅ Add an explicit `row_index` column
df["row_index"] = df.index  # Ensure original order is stored

# ✅ Spin up DuckDB and register DataFrame
conn = duckdb.connect(":memory:")
conn.register("raw", df)

# ✅ Ensure all tables maintain order & remove duplicates

conn.execute("""
CREATE TABLE locations AS
SELECT DISTINCT ON (LocationID, Address, City) 
    LocationID, Address, City, row_index 
FROM raw
ORDER BY LocationID, row_index;  -- ✅ Preserve Excel order
""")

conn.execute("""
CREATE TABLE premises AS
SELECT row_number() OVER (ORDER BY row_index) + 100 AS PremiseID, LocationID, PremiseType
FROM (
  SELECT DISTINCT ON (LocationID, PremiseType) 
    LocationID, PremiseType, row_index
  FROM raw
  ORDER BY row_index  -- ✅ Maintain original order after deduplication
) t
""")

conn.execute("""
CREATE TABLE leases AS
SELECT row_number() OVER (ORDER BY row_index) + 200 AS LeaseID, p.PremiseID, l.PremiseType, l.LeaseStart, l.LeaseEnd, p.LocationID
FROM (
  SELECT DISTINCT ON (PremiseType, LeaseStart, LeaseEnd) 
    PremiseType, LeaseStart, LeaseEnd, row_index
  FROM raw
  ORDER BY row_index  -- ✅ Deduplicate while keeping order
) l
LEFT JOIN premises p ON l.PremiseType = p.PremiseType
""")

conn.execute("""
CREATE TABLE terms AS
SELECT row_number() OVER (ORDER BY row_index) + 300 AS TermID, t.TermStart, t.TermEnd, t.Rent, le.LeaseID
FROM (
  SELECT DISTINCT ON (TermStart, TermEnd, Rent) 
    TermStart, TermEnd, Rent, row_index
  FROM raw
  ORDER BY row_index  -- ✅ Keep row sequence intact
) t
LEFT JOIN leases le ON t.TermStart = le.LeaseStart AND t.TermEnd = le.LeaseEnd
""")

# ✅ Retrieve results while maintaining order
location_df = conn.execute("SELECT * FROM locations ORDER BY row_index").fetchdf().set_index("LocationID")
premises_df = conn.execute("SELECT * FROM premises ORDER BY PremiseID").fetchdf().set_index("PremiseID")
lease_df    = conn.execute("SELECT * FROM leases ORDER BY LeaseID").fetchdf().set_index("LeaseID")
term_df     = conn.execute("SELECT * FROM terms ORDER BY TermID").fetchdf().set_index("TermID")

# ✅ Inspect results
print("\n✅ location_df:\n", location_df)
print("\n✅ premises_df:\n", premises_df)
print("\n✅ lease_df:\n", lease_df)
print("\n✅ term_df:\n", term_df)

