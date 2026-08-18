"""
Prediction service for HeartVision AI.

SOURCE OF TRUTH: Disease_Prediction_Model.ipynb

Notebook pipeline (cells 19–37):
  - Features = df.drop("target", axis=1) in CSV column order
  - RandomForestClassifier tuned via GridSearchCV on UNSCALED X_train
  - Sample inference: final_model.predict(X.iloc[[0]])  — NO scaler.transform
  - scaler.pkl is persisted for LR/SVM experiments but MUST NOT be applied
    to Random Forest inference

This service loads both artifacts and mirrors notebook RF inference exactly.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import joblib
import pandas as pd

from services.recommendations import generate_medical_recommendations
from utils.validators import FEATURE_META, FEATURE_NAMES

logger = logging.getLogger("HeartVisionAI.prediction")

# Notebook feature importance ranking (cell 33 / saved model)
FEATURE_IMPORTANCE_ORDER = [
    ("cp", 0.1969),
    ("thal", 0.1468),
    ("thalach", 0.1077),
    ("oldpeak", 0.1019),
    ("ca", 0.0995),
    ("exang", 0.0957),
    ("slope", 0.0675),
    ("chol", 0.0527),
    ("age", 0.0519),
    ("trestbps", 0.0370),
    ("sex", 0.0250),
    ("restecg", 0.0143),
    ("fbs", 0.0031),
]


class PredictionService:
    """Singleton-style loader and inference engine."""

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        self.model_path = os.path.join(base_dir, "Disease_Prediction_Model.pkl")
        self.scaler_path = os.path.join(base_dir, "scaler.pkl")
        self.model = None
        self.scaler = None
        self._load_assets()

    def _load_assets(self) -> None:
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info("Loaded Disease_Prediction_Model.pkl")
            else:
                logger.error("Model file missing: %s", self.model_path)

            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
                logger.info("Loaded scaler.pkl (not applied to RF inference)")
            else:
                logger.error("Scaler file missing: %s", self.scaler_path)
        except Exception:
            logger.exception("Failed to load ML assets")
            self.model = None
            self.scaler = None

    @property
    def is_ready(self) -> bool:
        return self.model is not None

    def predict(self, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run notebook-identical Random Forest inference on raw features.

        Parameters
        ----------
        cleaned_data : dict
            Validated feature map containing all FEATURE_NAMES keys.
        """
        if self.model is None:
            raise RuntimeError("Machine learning model is not loaded.")

        # Exact column order from notebook / heart.csv
        input_df = pd.DataFrame([cleaned_data], columns=FEATURE_NAMES)

        # Cell 37: predict / predict_proba on unscaled feature vector
        raw_pred = int(self.model.predict(input_df)[0])
        raw_probs = self.model.predict_proba(input_df)[0]

        prob_healthy = float(raw_probs[0])
        prob_disease = float(raw_probs[1])
        risk_percentage = round(prob_disease * 100, 1)
        confidence = round(max(prob_healthy, prob_disease) * 100, 1)

        if risk_percentage >= 65.0:
            risk_level = "High"
            risk_color = "#dc2626"
            risk_badge = "HIGH RISK — CARDIAC EVALUATION RECOMMENDED"
        elif risk_percentage >= 35.0:
            risk_level = "Moderate"
            risk_color = "#f59e0b"
            risk_badge = "MODERATE CARDIAC RISK DETECTED"
        else:
            risk_level = "Low"
            risk_color = "#059669"
            risk_badge = "LOW CARDIAC RISK LEVEL"

        recommendations = generate_medical_recommendations(
            cleaned_data, risk_level, prob_disease
        )

        human_summary = {
            "age": f"{cleaned_data['age']} years",
            "sex": FEATURE_META["sex"].get(cleaned_data["sex"], str(cleaned_data["sex"])),
            "cp": FEATURE_META["cp"].get(cleaned_data["cp"], str(cleaned_data["cp"])),
            "trestbps": f"{cleaned_data['trestbps']} mmHg",
            "chol": f"{cleaned_data['chol']} mg/dl",
            "fbs": FEATURE_META["fbs"].get(cleaned_data["fbs"], str(cleaned_data["fbs"])),
            "restecg": FEATURE_META["restecg"].get(
                cleaned_data["restecg"], str(cleaned_data["restecg"])
            ),
            "thalach": f"{cleaned_data['thalach']} bpm",
            "exang": FEATURE_META["exang"].get(
                cleaned_data["exang"], str(cleaned_data["exang"])
            ),
            "oldpeak": f"{float(cleaned_data['oldpeak']):.1f}",
            "slope": FEATURE_META["slope"].get(
                cleaned_data["slope"], str(cleaned_data["slope"])
            ),
            "ca": FEATURE_META["ca"].get(cleaned_data["ca"], str(cleaned_data["ca"])),
            "thal": FEATURE_META["thal"].get(
                cleaned_data["thal"], str(cleaned_data["thal"])
            ),
        }

        # Lightweight explainability using model importances when available
        influencing = []
        if hasattr(self.model, "feature_importances_"):
            pairs = sorted(
                zip(FEATURE_NAMES, self.model.feature_importances_),
                key=lambda item: item[1],
                reverse=True,
            )
            for name, weight in pairs[:5]:
                influencing.append(
                    {
                        "feature": name,
                        "importance": round(float(weight) * 100, 2),
                        "value": human_summary.get(name, cleaned_data.get(name)),
                        "label": {
                            "cp": "Chest Pain Type",
                            "thal": "Thalassemia",
                            "thalach": "Max Heart Rate",
                            "oldpeak": "ST Depression",
                            "ca": "Major Vessels",
                            "exang": "Exercise Angina",
                            "slope": "ST Slope",
                            "chol": "Cholesterol",
                            "age": "Age",
                            "trestbps": "Blood Pressure",
                            "sex": "Gender",
                            "restecg": "Resting ECG",
                            "fbs": "Fasting Blood Sugar",
                        }.get(name, name),
                    }
                )
        else:
            for name, weight in FEATURE_IMPORTANCE_ORDER[:5]:
                influencing.append(
                    {
                        "feature": name,
                        "importance": round(weight * 100, 2),
                        "value": human_summary.get(name, cleaned_data.get(name)),
                        "label": name,
                    }
                )

        return {
            "prediction": raw_pred,
            "prediction_text": (
                "Heart Disease Detected"
                if raw_pred == 1
                else "No Heart Disease Detected"
            ),
            "is_disease": raw_pred == 1,
            "prob_disease": prob_disease,
            "prob_healthy": prob_healthy,
            "risk_percentage": risk_percentage,
            "confidence": confidence,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_badge": risk_badge,
            "inputs_raw": cleaned_data,
            "inputs_human": human_summary,
            "recommendations": recommendations,
            "influencing_features": influencing,
            "model_name": type(self.model).__name__,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }


_service: Optional[PredictionService] = None


def get_prediction_service(base_dir: Optional[str] = None) -> PredictionService:
    global _service
    if _service is None:
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        _service = PredictionService(base_dir)
    return _service
