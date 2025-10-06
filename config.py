"""
Configuration for AI Room Guard
"""

# Paths
TRUSTED_FACES_DIR = "trusted_faces"
CAPTURES_DIR = "captures"
INTRUDER_DB_DIR = "intruder_database"

# Camera
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Face Recognition - STRICT SETTINGS
FACE_RECOGNITION_INTERVAL = 2  # seconds
UNKNOWN_THRESHOLD = 3  # detections before conversation
FACE_TOLERANCE = 0.5  # ✅ Stricter: lower = more strict (was 0.6)
MIN_CONFIDENCE = 0.55  # ✅ NEW: Reject if confidence < 0.55

# Conversation
CONVERSATION_TIMEOUT = 6
MAX_ESCALATION_LEVEL = 3

# LLM
LLM_MODEL = "phi3"

# TTS
TTS_RATE = 180
TTS_VOLUME = 1.0

# Activation
ACTIVATION_PHRASE = "Guard my room"
ACTIVATION_TIMEOUT = 10


# Siren Settings
SIREN_DURATION = 10.0        # Seconds
SIREN_VOLUME = 0.8          # 0.0-1.0
SIREN_PATTERN = [
    ('yelp', 3.5),  # 3.5s fast alternating
    ('wail', 4.0),  # 4.0s sweeping
    ('yelp', 2.5)   # 2.5s fast alternating
]