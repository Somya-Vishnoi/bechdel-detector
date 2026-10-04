# Predicting Gender Representation in Cinema: An End-to-End Machine Learning Framework and Dialogue-Level Bechdel Test Detector

**Course Code:** INT234: Predictive Analytics  
**Academic Task:** Academic Task 2 Project Report  
**Candidate Name:** Somya Vishnoi  
**Registration Number:** 12318492  
**Institution:** Lovely Professional University, Phagwara, Punjab, India  
**School:** School of Computer Science & Engineering | Department of Analytics  
**Repository:** [https://github.com/Somya-Vishnoi/bechdel-detector](https://github.com/Somya-Vishnoi/bechdel-detector)  
**Date:** October 2026  

---

## Executive Abstract

This report documents the end-to-end design, implementation, and empirical evaluation of the **Bechdel Test Detector**, a production-grade predictive machine learning system and natural language processing rule engine developed to analyze gender representation in cinematic narratives. Grounded in Alison Bechdel's 1985 cultural benchmark, a film passes if and only if it contains at least two named female characters who converse with each other about a topic other than a man.

To address the limitations of crowd-sourced repositories, we introduce a **Two-Tier Architectural Framework**:
1. **Tier 1 (Macro Dataset):** 9,368 films spanning 1888 to 2019, enriched with TMDB crew and cast demographics to analyze macro-historical trajectories.
2. **Tier 2 (Matched Screenplays):** 404 matched feature screenplays from the Cornell Movie-Dialogs Corpus (304,446 dialogue lines across 83,097 conversational scenes).

We implement a 3-stage sequential rule detector that evaluates character presence, female-female scene existence, and pronoun/kinship male-talk scores. Tuning the decision threshold strictly on training split films ($\tau = 0.10$), the detector attains **74.01% accuracy**, **75.00% precision**, **66.84% recall**, **0.7062 F1 score**, and **Cohen's $\kappa = 0.4728$**.

In supervised machine learning experiments, seven classification algorithms were benchmarked across Stratified 5-Fold Cross-Validation and out-of-time Temporal Splits. Incorporating conversational dialogue features alongside metadata generated an immediate **+7.5% absolute gain in Precision-Recall AUC (0.7111 to 0.7858)**, proving that dialogue exchange topology provides orthogonal predictive signal beyond genre and production era. Permutation feature importance and SHAP analyses confirm that dialogue exchange frequency dominates behind-the-camera crew features. Formal hypothesis testing confirms a statistically significant longitudinal increase in representation ($\chi^2 = 232.69, p < 10^{-41}$) and a strong correlation between female dialogue share and test passage (Welch's $t = 10.03, p < 10^{-20}, d = 1.026$).

---

## Chapter 1: Introduction & Societal Problem Formulation

### 1.1 The Cultural Imperative of Gender Representation in Media
Cinematic storytelling functions as both a reflection of prevailing cultural norms and an active instrument of social learning. According to social cognitive theory, mass media models behavioral expectations, professional aspirations, and social hierarchies. When women are persistently excluded from screen narratives, confined to peripheral romantic roles, or depicted solely in relationship to male protagonists, societal stereotypes regarding female agency are reinforced. Over eight decades of modern cinema, quantitative media studies have repeatedly highlighted profound gender disparities: male speaking characters outnumber female speaking characters by more than two to one, female screenwriters and directors occupy fewer than 18% of key creative positions, and female characters receive a disproportionately minor fraction of total conversational lines.

Analyzing narrative media through automated computational methods is vital for evidence-based cultural auditing. Traditional content analysis relies on manual human coding, which is labor-intensive, difficult to scale across thousands of feature releases, and vulnerable to subjective coder bias. Predictive analytics and natural language processing provide an empirical framework to quantify gender representation at scale, allowing researchers to evaluate thousands of screenplays and identify structural industry patterns.

### 1.2 The Bechdel-Wallace Test as a Cultural Diagnostic Instrument
Originating in Alison Bechdel's 1985 comic strip *Dykes to Watch Out For* (credited to Bechdel's friend Liz Wallace and inspired by Virginia Woolf's 1929 essay *A Room of One's Own*), the **Bechdel-Wallace Test** establishes three deceptively minimalist criteria:
- **Criterion 1 (Stage A):** The movie must feature at least two named female characters.
- **Criterion 2 (Stage B):** These two women must talk to each other.
- **Criterion 3 (Stage C):** Their conversation must be about something other than a man.

Despite its deliberate structural simplicity, an astonishing fraction of commercial cinema fails this baseline audit. The test serves not as a comprehensive measure of cinematic feminist merit, but rather as an essential floor below which female agency is entirely erased.

### 1.3 Formal Problem Formulation
Let a screenplay be formalized as an ordered sequence of dialogue turns $D = (d_1, d_2, ..., d_N)$, where each turn $d_k = (s_k, l_k, t_k)$ contains a speaker identifier $s_k \in C$, a sequence of lexical tokens $l_k$, and a scene index $t_k$. Let each character $c \in C$ possess an assigned gender $g(c) \in \{\text{Female}, \text{Male}, \text{Unknown}\}$ and a character name string. The automated audit problem resolves into two distinct computational tasks:
1. **Deterministic Rule Detection:** Construct a deterministic mapping $f_{\text{rule}}(D, C) \to \{0, 1\}$ that evaluates whether there exists at least one contiguous conversational subsequence $S = (d_i, ..., d_j)$ between two distinct female speakers ($g(s_a) = g(s_b) = \text{Female}$) such that the proportion of male-referential lexical items satisfies $M(S) < \tau$.
2. **Supervised Predictive Modeling:** Learn a probabilistic mapping $f_{\text{ML}}(x) = P(Y = 1 | x)$ over a 54-dimensional feature vector $x \in \mathbb{R}^{54}$, predicting whether a film satisfies the Bechdel standard from production metadata, demographic mix, and conversational network metrics under a zero-leakage training protocol.

### 1.4 Research Questions
- **RQ1 (Macro Historical Trajectories):** Has female representation in mainstream cinema exhibited a statistically significant upward secular trend over the past century, or are gains confined to specific eras?
- **RQ2 (Value of Dialogue Topology):** Does the incorporation of dialogue-level conversational features yield a statistically measurable performance gain over production metadata alone when predicting Bechdel Test outcomes?
- **RQ3 (Algorithmic Fidelity):** Can a lightweight, rule-based natural language processing detector match human crowd annotations on full-length screenplays without requiring multi-billion parameter foundation models?
- **RQ4 (Algorithmic Fairness):** Do predictive models maintain parity of performance across historical eras, film genres, and languages, or do structural biases in screenwriting corpora degrade performance on specific film cohorts?

---

## Chapter 2: Literature Review & Theoretical Foundations

### 2.1 Historical Perspectives on Gender Portrayal in Hollywood
In her seminal work *The Celluloid Ceiling*, Dr. Martha Lauzen (2022) documented that women comprised merely 17% of directors, writers, executive producers, and cinematographers working on the top 250 domestic grossing films. Lindner, Lindner, and Hawkins (2015) conducted longitudinal analyses of feature releases from 1980 to 2010, concluding that films directed or written by women were significantly more likely to pass the Bechdel Test and allocate dialogue turns to female characters. However, because female-led productions constituted less than a fifth of major studio releases, the industry-wide baseline remained heavily skewed toward male-dominated narratives.

### 2.2 Prior Computational & NLP Studies of Film Dialogue
The emergence of large screenplay corpora has enabled computational linguists to analyze cinematic dialogue through statistical natural language processing. Danescu-Niculescu-Mizil and Lee (2011) introduced the Cornell Movie-Dialogs Corpus to investigate linguistic style coordination, demonstrating that characters dynamically adapt their lexical patterns to conversational partners depending on power relationships. Schofield and Mehr (2016) analyzed gender-distinguishing linguistic features across thousands of screenplays, identifying that female characters were consistently assigned higher frequencies of emotional and domestic vocabulary, whereas male characters dominated imperative commands and narrative action verbs. Ramakrishna et al. (2017) applied acoustic and lexical modeling to cinematic dialogue, uncovering that female characters spoke fewer lines and occupied less linguistically diverse narrative roles.

### 2.3 Theoretical Grounding
- **Cultivation Theory (Gerbner & Gross, 1976):** Posits that persistent exposure to mass media cultivates viewers' perceptions of social reality. When cinematic narratives depict men as active agents and women as romantic accessories, viewers absorb these representations as normative baselines.
- **Gender Schema Theory (Bem, 1981):** Suggests that individuals develop cognitive schemas that filter information through gender-based categories. The Bechdel Test operationalizes Bem's theory by testing whether female characters exist as autonomous individuals with concerns independent of male validation.

---

## Chapter 3: System Architecture & Data Engineering

### 3.1 Two-Tier Data Architecture
- **Tier 1 (Macro Dataset, N = 9,368):** Sourced from BechdelTest.com and enriched via TMDB API. Spans 1888 to 2019, providing budget, revenue, runtime, IMDb user scores, vote counts, genres, and cast/crew demographics.
- **Tier 2 (Matched Screenplay Dataset, N = 404):** Created by linking Tier 1 films against the Cornell Movie-Dialogs Corpus. Encompasses 304,446 dialogue lines across 83,097 conversational scenes, with speaking character gender attributions and conversational turn graphs.

| Metric / Dimension | Tier 1: Macro Dataset (Bechdel + TMDB) | Tier 2: Matched Dialogue Corpus (Cornell) |
| :--- | :--- | :--- |
| **Total Film Count** | 9,368 unique films | 404 matched feature screenplays |
| **Temporal Coverage** | 1888 – 2019 (131 years) | 1929 – 2010 (81 years) |
| **Target Class Balance** | Pass: 56.8% (5,321) / Fail: 43.2% (4,047) | Pass: 46.3% (187) / Fail: 53.7% (217) |
| **Total Dialogue Turns** | N/A (Metadata only) | 304,446 verified dialogue utterances |
| **Conversational Scenes** | N/A (Metadata only) | 83,097 character-to-character scenes |
| **Speaking Characters** | Cast lists (Top 10 billed) | 3,034 speaking characters (Cornell) |
| **Average Runtime** | 106.4 ± 24.2 minutes | 112.8 ± 22.4 minutes |

### 3.2 Network Interception and Ingestion Resilience
1. **Reliance Jio ISP DNS Sinkhole Interception:** In several deployment environments, Indian ISP Reliance Jio implemented an active DNS sinkhole for `bechdeltest.com`. We engineered an in-memory socket interceptor (`src/bechdel/data/dns_override.py`) that overrides `socket.getaddrinfo`, resolving `bechdeltest.com` directly to its AWS origin IP address (**3.175.86.37**).
2. **Bechdel API HTTP 410 Fallback:** When the live endpoint returned HTTP 410 Gone, our ingestion module automatically fell back to an immutable Wayback Machine snapshot, retrieving all 9,368 records with zero data loss.
3. **PyArrow Object Serialization:** We eliminated `ArrowInvalid` errors by enforcing strict columnar typing before exporting to Parquet.

![Figure 1: Class Balance and Two-Tier Data Join Accounting Funnel](figures/fig01_class_balance.png)

---

## Chapter 4: Exploratory Data Analysis & Statistical Hypothesis Testing

### 4.1 Macro-Historical Representation Trajectories
In the overall Tier 1 corpus, **56.8% (5,321 films) pass** while **43.2% (4,047 films) fail**. Plotting annual pass rates over time reveals an upward secular trend: pre-1960 pass rates hovered between 30% and 42%, rising significantly in the post-Hays Code era (1970s) to stabilize near 65% in the 2010s.

![Figure 2: Longitudinal Trend of Bechdel Test Pass Rate](figures/fig02_yearly_trend.png)

### 4.2 Genre Disparities
Female representation is sharply segregated across genres:
- **High-Passing:** Horror (68.2%), Romance (66.4%), Comedy (63.8%), Drama (61.5%).
- **Low-Passing:** Action (38.4%), Sci-Fi (42.1%), Western (29.5%), War (18.2%).

![Figure 3: Bechdel Test Pass Rates Sliced by Cinematic Primary Genre](figures/fig03_genre_pass_rate.png)

### 4.3 Statistical Hypothesis Testing

#### Hypothesis 1: Pearson's Chi-Square Test of Independence (Decade vs. Pass Rate)
- **$H_0$:** Bechdel Test passage is independent of the release decade.
- **$H_1$:** Bechdel Test passage is dependent on the release decade.
- **Result:** $\chi^2 = 232.69$, degrees of freedom $df = 5$, $p = 1.34 \times 10^{-41}$, Cramér's $V = 0.1576$.
- **Conclusion:** Reject $H_0$. There is an overwhelmingly significant historical association between release era and representation.

#### Hypothesis 2: Welch's Two-Sample Independent t-Test (Dialogue Share)
- **$H_0$:** Mean female dialogue share in passing films equals mean female dialogue share in failing films.
- **$H_1$:** Passing films feature higher mean female dialogue share.
- **Result:** Passing films $\mu = 42.84\%$, Failing films $\mu = 26.31\%$. $t = 10.034$, $df = 384.2$, $p = 7.73 \times 10^{-21}$, Cohen's $d = 1.026$.
- **Conclusion:** Reject $H_0$. Passing films allocate more than $1.6\times$ the dialogue share to women compared to failing films.

![Figure 4: Correlation Topology Heatmap Across Numerical Features](figures/fig04_correlation_matrix.png)

---

## Chapter 5: Rule-Based Dialogue Detector Design & Evaluation

### 5.1 Three-Stage Algorithmic Architecture
The rule-based detector evaluates three criteria sequentially:
- **Stage A (2+ Women):** Screenplay must feature at least two female speaking characters ($n_f \ge 2$). Unknown characters are resolved via TMDB cast billing.
- **Stage B (Women Converse):** At least two identified female characters must speak in a contiguous conversational turn sequence.
- **Stage C (Not About Men):** Candidate female-female conversations are scored for male-talk density:
  $$\text{MaleScore}(\text{conv}) = \frac{\text{Count}(\text{MalePronouns}) + \text{Count}(\text{MaleKinship}) + \text{Count}(\text{MaleNames})}{\text{TotalWords}(\text{conv})}$$
  A conversation qualifies if $\text{MaleScore}(\text{conv}) \le \tau$. The optimal threshold was tuned strictly on training partition screenplays to **$\tau^* = 0.10$**.

### 5.2 Empirical Performance vs. Ground Truth Crowd Labels

| Evaluation Stage | Accuracy | Precision | Recall | F1 Score | Specificity | Cohen's Kappa ($\kappa$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage A Only** | 64.36% | 56.42% | 94.65% | 0.7068 | 38.25% | 0.3120 |
| **Stage B (A & B)** | 71.53% | 66.52% | 79.68% | 0.7251 | 64.52% | 0.4358 |
| **Stage C (Final $\tau=0.10$)** | **74.01%** | **75.00%** | **66.84%** | **0.7062** | **80.09%** | **0.4728** |

---

## Chapter 6: Machine Learning Feature Engineering & Model Development

### 6.1 Feature Store Formalization (54 Dimensions)
Each film is represented as a 54-dimensional vector comprising 16 metadata features, 22 cast and credit demographic features, and 16 dialogue graph metrics.

### 6.2 Regression Modeling
- **Female Dialogue Share:** Regularized Ridge Regression achieved $R^2 = 0.3024$, $\text{RMSE} = 0.1435$, and $\text{MAE} = 0.1085$.
- **Yearly Trend:** Linear trend modeling achieved $R^2 = 0.3294$, $\text{RMSE} = 0.0828$.

![Figure 5: Regression Model Residuals: Female Dialogue Share](figures/fig05_regression_predictions.png)

### 6.3 Mathematical Objectives of Evaluated Classifiers
1. **Logistic Regression:** Minimizes L2-regularized cross-entropy loss:
   $$\min_{w,b} \sum_{i=1}^N \log(1 + e^{-y_i(w^T x_i + b)}) + \lambda \|w\|_2^2$$
2. **Gaussian Naive Bayes:** Maximizes joint likelihood under conditional independence:
   $$\max_y P(y) \prod_{j=1}^D \frac{1}{\sqrt{2\pi\sigma_{jy}^2}} \exp\left(-\frac{(x_j - \mu_{jy})^2}{2\sigma_{jy}^2}\right)$$
3. **Random Forest:** Ensemble of decision trees minimizing Gini impurity via bootstrap aggregation.
4. **Support Vector Machine (RBF Kernel):** Maximizes dual soft margin in reproducing kernel Hilbert space:
   $$\max_\alpha \sum_i \alpha_i - \frac{1}{2} \sum_{i,j} \alpha_i \alpha_j y_i y_j \exp(-\gamma \|x_i - x_j\|^2)$$
5. **HistGradientBoosting:** Iterative second-order gradient boosting with histogram feature binning.
6. **Decision Tree (CART):** Recursive binary splitting minimizing Gini impurity.
7. **K-Nearest Neighbors:** Non-parametric local majority voting under Minkowski distance metric.

### 6.4 Comparative Algorithmic Benchmark

| Experiment | Algorithm | Feature Set | CV Acc | CV Prec | CV Rec | CV F1 | CV PR-AUC | CV ROC-AUC | Temp F1 | Temp PR-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Exp 3 (Headline)** | **Naive Bayes** | Meta + Dialogue | **73.76%** | **75.80%** | **63.64%** | **0.6919** | **0.7833** | **0.7841** | 0.5660 | 0.7787 |
| **Exp 3 (Headline)** | **Logistic Regression** | Meta + Dialogue | **72.03%** | **71.02%** | **66.84%** | **0.6887** | **0.7858** | **0.7660** | 0.5185 | 0.7741 |
| **Exp 2 (Metadata)** | Logistic Regression | Metadata Only | 69.31% | 65.67% | 70.59% | 0.6804 | 0.7111 | 0.7398 | 0.6667 | 0.7642 |
| **Exp 3 (Headline)** | Random Forest | Meta + Dialogue | 73.02% | 75.66% | 61.50% | 0.6785 | 0.7885 | 0.7892 | 0.5714 | 0.7768 |
| **Exp 3 (Headline)** | SVM (RBF Kernel) | Meta + Dialogue | 72.77% | 74.84% | 62.03% | 0.6784 | 0.7618 | 0.7776 | 0.5455 | 0.7343 |
| **Exp 3 (Headline)** | HistGradientBoosting | Meta + Dialogue | 69.80% | 68.57% | 64.17% | 0.6630 | 0.7701 | 0.7583 | 0.5926 | 0.7924 |
| **Exp 3 (Headline)** | Decision Tree | Meta + Dialogue | 68.56% | 66.67% | 64.17% | 0.6540 | 0.7227 | 0.7413 | 0.6038 | 0.6936 |
| **Exp 2 (Metadata)** | Random Forest | Metadata Only | 67.57% | 64.74% | 65.78% | 0.6525 | 0.6909 | 0.7350 | 0.5600 | 0.6929 |
| **Exp 2 (Metadata)** | Decision Tree | Metadata Only | 66.83% | 63.59% | 66.31% | 0.6492 | 0.6230 | 0.6960 | 0.7000 | 0.7392 |
| **Exp 2 (Metadata)** | HistGradientBoosting | Metadata Only | 66.34% | 63.64% | 63.64% | 0.6364 | 0.6807 | 0.7141 | 0.5532 | 0.6522 |
| **Exp 2 (Metadata)** | SVM (RBF Kernel) | Metadata Only | 65.59% | 63.19% | 61.50% | 0.6233 | 0.6797 | 0.7196 | 0.6349 | 0.7170 |
| **Exp 2 (Metadata)** | Naive Bayes | Metadata Only | 63.37% | 60.32% | 60.96% | 0.6064 | 0.6436 | 0.6727 | 0.6316 | 0.7118 |
| **Exp 2 (Metadata)** | KNN | Metadata Only | 64.11% | 62.35% | 56.68% | 0.5938 | 0.5938 | 0.6749 | 0.4727 | 0.5181 |
| **Exp 1 (Baseline)** | Majority Classifier | No Features | 53.71% | 0.00% | 0.00% | 0.0000 | 0.4596 | 0.4940 | 0.0000 | 0.5000 |

**Key Takeaway:** Incorporating dialogue features expands Logistic Regression CV PR-AUC from **0.7111 to 0.7858 (+7.47% absolute gain)**, confirming that conversational dynamics provide essential signal beyond metadata.

![Figure 6: Comparative Confusion Matrices: Rule-Based Detector vs. Best Supervised Classifier](figures/fig07_confusion_matrices.png)

---

## Chapter 7: Explainability, Demographic Fairness Auditing & Error Forensics

### 7.1 Permutation Importance and SHAP Attributions
Permutation feature importance confirms that `num_ff_conversations` (+0.142 importance drop), `female_line_share` (+0.098), and `detector_pred` (+0.084) dominate predictions. Production budget and runtime exhibit near-zero predictive influence (< 0.012).

![Figure 7: Permutation Feature Importance and Global SHAP Summary Feature Attributions](figures/fig08_feature_importance_shap.png)

### 7.2 Interrogating the Behind-the-Camera Hypothesis
While female directors and writers exert positive marginal influence (+0.18 log-odds in SHAP), their relative importance is secondary to dialogue topology. A movie directed by a man with substantive female conversational scenes readily passes, whereas a movie directed by a woman lacking female-female conversational scenes fails.

### 7.3 Demographic Fairness Auditing
Evaluating model performance across eras, genres, and languages reveals that predictive recall drops significantly in Action (52.6%) and Crime (40.0%) because female dialogue in crime narratives frequently revolves around interrogating male suspects, triggering male pronoun penalties even when women lead investigations.

![Figure 8: Demographic Fairness Performance Audit Across Decades, Genres, and Languages](figures/fig09_fairness_slices.png)

### 7.4 Qualitative Error Forensics
Forensic audits of divergent cases (`reports/error_analysis_top20.csv`) reveal three primary failure modes:
1. **Annotator Subjectivity (45% of FPs):** In *The Bourne Supremacy*, women discuss agency logistics, which crowd annotators deemed implicitly 'about Jason Bourne'.
2. **Script Metadata Gaps (60% of FNs):** In *Highlander* and *Basic*, passing scenes exist, but Stage A failed because minor female characters were marked as unknown `'?'` in the Cornell corpus.
3. **Shooting Script Divergence (25% of FNs):** Theatrical cuts contain dialogue not present in early draft screenplays.

---

## Chapter 8: Engineering Standards, Verification & Reproducibility

### 8.1 Software Architecture
The repository is structured into modular Python packages with zero circular dependencies:
- `configs/config.yaml`: Single source of truth for global random seed (42), paths, and parameters.
- `src/bechdel/`: Decoupled modules for data ingestion, feature extraction, detector rules, model training, and evaluation.
- `tests/`: 26 automated unit tests validating title normalization, corpus parsing, detector edge fixtures, and zero-leakage pipeline encapsulation.
- `Makefile` & CLI: Typer-based interface supporting reproducible execution (`make all`).

---

## Chapter 9: Critical Discussion & Limitations

1. **Crowdsourced Label Subjectivity:** Crowd consensus ratings carry subjective interpretations of what constitutes an independent conversation.
2. **Absence of Neural Coreference:** Lexical keyword matching cannot resolve ambiguous pronouns or metaphorical references.
3. **Conversational Turns vs. Physical Scenes:** The Cornell corpus structures dialogue by character turns rather than physical cinematographic scenes.
4. **Studio Selection Biases:** The corpus reflects historic English-language Hollywood studio releases and cannot be generalized uncritically to global film industries.
5. **Goodhart's Law:** Adopting automated detectors as studio quotas risks incentivizing superficial token dialogue rather than rich character development.

---

## Chapter 10: Conclusion & Future Work

This project demonstrates that natural language processing and predictive analytics can automate cinematic gender auditing with high precision and transparency. Future research will prioritize integrating transformer-based coreference resolution (RoBERTa / LLaMA) and multimodal video/audio face-tracking to measure true on-screen speaking time.

---

## Academic References

1. Agarwal, A., Zheng, J., Kamath, S., Balasubramanian, S., & Dey, S. A. (2015). Key female characters in feature films. *EMNLP 2015*, 430–440.
2. Bechdel, A. (1985). The Rule. *Dykes to Watch Out For* (Strip #22).
3. Bem, S. L. (1981). Gender schema theory: A cognitive account of sex typing. *Psychological Review*, 88(4), 354–364.
4. Danescu-Niculescu-Mizil, C., & Lee, L. (2011). Chameleons in imagined conversations. *CMCL 2011*, 76–87.
5. Geena Davis Institute on Gender in Media. (2018). *The Geena Davis Inclusion Quotient*.
6. Gerbner, G., & Gross, L. (1976). Living with television: The violence profile. *Journal of Communication*, 26(2), 172–199.
7. Lauzen, M. M. (2022). *The Celluloid Ceiling: Employment of behind-the-scenes women*. San Diego State University.
8. Lindner, A. M., Lindner, M. R., & Hawkins, J. (2015). From behind the camera to in front of the screen. *Feminist Media Studies*, 15(6), 1046–1063.
9. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *NeurIPS 2017*, 4765–4774.
10. Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *JMLR*, 12, 2825–2830.
11. Ramakrishna, A., et al. (2017). Linguistic analysis of differences in portrayal of movie characters. *ACL 2017*, 1669–1678.
12. Schofield, A., & Mehr, L. (2016). Gender-distinguishing features in film dialogue. *CLFL 2016*, 32–39.
13. Woolf, V. (1929). *A Room of One's Own*. Hogarth Press.

---

## Appendices

- **Appendix A:** Complete 54-Feature Dictionary & Schema (`reports/academic_project_report.pdf`, Pages 30–32)
- **Appendix B:** Full Mathematical & Statistical Formulations (`reports/academic_project_report.pdf`, Page 33)
- **Appendix C:** Comprehensive Forensic Discrepancy Case Studies (`reports/academic_project_report.pdf`, Pages 34–35)
- **Appendix D:** 50-Item Human Verification Sample Table (`reports/academic_project_report.pdf`, Pages 36–39)
- **Appendix E:** Cross-Validation Fold Stability & Hyperparameter Grids (`reports/academic_project_report.pdf`, Page 40)
