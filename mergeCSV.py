import pandas as pd
import numpy as np

# Read the files into two dataframes.
df1 = pd.read_csv('CATALOG_2023_09_19.csv')
df2 = pd.read_csv('CU_SR_OPEN_DATA_CATALOG_UTF8.csv')

classUnits = df2['Class Units']

# Add the extracted column into CSV2 DataFrame
df1['Class Units'] = classUnits
print(df1.columns)

for col in df1.columns:
    if df1[col].dtype == 'object':
        df1[col] = df1[col].str.strip()
        df1[col].replace('', np.nan, inplace=True)

# remove empty course codes and course names
df1 = df1.dropna(subset=['Course code', 'Course number'])

# Write the modified CSV2 DataFrame back to a new CSV file
df1.to_csv('CLEANED_DATA.csv', index=False)