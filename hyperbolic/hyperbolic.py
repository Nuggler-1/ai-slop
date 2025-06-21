from typing import List, Dict, Optional
import requests
import json
from config import HYPERBOLIC_API_URL
from loguru import logger 

class Hyperbolic: 

    def __init__(
            self, 
            api_key:str,  
            model_config:dict , 
            system_prompt:str | None = None,
            proxy:dict | None = None,
        ):
        self.api_key = api_key
        self.proxy = proxy 
        self.model_config = model_config
        self.system_prompt = system_prompt
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        
    def complete_prompt(
        self,
        messages: List[Dict[str, str]]
    ) -> Optional[str]:
    
        """Send a chat completion request to NOUS API"""
        
        messages.append(
            {"role": "system", "content": self.system_prompt}
        )
        
        payload = {
            "messages": messages,
            "model": self.model_config["model"],
            "max_tokens": self.model_config["max_tokens"],
            "temperature": self.model_config["temperature"],
            "top_p": self.model_config["top_p"]
        }

        try:
            response = requests.post(
                HYPERBOLIC_API_URL, 
                headers=self.headers, 
                json=payload, 
                proxies=self.proxy
            )
            response.raise_for_status()
            response_data = response.json()

            if len(response_data['choices']) > 0:
                assistant_message = response_data['choices'][0] 
                return assistant_message['message']['content'].strip()
            else:
                logger.warning(f"{self.api_key}: Hyperbolic API response did not contain expected data.")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"{self.api_key}: Error making Hyperbolic API request ({self.api_key}): {e}")
            if response is not None:
                logger.error(f"{self.api_key}: Status Code: {response.status_code}")
                try:
                    logger.error(f"{self.api_key}: Response Body: {response.json()}")
                except json.JSONDecodeError:
                    logger.error(f"{self.api_key}: Response Body: {response.content}")
            return None
            
        except Exception as e:
            logger.error(f"{self.api_key}: An unexpected error occurred during Hyperbolic API request ({self.api_key}): {e}")
            return None

