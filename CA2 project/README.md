# CA2 Project: Predictive Analytics & Gender Representation

This folder contains the complete project packaged in a **single Python script** (`bechdel_analysis.py`) and a **standalone CSV dataset** (`bechdel_dataset.csv`), structured for simple execution in **VS Code** or **Python IDLE**.

---

## 📁 Files in This Folder

1. **`bechdel_dataset.csv`**:
   - The consolidated dataset (404 movies, 21 columns) containing movie metadata (year, decade, genre, runtime, budget, IMDb score) and conversational dialogue metrics (female dialogue lines, female-female conversation count, male-talk scores, Bechdel pass/fail label).

2. **`bechdel_analysis.py`**:
   - The single-file Python script executing the complete end-to-end predictive pipeline from scratch.

---

## 🚀 How to Run

### Method 1: In Python IDLE
1. Open **Python IDLE**.
2. Go to **File -> Open...** and select `bechdel_analysis.py` inside the `CA2 project` folder.
3. Press **F5** (or click **Run -> Run Module**).
4. The output and statistical summaries will print in the Python Shell, and the Matplotlib chart windows will display sequentially. Close each chart window to view the next step.

### Method 2: In VS Code
1. Open VS Code.
2. Open the `CA2 project` folder (or the `bechdel-detector` folder).
3. Open `bechdel_analysis.py`.
4. Click the **Run Python File** button (play icon in the top-right corner) or run in the terminal:
   ```bash
   python bechdel_analysis.py
   ```

---

## 📊 Pipeline Flow (Step-by-Step)

1. **Data Loading & Inspection**:
   - Loads `bechdel_dataset.csv`
   - Prints `data.info()`, `data.describe()`, `data.head()`, `data.tail()`, and checks for missing values with `data.isna().sum()`.
2. **Data Cleaning**:
   - Imputes missing production budgets using median values.
3. **Objective 1 (Historical Trends)**:
   - Line chart showing Bechdel test pass rate per release decade.
4. **Objective 2 (Genre Analysis)**:
   - Bar chart comparing pass rates across film genres (Fantasy, Horror, Comedy, Action, etc.).
5. **Objective 3 (Distribution Analysis)**:
   - Histogram and KDE of female dialogue share across all screenplays.
6. **Objective 4 (Bivariate Scatter Plot)**:
   - Scatter plot showing relationship between female character share and female dialogue share.
7. **Objective 5 (Correlation Heatmap)**:
   - Seaborn heatmap showing correlations across 9 film parameters.
8. **Objective 6 (Outlier Detection & Removal)**:
   - Boxplots before and after IQR outlier filtering on runtime and dialogue line metrics.
9. **Objective 7 (Group Comparison)**:
   - Bar chart comparing average dialogue lines spoken by women in failing vs. passing films.
10. **Normalization**:
    - Features scaled between 0 and 1 using `MinMaxScaler`.
11. **Machine Learning Task 1: Linear Regression**:
    - Predicts continuous female dialogue share.
    - Evaluates using Mean Squared Error (MSE), Mean Absolute Error (MAE), and $R^2$ score.
    - Plots Actual vs. Predicted values with the ideal fit line.
12. **Machine Learning Task 2: Classification (Logistic Regression)**:
    - Predicts whether a film passes (1) or fails (0) the Bechdel test.
    - Outputs prediction and probability for a sample film.
    - Evaluates using Accuracy, Precision, Recall, and F1 score.
    - Plots the Confusion Matrix heatmap.
