"""
Translation Service for CodeAlpha Language Translation Tool.
Integrates deep-translator with automatic fallback to MyMemory API and langdetect.
"""

import logging
import requests
from deep_translator import GoogleTranslator, MyMemoryTranslator
from langdetect import detect, DetectorFactory

# Set seed for deterministic language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

# Curated list of popular & supported languages
SUPPORTED_LANGUAGES = {
    "auto": "Auto Detect",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "hi": "Hindi",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "ru": "Russian",
    "pt": "Portuguese",
    "it": "Italian",
    "nl": "Dutch",
    "tr": "Turkish",
    "pl": "Polish",
    "sv": "Swedish",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "th": "Thai",
    "el": "Greek",
    "cs": "Czech",
    "ro": "Romanian",
    "da": "Danish",
    "fi": "Finnish",
    "uk": "Ukrainian",
    "he": "Hebrew",
    "bn": "Bengali",
    "ur": "Urdu",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ms": "Malay",
    "fa": "Persian",
    "no": "Norwegian",
    "hu": "Hungarian",
    "sk": "Slovak",
    "bg": "Bulgarian",
    "hr": "Croatian",
    "sr": "Serbian",
    "lt": "Lithuanian",
    "sl": "Slovenian",
    "et": "Estonian",
    "lv": "Latvian",
    "sw": "Swahili",
    "af": "Afrikaans",
    "fil": "Filipino"
}

def detect_language_code(text: str) -> str:
    """Detects the ISO 639-1 code of the input text using langdetect."""
    if not text or not text.strip():
        return "en"
    try:
        detected = detect(text)
        # Handle Chinese variations
        if detected.startswith("zh"):
            return "zh-CN"
        return detected
    except Exception as e:
        logger.warning(f"Detection error: {e}. Defaulting to 'en'.")
        return "en"

def get_language_name(code: str) -> str:
    """Returns human-readable name for a language code."""
    return SUPPORTED_LANGUAGES.get(code, code.upper())

def translate_via_google(text: str, source_code: str, target_code: str) -> str:
    """Attempts translation using Google Translator."""
    gt_source = "auto" if source_code == "auto" else source_code
    return GoogleTranslator(source=gt_source, target=target_code).translate(text)

def translate_via_mymemory(text: str, source_code: str, target_code: str) -> str:
    """Translates using MyMemory API as a reliable, quota-friendly provider."""
    src = "autodetect" if source_code == "auto" else source_code
    url = "https://api.mymemory.translated.net/get"
    params = {
        "q": text,
        "langpair": f"{src}|{target_code}"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CodeAlphaTranslationTool/1.0"
    }
    response = requests.get(url, params=params, headers=headers, timeout=8)
    response.raise_for_status()
    data = response.json()
    translated_text = data.get("responseData", {}).get("translatedText")
    if not translated_text or "MYMEMORY WARNING" in translated_text:
        # Fallback to deep-translator's internal MyMemory translator if needed
        return MyMemoryTranslator(source=src, target=target_code).translate(text)
    return translated_text

def translate_text(text: str, source: str = "auto", target: str = "es") -> dict:
    """
    Main translation pipeline with auto-detection and multi-provider fallback.
    """
    cleaned_text = text.strip() if text else ""
    if not cleaned_text:
        raise ValueError("Please provide text to translate.")

    if not target or target == "auto":
        target = "en"

    # Handle auto-detection
    detected_code = source
    if source == "auto":
        detected_code = detect_language_code(cleaned_text)
        detected_name = get_language_name(detected_code)
    else:
        detected_name = get_language_name(source)

    # If source and target are the same, return early
    if detected_code.lower() == target.lower():
        return {
            "status": "success",
            "translated_text": cleaned_text,
            "detected_source": detected_name,
            "source_code": detected_code,
            "target_code": target,
            "provider": "Identical Language Match"
        }

    # Provider 1: Google Translator
    try:
        translated = translate_via_google(cleaned_text, source, target)
        if translated and translated.strip():
            return {
                "status": "success",
                "translated_text": translated,
                "detected_source": detected_name,
                "source_code": detected_code,
                "target_code": target,
                "provider": "Google Translate"
            }
    except Exception as g_err:
        logger.info(f"GoogleTranslator error ({g_err}), falling back to MyMemory API...")

    # Provider 2: MyMemory API Fallback
    try:
        translated = translate_via_mymemory(cleaned_text, detected_code, target)
        if translated and translated.strip():
            return {
                "status": "success",
                "translated_text": translated,
                "detected_source": detected_name,
                "source_code": detected_code,
                "target_code": target,
                "provider": "MyMemory Engine"
            }
    except Exception as m_err:
        logger.error(f"MyMemory fallback error: {m_err}")
        raise RuntimeError("Translation service is momentarily unavailable. Please check your connection or try again.")
