import json
import google.generativeai as genai
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Configure Gemini AI
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@csrf_exempt
@require_http_methods(["POST"])
def ussd_agent(request):
    """
    AI Agent for Nigerian Bank USSD Codes
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        # Check if API key is available
        if not GEMINI_API_KEY:
            return JsonResponse({
                "message": "🤖 Nigerian Bank USSD AI Assistant\n\nI can help you with USSD codes for all Nigerian banks! Currently in direct mode.\n\n🏦 UBA Balance: Dial *919*00#\n🏦 GTB: *737# for all services\n🏦 Access Bank: *901#\n\nAsk me anything about Nigerian bank USSD services!",
                "type": "text"
            })
        
        # AI Prompt with clear instructions for immediate response
        prompt = f"""You are a helpful Nigerian Bank USSD AI Assistant. User asked: "{user_message}"

Provide an IMMEDIATE, direct answer with the exact USSD code. Do not say "fetching" or "searching" - just give the answer directly.

BANK USSD CODES:
- Access Bank: *901# (Balance: *901*00#)
- GTB: *737# (Balance: *737*6*1#)
- Zenith Bank: *966# (Balance: *966*00#) 
- First Bank: *894# (Balance: *894*00#)
- UBA: *919# (Balance: *919*00#)
- Polaris Bank: *833# (Balance: *833*6#)
- Union Bank: *826# (Balance: *826*7#)
- Fidelity Bank: *770# (Balance: *770*00#)
- Ecobank: *326# (Balance: *326*00#)
- Wema Bank: *945# (Balance: *945*00#)
- Sterling Bank: *822# (Balance: *822*5#)
- FCMB: *329# (Balance: *329*00#)
- Unity Bank: *7799# (Balance: *7799*0#)
- Keystone Bank: *7111# (Balance: *7111*1#)
- Stanbic IBTC: *909# (Balance: *909*3#)
- Jaiz Bank: *773# (Balance: *773*3#)
- Heritage Bank: *745# (Balance: *745*0#)

Respond in a helpful, direct manner. If they ask for UBA balance, immediately respond with the exact code and steps."""

        # Use AI with better error handling
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.3
                )
            )
            
            ai_response = response.text.strip()
            
            # Ensure we have a valid response
            if ai_response and len(ai_response) > 10:
                return JsonResponse({
                    "message": ai_response,
                    "type": "text"
                })
            else:
                raise ValueError("AI returned empty response")
            
        except Exception as ai_error:
            print(f"AI Error: {ai_error}")
            # Smart fallback based on user query
            return smart_fallback(user_message)
        
    except Exception as e:
        print(f"General Error: {e}")
        return smart_fallback("")

def smart_fallback(user_message):
    """Intelligent fallback when AI fails"""
    user_lower = user_message.lower() if user_message else ""
    
    # UBA specific
    if 'uba' in user_lower:
        if 'balance' in user_lower:
            return JsonResponse({
                "message": "🏦 UBA Balance Check:\n\nTo check your UBA account balance, dial:\n\n*919*00#\n\nFollow the on-screen prompts and enter your UBA PIN when requested. You'll receive your balance via SMS.",
                "type": "text"
            })
        else:
            return JsonResponse({
                "message": "🏦 United Bank for Africa (UBA) USSD Banking:\n\n• Main Menu: *919#\n• Balance Check: *919*00#\n• Transfer: *919*3*Amount*AccountNumber#\n• Airtime: *919*Amount*PhoneNumber#\n• Data: *919*14#\n• Mini Statement: *919*5#",
                "type": "text"
            })
    
    # GTB
    elif 'gtb' in user_lower or 'guaranty trust' in user_lower:
        return JsonResponse({
            "message": "🏦 GTB (Guaranty Trust Bank) USSD Banking:\n\n• Main Menu: *737#\n• Balance: *737*6*1#\n• Transfer: *737*1*Amount*Account#\n• Airtime: *737*Amount*Phone#\n• Quick Services: *737*Amount*Account# for transfers",
            "type": "text"
        })
    
    # General bank response
    banks = {
        'access': "Access Bank: *901# (Balance: *901*00#)",
        'zenith': "Zenith Bank: *966# (Balance: *966*00#)",
        'first bank': "First Bank: *894# (Balance: *894*00#)",
        'polaris': "Polaris Bank: *833# (Balance: *833*6#)",
        'union bank': "Union Bank: *826# (Balance: *826*7#)",
        'fidelity': "Fidelity Bank: *770# (Balance: *770*00#)",
        'ecobank': "Ecobank: *326# (Balance: *326*00#)",
        'wema': "Wema Bank: *945# (Balance: *945*00#)",
        'sterling': "Sterling Bank: *822# (Balance: *822*5#)",
        'fcmb': "FCMB: *329# (Balance: *329*00#)"
    }
    
    for bank, code in banks.items():
        if bank in user_lower:
            return JsonResponse({
                "message": f"🏦 {code}",
                "type": "text"
            })
    
    # Default AI-like response
    return JsonResponse({
        "message": "🤖 Nigerian Bank USSD AI Assistant\n\nI can help you with USSD codes for all Nigerian banks! Here are some popular ones:\n\n🏦 UBA: *919# for all services\n🏦 GTB: *737# for transfers & airtime\n🏦 Access Bank: *901#\n🏦 Zenith Bank: *966#\n🏦 First Bank: *894#\n\nAsk me about any Nigerian bank's USSD codes or specific services!",
        "type": "text"
    })

@csrf_exempt
def health_check(request):
    ai_status = "active" if GEMINI_API_KEY else "no_api_key"
    return JsonResponse({
        "status": "healthy", 
        "service": "Nigerian Bank USSD AI Agent",
        "ai_status": ai_status,
        "ai_provider": "Google Gemini"
    })