import json
import google.generativeai as genai
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Configure Gemini AI
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

BANK_USSD_CODES = {
    "access bank": "*901#",
    "gtb": "*737#", 
    "zenith bank": "*966#",
    "first bank": "*894#",
    "uba": "*919#",
    "polaris bank": "*833#",
    "union bank": "*826#", 
    "fidelity bank": "*770#",
    "ecobank": "*326#",
    "wema bank": "*945#",
    "sterling bank": "*822#",
    "fcmb": "*329#",
    "unity bank": "*7799#",
    "keystone bank": "*7111#", 
    "stanbic ibtc bank": "*909#",
    "jaiz bank": "*773#",
    "heritage bank": "*745#"
}

@csrf_exempt
@require_http_methods(["POST"])
def ussd_agent(request):
    """
    AI Agent for Nigerian Bank USSD Helper
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        # Check if API key is available
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return JsonResponse({
                "message": "GTB: Dial *737# for transfers, airtime, banking services.",
                "type": "text"
            })
        
        # AI Prompt with clear instructions
        prompt = f"""
        You are a helpful Nigerian Bank USSD Assistant. Provide accurate USSD codes and helpful information.

        BANK USSD DATABASE:
        {json.dumps(BANK_USSD_CODES, indent=2)}

        USER QUESTION: {user_message}

        Provide a direct, helpful response with the correct USSD code. Be concise and accurate.
        """
        
        # Use AI with timeout for Telex.im compatibility
        try:
            model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
            response = model.generate_content(
                prompt,
                request_options={"timeout": 10}  # 10-second timeout
            )
            
            # Return AI response
            return JsonResponse({
                "message": response.text,
                "type": "text"
            })
            
        except Exception as ai_error:
            print(f"AI Error: {ai_error}")
            # Fallback to simple response
            return fallback_response(user_message)
        
    except Exception as e:
        print(f"General Error: {e}")
        return fallback_response(user_message if 'user_message' in locals() else "")

def fallback_response(user_message):
    """Simple fallback when AI fails"""
    user_lower = user_message.lower()
    
    # Quick bank matching
    for bank, code in BANK_USSD_CODES.items():
        if bank in user_lower:
            if 'balance' in user_lower:
                return JsonResponse({
                    "message": f"To check {bank.title()} balance, dial {code} and select balance inquiry.",
                    "type": "text"
                })
            elif 'transfer' in user_lower:
                return JsonResponse({
                    "message": f"{bank.title()} transfer: Dial {code[:-1]}*Amount*AccountNumber#",
                    "type": "text"
                })
            elif 'airtime' in user_lower:
                return JsonResponse({
                    "message": f"Buy airtime with {bank.title()}: Dial {code[:-1]}*Amount*PhoneNumber#", 
                    "type": "text"
                })
            else:
                return JsonResponse({
                    "message": f"{bank.title()}: Dial {code} for transfers, airtime, balance checks.",
                    "type": "text"
                })
    
    # General help
    bank_list = ", ".join([bank.title() for bank in list(BANK_USSD_CODES.keys())[:6]])
    return JsonResponse({
        "message": f"Nigerian Bank USSD AI Helper. Available banks: {bank_list}. Ask me anything about Nigerian bank USSD codes!",
        "type": "text"
    })

@csrf_exempt
def health_check(request):
    return JsonResponse({
        "status": "healthy", 
        "service": "Nigerian Bank USSD AI Agent",
        "ai_provider": "Google Gemini"
    })

@csrf_exempt
def simple_test(request):
    return JsonResponse({
        "message": "AI Agent is working! Ask me about Nigerian bank USSD codes.",
        "type": "text"
    })