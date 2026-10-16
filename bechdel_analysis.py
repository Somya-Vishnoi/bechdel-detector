import pandas as pd

# 1. Load Dataset
data = pd.read_csv('bechdel_pudding_dataset.csv')
print("Dataset Shape:", data.shape)

print("\nDataFrame Info:")
data.info()

print("\nSummary Statistics:\n", data.describe())

print("\nFirst 5 rows:\n", data.head())
print("\nLast 5 rows:\n", data.tail())

print("\nMissing Values:\n", data.isna().sum())
