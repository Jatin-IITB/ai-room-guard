"""
System state management
"""

class StateManager:
    """Manage guard system state"""
    
    def __init__(self):
        self.guard_active = False
        self.intruder_detected = False
        self.conversation_active = False
        print("✅ State manager initialized")
    
    def activate_guard(self):
        self.guard_active = True
        print("✅ Guard ACTIVE")
    
    def deactivate_guard(self):
        self.guard_active = False
        self.intruder_detected = False
        self.conversation_active = False
        print("🛑 Guard INACTIVE")
    
    def detect_intruder(self):
        self.intruder_detected = True
        print("⚠️ Intruder DETECTED")
    
    def start_conversation(self):
        self.conversation_active = True
        print("💬 Conversation STARTED")
    
    def end_conversation(self):
        self.conversation_active = False
        self.intruder_detected = False
        print("💬 Conversation ENDED")
