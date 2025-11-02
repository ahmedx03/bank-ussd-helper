import json
import google.generativeai as genai
import os
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Configure Gemini AI
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = 'gemini-2.0-flash-lite'

# Bank USSD Database
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
    Smart AI Agent - Uses AI for intelligent questions, direct for codes
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        user_lower = user_message.lower()
        
        # Check if this is a DIRECT USSD code query
        if is_direct_ussd_query(user_lower):
            response = generate_direct_ussd_response(user_lower)
            return JsonResponse({"message": response, "type": "text"})
        
        # Use AI for everything else
        elif GEMINI_API_KEY:
            return generate_ai_response(user_message)
        
        # Fallback if no API key
        else:
            response = "I can help with Nigerian bank USSD codes. Try asking about specific banks or comparing services."
            return JsonResponse({"message": response, "type": "text"})
        
    except Exception as e:
        return JsonResponse({
            "message": "First Bank Balance: *894*00#\nGTB: *737*6*1#\nUBA: *919*00#",
            "type": "text"
        })

def is_direct_ussd_query(user_lower):
    """Check if this is a simple USSD code request"""
    # List of very specific direct query patterns
    direct_patterns = [
        'balance', 'transfer', 'airtime', 'data', 'code'
    ]
    
    # Bank names
    bank_names = list(BANK_USSD_CODES.keys())
    
    # Check if it's a direct "bank + service" query
    bank_found = any(bank in user_lower for bank in bank_names)
    service_found = any(pattern in user_lower for pattern in direct_patterns)
    
    # Also check for specific code request patterns
    code_request = any(pattern in user_lower for pattern in [
        'ussd code', 'code for', 'what is the code', 'how to check'
    ])
    
    # If it's clearly a direct code request, return True
    if (bank_found and service_found) or (bank_found and code_request):
        return True
        
    return False

def generate_direct_ussd_response(user_lower):
    """Direct USSD code responses - NO AI"""
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

    return "Nigerian Bank USSD Helper\n\nAsk about specific banks: First Bank, GTB, UBA, Access Bank, etc."

def generate_ai_response(user_message):
    """Generate AI response for intelligent questions"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = f"""You are a helpful Nigerian banking expert. Answer this question naturally and helpfully.

User Question: "{user_message}"

Available Banks & USSD Codes:
- Access Bank: *901# (Balance: *901*00#)
- GTB: *737# (Balance: *737*6*1#)
- Zenith Bank: *966# (Balance: *966*00#)
- First Bank: *894# (Balance: *894*00#)
- UBA: *919# (Balance: *919*00#)
- Polaris Bank: *833# (Balance: *833*6#)
- Union Bank: *826# (Balance: *826*7#)
- 10 other Nigerian banks available

Provide a helpful, conversational response. If comparing banks, mention specific strengths and USSD codes. If asking for recommendations, be practical."""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=400,
                temperature=0.7
            ),
            request_options={"timeout": 10}
        )
        
        ai_response = response.text.strip()
        
        return JsonResponse({
            "message": ai_response,
            "type": "text"
        })
        
    except Exception as ai_error:
        # Fallback to direct response
        return JsonResponse({
            "message": "I can help with Nigerian bank USSD codes. Try asking about specific banks or comparing services.",
            "type": "text"
        })

@csrf_exempt
def health_check(request):
    return JsonResponse({
        "status": "healthy", 
        "service": "Smart USSD AI Agent",
        "ai_enabled": bool(GEMINI_API_KEY),
        "total_banks": len(BANK_USSD_CODES)
    })

# AI test endpoint
@csrf_exempt
@require_http_methods(["POST"]) 
def test_ai_direct(request):
    """Direct AI test endpoint"""
    if not GEMINI_API_KEY:
        return JsonResponse({"error": "No API key"}, status=500)
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            "Which Nigerian bank has the easiest USSD banking? Answer in 2 sentences.",
            request_options={"timeout": 5}
        )
        return JsonResponse({
            "ai_working": True,
            "response": response.text
        })
    except Exception as e:
        return JsonResponse({
            "ai_working": False,
            "error": str(e)
        }, status=500)

# Simple GET endpoint for testing
@csrf_exempt
def test_simple(request):
    return JsonResponse({
        "message": "AI Agent is working! Ask me about Nigerian bank USSD codes.",
        "type": "text"
    })