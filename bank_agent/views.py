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
    Fixed AI Agent - Correct API Syntax
    """
    try:
        data = json.loads(request.body)
        
        # SUPPORT BOTH A2A PROTOCOL AND YOUR EXISTING FORMAT
        user_message = data.get('content', '').strip()  # A2A protocol uses 'content'
        if not user_message:
            user_message = data.get('message', '').strip()  # Fallback to your existing 'message'
            
        user_lower = user_message.lower()
        
        print(f"USER QUERY: {user_message}")
        
        # Health check
        if user_lower in ['health', 'test', 'ping', 'status']:
            return JsonResponse({
                "status": "healthy",
                "service": "Nigerian Bank USSD AI Agent", 
                "ai_available": bool(GEMINI_API_KEY),
                "total_banks": len(BANK_USSD_CODES)
            })
        
        # Try AI first for non-simple queries
        if GEMINI_API_KEY and not is_very_simple_direct_query(user_lower):
            print("ATTEMPTING AI RESPONSE...")
            ai_response = generate_ai_response(user_message)
            if ai_response and len(ai_response) > 20:
                print("AI RESPONSE SUCCESSFUL")
                # RETURN A2A PROTOCOL FORMAT
                return JsonResponse({"content": ai_response, "type": "text"})
            else:
                print("AI RESPONSE FAILED")
        
        # Fallback to direct response
        response = generate_direct_ussd_response(user_lower)
        # RETURN A2A PROTOCOL FORMAT
        return JsonResponse({"content": response, "type": "text"})
        
    except Exception as e:
        print(f"ERROR: {e}")
        # RETURN A2A PROTOCOL FORMAT
        return JsonResponse({
            "content": "First Bank Balance: *894*00#\nGTB Balance: *737*6*1#\nUBA Balance: *919*00#",
            "type": "text"
        })
def is_very_simple_direct_query(user_lower):
    """Only use direct responses for very basic code requests"""
    # Very specific patterns that should get instant codes
    direct_patterns = [
        'balance code', 'transfer code', 'airtime code', 
        'ussd code', 'code for', 'what is the code'
    ]
    
    # Check for exact direct patterns
    if any(pattern in user_lower for pattern in direct_patterns):
        return True
    
    # For everything else (including comparisons), use AI
    return False
def generate_ai_response(user_message):
    """Generate AI responses with STRICT instructions to avoid 'fetching' language"""
    try:
        print("CALLING GEMINI AI...")
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = f"""CRITICAL: DO NOT use words like "fetching", "retrieving", "searching", "looking up", "getting", or "finding". Provide the answer DIRECTLY.

Question: {user_message}

Nigerian Bank USSD Codes:
- Access Bank: *901# (Balance: *901*00#)
- GTB: *737# (Balance: *737*6*1#)
- Zenith Bank: *966# (Balance: *966*00#)
- First Bank: *894# (Balance: *894*00#)
- UBA: *919# (Balance: *919*00#)
- Polaris Bank: *833# (Balance: *833*6#)
- Union Bank: *826# (Balance: *826*7#)
- 10 other Nigerian banks

Answer directly and helpfully. Start with the actual information immediately:"""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=350,
                temperature=0.1,  # Very low temperature for deterministic responses
                top_p=0.7,
                top_k=40
            )
        )
        
        ai_response = response.text.strip()
        print(f"RAW AI RESPONSE: {ai_response[:100]}...")
        
        # AGGRESSIVE cleaning of "fetching" language
        forbidden_words = [
            'fetching', 'retrieving', 'searching', 'looking up', 'getting', 'finding',
            'Fetching', 'Retrieving', 'Searching', 'Looking up', 'Getting', 'Finding'
        ]
        
        for word in forbidden_words:
            ai_response = ai_response.replace(word, "")
        
        # Remove any "..." or incomplete sentences caused by replacements
        ai_response = ai_response.replace("...", ".").replace("..", ".")
        ai_response = ai_response.strip()
        
        # If the response starts with weird punctuation after cleaning, fix it
        if ai_response and ai_response[0] in [',', '.', ';', ':']:
            ai_response = ai_response[1:].strip()
            
        print(f"CLEANED AI RESPONSE: {ai_response[:100]}...")
        return ai_response
        
    except Exception as ai_error:
        print(f"AI ERROR: {ai_error}")
        return None
def generate_ai_response(user_message):
    """Generate intelligent AI responses without 'fetching' language"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = f"""You are a helpful Nigerian banking AI assistant. Provide immediate, direct answers.

Question: {user_message}

Available Bank USSD Codes:
- Access Bank: *901# (Balance: *901*00#)
- GTB: *737# (Balance: *737*6*1#) 
- UBA: *919# (Balance: *919*00#)
- 14 other Nigerian banks

CRITICAL: Answer directly without using words like "fetching", "retrieving", or "searching". Provide the information immediately.

Response:"""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=300,
                temperature=0.2,  # More deterministic
                top_p=0.8
            )
        )
        
        return response.text.strip()
        
    except Exception as ai_error:
        return None
    
# Add the missing test-ai endpoint
@csrf_exempt
@require_http_methods(["POST"])
def test_ai(request):
    """Test AI directly"""
    if not GEMINI_API_KEY:
        return JsonResponse({"error": "No API key"}, status=500)
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            "What is 2+2? Answer with one number only."
        )
        return JsonResponse({
            "ai_working": True,
            "response": response.text,
            "model": MODEL_NAME
        })
    except Exception as e:
        return JsonResponse({
            "ai_working": False,
            "error": str(e)
        }, status=500)

@csrf_exempt
def a2a_health(request):
    """
    A2A Protocol health check endpoint
    """
    return JsonResponse({
        "status": "healthy",
        "service": "Nigerian Bank USSD AI Agent",
        "a2a_protocol": "supported",
        "ai_available": bool(GEMINI_API_KEY),
        "total_banks": len(BANK_USSD_CODES)
    })