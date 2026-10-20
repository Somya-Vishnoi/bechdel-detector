import pandas as pd
import matplotlib.pyplot as plt

# 1. Load Dataset
data = pd.read_csv('bechdel_pudding_dataset.csv')
print("Dataset Shape:", data.shape)

print("\nDataFrame Info:")
data.info()

print("\nSummary Statistics:\n", data.describe())
print("\nFirst 5 rows:\n", data.head())
print("\nLast 5 rows:\n", data.tail())
print("\nMissing Values Before Cleaning:\n", data.isna().sum())

# 2. Data Cleaning & Preprocessing
data["gross"] = data["gross"].fillna(data["gross"].mean())
data["words_female"] = data["words_female"].fillna(data["words_female"].mean())
data["words_male"] = data["words_male"].fillna(data["words_male"].mean())
data["female_dialogue_pct"] = data["female_dialogue_pct"].fillna(data["female_dialogue_pct"].mean())
data["num_female_chars"] = data["num_female_chars"].fillna(data["num_female_chars"].mean())
data["num_male_chars"] = data["num_male_chars"].fillna(data["num_male_chars"].mean())

print("\nMissing Values After Cleaning:\n", data.isna().sum())

# Decade extraction
data["decade"] = (data["year"] // 10 * 10).astype(int)

# ---------------- Objective 1 (Graph 1) ----------------
# Analyze average female dialogue percentage across Bechdel ratings

rating_group = data.groupby("bechdel_rating")["female_dialogue_pct"].mean().reset_index()
rating_group["bechdel_rating"] = rating_group["bechdel_rating"].astype(str)
print("\nAvg Female Dialogue % by Bechdel Rating:\n", rating_group)

plt.figure(figsize=(9, 5))
bars = plt.bar(rating_group["bechdel_rating"], rating_group["female_dialogue_pct"],
               color=["#d62728", "#ff7f0e", "#2ca02c", "#1f77b4"], edgecolor="black")
plt.xlabel("Bechdel Rating (0 = Fail, 3 = Pass)")
plt.ylabel("Average Female Dialogue (%)")
plt.title("Objective 1: Female Dialogue Share Across Bechdel Rating Categories")
for bar in bars:
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6,
             f"{bar.get_height():.1f}%", ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.show()
