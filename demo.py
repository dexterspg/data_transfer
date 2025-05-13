import pandas as pd
from sheet_utils import SheetUtils

# Define the dataset
data = {
    "LocationId": [
        "046611", "046606", "046324", "046595", "AUSBRI004", "AUSADE002", "AUSSYD007",
        "AUSHOB002", "AUSSYD006", "BELDIEM001", "CHNSHA001", "BOGOTA0001", "046528",
        "046572", "CZEPRA001"
    ],
    "LegalEntityId": [
        "BJSS Ltd", "CGI Technologies and Solutions Inc.", "CGI Inc.", "BJSS Australia Pty Ltd",
        "CGI ISMC (Australia) Pty Ltd.", "CGI Technologies and Solutions Australia Pty Limited",
        "CGI Technologies and Solutions Australia Pty Limited", "CGI Technologies and Solutions Australia Pty Limited",
        "CGI Technologies and Solutions Australia Pty Limited", "CGI Belgium NV", "CGI Federal Inc.",
        "CGI Colombia Ltda", "CGI IT Czech Republic s.r.o.", "CGI IT Czech Republic s.r.o.",
        "CGI IT Czech Republic s.r.o."
    ],
    "ErpSystemDisplayId": ["ErpSystem1"] * 15  # Repeating value for all rows
}

# Create the DataFrame
df = pd.DataFrame(data)

# Generate company table with auto-incremented company_id starting from 1000

# print(df[['LegalEntityId']])
# companies = df[['LegalEntityId']].drop_duplicates().reset_index(drop=True)
companies = SheetUtils.remove_duplicates_for_dataframe(df, 'LegalEntityId')
print(companies)
companies['company_id'] = range(1000, 1000 + len(companies))
print(companies)
# print("\n")
# print(df)
#
# # Merge to assign company_id to places
df = df.merge(companies, on='LegalEntityId', how='left')
# print("\n")
# print(df)
# Remove the old LegalEntityId and rename company_id to LegalEntityId
df = df.drop(columns=['LegalEntityId']).rename(columns={"company_id": "LegalEntityId"})

# Reorder columns based on the specified order
df = df[['LocationId', 'LegalEntityId', 'ErpSystemDisplayId']]

# Output results to console
print("=== Final Processed Data ===")
# print(df)

print("\n✅ Data processing completed!")#
