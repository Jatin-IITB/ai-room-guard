"""
Camera management module
"""
import cv2
import os
from threading import Thread, Lock

class CameraManager:
    """Non-blocking camera capture"""
    
    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self.frame = None
        self.running = False
        self.lock = Lock()
        self.thread = None
        print("✅ Camera manager initialized")
    
    def start(self):
        """Start camera capture"""
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        if not self.cap.isOpened():
            raise Exception("Cannot open camera!")
        
        self.running = True
        self.thread = Thread(target=self._update, daemon=True)
        self.thread.start()
        print("📹 Camera started")
    
    def _update(self):
        """Continuous frame capture"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
    
    def get_frame(self):
        """Get latest frame"""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None
    
    def save_frame(self, frame, filename):
        """Save frame to file"""
        cv2.imwrite(filename, frame)
    
    def stop(self):
        """Stop camera"""
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("🛑 Camera stopped")
