"""
LLM-based conversation agent using Ollama
"""
import ollama
import time

class ConversationAgent:
    """Phi-3 based conversation with fallbacks"""
    
    def __init__(self, model_name="phi3"):
        self.model_name = model_name
        self.escalation_level = 0
        self.max_escalation = 3
        
        # Check model
        try:
            models = ollama.list()
            model_list = [m.get('name', '').split(':')[0] for m in models.get('models', [])]
            if model_name not in model_list:
                print(f"⬇️ Pulling {model_name}...")
                ollama.pull(model_name)
        except:
            pass
        
        print(f"✅ LLM Agent: {model_name}")
    
    def get_response(self, user_input=None):
        """Get contextual response"""
        level = min(self.escalation_level, self.max_escalation)
        
        # Auto-escalate on hostile language
        if user_input:
            hostile = ['fuck', 'shit', 'bastard', 'bitch']
            if any(word in user_input.lower() for word in hostile):
                self.escalation_level = min(level + 1, self.max_escalation)
                level = self.escalation_level
                print(f"⚠️ Hostile language! → Level {level}")
        
        # Try LLM
        response = self._query_llm(user_input, level)
        
        # Fallback
        if not response:
            response = self._get_fallback(user_input, level)
        
        print(f"🤖 [L{level}] {response}")
        return response
    
    def _query_llm(self, user_input, level):
        """Query Ollama"""
        prompts = {
            0: "You are a security guard. Unknown person entered. Ask identity. ONE sentence, 15 words max.",
            1: "You are a stern guard. Tell them to leave private property NOW. ONE sentence, 20 words max.",
            2: "FINAL warning. Say police will be called. ONE sentence, 20 words max.",
            3: "MAX alert. Say police notified. ONE sentence, 15 words max."
        }
        
        try:
            if user_input:
                prompt = f"{prompts[level]}\nIntruder: \"{user_input}\"\nYour response:"
            else:
                prompt = f"{prompts[level]}\nYour response:"
            
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={'temperature': 0.5, 'num_predict': 30}
            )
            
            text = response.get('response', '').strip()
            text = text.replace('"', '').replace('**', '')
            text = " ".join(text.split())
            
            if '.' in text:
                text = text.split('.')[0] + '.'
            
            return text[:120] if text and len(text) > 5 else None
            
        except:
            return None
    
    def _get_fallback(self, user_input, level):
        """Fallback responses"""
        if user_input:
            user_lower = user_input.lower()
            
            if level == 0:
                if 'friend' in user_lower:
                    return "I don't recognize you. Call your friend or leave."
                elif 'lost' in user_lower:
                    return "Wrong room. Check room number and exit."
                else:
                    return "Who are you? Why are you here?"
            elif level == 1:
                return "You're trespassing! Leave NOW!"
            elif level == 2:
                return "LAST WARNING! Police being called!"
            else:
                return "POLICE NOTIFIED! GET OUT!"
        else:
            return ["Who are you?", "Leave NOW!", "FINAL WARNING!", "POLICE CALLED!"][level]
    
    def escalate(self):
        if self.escalation_level < self.max_escalation:
            self.escalation_level += 1
            print(f"📈 → Level {self.escalation_level}")
    
    def reset(self):
        self.escalation_level = 0
