# Bayesian Networks for Early Detection of Coronary Artery Disease

**Authors:** Chiara Sivieri, Jacopo Mauro, Liam Busnelli Urso  
**Course:** Fundamentals of AI and Knowledge Representation — Module 3  
**University:** Master's Degree in Artificial Intelligence, University of Bologna  
**Academic Year:** 2025/2026

## Overview

This project investigates the use of Bayesian Networks for estimating the probability of Coronary Artery Disease (CAD) from routine clinical measurements. The core idea is that CAD diagnosis traditionally relies on expensive and invasive procedures such as coronary angiography and echocardiography. We explore whether a probabilistic graphical model trained on standard clinical features can serve as a lightweight, interpretable alternative.

We adopt a progressive design methodology: starting from a fully data-driven baseline, we incrementally introduce domain knowledge in the form of forbidden edges, forced edges grounded in medical literature, and latent variables representing unobserved clinical constructs. All models are evaluated using stratified 5-fold cross-validation on accuracy and recall. We then test cross-population generalization by applying models trained on the Cleveland dataset directly to the Indian Heart Disease dataset.

Bayesian Networks are particularly suited to this domain because they naturally encode causal relationships between variables, handle uncertainty through probability distributions, support inference under partial evidence (not all clinical tests are available for every patient), and produce interpretable structures that clinicians can validate.


## Repository Structure

```
bayesian-networks-on-heart-diseases/
│
├── datasets/
│   ├── cleveland_dataset.csv
│   └── Indian_heart_disease_dataset.csv
│
├── report/
│   ├── report.tex
│   └── faikrmod3.bib
│
├── cleveland.ipynb
├── cleveland_data_presentation.ipynb
├── forced_edges.ipynb
├── latent_learned_networks_aic.ipynb
├── bayesian_networks_latent.ipynb
├── bayesian_networks_latent_indian.ipynb
├── indian_preprocessing.ipynb
├── indian_cross_test.ipynb
│
├── dataset_functions.py
├── network_functions.py
└── plot_functions.py
```

**cleveland_data_presentation.ipynb** contains the full data exploration and visualization of the Cleveland dataset, including distributions of all features before and after discretization.

**cleveland.ipynb** contains the unconstrained and blacklist models, with structure learning, parameter estimation and 5-fold cross-validation.

**forced_edges.ipynb** contains the model with medically grounded forced edges, including clinical justifications and references for each forced edge.

**latent_learned_networks_aic.ipynb** contains the three latent variable models on Cleveland (coronary_health, metabolic_risk, forced edges + latent), with 5-fold cross-validation and a comparative bar chart of accuracy and recall across all models.

**bayesian_networks_latent.ipynb** and **bayesian_networks_latent_indian.ipynb** contain exploratory latent variable experiments on both datasets.

**indian_preprocessing.ipynb** contains the full preprocessing pipeline for the Indian dataset, including feature renaming, cleaning (removal of invalid cholesterol values), and clinical discretization using the same thresholds as Cleveland.

**indian_cross_test.ipynb** contains the cross-dataset generalization experiment: models trained on Cleveland are evaluated directly on the Indian dataset without retraining.

**dataset_functions.py** contains utility functions for discretization, including bin edge computation and midpoint mapping.

**network_functions.py** contains utility functions for model creation (Hill Climbing with ExpertKnowledge), evaluation (Variable Elimination inference, accuracy and recall computation), cross-validation (stratified k-fold), and network visualization.

**plot_functions.py** contains visualization utilities including pie charts, bar frequency plots and grouped bar plots for model comparison.


## Datasets

### Cleveland Heart Disease Dataset

The Cleveland Heart Disease Dataset is sourced from the UCI Machine Learning Repository (Detrano et al., 1989). It contains 303 patients described by 13 clinical features and a binary target variable called **condition** (0 = no disease, 1 = disease). This is the primary dataset used for all model training and evaluation.

The 13 features are the following. **age** is the patient's age in years. **sex** encodes gender (1 = male, 0 = female). **cp** encodes chest pain type on a scale from 0 (typical angina) to 3 (asymptomatic). **trestbps** is the resting blood pressure in mmHg at hospital admission. **chol** is the serum cholesterol level in mg/dL. **fbs** indicates whether fasting blood sugar exceeds 120 mg/dL. **restecg** encodes resting electrocardiographic results (0 = normal, 1 = ST-T wave abnormality, 2 = left ventricular hypertrophy). **thalach** is the maximum heart rate achieved during a stress test. **exang** indicates whether exercise-induced angina was present. **oldpeak** is the ST depression induced by exercise relative to rest. **slope** encodes the slope of the peak exercise ST segment. **ca** is the number of major vessels colored by fluoroscopy (0 to 3). **thal** encodes the result of the thallium stress test (0 = normal, 1 = fixed defect, 2 = reversible defect).

The dataset link is: https://archive.ics.uci.edu/dataset/45/heart+disease

### Indian Heart Disease Dataset

The Indian Heart Disease Dataset is sourced from Mendeley Data. It contains 1000 patients originally, reduced to 947 after removing records with invalid cholesterol values (serumcholestrol = 0), and further preprocessed to 765 patients with 13 features after aligning the feature structure with Cleveland.

The Indian dataset uses different column names which are mapped during preprocessing to match the Cleveland convention. The key structural difference is that the Indian dataset does not contain the **thal** feature, which encodes the thallium stress test result and is one of the strongest individual predictors of CAD in the Cleveland data. This absence is a significant limitation for the cross-dataset experiment, particularly for latent variable models that rely on thal as an anchor feature.

After preprocessing, both datasets share the same 13 features with the same discretization thresholds, enabling direct cross-dataset evaluation.


## Discretization

Continuous variables were discretized using clinically established thresholds from peer-reviewed medical literature. The choice of clinical discretization over purely data-driven bins serves two purposes: it makes the Conditional Probability Tables interpretable (each bin corresponds to a medically meaningful category), and it ensures that the discretization is grounded in established medical knowledge rather than arbitrary numerical intervals.

### Serum Cholesterol (chol)

Source: NCEP ATP III Guidelines (National Heart, Lung, and Blood Institute, 2001)  
Link: https://www.nhlbi.nih.gov/files/docs/guidelines/atp3xsum.pdf

| Category | Range (mg/dL) | Clinical Meaning |
| :--- | :--- | :--- |
| Desirable | < 200 | Low risk of heart disease |
| Borderline High | 200 to 239 | Requires dietary or lifestyle intervention |
| High | >= 240 | High risk; often requires pharmacological treatment |

### Resting Blood Pressure (trestbps)

Source: 2017 ACC/AHA Hypertension Guidelines (Whelton et al., 2018)  
Link: https://www.heart.org

| Category | Range (mmHg) | Clinical Meaning |
| :--- | :--- | :--- |
| Normal | < 120 | Within normal range |
| Elevated | 120 to 129 | Consistent elevation; lifestyle changes recommended |
| Hypertension Stage 1 | 130 to 139 | Clinical intervention often needed |
| Hypertension Stage 2 | 140 to 180 | Consistent high readings; treatment required |
| Hypertensive Crisis | > 180 | Requires immediate medical attention |

### Maximum Heart Rate (thalach)

Source: AHA Target Heart Rates Chart (American Heart Association, 2023)  
Link: https://www.heart.org/en/healthy-living/fitness/fitness-basics/target-heart-rates

| Category | Range (BPM) | Clinical Meaning |
| :--- | :--- | :--- |
| Poor Response | < 120 | Possible chronotropic incompetence or low fitness |
| Moderate | 120 to 150 | Average threshold for cardiac patients under stress |
| Optimal | 151 to 180 | Normal diagnostic target for healthy adults |
| High | > 180 | Typical in younger or high-performance individuals |

### ST Depression (oldpeak)

Source: Yap et al. (2005), International Journal of Cardiovascular Imaging  
Link: https://doi.org/10.1007/s10554-004-2458-y  
Supporting reference: https://en.wikipedia.org/wiki/ST_depression

| Category | Range (mm) | Clinical Meaning |
| :--- | :--- | :--- |
| Optimal | 0 | No depression of the ST fragment |
| Low Risk | < 1.0 | Within normal physiological limits |
| Moderate Risk | 1.0 to 1.9 | Clinical suspicion of ischemia |
| High Risk | >= 2.0 | High probability of multi-vessel CAD |

### Age

Source: Global Burden of Disease Study / The Lancet (Roth et al., 2017)  
Link: https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(18)31694-5/fulltext

| Category | Range (Years) | Epidemiological Relevance |
| :--- | :--- | :--- |
| Early Adulthood | 20 to 29 | Rare incidence of clinical CAD |
| Early Middle Age | 30 to 39 | Subclinical plaque development |
| Late Middle Age | 40 to 49 | Increasing risk, especially in males |
| Peak Diagnosis | 50 to 59 | Significant rise in coronary events |
| High Prevalence | 60 to 69 | Peak of chronic heart disease cases |
| Late Onset | >= 70 | High mortality and heart failure risk |


## Model Design

### Structure Learning

All observed-only models use Hill Climbing with AIC scoring for structure learning, implemented via pgmpy's HillClimbSearch. Hill Climbing is a score-based greedy algorithm that iteratively adds, removes or reverses edges to maximize the chosen scoring function. It is the most widely used structure learning algorithm for discrete Bayesian Networks in practice and performs well on datasets of this size.

AIC (Akaike Information Criterion) was chosen over BIC (Bayesian Information Criterion) because AIC is less penalizing on model complexity, tending to produce richer network structures. With 303 patients and 13 features, this is a reasonable trade-off: the networks do not become dense enough to overfit structurally, and AIC allows the algorithm to recover weaker but real dependencies that BIC might discard. BDeu scoring was considered but introduces an additional hyperparameter (the Equivalent Sample Size) whose choice is arbitrary without domain-specific knowledge.

### Parameter Estimation

Parameters for all observed-only models are estimated using a Bayesian Estimator with BDeu (Bayesian Dirichlet equivalent uniform) prior, implemented via pgmpy's BayesianEstimator. BDeu is the standard prior for Bayesian parameter estimation in discrete Bayesian Networks. It assigns a uniform prior over parameters and provides smoothing that prevents zero probabilities in the CPTs, which would otherwise cause inference failures when a feature combination is not present in the training data.

### Inference

All inference is performed using Variable Elimination, implemented via pgmpy's VariableElimination. For each patient in the validation set, the model computes P(condition = 1 | observed features) and predicts disease if this probability is at least 0.5. Recall is used alongside accuracy as the primary evaluation metric because in a clinical context, false negatives (predicting no disease in a sick patient) carry a much higher cost than false positives.

### Cross-Validation

All models are evaluated using stratified 5-fold cross-validation. Stratification ensures that each fold preserves the original class distribution, which is important because the Cleveland dataset is not perfectly balanced between disease and no-disease cases.


## Progressive Network Design

### Model 1: Unconstrained

The unconstrained model applies Hill Climbing with AIC scoring with no restrictions on the network structure. It serves as the purely data-driven baseline. No domain knowledge is incorporated at this stage beyond the choice of scoring function.

### Model 2: Blacklist (Forbidden Edges)

The blacklist model adds a set of forbidden edges that prevent clinically implausible causal directions. Specifically, the target variable condition is forbidden from being a parent of any demographic variable. The rationale is that a CAD diagnosis cannot causally determine a patient's age or sex, as these are fixed biological characteristics that predate any disease. Forbidden edges enforced include condition to age and condition to sex.

### Model 3: Forced Edges

The forced edges model additionally requires specific edges to be present in the learned structure, based on peer-reviewed clinical evidence. These edges represent medical relationships that are well established in the literature and that the data-driven algorithm might not recover reliably on a dataset of 303 patients, or might orient in the wrong direction.

| Edge | Clinical Justification | Source |
| :--- | :--- | :--- |
| age to condition | Age is a primary non-modifiable risk factor for CAD, with incidence increasing significantly after age 50 | Lima Dos Santos et al. (2023), Cureus |
| age to trestbps | Blood pressure systematically increases with age due to progressive arterial stiffening | Lima Dos Santos et al. (2023), Cureus |
| ca to condition | The number of major coronary vessels showing significant stenosis is a direct diagnostic marker of CAD severity | AHA Guidelines |
| oldpeak to condition | ST depression >= 1mm during exercise stress test is the standard clinical criterion for a positive test, with specificity of 98.9% and PPV of 96% for significant CAD | Katheria et al. (2021), Indian Heart Journal |
| exang to oldpeak | Exercise-induced angina and ST depression co-occur as manifestations of the same ischemic event under physical stress | Clinical evidence |

### Model 4: Latent Variable Models

The latent variable models introduce hidden nodes representing unobserved clinical constructs that are hypothesized as common causes of groups of observed variables. Their conditional probability distributions are estimated via the Expectation-Maximization (EM) algorithm. EM alternates between an E-step, which computes the posterior distribution of the latent states given the observed data and current parameters, and an M-step, which updates all parameters to maximize the expected log-likelihood given those posterior estimates. The algorithm iterates until convergence.

Three latent variable configurations were tested on the Cleveland dataset.

**coronary_health** is a binary latent node with children oldpeak, exang, slope and condition. The clinical reasoning is that ST depression, exercise-induced angina and the slope of the ST segment are all different measurements of the same underlying physiological process: inducible myocardial ischemia, meaning insufficient coronary perfusion under physical stress. Modelling them as jointly caused by a single hidden state reduces redundancy and improves the interpretability of the network structure. This construct is grounded in the StatPearls clinical guidelines on chest pain, which specify that these three findings must co-occur as objective evidence of ischemia. Source: https://www.ncbi.nlm.nih.gov/books/NBK557672/

**metabolic_risk** is a binary latent node with children chol, trestbps and fbs. These three factors are the core components of metabolic syndrome, a well-documented cluster of cardiometabolic risk factors that tend to co-occur due to shared causes such as poor diet, sedentary lifestyle and genetic predisposition. Grundy (2004) in the Journal of the American College of Cardiology is the key clinical reference. This latent node was expected to be particularly relevant for the Indian dataset, where 78% of patients have high cholesterol, a much higher proportion than in Cleveland, suggesting a stronger metabolic syndrome component. Source: https://doi.org/10.1097/01.hjr.0000286917.26112.d0

A third configuration combines both latent nodes with forced edges simultaneously.


## Results

### Cleveland Dataset

All results are averaged over 5 stratified folds.

| Model | Accuracy | Recall |
| :--- | :---: | :---: |
| Unconstrained | 0.87 | 0.84 |
| Blacklist | 0.78 | 0.78 |
| Forced edges | 0.78 | 0.74 |
| Latent (coronary_health) | 0.76 | 0.72 |
| Latent (metabolic_risk) | 0.79 | 0.71 |
| Latent (forced + latent) | 0.73 | 0.67 |

The unconstrained model achieves the highest accuracy and recall. Adding domain knowledge does not improve predictive performance but produces more interpretable network structures whose edges align with established clinical relationships. Latent variable models underperform, likely because with only 303 patients the EM algorithm has insufficient data to reliably estimate the hidden variable distributions. The E-step posterior estimates are uncertain, leading to noisy parameter updates in the M-step and overfitting to Cleveland-specific patterns.

### Cross-Dataset Generalization

| Experiment | Accuracy | Recall |
| :--- | :---: | :---: |
| Cleveland unconstrained (in-distribution) | 0.87 | 0.84 |
| Cleveland to Indian, latent model | 0.54 | 0.57 |
| Cleveland to Indian, unconstrained | 0.68 | 0.80 |
| Indian dataset, own latent model | 0.81 | 0.75 |

The latent model collapses on the Indian dataset (0.54 accuracy, near chance) because its CPDs were estimated from Cleveland-specific distributions. When the Indian dataset presents very different cholesterol and blood pressure profiles, the EM-estimated latent states become unreliable. The unconstrained model transfers significantly better, achieving 0.68 accuracy and 0.80 recall. Notably, its recall on the Indian dataset (0.80) exceeds that of the Indian-trained model (0.75), suggesting that the causal structure learned from Cleveland captures biological relationships that generalize across populations. What differs between the two datasets are the numerical distributions of the features, not the underlying causal mechanisms of the disease.


## Dependencies

Python 3.11 or later is required. The following packages are needed:

```
pgmpy >= 1.1.0
scikit-learn
pandas
numpy
matplotlib
seaborn
networkx
jupyter
```

Install all dependencies with:

```bash
pip install pgmpy scikit-learn pandas numpy matplotlib seaborn networkx jupyter
```

Note: pgmpy 1.1.0 or later is required for ExpertKnowledge support in HillClimbSearch. Earlier versions do not include this class.


## References

Detrano, R. et al. (1989). International application of a new probability algorithm for the diagnosis of coronary artery disease. The American Journal of Cardiology, 64(5), 304-310. https://doi.org/10.1016/0002-9149(89)90524-9

Lima Dos Santos, C.C. et al. (2023). The Influence of Sex, Age, and Race on Coronary Artery Disease: A Narrative Review. Cureus, 15(10), e47799. https://doi.org/10.7759/cureus.47799

Katheria, R. et al. (2021). Significance of recovery ST-segment depression in exercise stress test. Indian Heart Journal, 73(6), 693-696. https://doi.org/10.1016/j.ihj.2021.10.001

Yap, L.B. et al. (2005). Significance of ST depression during exercise treadmill stress and adenosine infusion myocardial perfusion imaging. The International Journal of Cardiovascular Imaging, 21, 253-258. https://doi.org/10.1007/s10554-004-2458-y

Grundy, S.M. (2004). Metabolic syndrome and cardiovascular risk. Journal of the American College of Cardiology. https://doi.org/10.1097/01.hjr.0000286917.26112.d0

National Cholesterol Education Program (NCEP) Expert Panel (2001). Executive Summary of the Third Report of the NCEP Expert Panel on Detection, Evaluation, and Treatment of High Blood Cholesterol in Adults (Adult Treatment Panel III). National Heart, Lung, and Blood Institute.

Whelton, P.K. et al. (2018). 2017 ACC/AHA Guideline for the Prevention, Detection, Evaluation, and Management of High Blood Pressure in Adults. Hypertension, 71(6), e13-e115. https://doi.org/10.1161/HYP.0000000000000065

Roth, G.A. et al. (2017). Global, Regional, and National Burden of Cardiovascular Diseases for 10 Causes, 1990 to 2015. Journal of the American College of Cardiology, 70(1), 1-25. https://doi.org/10.1016/j.jacc.2017.04.052

Hachamovitch, R. et al. (1998). Incremental prognostic value of myocardial perfusion single photon emission computed tomography for the prediction of cardiac death. Circulation, 97(6), 535-543. https://doi.org/10.1161/01.cir.97.6.535
