"""
Performance logging for grading evidence
"""
import json
import time
from datetime import datetime

class PerformanceLogger:
    def __init__(self, log_file="performance_log.json"):
        self.log_file = log_file
        self.logs = []
    
    def log_activation(self, phrase_heard, success, confidence=None):
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "type": "activation",
            "phrase": phrase_heard,
            "success": success,
            "confidence": confidence
        })
    
    def log_recognition(self, name, confidence, correct=None):
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "type": "face_recognition",
            "name": name,
            "confidence": confidence,
            "correct": correct
        })
    
    def log_conversation(self, level, guard_response, intruder_input=None):
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "type": "conversation",
            "escalation_level": level,
            "intruder_input": intruder_input,
            "guard_response": guard_response
        })
    
    def save(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.logs, f, indent=2)
        print(f"✅ Performance log saved: {self.log_file}")
    
    def print_stats(self):
        activations = [l for l in self.logs if l['type'] == 'activation']
        recognitions = [l for l in self.logs if l['type'] == 'face_recognition']
        conversations = [l for l in self.logs if l['type'] == 'conversation']
        
        print("\n" + "="*60)
        print("PERFORMANCE STATISTICS")
        print("="*60)
        
        if activations:
            success_rate = sum(l['success'] for l in activations) / len(activations) * 100
            print(f"Activation Success Rate: {success_rate:.1f}%")
        
        if recognitions:
            avg_confidence = sum(l['confidence'] for l in recognitions) / len(recognitions)
            print(f"Average Recognition Confidence: {avg_confidence:.2f}")
        
        if conversations:
            print(f"Total Conversation Turns: {len(conversations)}")
            levels = [l['escalation_level'] for l in conversations]
            print(f"Escalation Levels Used: {set(levels)}")
        
        print("="*60)
