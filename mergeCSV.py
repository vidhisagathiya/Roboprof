import pandas as pd
import numpy as np

# Read the files into two dataframes.
# cleaned this file for one data which was on the same cell "JMSB_1"
df1 = pd.read_csv('CATALOG_2023_09_19.csv')
#converted this file from utf-16 to utf-8
df2 = pd.read_csv('CU_SR_OPEN_DATA_CATALOG_UTF8.csv')

classUnits = df2['Class Units']

# Add the extracted column into CSV2 DataFrame
# #df1 did not have any course credit column. Used df2 to extract that column
df1['Class Units'] = classUnits

for col in df1.columns:
    if df1[col].dtype == 'object':
        df1[col] = df1[col].str.strip()
        df1[col].replace('', np.nan, inplace=True)

# remove empty course codes and course names
df1 = df1.dropna(subset=['Course code', 'Course number'])

df1.loc[1249,'Course code'] = "COMP"
print(df1.loc[1249])

# Write the modified CSV2 DataFrame back to a new CSV file
df1.to_csv('CLEANED_DATA.csv', index=False)