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
ALERTS_ENABLED = True  # Set to False to disable all alerts
SEND_EMAIL_ALERTS = True  # Set to False to disable email alerts
SEND_TELEGRAM_ALERTS = True  # Set to False to disable Telegram alerts




# ============================================================
# EMAIL ALERTS (Gmail)
# ============================================================

EMAIL_ENABLED = True  # Set to False to disable

# Gmail account credentials
EMAIL_FROM = ""
EMAIL_PASSWORD = ""  # Use App Password, not regular password

# Recipients (can be list or single email)
EMAIL_TO = [
    "22b3967@iitb.ac.in",
    "22b3944@iitb.ac.in"
]

# Instructions to get Gmail App Password:
# 1. Go to https://myaccount.google.com/security
# 2. Enable 2-Step Verification
# 3. Go to https://myaccount.google.com/apppasswords
# 4. Generate new app password
# 5. Use that 16-character password above

TELEGRAM_ENABLED = True  # Set to False to disable

# Telegram Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN = ""

# Your Telegram Chat ID (from @userinfobot)
TELEGRAM_CHAT_ID = ""

# Instructions to setup Telegram:
# 1. Open Telegram and search for @BotFather
# 2. Send /newbot and follow instructions
# 3. Copy the bot token (looks like above)
# 4. Search for @userinfobot on Telegram
# 5. Start chat and it will send your chat ID
# 6. Message your bot to activate it
# 7. Use token and chat ID above
