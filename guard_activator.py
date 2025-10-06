"""
Voice activation module - PRONUNCIATION AWARE
"""
import speech_recognition as sr
from difflib import SequenceMatcher

class GuardActivator:
    """Smart voice activation handling Indian accent variations"""
    
    def __init__(self, activation_phrase="guard my room"):
        self.activation_phrase = activation_phrase.lower()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Balanced settings
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 1.0
        self.recognizer.phrase_threshold = 0.3
        
        # ✅ ALL common misrecognitions
        self.alternatives = [
            "guard my room",
            "guide my room",    # ✅ Most common!
            "god my room",
            "card my room",
            "guard the room",
            "guide the room",
            "guard ma room",
            "guide ma room",
            "gard my room",
            "guard room",
            "guide room"
        ]
        
        # Calibrate
        with self.microphone as source:
            print("🎤 Calibrating...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            
            if self.recognizer.energy_threshold < 150:
                self.recognizer.energy_threshold = 200
            elif self.recognizer.energy_threshold > 800:
                self.recognizer.energy_threshold = 400
            
            print(f"✅ Threshold: {self.recognizer.energy_threshold:.0f}")
    
    def _fuzzy_match(self, heard_text, threshold=0.65):
        """Match with pronunciation variants"""
        heard_lower = heard_text.lower().strip()
        
        # ✅ Exact match in alternatives
        for alt in self.alternatives:
            if alt in heard_lower:
                print(f"   ✓ Matched: '{alt}'")
                return True
        
        # ✅ Fuzzy match
        similarity = SequenceMatcher(None, self.activation_phrase, heard_lower).ratio()
        if similarity >= threshold:
            print(f"   ✓ Fuzzy: {similarity:.2f}")
            return True
        
        # ✅ Keyword variants (guard/guide + room)
        guard_words = ["guard", "guide", "god", "card", "gard"]
        room_words = ["room", "rum"]
        
        has_guard = any(word in heard_lower for word in guard_words)
        has_room = any(word in heard_lower for word in room_words)
        
        if has_guard and has_room:
            print(f"   ✓ Keywords match")
            return True
        
        print(f"   ✗ No match: {similarity:.2f}")
        return False
    
    def listen_for_activation(self, timeout=10, max_attempts=3):
        """Listen with retry logic"""
        
        for attempt in range(max_attempts):
            try:
                with self.microphone as source:
                    if attempt > 0:
                        print(f"🎧 Try {attempt + 1}/{max_attempts} - Say: 'GUARD MY ROOM'")
                    else:
                        print(f"🎧 Say: 'GUARD MY ROOM' (or 'GUIDE MY ROOM' works too)")
                    
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout, 
                        phrase_time_limit=5
                    )
                
                text = self.recognizer.recognize_google(audio, language='en-IN')
                self.last_heard = text
                print(f"📝 Heard: '{text}'")
                
                if self._fuzzy_match(text):
                    print("✅ ACTIVATED!")
                    return True
                else:
                    if attempt < max_attempts - 1:
                        print("⚠️ Not matched. Try again...")
                    continue
                
            except sr.WaitTimeoutError:
                print(f"⏰ Timeout")
                continue
            except sr.UnknownValueError:
                print(f"❓ Unclear")
                continue
            except Exception as e:
                print(f"⚠️ Error: {e}")
                continue
        
        return False
    
    def listen_for_activation_continuous(self):
        """Continuous listening"""
        print("\n" + "="*60)
        print("🎧 LISTENING FOR ACTIVATION")
        print("="*60)
        print("Say: 'GUARD MY ROOM' or 'GUIDE MY ROOM'")
        print("(Press Ctrl+C to cancel)")
        print("="*60 + "\n")
        
        while True:
            try:
                if self.listen_for_activation(timeout=15, max_attempts=1):
                    return True
            except KeyboardInterrupt:
                print("\n⚠️ Cancelled")
                return False
    
    def deactivate(self):
        print("🛑 Deactivated")