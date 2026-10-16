import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Sklearn libraries
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    accuracy_score,
    log_loss,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# ============================================================
# 1. Load Dataset & Initial Inspection
# ============================================================

data = pd.read_csv('/Users/somya/Desktop/CA2 project ML/bechdel_pudding_dataset.csv')
print("Dataset Shape:", data.shape)

print("\nDataFrame Info:")
data.info()

print("\nSummary Statistics:\n", data.describe())
print("\nFirst 5 rows:\n", data.head())
print("\nLast 5 rows:\n", data.tail())
print("\nMissing Values Before Cleaning:\n", data.isna().sum())

# ============================================================
# 2. Data Cleaning & Preprocessing
# ============================================================

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

# ---------------- Objective 2 (Graph 2) ----------------
# Track historical evolution of female dialogue share by decade

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
# Correlation matrix between dialogue features and Bechdel outcome

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

scaler = MinMaxScaler()
scale_features = ["words_female", "words_male", "num_female_chars", "num_male_chars"]
data[scale_features] = scaler.fit_transform(data[scale_features])
print("\nNormalized Features Summary:\n", data[scale_features].describe())

# ---------------- Objective 5 (Graph 5) ----------------
# Supervised Regression Modeling (Simple, Multiple OLS, Polynomial)

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

# Polynomial Regression (Degree 2)
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly_train = poly.fit_transform(X_mult_train)
X_poly_test = poly.transform(X_mult_test)

poly_lr = LinearRegression()
poly_lr.fit(X_poly_train, y_reg_train)
y_pred_poly = poly_lr.predict(X_poly_test)

def evaluate_regression(y_true, y_pred, name):
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    return {"Model": name, "MAE": mae, "MSE": mse, "RMSE": rmse, "R2_Score": r2}

reg_results = [
    evaluate_regression(y_reg_test, y_pred_simple, "Simple Linear Regression"),
    evaluate_regression(y_reg_test, y_pred_multi, "Multiple Linear Regression (OLS)"),
    evaluate_regression(y_reg_test, y_pred_poly, "Polynomial Regression (Degree 2)")
]

reg_df = pd.DataFrame(reg_results)
print("\n--- Regression Models Performance Comparison ---")
print(reg_df.to_string(index=False))

plt.figure(figsize=(10, 5))
plt.scatter(y_reg_test, y_pred_poly, color="purple", alpha=0.6, label="Polynomial Reg Predictions")
plt.plot([y_reg_test.min(), y_reg_test.max()], [y_reg_test.min(), y_reg_test.max()],
         color="red", linestyle="--", linewidth=2, label="Ideal Fit Line")
plt.xlabel("Actual Female Dialogue %")
plt.ylabel("Predicted Female Dialogue %")
plt.title(f"Objective 5: Regression Evaluation — Actual vs. Predicted (R² = {reg_df.loc[2, 'R2_Score']:.3f})")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ---------------- Objective 6 (Graph 6) ----------------
# Supervised Classification & Best-Fit Model Selection

X_clf = data[["female_dialogue_pct", "words_female", "words_male", "num_female_chars", "num_male_chars"]]
y_clf = data["pass_bechdel"]

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
    X_clf, y_clf, test_size=0.2, random_state=42, stratify=y_clf
)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "k-Nearest Neighbors (k-NN)": KNeighborsClassifier(n_neighbors=7),
    "Naïve Bayes": GaussianNB(),
    "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=42),
    "Support Vector Machine (SVM)": SVC(probability=True, kernel="rbf", random_state=42)
}

clf_metrics_list = []
trained_models = {}
predictions_dict = {}

for name, clf in models.items():
    clf.fit(X_train_c, y_train_c)
    trained_models[name] = clf
    
    y_pred = clf.predict(X_test_c)
    y_prob = clf.predict_proba(X_test_c)[:, 1]
    
    predictions_dict[name] = y_pred
    
    acc = accuracy_score(y_test_c, y_pred)
    loss = log_loss(y_test_c, y_prob)
    auc = roc_auc_score(y_test_c, y_prob)
    prec = precision_score(y_test_c, y_pred)
    rec = recall_score(y_test_c, y_pred)
    f1 = f1_score(y_test_c, y_pred)
    
    clf_metrics_list.append({
        "Model": name,
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1_Score": f1,
        "ROC_AUC": auc,
        "Log_Loss": loss
    })

clf_summary_df = pd.DataFrame(clf_metrics_list).sort_values(by="F1_Score", ascending=False)
print("\n--- Classification Models Performance Comparison ---")
print(clf_summary_df.to_string(index=False))

best_model_name = clf_summary_df.iloc[0]["Model"]
best_pred = predictions_dict[best_model_name]
print(f"\nBest-Fit Champion Model: {best_model_name}")
print("\nConfusion Matrix for Best Model:\n", confusion_matrix(y_test_c, best_pred))
print("\nClassification Report:\n", classification_report(y_test_c, best_pred, target_names=["Fail (0)", "Pass (1)"]))

# Graph 6: Model Comparison Chart across Accuracy & F1-Score
plt.figure(figsize=(11, 5))
x_indices = np.arange(len(clf_summary_df))
bar_width = 0.35

plt.bar(x_indices - bar_width/2, clf_summary_df["Accuracy"], width=bar_width,
        label="Accuracy", color="steelblue", edgecolor="black")
plt.bar(x_indices + bar_width/2, clf_summary_df["F1_Score"], width=bar_width,
        label="F1 Score", color="darkorange", edgecolor="black")

plt.xticks(x_indices, clf_summary_df["Model"], rotation=15, ha='right')
plt.ylabel("Score")
plt.ylim(0.5, 0.85)
plt.title(f"Objective 6: Model Performance Benchmark (Champion: {best_model_name})")
plt.legend()
plt.tight_layout()
plt.show()

print("\nAnalysis execution finished successfully.")
