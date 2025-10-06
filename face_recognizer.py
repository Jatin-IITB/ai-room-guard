"""
Face recognition with proper confidence thresholds
"""
import face_recognition
import cv2
import os
import pickle
from datetime import datetime
import numpy as np

class FaceRecognizer:
    """Face recognition with strict confidence thresholds"""
    
    def __init__(self, trusted_dir="trusted_faces", intruder_db_dir="intruder_database", tolerance=0.5):  # ✅ Lowered to 0.5
        self.trusted_dir = trusted_dir
        self.intruder_db_dir = intruder_db_dir
        self.tolerance = tolerance
        self.min_confidence = 0.55  # ✅ NEW: Minimum confidence threshold (1 - distance)
        
        os.makedirs(trusted_dir, exist_ok=True)
        os.makedirs(intruder_db_dir, exist_ok=True)
        
        self.known_encodings = []
        self.known_names = []
        self.intruder_encodings = []
        self.intruder_ids = []
        
        self._load_trusted_faces()
        self._load_intruder_database()
        
        unique_names = set(self.known_names)
        print(f"✅ Loaded {len(self.known_encodings)} photos of {len(unique_names)} people")
        print(f"✅ Confidence threshold: {self.min_confidence:.2f} (rejects < {self.min_confidence})")
        print(f"✅ Loaded {len(self.intruder_ids)} known intruders")
    
    def _load_trusted_faces(self):
        """Load all trusted face photos"""
        for filename in os.listdir(self.trusted_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(self.trusted_dir, filename)
                
                try:
                    image = face_recognition.load_image_file(path)
                    encodings = face_recognition.face_encodings(image)
                    
                    if encodings:
                        # Extract name: "Jatin Gupta_sample_1.jpg" → "Jatin Gupta"
                        name = filename.rsplit('_sample_', 1)[0]
                        name = name.rsplit('_', 1)[0]  # Also handle "Name_1.jpg"
                        name = name.rsplit('.', 1)[0]
                        
                        self.known_encodings.append(encodings[0])
                        self.known_names.append(name)
                        print(f"  ✓ Loaded: {filename} → {name}")
                    else:
                        print(f"  ⚠️ No face in: {filename}")
                
                except Exception as e:
                    print(f"  ❌ Error: {filename}: {e}")
    
    def _load_intruder_database(self):
        """Load known intruders"""
        db_file = os.path.join(self.intruder_db_dir, "intruders.pkl")
        if os.path.exists(db_file):
            try:
                with open(db_file, 'rb') as f:
                    data = pickle.load(f)
                    self.intruder_encodings = data.get('encodings', [])
                    self.intruder_ids = data.get('ids', [])
            except:
                pass
    
    def _save_intruder_database(self):
        """Save intruder database"""
        db_file = os.path.join(self.intruder_db_dir, "intruders.pkl")
        with open(db_file, 'wb') as f:
            pickle.dump({
                'encodings': self.intruder_encodings,
                'ids': self.intruder_ids
            }, f)
    
    def recognize_faces(self, frame):
        """Recognize faces with strict confidence filtering"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        results = []
        for encoding in face_encodings:
            name, intruder_id = self._identify_face(encoding)
            results.append((name, intruder_id, encoding))
        
        return results
    
    def _identify_face(self, encoding):
        """Identify face with STRICT confidence check"""
        
        # ✅ Check trusted faces with confidence threshold
        if self.known_encodings:
            distances = face_recognition.face_distance(self.known_encodings, encoding)
            
            if len(distances) > 0:
                min_distance = np.min(distances)
                confidence = 1 - min_distance  # ✅ Convert distance to confidence
                
                # ✅ STRICT: Must pass BOTH tolerance AND confidence threshold
                if min_distance < self.tolerance and confidence >= self.min_confidence:
                    best_match_idx = np.argmin(distances)
                    name = self.known_names[best_match_idx]
                    
                    print(f"  ✓ Recognized: {name} (confidence: {confidence:.2f})")
                    return name, None
                else:
                    # Log rejections for debugging
                    if min_distance < self.tolerance:
                        print(f"  ⚠️ Rejected: Low confidence {confidence:.2f} < {self.min_confidence:.2f}")
        
        # ✅ Check intruder database
        if self.intruder_encodings:
            distances = face_recognition.face_distance(self.intruder_encodings, encoding)
            
            if len(distances) > 0:
                min_distance = np.min(distances)
                confidence = 1 - min_distance
                
                if min_distance < self.tolerance and confidence >= self.min_confidence:
                    best_match_idx = np.argmin(distances)
                    intruder_id = self.intruder_ids[best_match_idx]
                    print(f"  🚨 REPEAT INTRUDER: {intruder_id} (confidence: {confidence:.2f})")
                    return "REPEAT_INTRUDER", intruder_id
        
        return "Unknown", None
    
    def add_intruder(self, frame, encoding):
        """Add new intruder to database"""
        intruder_id = f"INTRUDER_{len(self.intruder_ids) + 1:03d}"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save image
        img_path = os.path.join(self.intruder_db_dir, f"{intruder_id}_{timestamp}.jpg")
        cv2.imwrite(img_path, frame)
        
        # Add to database
        self.intruder_encodings.append(encoding)
        self.intruder_ids.append(intruder_id)
        self._save_intruder_database()
        
        print(f"💾 New intruder: {intruder_id}")
        return intruder_id
    
    def draw_results(self, frame, results):
        """Draw boxes with confidence scores"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        for (top, right, bottom, left), (name, intruder_id, encoding) in zip(face_locations, results):
            
            # Calculate confidence for display
            if name != "Unknown" and self.known_encodings:
                distances = face_recognition.face_distance(self.known_encodings, encoding)
                confidence = 1 - np.min(distances)
            else:
                confidence = 0.0
            
            # Color based on recognition
            if name == "Unknown":
                color = (0, 0, 255)  # Red
                label = "UNKNOWN"
            elif name == "REPEAT_INTRUDER":
                color = (255, 0, 255)  # Magenta
                label = f"{intruder_id}"
            else:
                color = (0, 255, 0)  # Green
                label = f"{name} ({confidence:.2f})"  # ✅ Show confidence
            
            # Draw box
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, label, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
