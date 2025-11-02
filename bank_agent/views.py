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
        
        # First, check if this is a health check or test message
        if user_lower in ['health', 'test', 'ping', 'status']:
            return JsonResponse({
                "status": "healthy",
                "service": "Nigerian Bank USSD AI Agent", 
                "ai_available": bool(GEMINI_API_KEY),
                "total_banks": len(BANK_USSD_CODES)
            })
        
        # Check if this is a CLEAR direct USSD code query
        if is_clear_direct_query(user_lower):
            response = generate_direct_ussd_response(user_lower)
            return JsonResponse({"message": response, "type": "text"})
        
        # Use AI for everything else if API key is available
        if GEMINI_API_KEY:
            ai_response = generate_ai_response(user_message)
            if ai_response and len(ai_response) > 10:  # Make sure we got a valid response
                return JsonResponse({"message": ai_response, "type": "text"})
        
        # Fallback to direct response
        response = generate_direct_ussd_response(user_lower)
        return JsonResponse({"message": response, "type": "text"})
        
    except Exception as e:
        # Ultimate fallback
        return JsonResponse({
            "message": "First Bank Balance: *894*00#\nGTB Balance: *737*6*1#\nUBA Balance: *919*00#\nAccess Bank: *901*00#",
            "type": "text"
        })

def is_clear_direct_query(user_lower):
    """
    Only return True for VERY CLEAR direct USSD code requests
    """
    # Very specific direct query patterns
    direct_patterns = [
        'balance code', 'transfer code', 'airtime code', 
        'ussd code', 'code for', 'what is the code',
        'how to check balance', 'how do i check balance'
    ]
    
    # Check for exact direct patterns
    if any(pattern in user_lower for pattern in direct_patterns):
        return True
    
    # Check for bank + simple service word (not AI words)
    banks = list(BANK_USSD_CODES.keys())
    simple_services = ['balance', 'transfer', 'airtime', 'data']
    
    bank_found = any(bank in user_lower for bank in banks)
    simple_service_found = any(service in user_lower for service in simple_services)
    
    # AI keywords that should NOT trigger direct response
    ai_keywords = [
        'compare', 'which', 'best', 'easiest', 'recommend',
        'difference', 'pros', 'cons', 'should i', 'what\'s the best',
        'better', 'versus', 'vs'
    ]
    
    ai_keyword_found = any(keyword in user_lower for keyword in ai_keywords)
    
    # If it's a simple bank+service query WITHOUT AI keywords, it's direct
    if bank_found and simple_service_found and not ai_keyword_found:
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
    
    return "Nigerian Bank USSD Helper. Ask about specific banks like First Bank, GTB, UBA for balance, transfer, or airtime codes."

def generate_ai_response(user_message):
    """Generate AI response for intelligent questions"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = f"""You are a helpful Nigerian banking expert. Answer this question naturally and helpfully.

User Question: "{user_message}"

Available Nigerian Banks & USSD Codes:
- Access Bank: *901# (Balance: *901*00#)
- GTB: *737# (Balance: *737*6*1#) 
- Zenith Bank: *966# (Balance: *966*00#)
- First Bank: *894# (Balance: *894*00#)
- UBA: *919# (Balance: *919*00#)
- Polaris Bank: *833# (Balance: *833*6#)
- Union Bank: *826# (Balance: *826*7#)
- 10 other Nigerian banks available

Provide a helpful, conversational response. If comparing banks, mention specific strengths. If asking for recommendations, be practical and mention actual USSD codes where relevant."""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=400,
                temperature=0.7
            ),
            request_options={"timeout": 10}
        )
        
        return response.text.strip()
        
    except Exception as ai_error:
        print(f"AI Error: {ai_error}")
        return None