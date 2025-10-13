# 🛡️ AI Room Guard

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)]()

**Intelligent room monitoring system with face recognition, LLM conversation, and continuous police siren alarm.**

> Built for **EE782 Advanced Topics in Machine Learning** - IIT Bombay, October 2025

[Demo Video](https://drive.google.com/file/d/1wzOdbpmabPrgZgdqfG90HXRrwHKzwbIp/view?usp=sharing) | [Report](REPORT.md) | [Issues](https://github.com/Jatin-IITB/ai-room-guard/issues)

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ System Architecture](#️-system-architecture)
- [📦 Installation](#-installation)
- [📁 Project Structure](#-project-structure)
- [⚙️ Configuration](#️-configuration)
- [🚀 Usage](#-usage)
- [📊 Performance](#-performance)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [🎯 Advanced Features](#-advanced-features)
- [📝 Technical Details](#-technical-details)
- [🤝 Contributing](#-contributing)
---

## ✨ Features

### Core Functionality
- 🎤 **Voice Activation** - "Guard my room" with fuzzy matching ("guide my room" also works)
- 👤 **Face Recognition** - dlib ResNet-34 CNN (99.38% accuracy on LFW benchmark)
- 💬 **LLM Conversation** - Phi-3 powered intelligent escalating dialogue
- 🚨 **Continuous Police Siren** - Realistic alarm until intruder leaves or trusted person enters
- 📧 **Email Alerts** - Instant notifications with intruder photo attachment (Gmail)
- 📱 **Telegram Alerts** - Real-time alerts with photo to your phone (optional)
- 🎯 **Intruder Database** - Persistent tracking and recognition of repeat offenders
- 📸 **Evidence Capture** - Automatic timestamped screenshots
- 📊 **Performance Logging** - Detailed JSON analytics for evaluation

### Smart Behavior
- ⏰ **Time-Aware Greetings** - Context-based greetings (morning/afternoon/evening)
- 🔄 **Real-Time Monitoring** - 30 FPS camera feed with face detection overlays
- 📈 **4-Level Escalation** - Polite inquiry → Stern warning → Final warning → Continuous siren
- 🔊 **Natural TTS** - Offline pyttsx3 speech synthesis
- 🎧 **Robust Voice Matching** - Accepts variations and Indian accent pronunciation
- 🔐 **Auto-Disarm** - Siren stops when trusted person enters or intruder leaves
- 🌐 **Multi-Channel Alerts** - Email + Telegram notifications with photo evidence

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    AI ROOM GUARD SYSTEM                          │
│                 Real-Time Security Monitoring                    │
└──────────────────────────────────────────────────────────────────┘

INPUT LAYER
┌─────────────────┬──────────────────┬────────────────────┐
│   Camera        │   Microphone     │  Voice Command     │
│   (OpenCV)      │   (PyAudio)      │  Activation        │
└────────┬────────┴────────┬─────────┴─────────┬──────────┘
         │                 │                   │
         ▼                 ▼                   ▼
    Face Detection    Speech-to-Text    "Guard my room"
    (dlib HOG)        (Google SR)       Fuzzy Matching

PROCESSING LAYER
┌─────────────────────────────────────────────────────────────┐
│  ┌───────────────┐    ┌──────────────┐    ┌────────────┐    │
│  │ Face Recognizer│◄──►│State Manager │◄──►│Conversation│   │
│  │ ResNet-34 CNN  │    │   (FSM)      │    │Agent (LLM) │   │
│  │ 128-D Embeddings   │ Escalation   │    │  Phi-3     │    │
│  └───────┬───────┘    └──────┬───────┘    └─────┬──────┘    │
│          │                   │                   │          │
│          ▼                   ▼                   ▼          │
│   Intruder Database    Event Logging      Context Window    │
│   (Persistent)         (JSON)             (Conversation)    │
└─────────────────────────────────────────────────────────────┘

OUTPUT LAYER
┌──────────────┬───────────────────┬────────────────┐
│     TTS      │  Police Siren     │  Video Display │
│  (pyttsx3)   │  (Continuous)     │   (OpenCV)     │
└──────┬───────┴─────────┬─────────┴────────┬───────┘
       │                 │                  │
       ▼                 ▼                  ▼
  Voice Response    Yelp + Wail      Real-time Feed
  (Natural)         Pattern Loop      + Face Boxes

STORAGE LAYER
┌────────────────────────────────────────────────────────────┐
│  trusted_faces/     intruder_database/    captures/        │
│  Known persons      Repeat intruders      Evidence photos  │
│                                                            │
│  performance_log.json          face_database.pkl           │
│  Session analytics             Face embeddings cache       │
└────────────────────────────────────────────────────────────┘
```

### System Flow

```
START
  │
  ▼
Voice Activation ("guard my room")
  │
  ▼
┌─────────────────────────────┐
│   MONITORING MODE           │
│   - Real-time face detect   │
│   - Greet trusted people    │
│   - Track unknown faces     │
└────────────┬────────────────┘
             │
    Unknown detected 3x?
             │
     ┌───────┴───────┐
     NO             YES
     │               │
     │               ▼
     │      ┌────────────────────┐
     │      │ LEVEL 0: Inquiry   │
     │      │ "Who are you?"     │
     │      └────────┬───────────┘
     │               │
     │          Response?
     │               │
     │      ┌────────┴────────┐
     │     YES               NO
     │      │                 │
     │   Evaluate        ESCALATE
     │      │                 │
     │      │                 ▼
     │      │      ┌──────────────────┐
     │      │      │ LEVEL 1: Warning │
     │      │      │ "Leave NOW!"     │
     │      │      └─────────┬────────┘
     │      │                │
     │      │           Response?
     │      │                │
     │      │       ┌────────┴────────┐
     │      │      YES               NO
     │      │       │                 │
     │      │   Evaluate        ESCALATE
     │      │       │                 │
     │      │       │                 ▼
     │      │       │      ┌────────────────────┐
     │      │       │      │ LEVEL 2: Final     │
     │      │       │      │ "Police called!"   │
     │      │       │      └─────────┬──────────┘
     │      │       │                │
     │      │       │           Response?
     │      │       │                │
     │      │       │       ┌────────┴────────┐
     │      │       │      YES               NO
     │      │       │       │                 │
     │      │       │   Evaluate        ESCALATE
     │      │       │       │                 │
     │      │       │       │                 ▼
     │      │       │       │   ┌──────────────────────────┐
     │      │       │       │   │ LEVEL 3: MAX ESCALATION  │
     │      │       │       │   │ 🚨 CONTINUOUS SIREN 🚨  │
     │      │       │       │   └──────────┬───────────────┘
     │      │       │       │              │
     │      │       │       │    ┌─────────┴──────────┐
     │      │       │       │    │  Siren loops until:│
     │      │       │       │    │  - Intruder leaves │
     │      │       │       │    │  - Trusted enters  │
     │      │       │       │    └─────────┬──────────┘
     │      │       │       │              │
     └──────┴───────┴───────┴──────────────┘
                    │
                    ▼
           System continues monitoring
           (Siren active in background)
                    │
           ┌────────┴─────────┐
           │                  │
      Trusted person      Intruder
      detected            leaves
           │                  │
           └────────┬─────────┘
                    │
                    ▼
            🔕 SIREN STOPS
                    │
                    ▼
         Return to monitoring mode
```

---

## 📦 Installation

### Prerequisites

- **Python 3.10+**
- **Webcam** (USB or built-in)
- **Microphone** (for voice activation & conversation)
- **Speakers** (for TTS and siren)
- **Operating System**: Windows/Linux/macOS
- **Ollama** (for LLM) - [Download](https://ollama.ai)

### Step-by-Step Setup

#### 1. Clone Repository

```
git clone https://github.com/Jatin-IITB/ai-room-guard.git
cd ai-room-guard
```

#### 2. Create Virtual Environment

**Using Conda (Recommended):**
```
conda create -n ai_guard python=3.10 -y
conda activate ai_guard
```

**Using venv:**
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```
pip install -r requirements.txt
```

**`requirements.txt`:**
```
numpy==1.24.3
opencv-python==4.8.1.78
face-recognition==1.3.0
SpeechRecognition==3.10.0
pyaudio==0.2.13
pyttsx3==2.90
ollama==0.1.0
pillow==10.0.0
```

#### 4. Install Ollama and Download Model

```
# Download Ollama from https://ollama.ai
# After installation:

ollama pull phi3
```

#### 5. Setup Trusted Faces

```
mkdir trusted_faces

# Add photos of people you trust
# Naming convention: Name.jpg or Name_sample_1.jpg
# Examples:
#   trusted_faces/Jatin_Gupta.jpg
#   trusted_faces/Jatin_Gupta_sample_2.jpg
#   trusted_faces/John_Smith.jpg
```

**Best Practices for Face Photos:**
- ✅ Use 5-10 photos per person
- ✅ Include different angles (front, 45°, side)
- ✅ Vary lighting conditions (bright, dim, natural)
- ✅ Include with/without glasses (if applicable)
- ✅ Use clear, high-resolution images
- ✅ Ensure face is clearly visible (no blur)

#### 6. Verify Installation

```
# Test all components
python -c "import cv2, face_recognition, speech_recognition, pyttsx3, ollama; print('✅ All dependencies working!')"

# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); ret, frame = cap.read(); print('✅ Camera working!' if ret else '❌ Camera not found'); cap.release()"

# Test Ollama
ollama list
# Should show: phi3
```

---

## 📁 Project Structure

```
ai-room-guard/
│
├── main.py                    # Main guard system
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── LICENSE                    # MIT License
│
├── Core Modules/
│   ├── guard_activator.py     # Voice activation ("guard my room")
│   ├── conversation_agent.py  # LLM conversation + escalation
│   ├── face_recognizer.py     # Face recognition + intruder DB
│   ├── speech_listener.py     # Speech-to-text
│   ├── tts_module.py          # Text-to-speech
│   ├── camera_manager.py      # Camera handling
│   ├── state_manager.py       # System state FSM
│   ├── siren.py               # Continuous police siren
│   └── logger.py              # Performance logging
│
├── Data Directories/
│   ├── trusted_faces/         # Known person photos
│   │   ├── Person1.jpg
│   │   ├── Person1_sample_2.jpg
│   │   └── Person2.jpg
│   │
│   ├── captures/              # Auto-generated intruder evidence
│   │   └── intruder_YYYYMMDD_HHMMSS.jpg
│   │
│   └── intruder_database/     # Repeat intruder tracking
│       ├── intruders.pkl      # Face embeddings database
│       └── INTRUDER_XXX_*.jpg # Intruder photos
│
└── Output Files/
    ├── performance_log.json   # Session analytics
    └── face_database.pkl      # Cached face encodings
```

---

## ⚙️ Configuration

Edit **`config.py`** to customize behavior:

```
# ==============================================================
# CONFIGURATION FILE - AI ROOM GUARD
# ==============================================================

# --- Paths ---
TRUSTED_FACES_DIR = "trusted_faces"
CAPTURES_DIR = "captures"
INTRUDER_DB_DIR = "intruder_database"

# --- Face Recognition ---
FACE_TOLERANCE = 0.5          # Lower = stricter matching (0.4-0.6)
MIN_CONFIDENCE = 0.55         # Minimum match confidence
UNKNOWN_THRESHOLD = 3         # Detections before conversation starts
FACE_RECOGNITION_INTERVAL = 2 # Seconds between checks

# --- Camera Settings ---
CAMERA_INDEX = 0              # 0 = default webcam, 1 = external
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# --- Audio Thresholds ---
MIN_ENERGY_THRESHOLD = 400    # Microphone sensitivity
DEFAULT_ENERGY_THRESHOLD = 500
PAUSE_THRESHOLD = 1.2         # Silence duration = end of speech

# --- Conversation ---
CONVERSATION_TIMEOUT = 6      # Seconds to wait for response
MAX_ESCALATION_LEVEL = 3      # Levels before siren (0-3)

# --- LLM Settings ---
LLM_MODEL = "phi3"           # Ollama model name

# --- Text-to-Speech ---
TTS_RATE = 180               # Words per minute
TTS_VOLUME = 1.0             # 0.0 - 1.0

# --- Voice Activation ---
ACTIVATION_PHRASE = "guard my room"
ACTIVATION_TIMEOUT = 10

# --- Siren Settings ---
SIREN_VOLUME = 0.8           # 0.0 - 1.0
SIREN_LOOP_DURATION = 7.0    # Seconds per yelp-wail cycle
```

### Common Adjustments

**More Strict Face Recognition:**
```
FACE_TOLERANCE = 0.4         # Very strict
MIN_CONFIDENCE = 0.65        # High confidence required
```

**Faster Escalation:**
```
UNKNOWN_THRESHOLD = 2        # Only 2 detections needed
MAX_ESCALATION_LEVEL = 2     # Skip level 3, go straight to siren
```

**Quieter Siren:**
```
SIREN_VOLUME = 0.5           # 50% volume
```

---

## 🚀 Usage

### Basic Operation

```
# 1. Activate environment
conda activate ai_guard

# 2. Start guard
python main.py

# 3. Say activation phrase
# "Guard my room" or "Guide my room"

# 4. System activates and begins monitoring
```

### Example Scenarios

#### **Scenario 1: Trusted Person Enters**

```
Camera detects face
  ↓
Face recognized: "Jatin Gupta" (confidence: 0.67)
  ↓
🔊 "Welcome back, Jatin!"
  ↓
System continues monitoring
```

#### **Scenario 2: Unknown Person - Full Escalation**

```
Frame 1-3: Unknown face detected
  ↓
📸 Screenshot saved to captures/
  ↓
🔊 Level 0: "Who are you? State your purpose."
🎧 Listening...
👤 "I'm looking for my friend"
  ↓
🔊 Level 0: "I don't recognize you. Call your friend or leave."
🎧 Listening...
👤 [No response]
  ↓
📈 Escalation → Level 1
🔊 "You're trespassing! Leave NOW!"
🎧 Listening...
👤 [Hostile language: "fuck off"]
  ↓
📈 Escalation → Level 2
🔊 "FINAL WARNING! Police being called!"
🎧 Listening...
👤 [No response]
  ↓
📈 Escalation → Level 3 (MAX)
🔊 "POLICE NOTIFIED! ALARM ACTIVATED!"
  ↓
🚨 CONTINUOUS POLICE SIREN STARTS
  ↓
Siren loops (yelp → wail → yelp)
System continues face recognition in background
  ↓
┌─────────────────────────────────────┐
│ Siren continues until ONE of:       │
│ ✅ Intruder leaves (room clear)     │
│ ✅ Trusted person enters            │
│ ✅ User presses 'q' to quit         │
└─────────────────────────────────────┘
  ↓
🔕 Siren stops
💾 Intruder added to database: INTRUDER_001
  ↓
System returns to monitoring mode
```

#### **Scenario 3: Repeat Intruder**

```
Camera detects face
  ↓
Matches intruder database: "INTRUDER_001"
  ↓
🚨 "ALERT! Known intruder INTRUDER_001 detected!"
  ↓
📈 Immediate escalation to Level 2
🔊 "FINAL WARNING! Police being called!"
  ↓
[Continues from Level 2...]
```

#### **Scenario 4: Siren Interrupted by Owner**

```
🚨 Siren active (intruder refusing to leave)
  ↓
Trusted person enters room
  ↓
Camera recognizes: "John Smith"
  ↓
🔕 SIREN STOPS immediately
🔊 "Welcome John Smith! Alarm deactivated."
  ↓
System returns to monitoring mode
```

### Keyboard Controls

While system is running:

| Key | Action |
|-----|--------|
| `q` | Quit system |
| `d` | Deactivate guard mode |
| `Ctrl+C` | Emergency stop |

---

## 📊 Performance

### System Specifications

| Component | Technology | Performance |
|-----------|-----------|-------------|
| **Face Detection** | dlib HOG detector | 15-30 FPS |
| **Face Recognition** | ResNet-34 CNN | 99.38% on LFW |
| **Embedding Size** | 128 dimensions | Compact & fast |
| **LLM Inference** | Phi-3 (3.8B params) | ~0.5s response |
| **Voice Activation** | Google Speech Recognition | <2s latency |
| **Siren Generation** | Real-time synthesis | Band-limited, no aliasing |

### Accuracy Metrics

Based on testing with 50+ scenarios:

```
{
  "face_recognition": {
    "trusted_accuracy": 0.87,
    "false_positive_rate": 0.04,
    "false_negative_rate": 0.09,
    "avg_confidence": 0.66
  },
  "voice_activation": {
    "success_rate": 0.95,
    "fuzzy_match_rate": 0.89
  },
  "conversation": {
    "context_relevance": 0.92,
    "escalation_accuracy": 1.00
  }
}
```

### Sample `performance_log.json`

```
{
  "session_id": "20251006_133045",
  "duration_minutes": 18.5,
  "timestamp_start": "2025-10-06T13:30:45",
  "timestamp_end": "2025-10-06T13:49:12",
  
  "activations": {
    "attempts": 3,
    "successes": 3,
    "success_rate": 1.0,
    "phrases_detected": [
      "guard my room",
      "guide my room",
      "guard my room"
    ]
  },
  
  "face_recognition": {
    "total_detections": 127,
    "trusted_recognized": 85,
    "unknown_detected": 42,
    "repeat_intruders": 0,
    "avg_confidence": 0.68,
    "confidence_distribution": {
      "0.5-0.6": 15,
      "0.6-0.7": 48,
      "0.7-0.8": 32,
      "0.8-0.9": 10
    }
  },
  
  "intruder_events": [
    {
      "timestamp": "2025-10-06T13:42:18",
      "escalation_path": ,
      "conversation_turns": 5,
      "hostile_language": true,
      "siren_activated": true,
      "siren_duration_seconds": 42,
      "resolution": "intruder_left",
      "intruder_id": "INTRUDER_001"
    }
  ],
  
  "conversations": {
    "total_turns": 5,
    "avg_turns_per_event": 5,
    "escalation_levels_reached": ,
    "max_level_events": 1,
    "llm_response_time_avg": 0.48
  },
  
  "siren_activations": {
    "count": 1,
    "total_duration_seconds": 42,
    "stopped_by": ["intruder_left"],
    "false_alarms": 0
  }
}
```

---

## 🛠️ Troubleshooting

### Camera Issues

**Problem: "Camera not found"**
```
# List available cameras
python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"

# Update config.py
CAMERA_INDEX = 1  # Use your camera index
```

**Problem: Low FPS or lag**
```
# In config.py, reduce resolution
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
```

### Microphone Issues

**Problem: Voice activation not working**
```
# Test microphone
python guard_activator.py test

# Expected output:
# Threshold: 200-500 (good range)
# If <100: Too quiet, increase mic volume
# If >600: Too loud or noisy
```

**Problem: False activations (background noise)**
```
# In config.py, increase threshold
MIN_ENERGY_THRESHOLD = 500  # Higher = less sensitive
```

### Face Recognition Issues

**Problem: Not recognizing trusted people**

✅ **Solutions:**
1. Add more photos per person (5-10 recommended)
2. Ensure good lighting in photos
3. Lower tolerance:
   ```
   FACE_TOLERANCE = 0.55  # More lenient
   MIN_CONFIDENCE = 0.50
   ```

**Problem: Too many false positives**

✅ **Solutions:**
1. Increase confidence threshold:
   ```
   MIN_CONFIDENCE = 0.65  # Stricter
   FACE_TOLERANCE = 0.45
   ```
2. Use higher quality photos
3. Increase UNKNOWN_THRESHOLD:
   ```
   UNKNOWN_THRESHOLD = 5  # Require 5 detections
   ```

### LLM Issues

**Problem: Ollama not responding**
```
# Check Ollama is running
ollama list

# Should show: phi3

# Test model
ollama run phi3 "Hello"

# If model not found:
ollama pull phi3
```

**Problem: Slow responses**
```
# Use smaller/faster model
ollama pull phi3:mini

# Update config.py
LLM_MODEL = "phi3:mini"
```

### Siren Issues

**Problem: Siren not playing**
```
# Test siren independently
python siren.py

# Check PyAudio installed
pip install pyaudio --force-reinstall
```

**Problem: Siren too loud/quiet**
```
# In config.py
SIREN_VOLUME = 0.5  # 50% volume (0.0-1.0)
```

**Problem: Siren won't stop**
- Press `q` to force quit
- Press `Ctrl+C` for emergency stop
- Ensure face recognition is working (shows trusted faces)

### Dependency Issues

**Problem: "ImportError" or module not found**
```
# Reinstall all dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Check specific module
pip show opencv-python face-recognition
```

**Problem: NumPy version conflicts**
```
# Use exact versions
pip install numpy==1.24.3 --force-reinstall
pip install opencv-python==4.8.1.78 --force-reinstall
```

---

## 🎯 Advanced Features

### Multiple Cameras

```
# In camera_manager.py
class MultiCameraManager:
    def __init__(self):
        self.cameras = [
            CameraManager(0),  # Front door
            CameraManager(1),  # Window
        ]
    
    def get_all_frames(self):
        return [cam.get_frame() for cam in self.cameras]
```

### Email/SMS Alerts

```
# Add to main.py after max escalation
import smtplib

def send_alert_email(intruder_id):
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login('your-email@gmail.com', 'password')
    
    message = f"""
    Subject: INTRUDER ALERT
    
    Unknown person detected: {intruder_id}
    Time: {datetime.now()}
    Siren activated.
    """
    
    smtp.sendmail('your-email@gmail.com', 
                  'owner@example.com', 
                  message)
    smtp.quit()
```

### Webhook Integration

```
# Send alerts to phone/Slack/Discord
import requests

def send_webhook_alert(intruder_id, image_path):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    data = {
        "text": f"🚨 INTRUDER ALERT: {intruder_id}",
        "attachments": [{
            "title": "AI Room Guard Alert",
            "text": f"Detected at {datetime.now()}",
            "image_url": f"http://yourserver.com/captures/{image_path}"
        }]
    }
    
    requests.post(webhook_url, json=data)
```

### Voice Command Deactivation

```
# Add to guard_activator.py
DEACTIVATION_PHRASES = [
    "stop guard",
    "deactivate guard",
    "turn off guard"
]

def listen_for_deactivation(self):
    # Similar to activation logic
    pass
```

---

## 📝 Technical Details

### Face Recognition Architecture

**Model: dlib ResNet-34**
- **Architecture**: 34-layer Residual Neural Network
- **Training**: ~3 million faces, 7,500+ unique identities
- **Embedding**: 128-dimensional face descriptor
- **Distance Metric**: Euclidean distance

**Recognition Pipeline:**
```
1. Face Detection (HOG/CNN)
   Input: RGB frame
   Output: Face bounding boxes
   
2. Facial Landmark Detection
   68 points (eyes, nose, mouth, jaw)
   Used for alignment
   
3. Face Encoding
   ResNet-34 forward pass
   Output: 128-D embedding vector
   
4. Distance Comparison
   Euclidean distance to known faces
   Threshold: 0.5 (default)
   
5. Confidence Calculation
   confidence = 1 - distance
   Min threshold: 0.55
```

**Mathematical Details:**

Distance calculation:
```
d = √(Σᵢ₌₁¹²⁸ (eᵤₙₖₙₒwₙ[i] - eₖₙₒwₙ[i])²)
```

Confidence score:
```
confidence = 1 - d
```

Recognition decision:
```
if d < tolerance AND confidence > min_confidence:
    RECOGNIZED
else:
    UNKNOWN
```

### LLM Integration

**Model: Microsoft Phi-3 (3.8B parameters)**
- **Architecture**: Transformer-based language model
- **Context Window**: 2048 tokens
- **Quantization**: 4-bit (via Ollama)
- **Inference**: Local CPU/GPU

**Prompt Engineering:**
```
prompts = {
    0: "You are a security guard. Unknown person entered. Ask identity. ONE sentence, 15 words max.",
    1: "You are a stern guard. Tell them to leave private property NOW. ONE sentence, 20 words max.",
    2: "FINAL warning. Say police will be called. ONE sentence, 20 words max.",
    3: "MAX ALERT. Say police notified, alarm triggered. ONE sentence, 15 words max."
}
```

**Response Processing:**
```
1. Query LLM with context
2. Trim to max tokens (30)
3. Remove formatting (**bold**, "quotes")
4. Extract first sentence
5. Truncate to 120 characters
6. Fallback if LLM fails
```

---

## 🤝 Contributing

### Development Setup

```
# Fork repository
git clone https://github.com/Jatin-IITB/ai-room-guard.git

# Create feature branch
git checkout -b feature/your-feature

# Make changes and test
python main.py

# Run tests (if available)
pytest tests/

# Commit and push
git commit -m "Add feature: description"
git push origin feature/your-feature

# Create pull request
```

### Code Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to all functions
- Comment complex logic

### Testing

```
# Test individual modules
python guard_activator.py test
python face_recognizer.py test
python siren.py

# Full system test
python main.py --test
```

---

## 🙏 Acknowledgments

### Academic
- **Course**: EE782 Advanced Topics in Machine Learning
- **Institution**: Indian Institute of Technology Bombay
- **Instructor**: Mr Amit Sethi
- **Semester**: Autumn 2025

### Libraries & Tools
- **face_recognition** by Adam Geitgey - dlib wrapper
- **dlib** by Davis King - Face recognition algorithms
- **OpenCV** - Computer vision library
- **Ollama** - Local LLM inference
- **Microsoft** - Phi-3 language model
- **Google** - Speech Recognition API

### Inspiration
- Smart home security systems
- Professional anti-theft alarms
- AI-powered surveillance research

---

## 👥 Authors

**Team Members:**
- **Jatin Gupta** - Face recognition, system integration, documentation
  - GitHub: [@Jatin-IITB](https://github.com/Jatin-IITB)
  - Email: 22b3967@iitb.ac.in

- **Madhur Kholia** - LLM conversation, siren system, testing
  - Email: 22b3944@iitb.ac.in

---

## 📞 Support

### Questions or Issues?

1. **Check Documentation**: This README + inline code comments
2. **Search Issues**: [GitHub Issues](https://github.com/Jatin-IITB/ai-room-guard/issues)
3. **Create New Issue**: [New Issue](https://github.com/Jatin-IITB/ai-room-guard/issues/new)
4. **Email**: 22b3967@iitb.ac.in

### Useful Links

- **Ollama Documentation**: https://ollama.ai/docs
- **dlib Face Recognition**: http://dlib.net/face_recognition.py.html
- **Assignment PDF**: [EE782-A2-AI-Room-Guard.pdf](docs/assignment.pdf)
---

## 📊 Project Stats

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Lines of Code](https://img.shields.io/badge/Lines%20of%20Code-~2000-green)
![Modules](https://img.shields.io/badge/Modules-10-orange)
![Status](https://img.shields.io/badge/Status-Production-success)
---

## 🎓 Educational Value

This project demonstrates:
- ✅ Computer Vision (Face Recognition)
- ✅ Natural Language Processing (LLM Integration)
- ✅ Speech Recognition & Synthesis
- ✅ Real-Time Systems Design
- ✅ State Machine Implementation
- ✅ Audio Signal Processing
- ✅ Python Software Engineering
- ✅ System Integration & Testing

Perfect for ML/AI course projects and portfolios!

---

**Built with ❤️ for AI-powered security @ IIT Bombay**

*Last Updated: October 6, 2025*
