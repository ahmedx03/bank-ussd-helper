import json
import google.generativeai as genai
import os
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Configure Gemini AI
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
print(f" GEMINI_API_KEY available: {bool(GEMINI_API_KEY)}")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print(" Gemini AI configured")
else:
    print(" No GEMINI_API_KEY found")

MODEL_NAME = 'gemini-2.0-flash-lite'

# Bank USSD Database (same as before)
BANK_USSD_CODES = {
    'access bank': {'balance': '*901*00#', 'transfer': '*901*Amount*AccountNumber#', 'airtime': '*901*Amount*PhoneNumber#', 'main': '*901#'},
    'gtb': {'balance': '*737*6*1#', 'transfer': '*737*1*Amount*AccountNumber#', 'airtime': '*737*Amount*PhoneNumber#', 'main': '*737#'},
    'zenith bank': {'balance': '*966*00#', 'transfer': '*966*Amount*AccountNumber#', 'airtime': '*966*Amount*PhoneNumber#', 'main': '*966#'},
    'first bank': {'balance': '*894*00#', 'transfer': '*894*Amount*AccountNumber#', 'airtime': '*894*Amount*PhoneNumber#', 'main': '*894#'},
    'uba': {'balance': '*919*00#', 'transfer': '*919*3*Amount*AccountNumber#', 'airtime': '*919*Amount*PhoneNumber#', 'main': '*919#'},
    'polaris bank': {'balance': '*833*6#', 'transfer': '*833*1*Amount*AccountNumber#', 'airtime': '*833*Amount*PhoneNumber#', 'main': '*833#'},
    'union bank': {'balance': '*826*7#', 'transfer': '*826*4*Amount*AccountNumber#', 'airtime': '*826*3*Amount*PhoneNumber#', 'main': '*826#'},
    'fidelity bank': {'balance': '*770*00#', 'transfer': '*770*Amount*AccountNumber#', 'airtime': '*770*Amount*PhoneNumber#', 'main': '*770#'},
    'ecobank': {'balance': '*326*00#', 'transfer': '*326*3*Amount*AccountNumber#', 'airtime': '*326*Amount*PhoneNumber#', 'main': '*326#'},
    'wema bank': {'balance': '*945*00#', 'transfer': '*945*2*Amount*AccountNumber#', 'airtime': '*945*1*Amount*PhoneNumber#', 'main': '*945#'},
    'sterling bank': {'balance': '*822*5#', 'transfer': '*822*1*Amount*AccountNumber#', 'airtime': '*822*2*Amount*PhoneNumber#', 'main': '*822#'},
    'fcmb': {'balance': '*329*00#', 'transfer': '*329*Amount*AccountNumber#', 'airtime': '*329*Amount*PhoneNumber#', 'main': '*329#'},
    'unity bank': {'balance': '*7799*0#', 'transfer': '*7799*2*Amount*AccountNumber#', 'airtime': '*7799*1*Amount*PhoneNumber#', 'main': '*7799#'},
    'keystone bank': {'balance': '*7111*1#', 'transfer': '*7111*2*Amount*AccountNumber#', 'airtime': '*7111*3*Amount*PhoneNumber#', 'main': '*7111#'},
    'stanbic ibtc': {'balance': '*909*3#', 'transfer': '*909*2*Amount*AccountNumber#', 'airtime': '*909*1*Amount*PhoneNumber#', 'main': '*909#'},
    'jaiz bank': {'balance': '*773*3#', 'transfer': '*773*2*Amount*AccountNumber#', 'airtime': '*773*1*Amount*PhoneNumber#', 'main': '*773#'},
    'heritage bank': {'balance': '*745*0#', 'transfer': '*745*1*Amount*AccountNumber#', 'airtime': '*745*2*Amount*PhoneNumber#', 'main': '*745#'}
}

@csrf_exempt
@require_http_methods(["POST"])
def ussd_agent(request):
    """
    Smart AI Agent - With Debug Logging
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        user_lower = user_message.lower()
        
        print(f" Received: {user_message}")
        print(f" GEMINI_API_KEY available: {bool(GEMINI_API_KEY)}")
        
        # Health check
        if user_lower in ['health', 'test', 'ping', 'status']:
            return JsonResponse({
                "status": "healthy",
                "service": "Nigerian Bank USSD AI Agent", 
                "ai_available": bool(GEMINI_API_KEY),
                "total_banks": len(BANK_USSD_CODES)
            })
        
        # Check if very simple direct query
        is_simple = is_very_simple_direct_query(user_lower)
        print(f"🔍 Is simple direct query: {is_simple}")
        
        # Try AI first for non-simple queries
        if GEMINI_API_KEY and not is_simple:
            print(" Attempting AI response...")
            ai_response = generate_ai_response(user_message)
            if ai_response and len(ai_response) > 20:
                print(" AI response successful")
                return JsonResponse({"message": ai_response, "type": "text"})
            else:
                print("❌ AI response failed or too short")
        
        # Fallback to direct response
        print(" Using direct response fallback")
        response = generate_direct_ussd_response(user_lower)
        return JsonResponse({"message": response, "type": "text"})
        
    except Exception as e:
        print(f" Main error: {e}")
        return JsonResponse({
            "message": "First Bank Balance: *894*00#\nGTB Balance: *737*6*1#\nUBA Balance: *919*00#",
            "type": "text"
        })

def is_very_simple_direct_query(user_lower):
    """Only return True for VERY simple direct queries"""
    simple_patterns = ['balance', 'transfer', 'airtime', 'data']
    
    banks = list(BANK_USSD_CODES.keys())
    bank_found = any(bank in user_lower for bank in banks)
    service_found = any(pattern in user_lower for pattern in simple_patterns)
    
    if bank_found and service_found:
        words = user_lower.split()
        if len(words) <= 3:
            return True
    
    return False

def generate_direct_ussd_response(user_lower):
    """Direct USSD code responses"""
    for bank_name, codes in BANK_USSD_CODES.items():
        if bank_name in user_lower:
            if 'balance' in user_lower:
                return f"{bank_name.title()} Balance Check:\nDial: {codes['balance']}\nFollow prompts and enter PIN."
            elif 'transfer' in user_lower:
                return f"{bank_name.title()} Transfer:\nDial: {codes['transfer']}\nReplace Amount and AccountNumber."
            elif 'airtime' in user_lower:
                return f"{bank_name.title()} Airtime:\nDial: {codes['airtime']}\nReplace Amount and PhoneNumber."
            else:
                return f"{bank_name.title()} USSD Codes:\nMain: {codes['main']}\nBalance: {codes['balance']}\nTransfer: {codes['transfer']}\nAirtime: {codes['airtime']}"
    
    return "Nigerian Bank USSD Helper. Available banks: Access, GTB, UBA, Zenith, First Bank, and 12 others."

def generate_ai_response(user_message):
    """Generate AI response with detailed error handling"""
    try:
        print(f" Calling Gemini AI with model: {MODEL_NAME}")
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = f"""You are a Nigerian banking expert. Answer this question helpfully:

User: {user_message}

Nigerian Bank USSD Codes:
- Access Bank: *901# (Balance: *901*00#)
- GTB: *737# (Balance: *737*6*1#)
- Zenith Bank: *966# (Balance: *966*00#)
- First Bank: *894# (Balance: *894*00#)
- UBA: *919# (Balance: *919*00#)
- Polaris Bank: *833# (Balance: *833*6#)
- Union Bank: *826# (Balance: *826*7#)
- 10 other banks available

Provide a helpful response about Nigerian bank USSD services."""

        print(" Sending request to Gemini...")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=400,
                temperature=0.7
            ),
            request_options={"timeout": 10}
        )
        
        ai_response = response.text.strip()
        print(f" AI Response received: {ai_response[:100]}...")
        
        return ai_response
        
    except Exception as ai_error:
        print(f" AI Error details: {type(ai_error).__name__}: {ai_error}")
        return None

# Test endpoint to check AI directly
@csrf_exempt
@require_http_methods(["POST"])
def test_ai(request):
    """Test AI directly"""
    if not GEMINI_API_KEY:
        return JsonResponse({"error": "No API key"}, status=500)
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            "What is 2+2? Answer in one word.",
            request_options={"timeout": 5}
        )
        return JsonResponse({
            "ai_working": True,
            "response": response.text,
            "model": MODEL_NAME
        })
    except Exception as e:
        return JsonResponse({
            "ai_working": False,
            "error": str(e),
            "error_type": type(e).__name__
        }, status=500)