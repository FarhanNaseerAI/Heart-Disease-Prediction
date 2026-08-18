"""
Input validation utilities for HeartVision AI.
Mirrors clinical feature domains from heart.csv / notebook.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


# Exact feature order from notebook: X = df.drop("target", axis=1)
FEATURE_NAMES: List[str] = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]

VALIDATION_RULES: Dict[str, Dict[str, Any]] = {
    "age": {
        "min": 1,
        "max": 120,
        "type": int,
        "label": "Age",
        "unit": "years",
    },
    "sex": {
        "allowed": [0, 1],
        "type": int,
        "label": "Gender",
    },
    "cp": {
        "allowed": [0, 1, 2, 3],
        "type": int,
        "label": "Chest Pain Type",
    },
    "trestbps": {
        "min": 80,
        "max": 250,
        "type": float,
        "label": "Resting Blood Pressure",
        "unit": "mmHg",
    },
    "chol": {
        "min": 100,
        "max": 600,
        "type": float,
        "label": "Serum Cholesterol",
        "unit": "mg/dl",
    },
    "fbs": {
        "allowed": [0, 1],
        "type": int,
        "label": "Fasting Blood Sugar",
    },
    "restecg": {
        "allowed": [0, 1, 2],
        "type": int,
        "label": "Resting Electrocardiogram",
    },
    "thalach": {
        "min": 60,
        "max": 220,
        "type": float,
        "label": "Maximum Heart Rate Achieved",
        "unit": "bpm",
    },
    "exang": {
        "allowed": [0, 1],
        "type": int,
        "label": "Exercise-Induced Angina",
    },
    "oldpeak": {
        "min": 0.0,
        "max": 10.0,
        "type": float,
        "label": "ST Depression (Oldpeak)",
    },
    "slope": {
        "allowed": [0, 1, 2],
        "type": int,
        "label": "Slope of Peak Exercise ST Segment",
    },
    "ca": {
        "allowed": [0, 1, 2, 3, 4],
        "type": int,
        "label": "Number of Major Vessels",
    },
    "thal": {
        "allowed": [0, 1, 2, 3],
        "type": int,
        "label": "Thalassemia",
    },
}

FEATURE_META: Dict[str, Dict[Any, str]] = {
    "sex": {0: "Female", 1: "Male"},
    "cp": {
        0: "Typical Angina",
        1: "Atypical Angina",
        2: "Non-Anginal Pain",
        3: "Asymptomatic",
    },
    "fbs": {
        0: "≤ 120 mg/dl (Normal)",
        1: "> 120 mg/dl (Elevated)",
    },
    "restecg": {
        0: "Normal",
        1: "ST-T Wave Abnormality",
        2: "Left Ventricular Hypertrophy",
    },
    "exang": {
        0: "No",
        1: "Yes",
    },
    "slope": {
        0: "Upsloping",
        1: "Flat",
        2: "Downsloping",
    },
    "ca": {
        0: "0 vessels",
        1: "1 vessel",
        2: "2 vessels",
        3: "3 vessels",
        4: "4 vessels",
    },
    "thal": {
        0: "Unknown / Not assessed",
        1: "Fixed Defect",
        2: "Normal",
        3: "Reversible Defect",
    },
}

FIELD_HELP: Dict[str, Dict[str, str]] = {
    "age": {
        "description": "Patient age in completed years.",
        "tooltip": "Cardiovascular risk rises with age. Enter age between 1 and 120.",
        "placeholder": "e.g. 54",
    },
    "sex": {
        "description": "Biological sex as encoded in the clinical dataset.",
        "tooltip": "0 = Female, 1 = Male (dataset encoding).",
        "placeholder": "Select gender",
    },
    "cp": {
        "description": "Chest pain classification from clinical assessment.",
        "tooltip": "0 Typical angina · 1 Atypical · 2 Non-anginal · 3 Asymptomatic",
        "placeholder": "Select chest pain type",
    },
    "trestbps": {
        "description": "Resting blood pressure measured in mmHg.",
        "tooltip": "Typical resting systolic range is roughly 90–180 mmHg.",
        "placeholder": "e.g. 130",
    },
    "chol": {
        "description": "Serum cholesterol level in mg/dl.",
        "tooltip": "Values above 200 mg/dl may indicate elevated lipid risk.",
        "placeholder": "e.g. 240",
    },
    "fbs": {
        "description": "Whether fasting blood sugar exceeds 120 mg/dl.",
        "tooltip": "1 if fasting blood sugar > 120 mg/dl, otherwise 0.",
        "placeholder": "Select fasting blood sugar status",
    },
    "restecg": {
        "description": "Resting electrocardiographic results.",
        "tooltip": "0 Normal · 1 ST-T abnormality · 2 Left ventricular hypertrophy",
        "placeholder": "Select resting ECG result",
    },
    "thalach": {
        "description": "Maximum heart rate achieved during exercise testing.",
        "tooltip": "Peak heart rate observed during stress testing (bpm).",
        "placeholder": "e.g. 150",
    },
    "exang": {
        "description": "Angina induced by exercise.",
        "tooltip": "1 if chest pain occurred during exercise, otherwise 0.",
        "placeholder": "Select exercise angina status",
    },
    "oldpeak": {
        "description": "ST depression induced by exercise relative to rest.",
        "tooltip": "Higher oldpeak values can indicate ischemia. Range 0.0–10.0.",
        "placeholder": "e.g. 1.4",
    },
    "slope": {
        "description": "Slope of the peak exercise ST segment.",
        "tooltip": "0 Upsloping · 1 Flat · 2 Downsloping",
        "placeholder": "Select ST slope",
    },
    "ca": {
        "description": "Number of major vessels colored by fluoroscopy (0–4).",
        "tooltip": "Count of major coronary vessels with visible fluoroscopic coloring.",
        "placeholder": "Select vessel count",
    },
    "thal": {
        "description": "Thalassemia / myocardial perfusion status.",
        "tooltip": "1 Fixed defect · 2 Normal · 3 Reversible defect (dataset encoding).",
        "placeholder": "Select thalassemia status",
    },
}


def validate_input_data(form_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Validate and coerce all required clinical features.

    Returns
    -------
    cleaned : dict
        Coerced feature values keyed by FEATURE_NAMES.
    errors : list[str]
        Human-readable validation messages (empty when valid).
    """
    cleaned: Dict[str, Any] = {}
    errors: List[str] = []

    for feature in FEATURE_NAMES:
        rule = VALIDATION_RULES[feature]
        label = rule["label"]

        if feature not in form_dict or form_dict[feature] in ("", None):
            errors.append(f"{label} is required.")
            continue

        raw_val = form_dict[feature]

        try:
            val = rule["type"](raw_val)
        except (ValueError, TypeError):
            errors.append(f"{label} must be a valid number.")
            continue

        if "min" in rule and val < rule["min"]:
            unit = rule.get("unit", "")
            suffix = f" {unit}" if unit else ""
            errors.append(f"{label} cannot be less than {rule['min']}{suffix}.")
            continue

        if "max" in rule and val > rule["max"]:
            unit = rule.get("unit", "")
            suffix = f" {unit}" if unit else ""
            errors.append(f"{label} cannot exceed {rule['max']}{suffix}.")
            continue

        if "allowed" in rule and val not in rule["allowed"]:
            errors.append(f"Invalid selection for {label}.")
            continue

        cleaned[feature] = val

    return cleaned, errors
