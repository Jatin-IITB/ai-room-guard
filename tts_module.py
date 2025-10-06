"""
Text-to-Speech module - Windows compatible
"""
import pyttsx3
import threading
import time

class TextToSpeech:
    """Simple, reliable TTS using pyttsx3"""
    
    def __init__(self, rate=180, volume=1.0):
        self.rate = rate
        self.volume = volume
        self.speaking = False
        self._lock = threading.Lock()
        print("✅ TTS initialized")
    
    def speak(self, text):
        """Speak text - thread-safe"""
        with self._lock:
            try:
                # Create new engine each time (fixes runAndWait error)
                engine = pyttsx3.init()
                engine.setProperty('rate', self.rate)
                engine.setProperty('volume', self.volume)
                
                print(f"🔊 Speaking: {text}")
                self.speaking = True
                engine.say(text)
                engine.runAndWait()
                engine.stop()
                self.speaking = False
                
            except Exception as e:
                print(f"⚠️ TTS error: {e}")
                self.speaking = False
    
    def speak_async(self, text):
        """Non-blocking speech"""
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()
        return thread
