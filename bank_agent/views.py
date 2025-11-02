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

@csrf_exempt
@require_http_methods(["POST"])
def ussd_agent(request):
    """
    Fast AI Agent for Nigerian Bank USSD Codes
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        user_lower = user_message.lower()
        
        # INSTANT responses for all common queries - NO AI delay
        instant_responses = {
            'uba balance': "UBA Balance: *919*00#\nDial this code and enter your PIN to check account balance.",
            'check uba balance': "UBA Balance Check: *919*00#\nFollow the prompts and enter your UBA PIN.",
            'uba balance check': "UBA Balance: *919*00#\nEnter your PIN when prompted.",
            'uba ussd': "UBA USSD Banking:\nBalance: *919*00#\nTransfer: *919*3*Amount*Account#\nAirtime: *919*Amount*Phone#\nMain Menu: *919#",
            'gtb balance': "GTB Balance: *737*6*1#\nDial and follow prompts to view balance.",
            'gtb ussd': "GTB USSD: *737#\nBalance: *737*6*1#\nTransfer: *737*1*Amount*Account#\nAirtime: *737*Amount*Phone#",
            'access bank balance': "Access Bank Balance: *901*00#\nEnter your PIN to check balance.",
            'access bank ussd': "Access Bank: *901#\nBalance: *901*00#\nTransfer: *901*Amount*Account#\nAirtime: *901*Amount*Phone#",
            'zenith bank balance': "Zenith Bank Balance: *966*00#\nDial and enter PIN for balance.",
            'first bank balance': "First Bank Balance: *894*00#\nFollow prompts to check account balance."
        }
        
        # Check for instant response matches
        for key, response in instant_responses.items():
            if key in user_lower:
                return JsonResponse({
                    "message": response,
                    "type": "text"
                })
        
        # Check if API key is available
        if not GEMINI_API_KEY:
            return JsonResponse({
                "message": "UBA Balance: *919*00#\nGTB: *737#\nAccess Bank: *901#\nSpecify which bank and service you need.",
                "type": "text"
            })
        
        # STRICT AI Prompt - No "retrieving" language allowed
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            
            prompt = f"""User: {user_message}

Provide the exact USSD code immediately. Do NOT say "retrieving", "fetching", "searching", or "looking up". 

CRITICAL: Start with the USSD code directly. No introductory phrases.

Bank Codes:
- UBA Balance: *919*00#
- GTB Balance: *737*6*1# 
- Access Bank Balance: *901*00#
- Zenith Bank Balance: *966*00#
- First Bank Balance: *894*00#
- UBA Transfer: *919*3*Amount*AccountNumber#
- GTB Transfer: *737*1*Amount*AccountNumber#
- UBA Airtime: *919*Amount*PhoneNumber#

Response must begin with the USSD code or bank name:"""

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=80,
                    temperature=0.1,
                    top_p=0.7
                ),
                request_options={"timeout": 4}
            )
            
            ai_response = response.text.strip()
            
            # Clean the response - remove any "retrieving" language
            ai_response = ai_response.replace("Retrieving", "").replace("retrieving", "")
            ai_response = ai_response.replace("Fetching", "").replace("fetching", "")
            ai_response = ai_response.replace("Searching", "").replace("searching", "")
            ai_response = ai_response.replace("Looking up", "").replace("looking up", "")
            
            if ai_response and len(ai_response) > 5:
                return JsonResponse({
                    "message": ai_response,
                    "type": "text"
                })
            else:
                raise ValueError("AI response invalid")
            
        except Exception as ai_error:
            return smart_fallback(user_lower)
        
    except Exception as e:
        return smart_fallback("")

def smart_fallback(user_lower):
    """Instant fallback responses"""
    if 'uba' in user_lower:
        if 'balance' in user_lower:
            return JsonResponse({
                "message": "UBA Balance: *919*00#\nDial and enter PIN to check balance.",
                "type": "text"
            })
        elif 'transfer' in user_lower:
            return JsonResponse({
                "message": "UBA Transfer: *919*3*Amount*AccountNumber#\nReplace Amount and AccountNumber.",
                "type": "text"
            })
        else:
            return JsonResponse({
                "message": "UBA USSD Codes:\nBalance: *919*00#\nTransfer: *919*3*Amount*Account#\nAirtime: *919*Amount*Phone#",
                "type": "text"
            })
    
    elif 'gtb' in user_lower:
        if 'balance' in user_lower:
            return JsonResponse({
                "message": "GTB Balance: *737*6*1#\nDial to check account balance.",
                "type": "text"
            })
        else:
            return JsonResponse({
                "message": "GTB USSD: *737#\nBalance: *737*6*1#\nTransfer: *737*1*Amount*Account#",
                "type": "text"
            })
    
    elif 'access' in user_lower:
        return JsonResponse({
            "message": "Access Bank: *901#\nBalance: *901*00#\nTransfer: *901*Amount*Account#",
            "type": "text"
        })
    
    elif 'zenith' in user_lower:
        return JsonResponse({
            "message": "Zenith Bank: *966#\nBalance: *966*00#\nTransfer services available.",
            "type": "text"
        })
    
    elif 'first bank' in user_lower:
        return JsonResponse({
            "message": "First Bank: *894#\nBalance: *894*00#\nTransfer: *894*Amount*Account#",
            "type": "text"
        })
    
    return JsonResponse({
        "message": "UBA: *919*00# for balance\nGTB: *737# for services\nAccess Bank: *901#\nSpecify bank and service needed.",
        "type": "text"
    })

@csrf_exempt
def health_check(request):
    return JsonResponse({
        "status": "healthy", 
        "service": "Instant USSD AI Agent",
        "model": MODEL_NAME
    })