"""Clinical recommendation engine for HeartVision AI reports."""

from __future__ import annotations

from typing import Any, Dict, List


def generate_medical_recommendations(
    cleaned: Dict[str, Any],
    risk_level: str,
    disease_prob: float,
) -> Dict[str, List[str]]:
    """
    Build structured lifestyle / clinical / preventive guidance.

    Recommendations are educational decision-support content only —
    they do not constitute a medical diagnosis.
    """
    recs: Dict[str, List[str]] = {
        "lifestyle": [],
        "clinical": [],
        "preventive": [],
        "alerts": [],
    }

    recs["preventive"].append(
        "Schedule routine annual comprehensive cardiovascular screenings with your primary clinician."
    )
    recs["preventive"].append(
        "Maintain a balanced Mediterranean or DASH-style diet low in saturated fats and sodium."
    )
    recs["preventive"].append(
        "Prioritize 7–9 hours of quality sleep and evidence-based stress reduction practices."
    )

    chol = cleaned.get("chol", 0)
    if chol > 240:
        recs["clinical"].append(
            f"Serum cholesterol is elevated ({chol} mg/dl). Request a full lipid panel (LDL, HDL, triglycerides)."
        )
        recs["lifestyle"].append(
            "Increase soluble fiber intake and aim for at least 150 minutes of moderate aerobic activity weekly."
        )
    elif chol > 200:
        recs["clinical"].append(
            f"Serum cholesterol is borderline high ({chol} mg/dl). Monitor lipids and discuss diet with a clinician."
        )
        recs["lifestyle"].append(
            "Reduce processed foods and emphasize whole grains, legumes, fruits, and vegetables."
        )
    else:
        recs["lifestyle"].append(
            "Serum cholesterol is within a favorable range (< 200 mg/dl). Continue current nutrition habits."
        )

    trestbps = cleaned.get("trestbps", 0)
    if trestbps >= 140:
        recs["clinical"].append(
            f"Resting blood pressure is high ({trestbps} mmHg). Initiate home BP logging and clinical follow-up."
        )
        recs["lifestyle"].append(
            "Limit sodium to under 2,000 mg/day and discuss blood-pressure management with your physician."
        )
    elif trestbps >= 130:
        recs["clinical"].append(
            f"Resting blood pressure is elevated ({trestbps} mmHg). Re-check readings and review lifestyle factors."
        )
        recs["lifestyle"].append(
            "Reduce caffeine/alcohol if applicable and incorporate daily walking or aerobic exercise."
        )

    if cleaned.get("fbs", 0) == 1:
        recs["clinical"].append(
            "Fasting blood sugar > 120 mg/dl indicated. Consider HbA1c testing for glycemic assessment."
        )
        recs["lifestyle"].append(
            "Focus on glycemic-friendly meals, portion control, and regular post-meal activity."
        )

    if cleaned.get("exang", 0) == 1 or cleaned.get("oldpeak", 0) > 1.0:
        recs["clinical"].append(
            "Exertional ischemic indicators present (exercise angina and/or ST depression). "
            "Stress imaging or specialist review may be appropriate."
        )

    ca = cleaned.get("ca", 0)
    if ca > 0:
        recs["alerts"].append(
            f"Fluoroscopy indicates {ca} major vessel(s) involved. Cardiology consultation is advised."
        )

    thal = cleaned.get("thal", 0)
    if thal in (1, 3):
        recs["clinical"].append(
            "Perfusion defect pattern indicated on thalassemia encoding. Discuss imaging correlation with cardiology."
        )

    age = cleaned.get("age", 0)
    if age >= 65:
        recs["preventive"].append(
            "Age-related cardiovascular risk is elevated. Ensure medication reconciliation and fall-safe activity plans."
        )

    if risk_level == "High":
        recs["alerts"].insert(
            0,
            "High cardiovascular disease probability detected. Prompt consultation with a board-certified "
            "cardiologist is strongly recommended.",
        )
        recs["clinical"].append(
            "Discuss 12-lead ECG, laboratory cardiac markers as indicated, and further ischemic evaluation."
        )
        recs["alerts"].append(
            "Seek emergency care for chest pain, sudden shortness of breath, syncope, or neurological deficits."
        )
    elif risk_level == "Moderate":
        recs["alerts"].append(
            "Moderate risk profile detected. Lifestyle optimization and cardiology follow-up within 30 days "
            "are recommended."
        )
        recs["lifestyle"].append(
            "Begin a supervised, progressive exercise plan after clinical clearance."
        )
    else:
        if disease_prob < 0.35:
            recs["lifestyle"].append(
                "Current model assessment suggests a lower-risk profile. Continue healthy lifestyle habits "
                "and routine preventive care."
            )
        recs["preventive"].append(
            "Keep annual checkups and update risk factors (smoking, weight, lipids, glucose) with your clinician."
        )

    return recs
