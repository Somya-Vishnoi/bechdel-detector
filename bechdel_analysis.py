import pandas as pd

# Load Dataset
data = pd.read_csv('bechdel_pudding_dataset.csv')
print("Dataset Shape:", data.shape)

print("\nFirst 5 rows:")
print(data.head())
