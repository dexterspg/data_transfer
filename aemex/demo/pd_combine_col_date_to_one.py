import pandas as pd

# Create a sample DataFrame with fiscal year and fiscal period
df = pd.DataFrame({
    'fiscal_year': [2024, 2024, 2023],
    'fiscal_period': [2, 10, 8]  # 2 => Feb, 10 => Oct, 8 => Aug
})

# Create a datetime column assuming the first day of the month
df['date'] = pd.to_datetime(
    df['fiscal_year'].astype(str) + '-' +
    df['fiscal_period'].astype(str) + '-01'
)

# Format the date to abbreviated month-year (e.g., 'feb-2024')
df['month_year'] = df['date'].dt.strftime('%b-%Y').str.lower()

# Prepend the desired text to create the final output format
df['transaction_info'] = 'transaction on ' + df['month_year']

print(df[['fiscal_year', 'fiscal_period', 'transaction_info']])
