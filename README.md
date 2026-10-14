# Screenplay Dialogue & Gender Representation Analysis (Bechdel Test)

This repository contains an empirical machine learning project investigating dialogue share, gender parity, and Bechdel Test outcomes across film screenplays.

## Overview
The Bechdel Test is a metric for evaluating gender representation in fiction. To pass, a film must meet three criteria:
1. It has at least two named female characters.
2. Who talk to each other.
3. About something besides a man.

This project examines over 1,300 film screenplays combining dialogue metadata from *The Pudding* with certified Bechdel Test community ratings.

## Dataset
- `bechdel_pudding_dataset.csv`: Contains 1,346 film scripts with character-level dialogue metrics, including female dialogue percentage, male dialogue words, character counts, and Bechdel classification ratings.

## Research Objectives
- **Objective 1:** Female dialogue percentage distribution across Bechdel rating categories (0 to 3).
- **Objective 2:** Historical decade-wise evolution of female dialogue share in Hollywood.
- **Objective 3:** Correlation and collinearity analysis of screenplay dialogue parameters.
- **Objective 4:** Interquartile Range (IQR) outlier detection and distribution filtering.
- **Objective 5:** Supervised Regression modeling (Simple, Multiple OLS, and Polynomial Regression) predicting female dialogue share.
- **Objective 6:** Supervised Classification benchmark evaluating 5 models (Logistic Regression, k-NN, Naïve Bayes, Decision Trees, Support Vector Machines) to identify the best-fit classifier.

## Setup & Execution
Install the required dependencies:
```bash
pip install -r requirements.txt
```

Run the complete pipeline:
```bash
python bechdel_analysis.py
```
