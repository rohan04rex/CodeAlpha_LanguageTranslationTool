"""
Unit tests for CodeAlpha Language Translation Tool.

External translation providers are mocked, so the whole suite runs offline and
deterministically while still exercising the real fallback logic and Flask API.
"""

import unittest
from unittest.mock import Mock, patch

from app import app
from translator_service import (
    SUPPORTED_LANGUAGES,
    detect_language_code,
    translate_text,
)


class TranslationServiceTests(unittest.TestCase):
    @patch("translator_service.detect", return_value="fr")
    def test_detect_language(self, _mock_detect):
        self.assertEqual(detect_language_code("Bonjour tout le monde"), "fr")

    @patch("translator_service.detect", return_value="zh-TW")
    def test_detect_chinese_maps_to_zh_cn(self, _mock_detect):
        self.assertEqual(detect_language_code("你好世界"), "zh-CN")

    def test_detect_empty_text_defaults_to_english(self):
        self.assertEqual(detect_language_code("   "), "en")

    @patch("translator_service.GoogleTranslator")
    def test_translate_text_service(self, mock_google):
        mock_google.return_value.translate.return_value = "¡Hola, amigo!"
        result = translate_text("Hello, friend!", source="en", target="es")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["translated_text"], "¡Hola, amigo!")
        self.assertEqual(result["target_code"], "es")
        self.assertEqual(result["provider"], "Google Translate")

    @patch("translator_service.GoogleTranslator")
    def test_google_failure_falls_back_to_mymemory(self, mock_google):
        mock_google.side_effect = RuntimeError("Google quota exceeded")

        fake_response = Mock()
        fake_response.raise_for_status.return_value = None
        fake_response.json.return_value = {
            "responseData": {"translatedText": "Hola, amigo!"}
        }

        with patch("translator_service.requests.get", return_value=fake_response) as mock_get:
            result = translate_text("Hello, friend!", source="en", target="es")

        self.assertEqual(result["provider"], "MyMemory Engine")
        self.assertEqual(result["translated_text"], "Hola, amigo!")
        mock_get.assert_called_once()

    def test_identical_source_and_target_skips_providers(self):
        result = translate_text("Hello!", source="en", target="en")
        self.assertEqual(result["provider"], "Identical Language Match")
        self.assertEqual(result["translated_text"], "Hello!")

    def test_empty_text_raises_value_error(self):
        with self.assertRaises(ValueError):
            translate_text("   ", source="auto", target="es")


class TranslationAPITests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CodeAlpha", response.data)
        self.assertIn(b"Translate", response.data)

    def test_get_languages(self):
        response = self.client.get("/api/languages")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("es", data["languages"])
        self.assertIn("auto", data["languages"])
        self.assertEqual(len(SUPPORTED_LANGUAGES), 52)

    @patch("app.get_language_name", return_value="French")
    @patch("app.detect_language_code", return_value="fr")
    def test_detect_language_endpoint(self, _mock_code, _mock_name):
        response = self.client.post("/api/detect", json={"text": "Bonjour"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["detected_code"], "fr")
        self.assertEqual(data["detected_name"], "French")

    def test_detect_language_requires_text(self):
        response = self.client.post("/api/detect", json={"text": ""})
        self.assertEqual(response.status_code, 400)

    @patch("app.translate_text", return_value={
        "status": "success",
        "translated_text": "¡Hola, mundo!",
        "detected_source": "English",
        "source_code": "en",
        "target_code": "es",
        "provider": "Google Translate",
    })
    def test_translate_api_endpoint(self, mock_translate):
        response = self.client.post("/api/translate", json={
            "text": "Hello world",
            "source": "en",
            "target": "es",
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["translated_text"], "¡Hola, mundo!")
        mock_translate.assert_called_once()

    def test_translate_empty_input(self):
        response = self.client.post("/api/translate", json={
            "text": "",
            "source": "auto",
            "target": "es",
        })
        self.assertEqual(response.status_code, 400)

    def test_translate_input_too_long(self):
        response = self.client.post("/api/translate", json={
            "text": "x" * 5001,
            "source": "auto",
            "target": "es",
        })
        self.assertEqual(response.status_code, 400)

    @patch("app.translate_text", side_effect=RuntimeError("provider down"))
    def test_translate_api_server_error(self, _mock_translate):
        response = self.client.post("/api/translate", json={
            "text": "Hello",
            "source": "en",
            "target": "es",
        })
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json()["status"], "error")


if __name__ == "__main__":
    unittest.main(verbosity=2)
