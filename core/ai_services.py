from openai import OpenAI
import os
from django.conf import settings

class BaseNVIDIAAIService:
    """
    Base class for NVIDIA NIM AI services using the OpenAI client.
    """
    def __init__(self, api_key=None, model=None, base_url="https://integrate.api.nvidia.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def chat(self, prompt, system_prompt="You are a helpful assistant.", stream=True, temperature=1.0, top_p=1.0, max_tokens=16384, enable_thinking=True):
        """
        Perform a chat completion request.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Some models might need clear_thinking: False to preserve the trace
        extra_body = {
            "chat_template_kwargs": {
                "enable_thinking": enable_thinking,
                "clear_thinking": False
            }
        }
        
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            extra_body=extra_body,
            stream=stream
        )

class KimiAIService(BaseNVIDIAAIService):
    """
    Service to interact with Moonshot AI's Kimi model via NVIDIA's API.
    """
    def __init__(self, api_key=None, model=None):
        api_key = api_key or getattr(settings, "NVIDIA_KIMI_API_KEY", os.getenv("NVIDIA_KIMI_API_KEY"))
        model = model or getattr(settings, "KIMI_MODEL", "moonshotai/kimi-k2.6")
        
        if not api_key:
            raise ValueError("NVIDIA_KIMI_API_KEY not found in settings or environment variables.")
            
        super().__init__(api_key=api_key, model=model)

