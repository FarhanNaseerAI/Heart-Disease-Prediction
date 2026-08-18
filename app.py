"""
HeartVision AI — Professional Heart Disease Prediction System
=============================================================
Entry point: python app.py

Prediction pipeline mirrors Disease_Prediction_Model.ipynb exactly:
  RandomForestClassifier on raw (unscaled) clinical features.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from services.prediction import get_prediction_service
from services.store import result_store
from utils.validators import (
    FEATURE_META,
    FEATURE_NAMES,
    FIELD_HELP,
    VALIDATION_RULES,
    validate_input_data,
)

# ---------------------------------------------------------------------------
# Application factory / configuration
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("HeartVisionAI")

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)
app.config["SECRET_KEY"] = os.environ.get(
    "HEARTVISION_SECRET_KEY",
    "heartvision-ai-dev-key-change-in-production",
)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

prediction_service = get_prediction_service(BASE_DIR)


@app.context_processor
def inject_globals() -> Dict[str, Any]:
    return {
        "app_name": "HeartVision AI",
        "app_tagline": "Professional AI-Powered Heart Disease Prediction",
        "feature_meta": FEATURE_META,
        "field_help": FIELD_HELP,
        "feature_names": FEATURE_NAMES,
        "validation_rules": VALIDATION_RULES,
    }


# ---------------------------------------------------------------------------
# Routes — pages
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Landing page: story, education, and clinical prediction console."""
    return render_template("index.html")


@app.route("/about")
def about():
    """About the AI model and clinical methodology."""
    return render_template("about.html")


@app.route("/predict", methods=["POST"])
def predict():
    """Handle clinical prediction from form or AJAX."""
    form_data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    wants_json = (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.is_json
        or request.accept_mimetypes.best == "application/json"
    )

    cleaned_data, errors = validate_input_data(form_data)
    if errors:
        if wants_json:
            return jsonify({"success": False, "errors": errors}), 400
        for err in errors:
            flash(err, "danger")
        return redirect(url_for("index") + "#prediction")

    try:
        result = prediction_service.predict(cleaned_data)
        session["latest_result_id"] = result_store.put(result)

        # Persist a compact history list in session (max 20)
        history = session.get("prediction_history", [])
        history.insert(
            0,
            {
                "timestamp": result["timestamp"],
                "prediction_text": result["prediction_text"],
                "risk_level": result["risk_level"],
                "risk_percentage": result["risk_percentage"],
                "confidence": result["confidence"],
            },
        )
        session["prediction_history"] = history[:20]

        if wants_json:
            return jsonify({"success": True, "result": result})
        return render_template("result.html", result=result)
    except Exception:
        logger.exception("Prediction failed")
        message = "Unable to complete prediction. Please verify inputs and try again."
        if wants_json:
            return jsonify({"success": False, "errors": [message]}), 500
        flash(message, "danger")
        return redirect(url_for("index") + "#prediction")


@app.route("/result")
def show_result():
    """Render the medical report dashboard from the latest session result."""
    result = result_store.get(session.get("latest_result_id"))
    if not result:
        flash("No active prediction found. Please submit patient data first.", "warning")
        return redirect(url_for("index") + "#prediction")
    return render_template("result.html", result=result)


@app.route("/history")
def history():
    """Prediction history page (session-backed)."""
    items = session.get("prediction_history", [])
    return render_template("history.html", history=items)


@app.route("/history/clear", methods=["POST"])
def clear_history():
    session.pop("prediction_history", None)
    flash("Prediction history cleared.", "success")
    return redirect(url_for("history"))


# ---------------------------------------------------------------------------
# Routes — API
# ---------------------------------------------------------------------------


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """REST API for clinical integrations."""
    payload = request.get_json(silent=True) or {}
    cleaned_data, errors = validate_input_data(payload)

    if errors:
        return (
            jsonify(
                {
                    "status": "error",
                    "code": 400,
                    "message": "Validation failed",
                    "errors": errors,
                }
            ),
            400,
        )

    try:
        result = prediction_service.predict(cleaned_data)
        return jsonify({"status": "success", "code": 200, "data": result})
    except Exception:
        logger.exception("API prediction failed")
        return (
            jsonify(
                {
                    "status": "error",
                    "code": 500,
                    "message": "Prediction engine unavailable",
                }
            ),
            500,
        )


@app.route("/api/health")
def api_health():
    """Liveness / readiness probe."""
    return jsonify(
        {
            "status": "healthy" if prediction_service.is_ready else "degraded",
            "model_loaded": prediction_service.model is not None,
            "scaler_loaded": prediction_service.scaler is not None,
            "engine": "HeartVision AI v1.0",
            "algorithm": "RandomForestClassifier (GridSearchCV tuned)",
            "features": FEATURE_NAMES,
            "scaling_applied": False,
            "note": "Scaler is loaded for artifact parity; RF inference uses raw features per notebook.",
        }
    )


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(_error):
    logger.exception("Unhandled server error")
    return render_template("errors/500.html"), 500


@app.errorhandler(413)
def payload_too_large(_error):
    return (
        jsonify({"status": "error", "message": "Request payload too large."}),
        413,
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    ready = prediction_service.is_ready
    print("=" * 72)
    print("  HeartVision AI — Professional Heart Disease Prediction System")
    print("  http://127.0.0.1:5000")
    print(f"  Model : {'LOADED' if ready else 'MISSING — place Disease_Prediction_Model.pkl'}")
    print(f"  Scaler: {'LOADED' if prediction_service.scaler is not None else 'MISSING'}")
    print("=" * 72)
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=debug)
