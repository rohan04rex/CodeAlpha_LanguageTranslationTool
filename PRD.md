# Product Requirement Document (PRD)
## CodeAlpha AI Internship — Task 1: Language Translation Tool

---

### Document Information
- **Project Name:** CodeAlpha Language Translation Tool
- **Repository Name:** `CodeAlpha_LanguageTranslationTool`
- **Domain:** Artificial Intelligence / Natural Language Processing
- **Document Version:** 1.2.0
- **Status:** Implemented / Ready for Submission
- **Target Audience:** CodeAlpha Evaluators, Developers

---

## 1. Executive Summary & Problem Statement

### 1.1 Overview
The **CodeAlpha Language Translation Tool** is a clean, lightweight web application that translates text between 51 languages in real time. Built for **Task 1** of the CodeAlpha AI Internship, it focuses on the core functional requirements without heavy dependencies, using `deep-translator` with a MyMemory fallback and no API key.

### 1.2 Problem Statement
Users need a straightforward translation tool that:
1. Provides a distraction-free UI for input and language selection.
2. Detects the source language automatically or accepts a manual choice.
3. Translates accurately through a free translation engine.
4. Presents output clearly with a one-click copy button.

---

## 2. Project Goals & Scope

### 2.1 In-Scope (Core Requirements)
- **Interactive UI:** Dual-card layout (source input, target output) with swap.
- **Language Selection:** 51 languages plus *Auto Detect*.
- **Auto-Detection:** `langdetect` with deterministic seeding; Chinese variants map to `zh-CN`.
- **Translation Engine:** Google Translate via `deep-translator`, with MyMemory API fallback.
- **Output & Copy:** Readable result card, character/word statistics, and one-click copy.
- **Session History:** Up to 8 recent translations stored in `localStorage`.
- **Zero Heavy Dependencies:** Four lightweight Python packages.

### 2.2 Out-of-Scope
- ❌ Text-to-Speech / audio generation (optional in the task brief).
- ❌ Microphone speech-to-text and media streaming.
- ❌ User authentication, database setup, or complex state stores.

### 2.3 Success Metrics
| Metric | Target | Verification |
| :--- | :--- | :--- |
| Setup Time | < 2 minutes | `pip install -r requirements.txt` then `python app.py` |
| Translation Latency | Typically < 1 s | Browser fetch to Flask API (network dependent) |
| Dependencies | 4 lightweight packages | `requirements.txt` |
| Task Compliance | 100% adherence to Task 1 specs | checklist in section 8 |

---

## 3. User Flow

```
[User Lands on Page]
        │
        ▼
[Enters Text into Source Box]
        │
        ▼
[Selects Source & Target Language (or leaves Source as 'Auto Detect')]
        │
        ▼
[Clicks 'Translate Text' or presses Ctrl/Cmd + Enter]
        │
        ▼
[Frontend sends POST request to Flask '/api/translate']
        │
        ▼
[Backend translates via Google, falling back to MyMemory]
        │
        ▼
[Translated text renders in Output Box + stats/provider badge]
        │
        ▼
[User clicks 'Copy' and gets instant confirmation]
```

---

## 4. Functional Requirements

### 4.1 Input Section (FR-1)
- **FR-1.1 Text Area:** Textarea with placeholder and live character/word counters, 5,000-character limit.
- **FR-1.2 Language Selectors:** Source dropdown (Auto Detect + 51 languages); target dropdown (51 languages, Spanish default).
- **FR-1.3 Swap Button:** Exchanges source/target languages and moves output text into the source box.
- **FR-1.4 Clear Button:** Wipes input and output.

### 4.2 Translation Engine (FR-2)
- **FR-2.1 Endpoint:** `POST /api/translate`.
- **FR-2.2 Processing:** `GoogleTranslator` from `deep-translator`, falling back to MyMemory API.
- **FR-2.3 Auto-detection:** `langdetect` identifies source when `auto` is selected.
- **FR-2.4 Validation:** Empty and over-limit inputs return HTTP 400 with a helpful message.

### 4.3 Output Section (FR-3)
- **FR-3.1 Result Display:** Distinct result card with preserved formatting.
- **FR-3.2 Copy to Clipboard:** One-click button with "Copied!" feedback and an `execCommand` fallback.
- **FR-3.3 Detected Language Badge:** Shown when Auto Detect is used.
- **FR-3.4 Provider Badge:** Shows which engine produced the translation.

### 4.4 REST API Endpoints (FR-4)
| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/` | GET | Renders the single-page interface |
| `/api/languages` | GET | Returns the supported language map |
| `/api/detect` | POST | Detects the language of the supplied text |
| `/api/translate` | POST | Translates text (max 5,000 chars) |

**`POST /api/translate` success response (200 OK):**
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

**Error response (400 / 500):**
```json
{ "status": "error", "message": "Input text cannot be empty." }
```

---

## 5. System Architecture & Tech Stack

### 5.1 Tech Stack
- **Backend:** Python 3 (Flask 3)
- **Translation Library:** `deep-translator` (free, no API key)
- **Detection Library:** `langdetect`
- **Frontend:** HTML5, vanilla CSS, vanilla JavaScript (`fetch`)

### 5.2 Project File Structure
```text
CodeAlpha_LanguageTranslationTool/
├── app.py                  # Flask app and REST API endpoints
├── translator_service.py   # Translation providers and detection
├── requirements.txt        # flask, requests, deep-translator, langdetect
├── .gitignore              # Git ignore rules
├── PRD.md                  # This document
├── README.md               # Setup and usage guide
├── test_translation.py     # 15 offline tests (mocked providers + API)
├── static/css/style.css    # Theme, layout and animations
├── static/js/app.js        # Client-side translation, copy and history
└── templates/index.html    # Single-page interface
```

### 5.3 Non-Functional Notes
- The development server binds to `127.0.0.1` with the Werkzeug debugger disabled by default; both are configurable via environment variables.
- All dynamic client-side text is HTML-escaped before insertion.
- Google Fonts are the only external front-end asset; the app otherwise has no build step.

---

## 6. UI Wireframe / Layout

```
+---------------------------------------------------------------------------------+
|  CodeAlpha — Task 1                                     [AI Online] [Mode]      |
+---------------------------------------------------------------------------------+
|  Translate, explore, be understood                                              |
|  High-performance AI translation across 51 global languages                     |
+---------------------------------------------------------------------------------+
|  [AI Internship]      [Deep Learning]      [Auto Detect]                        |
+---------------------------------------------------------------------------------+
|  [Source: Auto Detect v]  [X]      [ ⇄ ]      [Target: Spanish v]   [Copy]      |
|  +--------------------------------+           +-----------------------------+   |
|  | Enter text to translate...    |           | Translated text will appear |   |
|  |                                |           | here...                     |   |
|  +--------------------------------+           +-----------------------------+   |
|  | 15 chars • 3 words             |           | [Google Engine] 19 chars    |   |
|  +--------------------------------+           +-----------------------------+   |
+---------------------------------------------------------------------------------+
|                          [   Translate Text   ]                                 |
+---------------------------------------------------------------------------------+
|  History                                                     [Clear all]        |
+---------------------------------------------------------------------------------+
```

---

## 7. Implementation Plan

| Step | Action | Status |
| :--- | :--- | :--- |
| 1 | Install lightweight `requirements.txt` | ✅ |
| 2 | Build `app.py` with `/api/translate` and `/api/languages` | ✅ |
| 3 | Create responsive UI (`index.html`, `style.css`) | ✅ |
| 4 | Implement client logic (`app.js`): fetch, swap, copy, history | ✅ |
| 5 | Verify end-to-end with offline tests and write documentation | ✅ |

---

## 8. CodeAlpha Submission Checklist

- [x] Repository named `CodeAlpha_LanguageTranslationTool`
- [x] User can enter text and select source & target languages
- [x] Uses a translation API (`deep-translator` / Google Translate)
- [x] Displays translated text clearly with character count
- [x] One-click copy button works with feedback
- [x] Clean `README.md` with setup instructions and API guide
- [x] Record a brief video demo for LinkedIn tagging `@CodeAlpha` (submission step)
