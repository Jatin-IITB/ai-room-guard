"""
Speech recognition module - OPTIMIZED FOR CONVERSATION
"""
import speech_recognition as sr

class SpeechListener:
    """Google Speech Recognition optimized for intruder conversation"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # ✅ CONVERSATION thresholds (more sensitive than activation)
        self.recognizer.dynamic_energy_threshold = True  # ✅ Adapt during conversation
        self.recognizer.energy_threshold = 250  # ✅ Lower for conversation
        self.recognizer.pause_threshold = 1.2
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.8
        
        # Calibrate
        with self.microphone as source:
            print("🎤 Calibrating speech listener...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            
            # ✅ Set conversation-friendly bounds
            if self.recognizer.energy_threshold < 150:
                self.recognizer.energy_threshold = 200
            elif self.recognizer.energy_threshold > 500:
                self.recognizer.energy_threshold = 300
            
            print(f"✅ Conversation threshold: {self.recognizer.energy_threshold:.0f}")
    
    def listen_for_response(self, timeout=6):
        """Listen for intruder response with smart validation"""
        try:
            with self.microphone as source:
                print("🎧 Listening...")
                
                # Quick adjustment
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                # ✅ Don't force too high threshold during conversation
                if self.recognizer.energy_threshold > 500:
                    self.recognizer.energy_threshold = 300
                
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=10
                )
            
            # Recognize
            text = self.recognizer.recognize_google(audio, language='en-IN').strip()
            # ✅ Accept reasonable responses
            print(f"📝 '{text}'")
            return text
            
        except sr.WaitTimeoutError:
            print("⏰ Timeout")
            return None
        except sr.UnknownValueError:
            print("❓ Unclear")
            return None
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return None
