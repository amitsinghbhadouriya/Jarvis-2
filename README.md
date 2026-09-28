# Jarvis 2 - Intelligent Desktop AI Voice Assistant

<div align="center">
  <img src="frontend/assets/images/logo.ico" alt="Jarvis Logo" width="96" height="96" />
  <p><strong>A futuristic desktop voice assistant featuring biometric facial authentication, real-time audio synthesis, and an interactive sci-fi HUD.</strong></p>
</div>

---

## 🚀 Overview

**Jarvis 2** is a modular, high-performance desktop assistant combining a **Python Eel** backend with a responsive **HTML5/Bootstrap** holographic HUD. It incorporates OpenCV for face recognition on launch, `pyttsx3` for local text-to-speech synthesis, Google Speech-to-Text for voice commands, and SQLite for conversation memory and contacts management.

---

## ✨ Key Features

- **Biometric Face Authentication**: Uses OpenCV Haar Cascades with multi-backend camera probing and graceful fallback.
- **Natural Voice & Chat I/O**: Dual-mode interaction supporting spoken voice commands and typed chat.
- **Sci-Fi Holographic HUD**: Interactive canvas particle sphere, Lottie animations, and SiriWave audio visualizer.
- **Conversational & System Intents**:
  - 🕒 Time & Date inquiries
  - 📊 Real-time hardware telemetry (CPU, RAM, Battery, OS)
  - 🌐 Search & Media (Google, YouTube, Wikipedia summaries)
  - 🖥️ Desktop app launcher (Notepad, Calculator, Command Prompt, etc.)
  - 📇 SQLite Contacts directory and CSV batch import
  - 📝 Quick notes and memos
  - 🎭 Small-talk and humor engine
- **Audio Feedback**: Custom high-fidelity WAV sound effects for startup, success, and error alerts.
- **Enterprise-Grade Architecture**: Zero XSS vulnerabilities, input sanitization, background worker queues, and structured logging.

---

## 📁 Project Structure

```plaintext
jarvis-2/
├── backend/
│   ├── auth/              # Facial recognition & biometric verification
│   ├── command/           # Command dispatcher and domain handlers
│   │   └── handlers/      # System, search, apps, notes, contacts, conversation
│   ├── feature/           # Speech synthesis (TTS), recognition (STT), hotword
│   ├── utils/             # Audio playback, hardware telemetry, input sanitization
│   ├── config.py          # Centralized configuration & environment loader
│   ├── database.py        # SQLite persistence layer (history, contacts, settings)
│   └── logger.py          # Standardized logging framework
├── frontend/
│   ├── assets/            # Audio chimes, images, and vendor libraries
│   ├── controller.js      # Eel frontend bindings, toasts, and DOM rendering
│   ├── index.html         # HUD interface, offcanvas chat drawer, and settings
│   ├── main.js            # User interactions, keyboard shortcuts, event handlers
│   ├── script.js          # Optimized 60fps canvas particle sphere
│   └── style.css          # Arc-Reactor cyber theme and responsive layout
├── tests/                 # 100% green unit & integration test suite
├── .env.example           # Environment configuration template
├── pyproject.toml         # Package metadata and QA tool configurations
├── pytest.ini             # Pytest discovery configuration
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Testing and development dependencies
├── main.py                # Main application entry point
└── run.py                 # Multi-process orchestrator (GUI + hotword daemon)
```

---

## 🛠️ Getting Started

### 1. Prerequisites
- Python 3.9+ (Python 3.10+ recommended)
- A working microphone and camera (optional for headless mode)

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/amitsinghbhadouriya/Jarvis-2.git
cd jarvis-2

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the sample environment file:

```bash
cp .env.example .env
```

Tune any desired parameters in `.env`:
- `TTS_RATE`: Speech speed (default: `175` words/min)
- `HOTWORD`: Wake word (default: `jarvis`)
- `FACE_AUTH_ENABLED`: Set to `True` or `False`

### 4. Running the Assistant

To start both the assistant GUI and background hotword listener:

```bash
python run.py
```

Or run the GUI server directly:

```bash
python main.py
```

---

## ⌨️ Keyboard & Voice Shortcuts

- **Ctrl + J** (or **Cmd + J** on macOS): Instantly activate listening mode.
- **Enter**: Submit typed chat message.
- **Hotword "Jarvis"**: Wake assistant via background microphone daemon.

---

## 🧪 Running the Test Suite

Jarvis includes a comprehensive `pytest` test suite covering database persistence, command intent dispatching, sanitization, audio managers, and biometric mocks:

```bash
pytest
```

---

## 🔒 Security & Privacy

- All user inputs are sanitized against XSS injection before DOM rendering.
- Database records and speech operations run locally without external cloud telemetry.
- Applications are launched securely using validated binaries without raw shell execution.

---

## 📄 License

Licensed under the MIT License. Built with ❤️ for advanced desktop AI automation.
