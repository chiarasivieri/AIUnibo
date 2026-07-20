# Anomaly Detection on Industrial Data — AI in Industry Project

Comparison of three density estimation methods for anomaly detection on the SKAB dataset:
- Kernel Density Estimation (KDE)
- Gaussian Mixture Model (GMM)
- Normalizing Flows (NF)

## Dataset

SKAB (Skoltech Anomaly Benchmark) — time series data from a hydraulic testbed at Skoltech.
Source: https://github.com/waico/SKAB

## Structure

```
aiinindustry-skab/
├── SKAB/                        # Dataset (cloned from GitHub)
├── 01_data_exploration.ipynb
├── 02_preprocessing.ipynb
├── 03_model_kde.ipynb
├── 04_model_gmm.ipynb
├── 05_model_nf.ipynb
├── 06_evaluation.ipynb
├── preprocessing.pkl
├── requirements.txt
└── README.md
```

## Setup

```bash
git clone https://github.com/waico/SKAB
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m ipykernel install --user --name=skab --display-name "SKAB"
```

## Evaluation metric

First detection time: number of timesteps between the start of the anomaly and the first alarm raised by the model.

## Results

| Model | Mean delay (timesteps) |
|-------|----------------------|
| KDE   | 0.5                  |
| GMM   | 9.8                  |
| NF    | 0.5                  |