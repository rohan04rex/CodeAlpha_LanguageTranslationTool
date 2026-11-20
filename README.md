# CodeAlpha — Language Translation Tool 

A lightweight, modern web application for multilingual text translation. Built as part of the **CodeAlpha Artificial Intelligence Internship** .

![Project Banner](https://img.shields.io/badge/CodeAlpha-AI_Internship-6366f1?style=for-the-badge)
![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Framework-Flask_3.0-000000?style=for-the-badge&logo=flask)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

---

## 📌 Project Overview

This project satisfies all requirements for **Task 1: Language Translation Tool** in the CodeAlpha AI Internship:

1. **Interactive UI:** Clean dual-card layout for entering text and selecting source/target languages.
2. **Translation Engine:** `deep-translator` (Google Translate) with automatic fallback to the MyMemory API — no API key required.
3. **Auto Language Detection:** `langdetect` identifies the source language when *Auto Detect* is selected.
4. **Display & Usability:** Clearly formatted output, character/word counters, language swap, preset sample chips, and one-click clipboard copy with feedback.
5. **Session History:** Recent translations are kept locally in `localStorage` for quick reuse.

---

## 🚀 Features

- 🌐 **51 Languages + Auto Detect:** English, Spanish, French, German, Hindi, Japanese, Chinese, Arabic, and many more.
- 🔍 **Intelligent Auto-Detection:** Identifies the source language on demand (Chinese variants map to Simplified Chinese).
- ⇄ **Instant Language Swap:** Switches languages and moves the translated text into the source box.
- 📋 **One-Click Copy:** Clipboard copy with dynamic "Copied!" feedback and a fallback for insecure contexts.
- ⚡ **Lightweight & Fast:** Pure Python Flask, vanilla CSS, and native JavaScript — no build tools or heavy audio libraries.
- 🌓 **Dark & Light Mode:** Glassmorphism interface with a persisted theme toggle.
- ⏱️ **Recent Translation History:** Keeps up to 8 entries locally with one-click reload or deletion.
- ♿ **Keyboard Accessible:** Sample cards and history entries support Enter/Space activation.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Flask 3.0+
- **Translation:** `deep-translator` (Google Translate with MyMemory fallback)
- **Detection:** `langdetect`
- **Frontend:** HTML5, vanilla CSS (custom properties, glassmorphism), vanilla JavaScript (ES6+ Fetch API)

---

## 📂 Project Structure

```text
CodeAlpha_LanguageTranslationTool/
│
├── app.py                  # Flask server and REST API endpoints
├── translator_service.py   # Multi-provider translation and detection logic
├── requirements.txt        # Dependencies (flask, requests, deep-translator, langdetect)
├── PRD.md                  # Product Requirement Document
├── README.md               # Project documentation and guide
├── test_translation.py     # 15 offline tests (mocked providers + Flask API)
│
├── static/
│   ├── css/style.css       # Theme, layout and animations
│   └── js/app.js           # Translation, swap, copy and history controller
│
└── templates/
    └── index.html          # Semantic single-page interface
```

---

## ⚡ Quickstart Guide

### 1. Clone and enter the repository
```bash
git clone https://github.com/<your-username>/CodeAlpha_LanguageTranslationTool.git
cd CodeAlpha_LanguageTranslationTool
```

### 2. Set up a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```
Open **`http://127.0.0.1:5000`**.

By default the app binds to `127.0.0.1` with the debugger disabled. Override with the `HOST`, `PORT`, and `FLASK_DEBUG` environment variables when needed.

> Real translations require internet access (Google Translate, with MyMemory as fallback). The UI works normally offline apart from the translation request itself.

---

## 🧪 Running Automated Tests

```bash
python test_translation.py
```
*Output: `Ran 15 tests ... OK`*

Translation providers are mocked, so the suite is deterministic and needs no network access. It covers the Google → MyMemory fallback, language detection, identical-language shortcut, validation, and all Flask endpoints.

---

## 📑 API Endpoints

### 1. Translate — `POST /api/translate`
```json
{ "text": "Hello, welcome to CodeAlpha!", "source": "auto", "target": "es" }
```
```json
{
  "status": "success",
  "translated_text": "¡Hola, bienvenido a CodeAlpha!",
  "detected_source": "English",
  "source_code": "en",
  "target_code": "es",
  "provider": "Google Translate"
}
```
Input is limited to 5,000 characters.

### 2. Supported languages — `GET /api/languages`

### 3. Detect language — `POST /api/detect`
```json
{ "text": "Bonjour tout le monde" }
```

---

## 👤 Author

Developed for the **CodeAlpha Artificial Intelligence Internship**.
