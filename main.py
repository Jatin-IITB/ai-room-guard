"""
AI Room Guard - Main System (PRODUCTION VERSION)
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
from alerts import AlertSystem


class AIRoomGuard:
    """Complete AI Room Guard System"""
    
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
        
        if ALERTS_ENABLED:
            self.alert_system = AlertSystem()
        else:
            self.alert_system = None
            print("⚠️ Alerts disabled in config")
        
        # State
        self.conversation_queue = Queue()
        self.speaking = False
        self.listening = False
        self.last_greeted = {}
        self.conversation_lock = threading.Lock()
        self.start_time = time.time()
        
        print("✅ ALL SYSTEMS READY!")
        print("="*60)
    
    def wait_for_activation(self):
        """Wait for voice activation"""
        print("\n" + "="*60)
        print("🎧 VOICE ACTIVATION")
        print("="*60)
        print("Say clearly: 'Guard my room'")
        print("(The system will keep listening until you say it)")
        print("="*60 + "\n")
        
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
        """Handle one conversation turn"""
        def _converse():
            with self.conversation_lock:
                response = self.agent.get_response(user_input=intruder_reply)
                self.logger.log_conversation(
                    level=self.agent.escalation_level,
                    guard_response=response,
                    intruder_input=intruder_reply
                )
                
                while self.speaking or self.listening:
                    time.sleep(0.3)
                
                self.speak_async(response)
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
        time.sleep(1)
        
        # State variables
        unknown_count = 0
        last_check_time = time.time()
        in_conversation = False
        waiting_for_response = False
        intruder_encoding = None
        intruder_added = False
        consecutive_unknown = 0
        siren_active = False
        frames_since_clear = 0
        alerted_intruders = set()
        current_intruder_id = None
        
        try:
            while self.state.guard_active:
                frame = self.camera.get_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                current_time = time.time()
                
                # FACE RECOGNITION (always check, even during conversation)
                if (current_time - last_check_time >= FACE_RECOGNITION_INTERVAL):
                    
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face_locations = face_recognition.face_locations(rgb_frame)
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                    
                    results = []
                    for encoding in face_encodings:
                        name, intruder_id = self.recognizer._identify_face(encoding)
                        if name != "Unknown":
                            if self.recognizer.known_encodings:
                                distances = face_recognition.face_distance(self.recognizer.known_encodings, encoding)
                                confidence = 1 - min(distances) if len(distances) > 0 else 0.0
                                self.logger.log_recognition(name=name, confidence=confidence, correct=True)
                        results.append((name, intruder_id, encoding))
                    
                    has_unknown = any(name in ["Unknown", "REPEAT_INTRUDER"] for name, _, _ in results)
                    has_known = any(name not in ["Unknown", "REPEAT_INTRUDER"] for name, _, _ in results)
                    
                    # PRIORITY 1: Stop siren if trusted person detected
                    if siren_active and has_known:
                        print("\n✅ TRUSTED PERSON DETECTED - STOPPING SIREN\n")
                        self.siren.stop()
                        siren_active = False
                        
                        for name, _, _ in results:
                            if name not in ["Unknown", "REPEAT_INTRUDER"]:
                                self.speak_async(f"Welcome {name}! Alarm deactivated.")
                        
                        # Reset all state
                        in_conversation = False
                        waiting_for_response = False
                        unknown_count = 0
                        consecutive_unknown = 0
                        intruder_encoding = None
                        intruder_added = False
                        current_intruder_id = None
                        self.agent.reset()
                        self.state.end_conversation()
                        last_check_time = current_time
                        continue
                    
                    # PRIORITY 2: Stop siren if room clear
                    if siren_active and not has_unknown and not has_known:
                        frames_since_clear += 1
                        if frames_since_clear >= 30:
                            print("\n✅ ROOM CLEAR - STOPPING SIREN\n")
                            self.siren.stop()
                            siren_active = False
                            self.speak_async("Intruder has left. Alarm Deactivated")
                            
                            # Reset all state
                            in_conversation = False
                            waiting_for_response = False
                            unknown_count = 0
                            consecutive_unknown = 0
                            intruder_encoding = None
                            intruder_added = False
                            current_intruder_id = None
                            frames_since_clear = 0
                            self.agent.reset()
                            self.state.end_conversation()
                            last_check_time = current_time
                            continue
                    else:
                        frames_since_clear = 0
                    
                    # NEW DETECTIONS (only if not in conversation)
                    if not in_conversation and not self.speaking and not self.listening:
                        
                        # Greet known people
                        if has_known and not siren_active:
                            for name, _, _ in results:
                                if name not in ["Unknown", "REPEAT_INTRUDER"]:
                                    self.greet_known_person(name)
                            
                            if unknown_count > 0:
                                print("✅ Trusted person. Resetting.")
                                unknown_count = 0
                                consecutive_unknown = 0
                                intruder_encoding = None
                        
                        # Handle unknowns
                        if has_unknown and not has_known and not siren_active:
                            consecutive_unknown += 1
                            
                            if consecutive_unknown >= 2:
                                unknown_count += 1
                                consecutive_unknown = 0
                                print(f"⚠️ Unknown person! ({unknown_count}/{UNKNOWN_THRESHOLD})")
                                
                                os.makedirs(CAPTURES_DIR, exist_ok=True)
                                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                
                                current_intruder_id = None
                                is_repeat_intruder = False
                                
                                for name, intruder_id, encoding in results:
                                    if name == "REPEAT_INTRUDER":
                                        print(f"🚨 KNOWN INTRUDER: {intruder_id}")
                                        current_intruder_id = intruder_id
                                        is_repeat_intruder = True
                                        
                                        if self.alert_system and intruder_id not in alerted_intruders:
                                            intruder_image_path = None
                                            for filename in os.listdir(INTRUDER_DB_DIR):
                                                if intruder_id in filename and filename.endswith('.jpg'):
                                                    intruder_image_path = os.path.join(INTRUDER_DB_DIR, filename)
                                                    break
                                            
                                            if intruder_image_path:
                                                print(f"\n🚨 REPEAT INTRUDER ALERT: {intruder_id}")
                                                print("📨 Sending immediate alert...")
                                                
                                                alert_thread = threading.Thread(
                                                    target=self.alert_system.send_repeat_intruder_alert,
                                                    args=(intruder_id, intruder_image_path),
                                                    daemon=True
                                                )
                                                alert_thread.start()
                                                alerted_intruders.add(intruder_id)
                                        
                                        self.speak_async(f"Alert! Known intruder {intruder_id} detected!")
                                        self.agent.escalation_level = 2
                                    
                                    elif name == "Unknown":
                                        intruder_encoding = encoding
                                
                                filepath = os.path.join(CAPTURES_DIR, f"intruder_{timestamp}.jpg")
                                self.camera.save_frame(frame, filepath)
                                
                                if unknown_count >= UNKNOWN_THRESHOLD:
                                    self.state.detect_intruder()
                                    self.state.start_conversation()
                                    in_conversation = True
                                    waiting_for_response = True
                                    
                                    print("\n💬 STARTING CONVERSATION\n")
                                    if is_repeat_intruder:
                                        print(f"⚠️ Starting at Level {self.agent.escalation_level}")
                                    
                                    time.sleep(0.5)
                                    self.handle_conversation_turn(intruder_reply=None)
                        else:
                            consecutive_unknown = 0
                    
                    last_check_time = current_time
                
                # CONVERSATION HANDLING
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
                                print("🚨 ACTIVATING CONTINUOUS SIREN!\n")
                                self.speak_async("FINAL WARNING! AUTHORITIES NOTIFIED! ALARM ACTIVATED!")
                                time.sleep(2)
                                
                                self.siren.start()
                                siren_active = True
                                
                                # Send alerts
                                if self.alert_system:
                                    alert_image_path = None
                                    alert_intruder_id = None
                                    
                                    if intruder_encoding is not None and not intruder_added:
                                        new_intruder_id = self.recognizer.add_intruder(frame, intruder_encoding)
                                        
                                        if new_intruder_id:
                                            intruder_added = True
                                            alert_intruder_id = new_intruder_id
                                            
                                            for filename in os.listdir(INTRUDER_DB_DIR):
                                                if new_intruder_id in filename and filename.endswith('.jpg'):
                                                    alert_image_path = os.path.join(INTRUDER_DB_DIR, filename)
                                                    break
                                    
                                    elif current_intruder_id:
                                        alert_intruder_id = current_intruder_id
                                        
                                        for filename in os.listdir(INTRUDER_DB_DIR):
                                            if current_intruder_id in filename and filename.endswith('.jpg'):
                                                alert_image_path = os.path.join(INTRUDER_DB_DIR, filename)
                                                break
                                    
                                    if alert_intruder_id and alert_image_path:
                                        print("\n📨 Sending maximum escalation alert...")
                                        print(f"   Intruder: {alert_intruder_id}")
                                        print(f"   Image: {alert_image_path}")
                                        
                                        alert_thread = threading.Thread(
                                            target=self.alert_system.send_all_alerts,
                                            args=(alert_intruder_id, alert_image_path, self.agent.escalation_level),
                                            daemon=True
                                        )
                                        alert_thread.start()
                                        alerted_intruders.add(alert_intruder_id)
                                    else:
                                        print("⚠️ Unable to send alert - no intruder image found")
                                
                                waiting_for_response = False
                            else:
                                time.sleep(0.5)
                                self.handle_conversation_turn(intruder_reply=None)
                
                # DISPLAY
                display_frame = frame.copy()
                
                if 'results' in locals() and results:
                    display_frame = self.recognizer.draw_results(display_frame, results)
                
                status = "MONITORING"
                if siren_active:
                    status = "🚨 SIREN ACTIVE 🚨"
                elif in_conversation:
                    status = f"ALERT-L{self.agent.escalation_level}"
                if self.speaking:
                    status += " | SPEAKING"
                if self.listening:
                    status += " | LISTENING"
                
                cv2.putText(display_frame, status, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.imshow('AI Room Guard', display_frame)
                
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
            if siren_active:
                self.siren.stop()
            self.camera.stop()
            cv2.destroyAllWindows()
    
    def deactivate(self):
        """Deactivate system"""
        if self.state.guard_active:
            session_duration = (time.time() - self.start_time) / 60.0
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
