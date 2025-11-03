import json
import google.generativeai as genai
import os
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from dotenv import load_dotenv  # ADD THIS

# Load environment variables from .env file
load_dotenv() 

# Configure Gemini AI with API key from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = 'gemini-2.0-flash-lite'

# Complete database of Nigerian bank USSD codes
# Contains all major Nigerian banks with their USSD codes for different services
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

# Helper function to determine if a query is simple enough for direct response
# This helps decide whether to use AI or just return direct USSD codes
def is_very_simple_direct_query(user_lower):
    """
    Check if the user query is a simple request for USSD codes
    Returns True for basic queries like 'uba balance', False for complex questions
    """
    simple_patterns = ['balance', 'transfer', 'airtime', 'data']
    
    banks = list(BANK_USSD_CODES.keys())
    bank_found = any(bank in user_lower for bank in banks)
    service_found = any(pattern in user_lower for pattern in simple_patterns)
    
    # If it's a bank + service query with few words, use direct response
    if bank_found and service_found:
        words = user_lower.split()
        if len(words) <= 3:
            return True
    
    return False

# Generate direct USSD code responses without using AI
# This provides instant responses for simple code requests
def generate_direct_ussd_response(user_lower):
    """
    Generate direct USSD code responses for simple queries
    Returns formatted USSD codes without AI processing
    """
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

# Generate AI-powered responses using Google Gemini
# This handles complex questions that need intelligent answers
def generate_ai_response(user_message):
    """
    Generate intelligent AI responses for complex banking questions
    Uses Google Gemini AI to provide helpful, contextual answers
    """
    try:
        print("Calling Gemini AI for intelligent response...")
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Prompt designed to get direct, helpful responses without 'fetching' language
        prompt = f"""You are a Nigerian banking expert. Answer this question helpfully and directly:

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

Provide a helpful response about Nigerian bank USSD services. Answer directly without saying you are fetching or retrieving information."""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=400,
                temperature=0.7
            )
        )
        
        ai_response = response.text.strip()
        print(f"AI response generated successfully")
        
        return ai_response
        
    except Exception as ai_error:
        print(f"AI Error: {ai_error}")
        return None

# Main agent endpoint that handles all incoming requests
# Supports both A2A protocol and regular JSON formats
@csrf_exempt
@require_http_methods(["POST"])
def ussd_agent(request):
    """
    Main AI agent endpoint for Nigerian Bank USSD codes
    Handles both simple code requests and complex AI questions
    Compatible with Telex.im A2A protocol
    """
    try:
        data = json.loads(request.body)
        
        # Support both A2A protocol (content field) and regular format (message field)
        user_message = data.get('content', '').strip()
        if not user_message:
            user_message = data.get('message', '').strip()
            
        user_lower = user_message.lower()
        
        print(f"Processing user query: {user_message}")
        
        # Health check endpoint for monitoring
        if user_lower in ['health', 'test', 'ping', 'status']:
            return JsonResponse({
                "status": "healthy",
                "service": "Nigerian Bank USSD AI Agent", 
                "ai_available": bool(GEMINI_API_KEY),
                "total_banks": len(BANK_USSD_CODES)
            })
        
        # Use AI for complex questions, direct responses for simple code requests
        if GEMINI_API_KEY and not is_very_simple_direct_query(user_lower):
            print("Using AI for complex query...")
            ai_response = generate_ai_response(user_message)
            if ai_response and len(ai_response) > 20:
                print("AI response successful")
                # Return in A2A protocol format
                return JsonResponse({"content": ai_response, "type": "text"})
            else:
                print("AI response failed, using fallback")
        
        # Fallback to direct USSD code responses
        response = generate_direct_ussd_response(user_lower)
        # Return in A2A protocol format
        return JsonResponse({"content": response, "type": "text"})
        
    except Exception as e:
        print(f"Error in ussd_agent: {e}")
        # Emergency fallback response
        return JsonResponse({
            "content": "First Bank Balance: *894*00#\nGTB Balance: *737*6*1#\nUBA Balance: *919*00#",
            "type": "text"
        })

# Test endpoint to verify AI functionality
@csrf_exempt
@require_http_methods(["POST"])
def test_ai(request):
    """Test endpoint to verify Gemini AI is working correctly"""
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

# A2A protocol health check endpoint required by Telex.im
@csrf_exempt
def a2a_health(request):
    """
    Health check endpoint for A2A protocol compliance
    Required by Telex.im to verify agent status
    """
    return JsonResponse({
        "status": "healthy",
        "service": "Nigerian Bank USSD AI Agent",
        "a2a_protocol": "supported",
        "ai_available": bool(GEMINI_API_KEY),
        "total_banks": len(BANK_USSD_CODES)
    })