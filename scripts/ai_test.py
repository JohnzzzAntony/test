import os
import sys
import django
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')
django.setup()

from core.ai_services import KimiAIService

def test_service(service_class, name):
    print(f"\n--- Testing {name} ---")
    try:
        service = service_class()
        prompt = "Hello, who are you? Please keep it very short (one sentence)."
        
        # Use stream=False for simple testing
        response = service.chat(prompt, stream=False)
        
        # Handling the response object from openai client (chat.completions.create)
        content = response.choices[0].message.content
        print(f"Response: {content}")
        
    except Exception as e:
        print(f"Error testing {name}: {str(e)}")

def main():
    print("Starting AI Services Verification...")
    
    test_service(KimiAIService, "Kimi (Moonshot)")

if __name__ == "__main__":
    main()

