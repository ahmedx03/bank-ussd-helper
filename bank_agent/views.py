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

# Use the fastest model
MODEL_NAME = 'gemini-2.0-flash-lite'

@csrf_exempt
@require_http_methods(["POST"])
def ussd_agent(request):
    """
    Fast AI Agent for Nigerian Bank USSD Codes
    """
    start_time = time.time()
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        # Immediate response for common queries
        user_lower = user_message.lower()
        
        # Instant responses for fastest performance
        if 'uba balance' in user_lower:
            return JsonResponse({
                "message": "UBA Balance Check: Dial *919*00#\n\nFollow the prompts and enter your UBA PIN to check your account balance.",
                "type": "text"
            })
            
        if 'uba' in user_lower and 'balance' in user_lower:
            return JsonResponse({
                "message": "UBA Balance: *919*00#\nEnter your PIN when prompted to view your account balance.",
                "type": "text"
            })
        
        # Check if API key is available
        if not GEMINI_API_KEY:
            return JsonResponse({
                "message": "UBA Balance Check: *919*00#\nGTB: *737#\nAccess Bank: *901#\nZenith Bank: *966#\nFirst Bank: *894#",
                "type": "text"
            })
        
        # Fast AI Response with optimized prompt
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            
            prompt = f"""User Question: {user_message}

You are a Nigerian bank USSD code assistant. Provide direct, accurate USSD codes immediately.

Important: 
- Respond with only the USSD code and brief instructions
- No introductions or greetings
- Be specific and accurate
- Maximum 2 sentences

Bank USSD Codes:
- UBA: *919# (Balance: *919*00#)
- GTB: *737# (Balance: *737*6*1#)
- Access Bank: *901# (Balance: *901*00#)
- Zenith Bank: *966# (Balance: *966*00#)
- First Bank: *894# (Balance: *894*00#)
- Polaris Bank: *833# (Balance: *833*6#)
- Union Bank: *826# (Balance: *826*7#)
- Fidelity Bank: *770# (Balance: *770*00#)
- Ecobank: *326# (Balance: *326*00#)

Response:"""

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=100,
                    temperature=0.1,
                    top_p=0.8
                ),
                request_options={"timeout": 5}
            )
            
            ai_response = response.text.strip()
            
            if ai_response and len(ai_response) > 10:
                return JsonResponse({
                    "message": ai_response,
                    "type": "text"
                })
            else:
                raise ValueError("AI response too short")
            
        except Exception as ai_error:
            # Smart fallback based on query
            return smart_fallback(user_lower)
        
    except Exception as e:
        return smart_fallback("")

def smart_fallback(user_lower):
    """Intelligent fallback without emojis"""
    if not user_lower:
        return JsonResponse({
            "message": "UBA Balance: *919*00#\nFor other banks, specify which bank you need.",
            "type": "text"
        })
    
    # UBA responses
    if 'uba' in user_lower:
        if 'balance' in user_lower:
            return JsonResponse({
                "message": "UBA Balance Check: Dial *919*00#\nFollow the prompts and enter your UBA PIN.",
                "type": "text"
            })
        elif 'transfer' in user_lower:
            return JsonResponse({
                "message": "UBA Transfer: Dial *919*3*Amount*AccountNumber#\nReplace Amount and AccountNumber with actual values.",
                "type": "text"
            })
        elif 'airtime' in user_lower:
            return JsonResponse({
                "message": "UBA Airtime: Dial *919*Amount*PhoneNumber#\nReplace Amount and PhoneNumber with actual values.",
                "type": "text"
            })
        else:
            return JsonResponse({
                "message": "UBA USSD Codes:\nBalance: *919*00#\nTransfer: *919*3*Amount*Account#\nAirtime: *919*Amount*Phone#\nData: *919*14#",
                "type": "text"
            })
    
    # GTB responses
    elif 'gtb' in user_lower:
        if 'balance' in user_lower:
            return JsonResponse({
                "message": "GTB Balance: Dial *737*6*1#\nFollow the prompts to view your account balance.",
                "type": "text"
            })
        else:
            return JsonResponse({
                "message": "GTB USSD: *737#\nBalance: *737*6*1#\nTransfer: *737*1*Amount*Account#\nAirtime: *737*Amount*Phone#",
                "type": "text"
            })
    
    # Access Bank
    elif 'access' in user_lower:
        if 'balance' in user_lower:
            return JsonResponse({
                "message": "Access Bank Balance: Dial *901*00#\nEnter your PIN to check balance.",
                "type": "text"
            })
        else:
            return JsonResponse({
                "message": "Access Bank: *901#\nBalance: *901*00#\nTransfer: *901*Amount*Account#\nAirtime: *901*Amount*Phone#",
                "type": "text"
            })
    
    # General bank list
    banks = [
        "UBA: *919#", "GTB: *737#", "Access Bank: *901#", 
        "Zenith Bank: *966#", "First Bank: *894#", "Polaris Bank: *833#"
    ]
    
    return JsonResponse({
        "message": f"Bank USSD Codes: {', '.join(banks[:4])}. Specify which bank you need help with.",
        "type": "text"
    })

@csrf_exempt
def health_check(request):
    return JsonResponse({
        "status": "healthy", 
        "service": "Nigerian Bank USSD AI Agent",
        "model": MODEL_NAME,
        "ai_enabled": bool(GEMINI_API_KEY)
    })

@csrf_exempt
@require_http_methods(["POST"])
def test_direct(request):
    """Direct test endpoint"""
    return JsonResponse({
        "message": "UBA Balance Check USSD Code: *919*00#\nDial this code and follow the prompts to check your account balance.",
        "type": "text"
    })