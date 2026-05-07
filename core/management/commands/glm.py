from django.core.management.base import BaseCommand
from core.ai_services import GLMAIService
import sys
import os
import json

class Command(BaseCommand):
    help = 'Chat with GLM AI via NVIDIA API (with Thinking/Reasoning)'

    def add_arguments(self, parser):
        parser.add_argument('prompt', type=str, help='The prompt to send to GLM')
        parser.add_argument('--system', type=str, default='You are a helpful assistant.', help='System prompt')

    def handle(self, *args, **options):
        prompt = options['prompt']
        system = options['system']
        
        # Color configuration
        use_color = sys.stdout.isatty() and os.getenv("NO_COLOR") is None
        reasoning_color = "\033[90m" if use_color else ""
        reset_color = "\033[0m" if use_color else ""
        
        self.stdout.write(self.style.NOTICE(f"Connecting to GLM..."))
        
        try:
            service = GLMAIService()
            stream = service.chat(prompt, system_prompt=system, stream=True)
            
            self.stdout.write(self.style.SUCCESS("\nGLM's Response:\n" + "-"*30))
            
            for line in stream:
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        data_str = decoded_line[6:].strip()
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data['choices'][0].get('delta', {})
                            
                            # Handle Reasoning Content (Thinking)
                            reasoning = delta.get('reasoning_content')
                            if reasoning:
                                sys.stdout.write(f"{reasoning_color}{reasoning}{reset_color}")
                                sys.stdout.flush()
                            
                            # Handle Normal Content
                            content = delta.get('content')
                            if content:
                                sys.stdout.write(content)
                                sys.stdout.flush()
                        except Exception:
                            pass
            
            self.stdout.write("\n" + "-"*30)
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))
