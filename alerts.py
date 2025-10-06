"""
Alert System - Email with photo attachment & Telegram notifications
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import requests


class AlertSystem:
    """Send intruder alerts via email and Telegram"""
    
    def __init__(self, config_file="alert_config.py"):
        """
        Initialize alert system
        Configure your credentials in alert_config.py
        """
        self.email_enabled = False
        self.telegram_enabled = False
        
        # Load config
        try:
            from config import (
                EMAIL_ENABLED, EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO,
                TELEGRAM_ENABLED, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
            )
            
            if EMAIL_ENABLED:
                self.email_from = EMAIL_FROM
                self.email_password = EMAIL_PASSWORD
                self.email_to = EMAIL_TO if isinstance(EMAIL_TO, list) else [EMAIL_TO]
                self.email_enabled = True
                print("✅ Email alerts enabled")
            
            if TELEGRAM_ENABLED:
                self.telegram_bot_token = TELEGRAM_BOT_TOKEN
                self.telegram_chat_id = TELEGRAM_CHAT_ID
                self.telegram_enabled = True
                print("✅ Telegram alerts enabled")
                
        except ImportError:
            print("⚠️ alert_config.py not found - alerts disabled")
            print("   Create alert_config.py to enable alerts")
    
    def send_email_alert(self, intruder_id, image_path, escalation_level=3):
        """Send email with intruder photo attached"""
        if not self.email_enabled:
            return False
        
        try:
            print(f"📧 Sending email alert for {intruder_id}...")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)
            msg['Subject'] = f"🚨 INTRUDER ALERT - {intruder_id}"
            
            # Email body
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            body = f"""
🚨 INTRUDER ALERT 🚨

Intruder ID: {intruder_id}
Time: {timestamp}
Escalation Level: {escalation_level}/3
Status: Siren activated

An unknown person was detected in your room and refused to leave after multiple warnings.

Photo of intruder is attached.

- AI Room Guard System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach image
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    img_data = f.read()
                
                image = MIMEImage(img_data, name=os.path.basename(image_path))
                msg.attach(image)
            
            # Send email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {len(self.email_to)} recipient(s)")
            return True
            
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False
        
    def send_telegram_alert(self, intruder_id, image_path, escalation_level=3):
        """Send Telegram message with photo"""
        if not self.telegram_enabled:
            return False
        
        try:
            print(f"📱 Sending Telegram alert for {intruder_id}...")
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Send photo with caption
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendPhoto"
            
            # ✅ FIXED: Escape special characters or use plain text
            caption = f"""
    🚨 INTRUDER ALERT

    ID: {intruder_id}
    Time: {timestamp}
    Level: {escalation_level}/3
    Status: Siren Active

    Unknown person detected and refused to leave.
            """
            # ✅ Remove parse_mode to avoid markdown issues
            data = {
                'chat_id': self.telegram_chat_id,
                'caption': caption
                # Removed: 'parse_mode': 'Markdown'
            }
            
            # Attach photo
            if os.path.exists(image_path):
                with open(image_path, 'rb') as photo:
                    files = {'photo': photo}
                    response = requests.post(url, data=data, files=files)
                
                if response.status_code == 200:
                    print("✅ Telegram alert sent")
                    return True
                else:
                    print(f"❌ Telegram failed: {response.text}")
                    return False
            else:
                print(f"❌ Image not found: {image_path}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram failed: {e}")
            return False


    def send_repeat_intruder_alert(self, intruder_id, image_path):
        """Send alert specifically for repeat intruder"""
        if not self.email_enabled and not self.telegram_enabled:
            return {'email': False, 'telegram': False}
        
        results = {
            'email': False,
            'telegram': False
        }
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Email (keep as is)
        if self.email_enabled:
            # ... email code stays the same ...
            pass
        
        # ✅ TELEGRAM FIX for repeat intruder
        if self.telegram_enabled:
            try:
                print(f"📱 Sending repeat intruder Telegram for {intruder_id}...")
                
                url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendPhoto"
                
                # ✅ Plain text, no markdown
                caption = f"""
    🚨 REPEAT INTRUDER ALERT

    WARNING: Previously Warned!

    ID: {intruder_id}
    Time: {timestamp}
    Status: Detected again

    This person was caught and warned before!
                """
                
                data = {
                    'chat_id': self.telegram_chat_id,
                    'caption': caption
                    # No parse_mode
                }
                
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as photo:
                        files = {'photo': photo}
                        response = requests.post(url, data=data, files=files)
                    
                    if response.status_code == 200:
                        print("✅ Repeat intruder Telegram sent")
                        results['telegram'] = True
                    else:
                        print(f"❌ Telegram failed: {response.text}")
                
            except Exception as e:
                print(f"❌ Telegram failed: {e}")
        
        return results

    
    def send_all_alerts(self, intruder_id, image_path, escalation_level=3):
        """Send alerts via all enabled channels"""
        results = {
            'email': False,
            'telegram': False
        }
        
        if self.email_enabled:
            results['email'] = self.send_email_alert(intruder_id, image_path, escalation_level)
        
        if self.telegram_enabled:
            results['telegram'] = self.send_telegram_alert(intruder_id, image_path, escalation_level)
        
        return results
    def send_repeat_intruder_alert(self, intruder_id, image_path):
        """Send alert specifically for repeat intruder"""
        if not self.email_enabled and not self.telegram_enabled:
            return {'email': False, 'telegram': False}
        
        results = {
            'email': False,
            'telegram': False
        }
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ✅ EMAIL for repeat intruder
        if self.email_enabled:
            try:
                print(f"📧 Sending repeat intruder email for {intruder_id}...")
                
                msg = MIMEMultipart()
                msg['From'] = self.email_from
                msg['To'] = ', '.join(self.email_to)
                msg['Subject'] = f"🚨 REPEAT INTRUDER - {intruder_id}"
                
                body = f"""
    🚨 REPEAT INTRUDER ALERT 🚨

    ⚠️ This person has been detected before!

    Intruder ID: {intruder_id}
    Time: {timestamp}
    Status: Previously warned, detected again

    This intruder has entered your room again after being 
    warned and added to the database previously.

    Photo from previous encounter attached.

    - AI Room Guard System
                """
                
                msg.attach(MIMEText(body, 'plain'))
                
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        img_data = f.read()
                    image = MIMEImage(img_data, name=os.path.basename(image_path))
                    msg.attach(image)
                
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(self.email_from, self.email_password)
                    server.send_message(msg)
                
                print(f"✅ Repeat intruder email sent")
                results['email'] = True
                
            except Exception as e:
                print(f"❌ Email failed: {e}")
        
        # ✅ TELEGRAM for repeat intruder
        if self.telegram_enabled:
            try:
                print(f"📱 Sending repeat intruder Telegram for {intruder_id}...")
                
                url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendPhoto"
                
                caption = f"""
    🚨 *REPEAT INTRUDER ALERT*

    ⚠️ *Previously Warned!*

    *ID:* {intruder_id}
    *Time:* {timestamp}
    *Status:* Detected again

    This person was caught and warned before!
                """
                
                data = {
                    'chat_id': self.telegram_chat_id,
                    'caption': caption
                }
                
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as photo:
                        files = {'photo': photo}
                        response = requests.post(url, data=data, files=files)
                    
                    if response.status_code == 200:
                        print("✅ Repeat intruder Telegram sent")
                        results['telegram'] = True
                    else:
                        print(f"❌ Telegram failed: {response.text}")
                
            except Exception as e:
                print(f"❌ Telegram failed: {e}")
        
        return results


# Test function
def test_alerts():
    """Test alert system"""
    import cv2
    import numpy as np
    
    print("\n" + "="*60)
    print("TESTING ALERT SYSTEM")
    print("="*60)
    
    # Create dummy image
    dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(dummy_image, "TEST INTRUDER", (150, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
    
    test_image_path = "test_intruder.jpg"
    cv2.imwrite(test_image_path, dummy_image)
    
    # Test alerts
    alert_system = AlertSystem()
    results = alert_system.send_all_alerts("TEST_001", test_image_path, 3)
    
    print("\nResults:")
    print(f"  Email: {'✅' if results['email'] else '❌'}")
    print(f"  Telegram: {'✅' if results['telegram'] else '❌'}")
    
    # Cleanup
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
    
    print("="*60)


if __name__ == "__main__":
    test_alerts()
