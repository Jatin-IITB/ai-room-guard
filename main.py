"""
AI Room Guard - Main System (FIXED VERSION)
"""
import time
import threading
from queue import Queue
import datetime
import cv2
import os
import face_recognition

from config import *
from tts_module import TextToSpeech
from speech_listener import SpeechListener
from conversation_agent import ConversationAgent
from face_recognizer import FaceRecognizer
from camera_manager import CameraManager
from state_manager import StateManager
from guard_activator import GuardActivator
from logger import PerformanceLogger
from siren import EmergencySiren
class AIRoomGuard:
    """Complete AI Room Guard System - FIXED"""
    
    def __init__(self):
        print("\n" + "="*60)
        print("🤖 INITIALIZING AI ROOM GUARD")
        print("="*60)
        
        self.activator = GuardActivator(ACTIVATION_PHRASE)
        self.camera = CameraManager(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT)
        self.state = StateManager()
        self.recognizer = FaceRecognizer(TRUSTED_FACES_DIR, INTRUDER_DB_DIR, FACE_TOLERANCE)
        self.tts = TextToSpeech(TTS_RATE, TTS_VOLUME)
        self.listener = SpeechListener()
        self.agent = ConversationAgent(LLM_MODEL)
        self.logger = PerformanceLogger()
        self.siren = EmergencySiren(SIREN_VOLUME)
        # State
        self.conversation_queue = Queue()
        self.speaking = False
        self.listening = False
        self.last_greeted = {}
        self.conversation_lock = threading.Lock()  # ✅ Prevent overlapping conversations
        self.start_time = time.time()
        print("✅ ALL SYSTEMS READY!")
        print("="*60)
    
    def wait_for_activation(self):
        """Wait for voice activation with continuous mode"""
        print("\n" + "="*60)
        print("🎧 VOICE ACTIVATION")
        print("="*60)
        print("Say clearly: 'Guard my room'")
        print("(The system will keep listening until you say it)")
        print("="*60 + "\n")
        
        # Use continuous listening mode
        if self.activator.listen_for_activation_continuous():
            self.logger.log_activation(
                phrase_heard=self.activator.last_heard,
                success=True,
                confidence=1.0
            )
            self.state.activate_guard()
            self.tts.speak("Guard mode activated. Monitoring your room now.")
            return True
        else:
            self.logger.log_activation(
                phrase_heard=self.activator.last_heard,
                success=False,
                confidence=0.0
            )
        return False
    
    def speak_async(self, text):
        """Non-blocking speech"""
        def _speak():
            self.speaking = True
            self.tts.speak(text)
            self.speaking = False
        
        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()
        return thread
    
    def listen_async(self):
        """Non-blocking listening"""
        def _listen():
            # Wait for speaking to finish
            while self.speaking:
                time.sleep(0.2)
            
            self.listening = True
            response = self.listener.listen_for_response(timeout=CONVERSATION_TIMEOUT)
            self.conversation_queue.put(response)
            self.listening = False
        
        thread = threading.Thread(target=_listen, daemon=True)
        thread.start()
        return thread
    
    def greet_known_person(self, name):
        """Greet recognized person"""
        current_time = time.time()
        
        # Don't repeat within 60 seconds
        if name in self.last_greeted and (current_time - self.last_greeted[name]) < 60:
            return
        
        self.last_greeted[name] = current_time
        
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            greeting = f"Good morning, {name}!"
        elif 12 <= hour < 17:
            greeting = f"Good afternoon, {name}!"
        elif 17 <= hour < 21:
            greeting = f"Welcome back, {name}!"
        else:
            greeting = f"Working late, {name}?"
        
        print(f"👋 {greeting}")
        self.speak_async(greeting)
    
    def handle_conversation_turn(self, intruder_reply=None):
        """Handle one conversation turn - thread-safe"""
        def _converse():
            with self.conversation_lock:  # ✅ Prevent overlapping
                response = self.agent.get_response(user_input=intruder_reply)
                self.logger.log_conversation(
                    level=self.agent.escalation_level,
                    guard_response=response,
                    intruder_input=intruder_reply
                )
                # Wait a bit before speaking if still processing previous
                while self.speaking or self.listening:
                    time.sleep(0.3)
                
                self.speak_async(response)
                
                # Wait for speech to finish before listening
                time.sleep(0.5)
                self.listen_async()
        
        thread = threading.Thread(target=_converse, daemon=True)
        thread.start()
    
    def monitor_room(self):
        """Main monitoring loop"""
        print("\n" + "="*60)
        print("👁️  MONITORING ROOM")
        print("="*60)
        print("Press 'q' to quit | 'd' to deactivate\n")
        
        self.camera.start()
        time.sleep(1)  # ✅ Let camera stabilize
        
        unknown_count = 0
        last_check_time = time.time()
        in_conversation = False
        waiting_for_response = False
        intruder_encoding = None
        intruder_added = False
        consecutive_unknown = 0  # ✅ Track consecutive unknown frames
        siren_active=False
        frames_since_clear=0
        
        try:
            while self.state.guard_active:
                frame = self.camera.get_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                current_time = time.time()
                
                # ✅ ONLY do face recognition when NOT in active conversation
                if not in_conversation and not self.speaking and not self.listening:
                    if (current_time - last_check_time >= FACE_RECOGNITION_INTERVAL):
                        
                        # Face recognition
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        face_locations = face_recognition.face_locations(rgb_frame)
                        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                        
                        results = []
                        for encoding in face_encodings:
                            name, intruder_id = self.recognizer._identify_face(encoding)
                            if name!= "Unknown":
                                if self.recognizer.known_encodings:
                                    distances = face_recognition.face_distance(self.recognizer.known_encodings, encoding)
                                    confidence= 1- min(distances) if len(distances)>0 else 0.0
                                    self.logger.log_recognition(name=name, confidence=confidence, correct=True)
                            results.append((name, intruder_id, encoding))
                        
                        has_unknown = any(name in ["Unknown", "REPEAT_INTRUDER"] for name, _, _ in results)
                        has_known = any(name not in ["Unknown", "REPEAT_INTRUDER"] for name, _, _ in results)
                        if siren_active and has_known:
                            print("✅ Trusted person detected - stopping siren")
                            self.siren.stop()
                            siren_active=False
                            for name, _, _ in results:
                                if name not in ["Unknown", "REPEAT_INTRUDER"]:
                                    self.speak_async(f"Welcome {name}! Alarm deactivated.")
                            in_conversation=False
                            waiting_for_response=False
                            unknown_count=0
                            self.agent.reset()
                            self.state.end_conversation()
                            continue
                        if siren_active and not has_unknown and not has_known:
                            frames_since_clear+=1
                            if frames_since_clear>=30: # 30 frames ~1 second
                                print("✅ ROOM CLEAR - STOPPING SIREN")
                                self.siren.stop()
                                siren_active=False
                                self.speak_async("Intruder has left. Alarm Deactivated")

                                #Reset State
                                in_conversation=False
                                waiting_for_response=False
                                unknown_count=0
                                self.agent.reset()
                                self.state.end_conversation()
                                frames_since_clear=0
                                continue
                        else:
                            frames_since_clear=0
                        # ✅ Greet known people (only if no conversation)
                        if has_known and not siren_active:
                            for name, intruder_id, _ in results:
                                if name not in ["Unknown", "REPEAT_INTRUDER"]:
                                    self.greet_known_person(name)
                            
                            # Reset unknown count
                            if unknown_count > 0:
                                print("✅ Trusted person. Resetting.")
                                unknown_count = 0
                                consecutive_unknown = 0
                        
                        # ✅ Handle unknowns with stricter criteria
                        if has_unknown and not has_known and not siren_active:
                            consecutive_unknown += 1
                            
                            # Only count if seen in multiple consecutive frames
                            if consecutive_unknown >= 2:  # ✅ Must appear 2+ times
                                unknown_count += 1
                                consecutive_unknown = 0
                                print(f"⚠️ Unknown person! ({unknown_count}/{UNKNOWN_THRESHOLD})")
                                
                                # Save evidence
                                os.makedirs(CAPTURES_DIR, exist_ok=True)
                                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                
                                for name, intruder_id, encoding in results:
                                    if name == "REPEAT_INTRUDER":
                                        print(f"🚨 KNOWN INTRUDER: {intruder_id}")
                                        self.speak_async(f"Alert! Known intruder {intruder_id} detected!")
                                    elif name == "Unknown":
                                        intruder_encoding = encoding
                                
                                filepath = os.path.join(CAPTURES_DIR, f"intruder_{timestamp}.jpg")
                                self.camera.save_frame(frame, filepath)
                                
                                # Start conversation
                                if unknown_count >= UNKNOWN_THRESHOLD:
                                    self.state.detect_intruder()
                                    self.state.start_conversation()
                                    in_conversation = True
                                    waiting_for_response = True
                                    
                                    print("\n💬 STARTING CONVERSATION\n")
                                    time.sleep(0.5)  # ✅ Brief pause
                                    self.handle_conversation_turn(intruder_reply=None)
                        else:
                            # Reset consecutive counter if no unknown
                            consecutive_unknown = 0
                        
                        last_check_time = current_time
                
                # ✅ Handle intruder responses (only when ready)
                if in_conversation and waiting_for_response:
                    if not self.speaking and not self.listening and not self.conversation_queue.empty():
                        intruder_reply = self.conversation_queue.get()
                        
                        if intruder_reply:
                            print(f"✅ Intruder: '{intruder_reply}'")
                            self.handle_conversation_turn(intruder_reply=intruder_reply)
                        else:
                            print("⚠️ No valid response - escalating")
                            self.agent.escalate()
                            
                            if self.agent.escalation_level >= MAX_ESCALATION_LEVEL:
                                print("\n🚨 MAXIMUM ESCALATION!\n")
                                self.speak_async("FINAL WARNING! AUTHORITIES NOTIFIED! ALARM ACTIVATED!")
                                time.sleep(2)

                                self.siren.start()
                                siren_active=True

                                # Add to database
                                if intruder_encoding is not None and not intruder_added:
                                    self.recognizer.add_intruder(frame, intruder_encoding)
                                    intruder_added = True
                                
                                # time.sleep(3)
                                # in_conversation = False
                                waiting_for_response = False
                                # unknown_count = 0
                                # self.state.end_conversation()
                            else:
                                time.sleep(0.5)
                                self.handle_conversation_turn(intruder_reply=None)
                
                # ✅ Display with better annotations
                display_frame = frame.copy()
                
                # Draw face boxes if we have results
                if 'results' in locals() and results:
                    display_frame = self.recognizer.draw_results(display_frame, results)
                
                # Status overlay
                status = "MONITORING"
                if siren_active:
                    status= "🚨 SIREN ACTIVE 🚨"
                elif in_conversation:
                    status = f"ALERT-L{self.agent.escalation_level}"
                if self.speaking:
                    status += " | SPEAKING"
                if self.listening:
                    status += " | LISTENING"
                
                cv2.putText(display_frame, status, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.imshow('AI Room Guard', display_frame)
                
                # Keyboard
                key = cv2.waitKey(30) & 0xFF
                if key == ord('q'):
                    print("\n🛑 QUIT\n")
                    if siren_active:
                        self.siren.stop()
                    break
                elif key == ord('d'):
                    print("\n🛑 DEACTIVATE\n")
                    if siren_active:
                        self.siren.stop()
                    break
        
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.camera.stop()
    
    def deactivate(self):
        """Deactivate system"""
        if self.state.guard_active:
            session_duration = (time.time() - self.start_time) / 60.0  # in minutes
            print("\n" + "="*60)
            print(f"📊 Session Duration: {session_duration:.1f} minutes")
            
            self.logger.print_stats()
            self.logger.save()
            
            print("="*60)
            
            self.state.deactivate_guard()
            self.activator.deactivate()
            self.agent.reset()
            self.tts.speak("Guard mode deactivated. Goodbye!")
    
    def run(self):
        """Main execution"""
        print("\n🛡️  AI ROOM GUARD SYSTEM")
        print("="*60)
        
        try:
            if self.wait_for_activation():
                self.monitor_room()
        except KeyboardInterrupt:
            print("\n\n⚠️ INTERRUPTED\n")
        finally:
            self.deactivate()
            print("\n✅ SYSTEM SHUTDOWN COMPLETE\n")


if __name__ == "__main__":
    guard = AIRoomGuard()
    guard.run()
