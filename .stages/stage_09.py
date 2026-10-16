import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# ---------------- Objective 2 (Graph 2) ----------------
decade_trend = data.groupby("decade")["female_dialogue_pct"].mean().reset_index()
print("\nAverage Female Dialogue % by Decade:\n", decade_trend)

plt.figure(figsize=(10, 5))
plt.plot(decade_trend["decade"], decade_trend["female_dialogue_pct"],
         marker="o", color="purple", linewidth=2.5, markersize=7)
plt.fill_between(decade_trend["decade"], decade_trend["female_dialogue_pct"], alpha=0.15, color="purple")
plt.xlabel("Decade")
plt.ylabel("Average Female Dialogue (%)")
plt.title("Objective 2: Historical Evolution of Female Dialogue Share (Decade-wise)")
plt.grid(True, linestyle="--", alpha=0.6)
plt.xticks(decade_trend["decade"], rotation=45)
plt.tight_layout()
plt.show()

# ---------------- Objective 3 (Graph 3) ----------------
corr_cols = ["words_female", "words_male", "female_dialogue_pct",
             "num_female_chars", "num_male_chars", "bechdel_rating", "pass_bechdel"]
print("\nCorrelation Matrix:\n", data[corr_cols].corr())

plt.figure(figsize=(9, 6))
sns.heatmap(data[corr_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Objective 3: Correlation Matrix of Dialogue Parameters & Bechdel Test")
plt.tight_layout()
plt.show()

# ---------------- Objective 4 (Graph 4) ----------------
# Outlier detection and filtering using Interquartile Range (IQR)

outlier_cols = ["words_female", "words_male", "female_dialogue_pct"]

condition = pd.Series(True, index=data.index)
for col in outlier_cols:
    Q1 = data[col].quantile(0.25)
    Q3 = data[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    condition &= (data[col] >= lower_bound) & (data[col] <= upper_bound)

data = data[condition].reset_index(drop=True)
print(f"\nDataset size after IQR outlier filtering: {len(data)} rows")

plt.figure(figsize=(10, 5))
sns.boxplot(data=data[outlier_cols], palette="Set2")
plt.title("Objective 4: Outlier Detection & Cleaned Distribution in Dialogue Metrics")
plt.tight_layout()
plt.show()

# ============================================================
# 3. Normalization (MinMaxScaler)
# ============================================================

from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
scale_features = ["words_female", "words_male", "num_female_chars", "num_male_chars"]
data[scale_features] = scaler.fit_transform(data[scale_features])
print("\nNormalized Features Summary:\n", data[scale_features].describe())

# ---------------- Objective 5 (Regression Baselines) ----------------
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

y_reg = data["female_dialogue_pct"]
train_idx, test_idx = train_test_split(data.index, test_size=0.2, random_state=42)

# Simple Linear Regression
X_simple_train = data.loc[train_idx, [scale_features[0]]]
X_simple_test = data.loc[test_idx, [scale_features[0]]]
y_reg_train = y_reg.loc[train_idx]
y_reg_test = y_reg.loc[test_idx]

simple_lr = LinearRegression()
simple_lr.fit(X_simple_train, y_reg_train)
y_pred_simple = simple_lr.predict(X_simple_test)

# Multiple Linear Regression (OLS)
X_mult_train = data.loc[train_idx, scale_features]
X_mult_test = data.loc[test_idx, scale_features]

multi_lr = LinearRegression()
multi_lr.fit(X_mult_train, y_reg_train)
y_pred_multi = multi_lr.predict(X_mult_test)

print("\nSimple Linear Regression R2:", r2_score(y_reg_test, y_pred_simple))
print("Multiple Linear Regression R2:", r2_score(y_reg_test, y_pred_multi))
