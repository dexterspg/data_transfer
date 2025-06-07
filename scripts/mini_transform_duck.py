
import pandas as pd
import duckdb

# ─── 1) Sample Pandas DataFrame (~15 000 rows) ───────────────────
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

# ─── 2) Spin up DuckDB & register your DataFrame ────────────────
conn = duckdb.connect(":memory:")
conn.register("raw", df)

# ─── 3) Extract each “table” in SQL and persist it in DuckDB ────

# 3a) Unique locations
conn.execute("""
CREATE TABLE locations AS
SELECT DISTINCT
    LocationID,
    Address,
    City
FROM raw
""")

# 3b) Premises: unique (LocationID, PremiseType) + assign PremiseID offset 100
conn.execute("""
CREATE TABLE premises AS
SELECT
    row_number() OVER (ORDER BY LocationID, PremiseType) + 100 AS PremiseID,
    LocationID,
    PremiseType
FROM (
  SELECT DISTINCT LocationID, PremiseType
  FROM raw
) t
""")

# 3c) Leases: unique (PremiseType, LeaseStart, LeaseEnd) + join to premises + LeaseID offset 200
conn.execute("""
CREATE TABLE leases AS
SELECT
    row_number() OVER (ORDER BY l.PremiseType, l.LeaseStart, l.LeaseEnd) + 200 AS LeaseID,
    p.PremiseID,
    l.PremiseType,
    l.LeaseStart,
    l.LeaseEnd,
    p.LocationID
FROM (
  SELECT DISTINCT PremiseType, LeaseStart, LeaseEnd
  FROM raw
) l
LEFT JOIN premises p
  ON l.PremiseType = p.PremiseType
""")

# 3d) Terms: unique (TermStart, TermEnd, Rent) + join to leases + TermID offset 300
conn.execute("""
CREATE TABLE terms AS
SELECT
    row_number() OVER (ORDER BY t.TermStart, t.TermEnd, t.Rent) + 300 AS TermID,
    t.TermStart,
    t.TermEnd,
    t.Rent,
    le.LeaseID
FROM (
  SELECT DISTINCT TermStart, TermEnd, Rent
  FROM raw
) t
LEFT JOIN leases le
  ON t.TermStart = le.LeaseStart
 AND t.TermEnd   = le.LeaseEnd
""")

# ─── 4) Pull back into pandas (and set indices) ────────────────
location_df = conn.execute("SELECT * FROM locations").fetchdf().set_index("LocationID")
premises_df = conn.execute("SELECT * FROM premises").fetchdf().set_index("PremiseID")
lease_df    = conn.execute("SELECT * FROM leases").fetchdf().set_index("LeaseID")
term_df     = conn.execute("SELECT * FROM terms").fetchdf().set_index("TermID")

# ─── 5) (Optional) Optimize pandas categories as before ─────────
location_df["City"]        = location_df["City"].astype("category")
premises_df["PremiseType"] = premises_df["PremiseType"].astype("category")

# ─── 6) Memory Usage Summary ───────────────────────────────────
print("\n🚀 Memory Usage Summary (bytes):")
print("locations:", location_df.memory_usage(deep=True).sum())
print("premises:", premises_df.memory_usage(deep=True).sum())
print("leases:   ", lease_df.memory_usage(deep=True).sum())
print("terms:    ", term_df.memory_usage(deep=True).sum())

# ─── 7) Inspect the results ────────────────────────────────────
print("\n✅ location_df:\n", location_df)
print("\n✅ premises_df:\n", premises_df)
print("\n✅ lease_df:\n", lease_df)
print("\n✅ term_df:\n", term_df)
