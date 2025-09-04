import json
import hashlib
import base64
import requests
from typing import Dict, Any, Optional
from loguru import logger
from config.settings import settings


class FeishuService:
    def __init__(self):
        self.app_id = settings.feishu_app_id
        self.app_secret = settings.feishu_app_secret
        self.verification_token = settings.feishu_verification_token
        self.encrypt_key = settings.feishu_encrypt_key
        self._access_token = None
        self._token_expiry = 0
    
    def verify_request(self, timestamp: str, nonce: str, signature: str, body: bytes) -> bool:
        """Verify Feishu webhook request"""
        # Calculate signature
        content = timestamp + nonce + self.verification_token + body.decode('utf-8')
        calculated_signature = hashlib.sha256(content.encode()).hexdigest()
        
        return calculated_signature == signature
    
    def decrypt_message(self, encrypt_data: str) -> Dict[str, Any]:
        """Decrypt Feishu encrypted message"""
        if not self.encrypt_key:
            return json.loads(encrypt_data)
        
        # Implement decryption logic here if needed
        # For now, assuming unencrypted messages
        return json.loads(encrypt_data)
    
    def get_access_token(self) -> str:
        """Get Feishu access token"""
        import time
        
        # Check if token is still valid
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token
        
        # Request new token
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                self._access_token = result["tenant_access_token"]
                self._token_expiry = time.time() + result["expire"] - 60  # Refresh 1 min early
                return self._access_token
            else:
                logger.error(f"Failed to get access token: {result}")
                raise Exception("Failed to get access token")
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            raise
    
    def send_message(self, receive_id: str, content: str, msg_type: str = "text", receive_id_type: str = "open_id"):
        """Send message to Feishu user or chat"""
        url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        
        # Prepare message content based on type
        if msg_type == "text":
            content_data = json.dumps({"text": content})
        elif msg_type == "interactive":
            content_data = json.dumps(content)
        else:
            content_data = content
        
        data = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": content_data
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != 0:
                logger.error(f"Failed to send message: {result}")
            else:
                logger.info(f"Message sent successfully to {receive_id}")
            
            return result
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    def reply_message(self, message_id: str, content: str, msg_type: str = "text"):
        """Reply to a specific message"""
        url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        
        # Prepare message content
        if msg_type == "text":
            content_data = json.dumps({"text": content})
        else:
            content_data = content
        
        data = {
            "msg_type": msg_type,
            "content": content_data
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != 0:
                logger.error(f"Failed to reply message: {result}")
            else:
                logger.info(f"Reply sent successfully to message {message_id}")
            
            return result
        except Exception as e:
            logger.error(f"Error replying to message: {e}")
            raise
    
    def create_interactive_card(self, title: str, content: str, buttons: Optional[list] = None) -> Dict[str, Any]:
        """Create an interactive card message"""
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                }
            ]
        }
        
        if buttons:
            button_elements = []
            for button in buttons:
                button_elements.append({
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": button["text"]
                    },
                    "type": button.get("type", "default"),
                    "value": button.get("value", {})
                })
            
            card["elements"].append({
                "tag": "action",
                "actions": button_elements
            })
        
        return {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                }
            },
            "card": card
        }


feishu_service = FeishuService()