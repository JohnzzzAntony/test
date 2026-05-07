import requests
import os
from django.conf import settings

class KimiAIService:
    """
    Service to interact with Moonshot AI's Kimi model via NVIDIA's API.
    """
    INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or getattr(settings, "NVIDIA_KIMI_API_KEY", None)
        self.model = model or getattr(settings, "KIMI_MODEL", "moonshotai/kimi-k2.6")
        
        if not self.api_key:
            # Fallback to env if not in settings
            self.api_key = os.getenv("NVIDIA_KIMI_API_KEY")
        
        if not self.api_key:
            raise ValueError("NVIDIA_KIMI_API_KEY not found in Django settings or environment variables.")

    def get_headers(self, stream=False):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream" if stream else "application/json"
        }

    def chat(self, prompt, system_prompt="You are a helpful assistant.", stream=True, temperature=1.0, top_p=1.0, max_tokens=16384):
        """
        Perform a chat completion request.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
            "chat_template_kwargs": {"thinking": True},
        }

        response = requests.post(
            self.INVOKE_URL, 
            headers=self.get_headers(stream), 
            json=payload, 
            stream=stream
        )
        
        if stream:
            return response.iter_lines()
        
        response.raise_for_status()
        return response.json()

class MinimaxAIService:
    """
    Service to interact with Minimax AI via NVIDIA's API.
    """
    INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or getattr(settings, "NVIDIA_MINIMAX_API_KEY", None)
        self.model = model or getattr(settings, "MINIMAX_MODEL", "minimaxai/minimax-m2.7")
        
        if not self.api_key:
            self.api_key = os.getenv("NVIDIA_MINIMAX_API_KEY")
        
        if not self.api_key:
            raise ValueError("NVIDIA_MINIMAX_API_KEY not found in Django settings or environment variables.")

    def get_headers(self, stream=False):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream" if stream else "application/json"
        }

    def chat(self, prompt, system_prompt="You are a helpful assistant.", stream=True, temperature=1.0, top_p=0.95, max_tokens=8192):
        """
        Perform a chat completion request.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
        }

        response = requests.post(
            self.INVOKE_URL, 
            headers=self.get_headers(stream), 
            json=payload, 
            stream=stream
        )
        
        if stream:
            return response.iter_lines()
        
        response.raise_for_status()
        return response.json()

class GLMAIService:
    """
    Service to interact with GLM AI via NVIDIA's API.
    """
    INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or getattr(settings, "NVIDIA_GLM_API_KEY", None)
        self.model = model or getattr(settings, "GLM_MODEL", "z-ai/glm-5.1")
        
        if not self.api_key:
            self.api_key = os.getenv("NVIDIA_GLM_API_KEY")
        
        if not self.api_key:
            raise ValueError("NVIDIA_GLM_API_KEY not found in Django settings or environment variables.")

    def get_headers(self, stream=False):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream" if stream else "application/json"
        }

    def chat(self, prompt, system_prompt="You are a helpful assistant.", stream=True, temperature=1.0, top_p=1.0, max_tokens=16384):
        """
        Perform a chat completion request.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
            "extra_body": {
                "chat_template_kwargs": {
                    "enable_thinking": True,
                    "clear_thinking": False
                }
            }
        }

        response = requests.post(
            self.INVOKE_URL, 
            headers=self.get_headers(stream), 
            json=payload, 
            stream=stream
        )
        
        if stream:
            return response.iter_lines()
        
        response.raise_for_status()
        return response.json()
