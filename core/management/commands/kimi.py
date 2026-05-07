from django.core.management.base import BaseCommand
from core.ai_services import KimiAIService
import sys

class Command(BaseCommand):
    help = 'Chat with Kimi AI via NVIDIA API (Streaming)'

    def add_arguments(self, parser):
        parser.add_argument('prompt', type=str, help='The prompt to send to Kimi')
        parser.add_argument('--system', type=str, default='You are a helpful assistant.', help='System prompt')

    def handle(self, *args, **options):
        prompt = options['prompt']
        system = options['system']
        
        self.stdout.write(self.style.NOTICE(f"Connecting to Kimi..."))
        
        try:
            service = KimiAIService()
            stream = service.chat(prompt, system_prompt=system, stream=True)
            
            self.stdout.write(self.style.SUCCESS("\nKimi's Response:\n" + "-"*30))
            
            for line in stream:
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        data_str = decoded_line[6:].strip()
                        if data_str == '[DONE]':
                            break
                        try:
                            import json
                            data = json.loads(data_str)
                            content = data['choices'][0]['delta'].get('content', '')
                            sys.stdout.write(content)
                            sys.stdout.flush()
                        except:
                            pass
            
            self.stdout.write("\n" + "-"*30)
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))
