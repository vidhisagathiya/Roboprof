import pandas as pd
import numpy as np
import os

# Get the directory of the current script (main.py)
current_directory = os.path.dirname(__file__)

# Construct the relative path to the CSV file
relative_path_to_csv1 = os.path.join("..", "Dataset", "CATALOG_2023_09_19.csv")
relative_path_to_csv2 = os.path.join("..", "Dataset", "CU_SR_OPEN_DATA_CATALOG_UTF8.csv")
relative_path_to_save = os.path.join("..", "Dataset","CLEANED_DATA.csv")

# Construct the absolute path
absolute_path_to_csv1 = os.path.abspath(os.path.join(current_directory, relative_path_to_csv1))
absolute_path_to_csv2 = os.path.abspath(os.path.join(current_directory, relative_path_to_csv2))
absolute_path_to_save = os.path.abspath(os.path.join(current_directory, relative_path_to_save))

# Read the files into two dataframes.
df1 = pd.read_csv(absolute_path_to_csv1)
#converted this file from utf-16 to utf-8
df2 = pd.read_csv(absolute_path_to_csv2)

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

# Write the modified CSV2 DataFrame back to a new CSV file
df1.to_csv(absolute_path_to_save)