from django.core.management.base import BaseCommand
from core.ai_services import KimiAIService
import sys
import os

_USE_COLOR = sys.stdout.isatty() and os.getenv("NO_COLOR") is None
_REASONING_COLOR = "\033[90m" if _USE_COLOR else ""
_RESET_COLOR = "\033[0m" if _USE_COLOR else ""

class Command(BaseCommand):
    help = 'Chat with Kimi AI via NVIDIA API (Streaming)'

    def add_arguments(self, parser):
        parser.add_argument('prompt', type=str, help='The prompt to send to Kimi')
        parser.add_argument('--system', type=str, default='You are a helpful assistant.', help='System prompt')
        parser.add_argument('--no-stream', action='store_true', help='Disable streaming')

    def handle(self, *args, **options):
        prompt = options['prompt']
        system = options['system']
        stream_enabled = not options['no_stream']
        
        self.stdout.write(self.style.NOTICE(f"Connecting to Kimi (moonshotai/kimi-k2.6)..."))
        
        try:
            service = KimiAIService()
            completion = service.chat(prompt, system_prompt=system, stream=stream_enabled)
            
            self.stdout.write(self.style.SUCCESS("\nKimi's Response:\n" + "-"*30))
            
            if stream_enabled:
                for chunk in completion:
                    if not getattr(chunk, "choices", None):
                        continue
                    if len(chunk.choices) == 0 or getattr(chunk.choices[0], "delta", None) is None:
                        continue
                    
                    delta = chunk.choices[0].delta
                    reasoning = getattr(delta, "reasoning_content", None)
                    if reasoning:
                        sys.stdout.write(f"{_REASONING_COLOR}{reasoning}{_RESET_COLOR}")
                        sys.stdout.flush()
                    
                    if getattr(delta, "content", None) is not None:
                        sys.stdout.write(delta.content)
                        sys.stdout.flush()
            else:
                # Non-streaming mode
                message = completion.choices[0].message
                reasoning = getattr(message, "reasoning_content", None)
                if reasoning:
                    self.stdout.write(f"{_REASONING_COLOR}{reasoning}{_RESET_COLOR}")
                self.stdout.write(message.content)
            
            self.stdout.write("\n" + "-"*30)
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))
