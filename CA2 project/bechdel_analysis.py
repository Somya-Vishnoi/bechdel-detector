import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Import Sklearn Library (for ML)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Load the dataset from csv file
csv_filename = "bechdel_dataset.csv"
if os.path.exists(csv_filename):
    data_path = csv_filename
else:
    data_path = os.path.join(os.path.dirname(__file__), csv_filename)

data = pd.read_csv(data_path)
print("=== Bechdel Test Dataset ===")
print(data)

# Display concise summary of the data
print("\nDataFrame Info:")
print(data.info())

# Display descriptive statistics to understand the data
print("\nSummary Statistics:\n", data.describe())

# Display top and bottom rows of the dataset for initial glance
print("\nFirst 5 Rows:")
print(data.head())
print("\nLast 5 Rows:")
print(data.tail())

# Identify the NAs or null values in the data
print("\nMissing Values Count (Before Cleaning):")
print(data.isna().sum())

# Handles NA's in the data
data["budget"] = data["budget"].fillna(data["budget"].median())
data["runtime"] = data["runtime"].fillna(data["runtime"].mean())
print("\nMissing Values Count (After Cleaning):")
print(data.isna().sum())

# ---------------- Objective 1 ----------------
# Find average Bechdel pass rate per decade

decade_pass = data.groupby("decade")["pass_bechdel"].mean() * 100
print("\n--- Objective 1: Average Pass Rate (%) Per Decade ---")
print(decade_pass)

# Line Chart
plt.figure(figsize=(10, 5))
decade_pass.plot(kind="line", marker="o", color="royalblue", linewidth=2.5, markersize=8)
plt.title("Historical Trend of Bechdel Test Pass Rate (by Decade)")
plt.xlabel("Release Decade")
plt.ylabel("Pass Rate (%)")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()

# ---------------- Objective 2 ----------------
# Identify the genres with the highest and lowest representation

# CLEAN DATA FIRST
print("\nBefore cleaning genre data:")
print(data[["genre", "pass_bechdel"]].isna().sum())

data = data.dropna(subset=["genre", "pass_bechdel"])

print("After cleaning genre data:")
print(data[["genre", "pass_bechdel"]].isna().sum())

# THEN group
genre_pass = (
    data.groupby("genre")["pass_bechdel"]
    .mean() * 100
).sort_values(ascending=False)

print("\n--- Objective 2: Pass Rate (%) by Genre ---")
print(genre_pass)

# Bar Chart
plt.figure(figsize=(12, 6))
genre_pass.plot(kind="bar", color="coral")
plt.title("Bechdel Test Pass Rate Across Film Genres")
plt.xlabel("Genre")
plt.ylabel("Pass Rate (%)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

# ---------------- Objective 3 ----------------
# Visualize the distribution of female dialogue share across all films

plt.figure(figsize=(10, 5))
sns.histplot(data["female_line_share"], bins=20, kde=True, color="purple")
plt.xlabel("Female Dialogue Share (0.0 to 1.0)")
plt.ylabel("Frequency")
plt.title("Distribution of Female Dialogue Share Across Films")
plt.tight_layout()
plt.show()

# ---------------- Objective 4 ----------------
# Analyze the relationship between female character share and female dialogue share

plt.figure(figsize=(10, 5))
plt.scatter(data["female_char_share"], data["female_line_share"], color="teal", alpha=0.7, edgecolors="black")
plt.xlabel("Female Character Share")
plt.ylabel("Female Dialogue Share")
plt.title("Relationship Between Female Character Share and Dialogue Share")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()

# ---------------- Objective 5 ----------------
# Correlation heatmap between different cinematic and dialogue parameters

corr_cols = [
    "imdb_rating",
    "runtime",
    "num_female_chars",
    "num_male_chars",
    "female_char_share",
    "female_line_share",
    "num_ff_conversations",
    "male_talk_score",
    "pass_bechdel",
]

plt.figure(figsize=(10, 7))
sns.heatmap(data[corr_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Correlation Matrix of Movie & Dialogue Features")
plt.tight_layout()
plt.show()

# ---------------- Objective 6 ----------------
# Detect outliers in dialogue and runtime data

outlier_cols = ["runtime", "total_lines_count", "longest_ff_exchange"]

plt.figure(figsize=(10, 5))
sns.boxplot(data=data[outlier_cols], palette="Set2")
plt.xlabel("Film Parameters")
plt.ylabel("Values")
plt.title("Outlier Detection in Film Features")
plt.tight_layout()
plt.show()

# ---------------- Outlier Removal (Fixed) ----------------

condition = pd.Series(True, index=data.index)

for col in outlier_cols:
    Q1 = data[col].quantile(0.25)
    Q3 = data[col].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    condition &= (data[col] >= lower) & (data[col] <= upper)

# Apply filter
data = data[condition]
print("\nOutliers removed correctly from columns:", outlier_cols)
print("Remaining rows after outlier removal:", len(data))

# ---------------- Objective 6 (After) ----------------
# Visualize data after removing outliers

plt.figure(figsize=(10, 5))
sns.boxplot(data=data[outlier_cols], palette="Set2")
plt.xlabel("Film Parameters")
plt.ylabel("Values")
plt.title("Outlier Detection After Removing Outliers")
plt.tight_layout()
plt.show()

# ---------------- Objective 7 ----------------
# Compare average female lines count across pass vs fail films
# Bar Chart

plt.figure(figsize=(8, 5))
avg_lines = data.groupby("pass_bechdel")["female_lines_count"].mean()
avg_lines.plot(kind="bar", color=["#ff9999", "#66b3ff"])
plt.xlabel("Bechdel Outcome")
plt.ylabel("Average Female Dialogue Lines")
plt.title("Average Female Dialogue Lines: Failing vs Passing Films")
plt.xticks([0, 1], ["Failing Films (0)", "Passing Films (1)"], rotation=0)
plt.tight_layout()
plt.show()

# ---------------- Normalization ----------------
# Scaling the features so that all values are in the same range (0 to 1)

scaler = MinMaxScaler()
data[["num_female_chars_norm", "female_char_share_norm"]] = scaler.fit_transform(
    data[["num_female_chars", "female_char_share"]]
)

print("\nAfter Normalization:")
print(data[["num_female_chars_norm", "female_char_share_norm"]].describe())

# ---------------- Scatter Plot ----------------
# Visualizing relationship between normalized female char share and female dialogue share

plt.figure(figsize=(8, 4))
plt.scatter(data["female_char_share_norm"], data["female_line_share"], color="darkorange", alpha=0.7)
plt.title("Scatter Plot: Normalized Female Char Share vs Dialogue Share")
plt.xlabel("Normalized Female Character Share")
plt.ylabel("Female Dialogue Share")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()

# ---------------- Linear Regression Model (Task 1) ----------------
# Using cast and character metrics to predict continuous female_line_share

features_reg = [
    "num_female_chars",
    "female_char_share",
    "num_male_chars",
    "director_female_presence",
]
x_reg = data[features_reg]
y_reg = data["female_line_share"]

# Splitting data into training and testing sets
x_train_reg, x_test_reg, y_train_reg, y_test_reg = train_test_split(
    x_reg, y_reg, test_size=0.2, random_state=42
)

# Training the model
model_reg = LinearRegression()
model_reg.fit(x_train_reg, y_train_reg)

# ---------------- Prediction ----------------
# Predicting for a sample film: 3 female chars, 40% female share, 4 male chars, female director (1)
sample_reg = pd.DataFrame(
    {
        "num_female_chars": [3],
        "female_char_share": [0.428],
        "num_male_chars": [4],
        "director_female_presence": [1],
    }
)
result_reg = model_reg.predict(sample_reg)
print(f"\n--- Linear Regression Prediction ---")
print(f"Predicted Female Dialogue Share for Sample Film: {result_reg[0]:.4f} ({result_reg[0]*100:.1f}%)")

# ---------------- Model Evaluation (Regression) ----------------
# Checking regression performance
y_pred_reg = model_reg.predict(x_test_reg)

# Visualizing Actual vs Predicted values
plt.figure(figsize=(8, 5))
plt.scatter(y_test_reg, y_pred_reg, color="royalblue", alpha=0.7)
# Perfect prediction line
plt.plot(
    [y_test_reg.min(), y_test_reg.max()],
    [y_test_reg.min(), y_test_reg.max()],
    color="red",
    linewidth=2,
)
plt.xlabel("Actual Dialogue Share")
plt.ylabel("Predicted Dialogue Share")
plt.title("Actual vs Predicted Dialogue Share (Linear Regression)")
plt.tight_layout()
plt.show()

# Mean Squared Error
mse = mean_squared_error(y_test_reg, y_pred_reg)
print(f"Mean Squared Error (MSE): {mse:.4f}")

# R-Square Score (Goodness of Fit)
r2 = r2_score(y_test_reg, y_pred_reg)
print(f"R-Square Score (R2): {r2:.4f}")

# Mean Absolute Error
mae = mean_absolute_error(y_test_reg, y_pred_reg)
print(f"Mean Absolute Error (MAE): {mae:.4f}")

# ---------------- Classification Model (Task 2) ----------------
# Predicting whether a film passes (1) or fails (0) the Bechdel Test

features_clf = [
    "female_char_share",
    "female_line_share",
    "num_ff_conversations",
    "longest_ff_exchange",
    "male_talk_score",
    "director_female_presence",
]
x_clf = data[features_clf]
y_clf = data["pass_bechdel"]

# Splitting data into training and testing sets
x_train_clf, x_test_clf, y_train_clf, y_test_clf = train_test_split(
    x_clf, y_clf, test_size=0.2, random_state=42, stratify=y_clf
)

# Training the model
model_clf = LogisticRegression(max_iter=1000)
model_clf.fit(x_train_clf, y_train_clf)

# ---------------- Prediction (Classification) ----------------
# Sample film: 50% female share, 45% line share, 4 F-F convos, longest exchange 8, male talk score 0.05, female director 1
sample_clf = pd.DataFrame(
    {
        "female_char_share": [0.50],
        "female_line_share": [0.45],
        "num_ff_conversations": [4],
        "longest_ff_exchange": [8],
        "male_talk_score": [0.05],
        "director_female_presence": [1],
    }
)
clf_result = model_clf.predict(sample_clf)
clf_prob = model_clf.predict_proba(sample_clf)[0][1]

print(f"\n--- Classification Prediction ---")
print(f"Predicted Bechdel Outcome: {'PASS (1)' if clf_result[0] == 1 else 'FAIL (0)'}")
print(f"Predicted Probability of Passing: {clf_prob * 100:.2f}%")

# ---------------- Model Evaluation (Classification) ----------------
# Checking classification performance
y_pred_clf = model_clf.predict(x_test_clf)

acc = accuracy_score(y_test_clf, y_pred_clf)
prec = precision_score(y_test_clf, y_pred_clf)
rec = recall_score(y_test_clf, y_pred_clf)
f1 = f1_score(y_test_clf, y_pred_clf)

print("\n--- Classification Evaluation Metrics ---")
print(f"Accuracy:  {acc * 100:.2f}%")
print(f"Precision: {prec * 100:.2f}%")
print(f"Recall:    {rec * 100:.2f}%")
print(f"F1 Score:  {f1:.4f}")

# ---------------- Model Visualization (Confusion Matrix) ----------------
cm = confusion_matrix(y_test_clf, y_pred_clf)

plt.figure(figsize=(6, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    cbar=False,
    xticklabels=["Predicted Fail (0)", "Predicted Pass (1)"],
    yticklabels=["Actual Fail (0)", "Actual Pass (1)"],
)
plt.title("Confusion Matrix (Bechdel Test Classification)")
plt.ylabel("Actual Label")
plt.xlabel("Predicted Label")
plt.tight_layout()
plt.show()

print("\n=== Project Execution Completed Successfully ===")
