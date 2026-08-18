# HeartVision AI

**Professional AI-Powered Heart Disease Prediction System**

HeartVision AI is a production-ready Flask application that delivers clinical decision-support predictions for cardiovascular disease risk. The inference pipeline is locked to the research notebook (`Disease_Prediction_Model.ipynb`) — the same Random Forest model, the same feature order, and the same unscaled prediction path.

> **Medical disclaimer:** HeartVision AI assists clinicians and care teams. It does **not** replace professional medical diagnosis, treatment, imaging, laboratory confirmation, or emergency care.

---

## Overview

| Item | Detail |
|------|--------|
| Product | HeartVision AI |
| Domain | Cardiovascular risk decision support |
| Backend | Flask + joblib + scikit-learn |
| Model | `RandomForestClassifier` (GridSearchCV tuned) |
| Artifacts | `Disease_Prediction_Model.pkl`, `scaler.pkl` |
| UI | Responsive medical dashboard (light / dark) |

---

## Features

- Premium landing experience with heartbeat / ECG motion and ambient particles
- Clinical prediction console with grouped fields, tooltips, and strict validation
- Fullscreen AI processing animation with staged progress messaging
- Medical report dashboard: prediction, confidence, risk meter, circular gauge
- Patient summary, recommendations, and explainable feature influence
- Prediction history (session-backed)
- Copy / print / export-to-PDF (print dialog) report actions
- Light & dark mode with remembered preference
- REST API (`/api/predict`, `/api/health`)
- Accessibility: semantic HTML, ARIA labels, skip link, keyboard-friendly controls

---

## Screenshots

Place product captures in `screenshots/`:

| File | Description |
|------|-------------|
| `screenshots/landing.png` | Hero / landing composition |
| `screenshots/prediction.png` | Clinical prediction console |
| `screenshots/report.png` | AI medical report dashboard |
| `screenshots/dark-mode.png` | Dark theme |

---

## Installation

Requires **Python 3.11+** (scikit-learn 1.9.0).

```bash
# 1. Clone
git clone <your-repo-url>
cd "Dieses prediction"

# 2. (Recommended) virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

Ensure these files are present in the project root:

- `Disease_Prediction_Model.pkl`
- `scaler.pkl`
- `heart.csv` (reference dataset; not required at runtime)

---

## Usage

```bash
python app.py
```

Open **http://127.0.0.1:5000**

Optional environment variables:

| Variable | Purpose |
|----------|---------|
| `HEARTVISION_SECRET_KEY` | Stable Flask session secret |
| `PORT` | HTTP port (default `5000`) |
| `FLASK_DEBUG` | Set to `1` to enable debug mode |

### API examples

```bash
# Health
curl http://127.0.0.1:5000/api/health

# Predict (notebook sample row 0)
curl -X POST http://127.0.0.1:5000/api/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"age\":63,\"sex\":1,\"cp\":3,\"trestbps\":145,\"chol\":233,\"fbs\":1,\"restecg\":0,\"thalach\":150,\"exang\":0,\"oldpeak\":2.3,\"slope\":0,\"ca\":0,\"thal\":1}"
```

---

## Technology

- Python 3.10+
- Flask
- scikit-learn
- pandas / NumPy
- joblib
- Modern HTML5 / CSS3 / vanilla JavaScript

---

## Model Information

### Source of truth

`Disease_Prediction_Model.ipynb`

### Selected model

- Algorithm: **RandomForestClassifier**
- Tuning: **GridSearchCV** (`cv=5`, scoring=`accuracy`)
- Best params: `n_estimators=300`, `max_depth=5`, `min_samples_leaf=4`, `min_samples_split=2`, `random_state=42`

### Held-out metrics (notebook summary)

| Metric | Value |
|--------|------:|
| Accuracy | 0.820 |
| Precision | 0.762 |
| Recall | 0.970 |
| F1 Score | 0.853 |
| ROC-AUC | 0.902 |

### Feature order (must never change)

`age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal`

### Critical inference rule

The Random Forest was trained on **raw** features. Notebook sample inference:

```python
sample = X.iloc[[0]]
prediction = final_model.predict(sample)
probability = final_model.predict_proba(sample)
```

HeartVision AI loads `scaler.pkl` for artifact parity but **does not** apply scaling during Random Forest prediction.

---

## Project Structure

```text
.
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── Disease_Prediction_Model.ipynb
├── Disease_Prediction_Model.pkl
├── scaler.pkl
├── heart.csv
├── services/
│   ├── prediction.py
│   └── recommendations.py
├── utils/
│   └── validators.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── about.html
│   ├── history.html
│   └── errors/
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── animations/
└── screenshots/
```

---

## Future Improvements

- Persistent encrypted prediction store with clinician authentication
- Prospective monitoring / drift detection on live inputs
- Deeper SHAP-based local explanations
- HL7 FHIR / EHR connector adapters
- Containerized deployment (Docker + Gunicorn) on Render / Railway / Azure

---

## License

MIT License — see [LICENSE](LICENSE).
