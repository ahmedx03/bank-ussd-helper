import json
import os
import time
import hashlib
import hmac
import threading
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Gemini AI Configuration

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini AI configured successfully!")
else:
    print("GEMINI_API_KEY not found in .env")

MODEL_NAME = 'gemini-2.0-flash-lite'

#  Bank USSD Code Database
BANK_USSD_CODES = {
    'access bank': {'balance': '*901*00#', 'transfer': '*901*Amount*AccountNumber#', 'airtime': '*901*Amount*PhoneNumber#', 'main': '*901#'},
    'gtb': {'balance': '*737*6*1#', 'transfer': '*737*1*Amount*AccountNumber#', 'airtime': '*737*Amount*PhoneNumber#', 'main': '*737#'},
    'zenith bank': {'balance': '*966*00#', 'transfer': '*966*Amount*AccountNumber#', 'airtime': '*966*Amount*PhoneNumber#', 'main': '*966#'},
    'first bank': {'balance': '*894*00#', 'transfer': '*894*Amount*AccountNumber#', 'airtime': '*894*Amount*PhoneNumber#', 'main': '*894#'},
    'uba': {'balance': '*919*00#', 'transfer': '*919*3*Amount*AccountNumber#', 'airtime': '*919*Amount*PhoneNumber#', 'main': '*919#'},
}

# In-memory Cache (Simple)
CACHE = {}  # key: user_message.lower(), value: response

def get_cached_response(message):
    return CACHE.get(message.lower())

def set_cached_response(message, response):
    if len(CACHE) > 50:  # avoid memory bloat
        CACHE.clear()
    CACHE[message.lower()] = response

# Logging System
LOG_FILE = "logs/ai_logs.json"
os.makedirs("logs", exist_ok=True)

def log_interaction(user_message, ai_response, source="unknown"):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,
        "user_message": user_message,
        "ai_response": ai_response,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


# Gemini AI Function
def generate_ai_response(user_message):
    """Generate a response using Gemini AI"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = f"""
You are a helpful Nigerian banking expert. Provide direct, immediate answers about Nigerian bank USSD codes and services.

User Question: "{user_message}"

Rules:
- Give direct, factual answers. No filler.
- Use exact USSD codes when relevant.
- Keep answers under 100 words.
- Example: "UBA balance" → "UBA Balance: Dial *919*00#"
"""
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=300,
                temperature=0.7
            )
        )
        ai_response = response.text.strip()
        if len(ai_response) > 1000:
            ai_response = ai_response[:1000] + "..."
        return ai_response
    except Exception as e:
        print(f" AI generation error: {e}")
        return "Access Bank: *901*00# | GTB: *737*6*1# | UBA: *919*00# | Zenith: *966*00#"

# Main AI Endpoint
@csrf_exempt
@require_http_methods(["POST"])
def ussd_agent(request):
    """Main AI endpoint for Nigerian Bank USSD assistant"""
    try:
        # Health/test messages
        if user_message.lower() in ["ping", "health", "status", "test"]:
            return JsonResponse({
                "status": "healthy",
                "ai_available": bool(GEMINI_API_KEY),
                "cache_size": len(CACHE),
                "total_banks": len(BANK_USSD_CODES),
            })

        # Use cached result if available
        cached = get_cached_response(user_message)
        if cached:
            print(f"🧠 Cache hit for '{user_message}'")
            return JsonResponse({"content": cached, "cached": True, "type": "text"})

        print(f" Processing: {user_message}")

        ai_response = None
        def worker():
            nonlocal ai_response
            ai_response = generate_ai_response(user_message)

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=60)

        if not ai_response:
            ai_response = "I can help with Nigerian bank USSD codes. Try UBA *919#, GTB *737#, Access *901#."

        # Cache + Log
        set_cached_response(user_message, ai_response)
        log_interaction(user_message, ai_response, source="telex")

        return JsonResponse({"content": ai_response, "cached": False, "type": "text"})

    except Exception as e:
        print(f" Error: {e}")
        return JsonResponse({"content": "Something went wrong. Try again."}, status=500)

# A2A Health Endpoint
@csrf_exempt
def a2a_health(request):
    """A2A protocol health check"""
    return JsonResponse({
        "status": "healthy",
        "ai_available": bool(GEMINI_API_KEY),
        "a2a_protocol": "supported",
        "total_banks": len(BANK_USSD_CODES),
    })

# Root Index Endpoint
def index(request):
    """Simple landing route"""
    return HttpResponse(
        "<h3> Nigerian Bank USSD AI Agent</h3><p>Status: Running</p>",
        content_type="text/html"
    )
