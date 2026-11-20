"""
CodeAlpha AI Internship - Task 1: Language Translation Tool
Flask Web Application Server
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
from translator_service import (
    SUPPORTED_LANGUAGES,
    translate_text,
    detect_language_code,
    get_language_name
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Flask 3 uses the JSON provider instead of the removed JSON_AS_ASCII config key.
app.json.ensure_ascii = False

@app.route("/")
def index():
    """Renders the main single-page translation interface."""
    return render_template("index.html", languages=SUPPORTED_LANGUAGES)

@app.route("/api/languages", methods=["GET"])
def get_languages():
    """Returns available supported languages."""
    return jsonify({
        "status": "success",
        "languages": SUPPORTED_LANGUAGES
    })

@app.route("/api/detect", methods=["POST"])
def detect_language():
    """Detects the language of given text."""
    try:
        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"status": "error", "message": "Text is required for detection."}), 400

        detected_code = detect_language_code(text)
        detected_name = get_language_name(detected_code)

        return jsonify({
            "status": "success",
            "detected_code": detected_code,
            "detected_name": detected_name
        })
    except Exception as e:
        logger.error(f"Detection API error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Language detection failed. Please try again."
        }), 500

@app.route("/api/translate", methods=["POST"])
def translate():
    """Handles text translation requests."""
    try:
        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip()
        source_lang = data.get("source", "auto").strip()
        target_lang = data.get("target", "es").strip()

        if not text:
            return jsonify({"status": "error", "message": "Please enter some text to translate."}), 400

        if len(text) > 5000:
            return jsonify({"status": "error", "message": "Text exceeds the 5,000 character limit."}), 400

        result = translate_text(text, source=source_lang, target=target_lang)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        logger.error(f"Translation API error: {e}")
        return jsonify({
            "status": "error",
            "message": "Translation request failed. Please check your network connection and try again."
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    # The Werkzeug debugger is disabled by default; enable only in development.
    debug = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    print(f"Starting CodeAlpha Language Translation Tool at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
