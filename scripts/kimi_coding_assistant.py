import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')
django.setup()

from core.ai_services import KimiAIService
from dotenv import load_dotenv

load_dotenv()

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/kimi_coding_assistant.py 'your coding task description'")
        sys.exit(1)

    task = " ".join(sys.argv[1:])
    
    print(f"Kimi is thinking about your task: {task}...\n")
    
    service = KimiAIService()
    
    try:
        # Use streaming to show progress/thinking if possible, 
        # but for simplicity in this script we'll just handle the response.
        result = service.chat(task, stream=False)
        
        # NVIDIA's implementation of moonshotai/kimi-k2.6 might include thinking in the content
        # or as a separate field depending on the exact API response structure.
        # Standard chat completion response: result['choices'][0]['message']['content']
        
        content = result.get('choices', [{}])[0].get('message', {}).get('content', 'No response content.')
        print("-" * 50)
        print(content)
        print("-" * 50)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
