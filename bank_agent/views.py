import json
import google.generativeai as genai
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Configure Gemini AI with your REAL API key
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
    AI Agent endpoint for Nigerian Bank USSD Helper 
    """
    try:
        # Parse incoming JSON data from Telex.im
        data = json.loads(request.body)
        user_message = data.get('message', '').strip().lower()
        print(f"Received message: {user_message}")
        
        # FIRST: Quick rule-based responses for common queries (FAST)
        quick_responses = {
            "access bank": "Access Bank: Dial *901# for transfers, airtime, bills, balance checks. Transfer format: *901*Amount*AccountNumber#",
            "gtb": "GTB: Dial *737# for transfers, airtime, banking services. Transfer format: *737*2*Amount*AccountNumber#", 
            "uba": "UBA: Dial *919# for transfers, airtime, balance checks. Transfer format: *919*Amount*AccountNumber#",
            "zenith bank": "Zenith Bank: Dial *966# for transfers, airtime, bills. Transfer format: *966*Amount*AccountNumber#",
            "first bank": "First Bank: Dial *894# for transfers, airtime, balance checks. Transfer format: *894*Amount*AccountNumber#",
            "polaris bank": "Polaris Bank: Dial *833# for transfers, airtime, balance checks.",
            "union bank": "Union Bank: Dial *826# for transfers, airtime, balance checks.",
            "fidelity bank": "Fidelity Bank: Dial *770# for transfers, airtime, balance checks.",
            "ecobank": "Ecobank: Dial *326# for transfers, airtime, balance checks.",
            "wema bank": "Wema Bank: Dial *945# for transfers, airtime, balance checks.",
            "sterling bank": "Sterling Bank: Dial *822# for transfers, airtime, balance checks.",
            "fcmb": "FCMB: Dial *329# for transfers, airtime, balance checks.",
            "unity bank": "Unity Bank: Dial *7799# for transfers, airtime, balance checks.",
            "keystone bank": "Keystone Bank: Dial *7111# for transfers, airtime, balance checks.",
            "stanbic ibtc bank": "Stanbic IBTC Bank: Dial *909# for transfers, airtime, balance checks.",
            "jaiz bank": "Jaiz Bank: Dial *773# for transfers, airtime, balance checks.",
            "heritage bank": "Heritage Bank: Dial *745# for transfers, airtime, balance checks."
        }
        
        # Check for quick matches first
        for bank, response in quick_responses.items():
            if bank in user_message:
                if 'transfer' in user_message and 'format' in response:
                    # Enhanced transfer response
                    transfer_info = response.split('Transfer format: ')[1] if 'Transfer format:' in response else ""
                    if transfer_info:
                        example = transfer_info.replace('Amount', '1000').replace('AccountNumber', '1234567890')
                        bank_name = bank.title()
                        ussd_code = response.split('Dial ')[1].split(' ')[0] if 'Dial' in response else ""
                        return JsonResponse({
                            "message": f"{bank_name} Transfer:\nUSSD: {ussd_code}\nFormat: {transfer_info}\nExample: {example}",
                            "type": "text"
                        })
                return JsonResponse({"message": response, "type": "text"})
        
        # SECOND: Use AI for complex questions (only if needed)
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            try:
                # FASTER, SIMPLER PROMPT for Telex.im
                prompt = f"""User asked: "{user_message}"
                
                Nigerian Bank USSD Codes: {BANK_USSD_CODES}
                
                Provide a SHORT, helpful response (max 2-3 lines). Focus on the USSD code and main uses."""
                
                print("Calling Gemini AI...")
                model = genai.GenerativeModel('models/gemini-2.0-flash-lite')  # Faster model
                response = model.generate_content(prompt, request_options={"timeout": 10})
                
                if response.text and len(response.text) > 20:  # Ensure meaningful response
                    print(f"AI Response: {response.text}")
                    return JsonResponse({
                        "message": response.text,
                        "type": "text"
                    })
            except Exception as ai_error:
                print(f"AI Error: {ai_error}")
        
        # THIRD: Fallback to comprehensive rule-based response
        return rule_based_fallback(user_message)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return rule_based_fallback(user_message if 'user_message' in locals() else "")

def rule_based_fallback(user_message):
    """Comprehensive rule-based fallback"""
    banks_detailed = {
        "access bank": {"code": "*901#", "uses": "transfers, airtime, bills, balance checks", "transfer": "*901*Amount*AccountNumber#"},
        "gtb": {"code": "*737#", "uses": "transfers, airtime, banking services", "transfer": "*737*2*Amount*AccountNumber#"}, 
        "zenith bank": {"code": "*966#", "uses": "transfers, airtime, bills", "transfer": "*966*Amount*AccountNumber#"},
        "first bank": {"code": "*894#", "uses": "transfers, airtime, balance checks", "transfer": "*894*Amount*AccountNumber#"},
        "uba": {"code": "*919#", "uses": "transfers, airtime, balance checks", "transfer": "*919*Amount*AccountNumber#"},
        "polaris bank": {"code": "*833#", "uses": "transfers, airtime, balance checks", "transfer": "*833*Amount*AccountNumber#"},
        "union bank": {"code": "*826#", "uses": "transfers, airtime, balance checks", "transfer": "*826*Amount*AccountNumber#"},
        "fidelity bank": {"code": "*770#", "uses": "transfers, airtime, balance checks", "transfer": "*770*Amount*AccountNumber#"},
        "ecobank": {"code": "*326#", "uses": "transfers, airtime, balance checks", "transfer": "*326*Amount*AccountNumber#"},
        "wema bank": {"code": "*945#", "uses": "transfers, airtime, balance checks", "transfer": "*945*Amount*AccountNumber#"},
        "sterling bank": {"code": "*822#", "uses": "transfers, airtime, balance checks", "transfer": "*822*Amount*AccountNumber#"},
        "fcmb": {"code": "*329#", "uses": "transfers, airtime, balance checks", "transfer": "*329*Amount*AccountNumber#"},
        "unity bank": {"code": "*7799#", "uses": "transfers, airtime, balance checks", "transfer": "*7799*Amount*AccountNumber#"},
        "keystone bank": {"code": "*7111#", "uses": "transfers, airtime, balance checks", "transfer": "*7111*Amount*AccountNumber#"},
        "stanbic ibtc bank": {"code": "*909#", "uses": "transfers, airtime, balance checks", "transfer": "*909*Amount*AccountNumber#"},
        "jaiz bank": {"code": "*773#", "uses": "transfers, airtime, balance checks", "transfer": "*773*Amount*AccountNumber#"},
        "heritage bank": {"code": "*745#", "uses": "transfers, airtime, balance checks", "transfer": "*745*Amount*AccountNumber#"}
    }
    
    user_lower = user_message.lower()
    
    # Check for specific bank
    for bank, info in banks_detailed.items():
        if bank in user_lower:
            if 'transfer' in user_lower:
                example = info['transfer'].replace('Amount', '1000').replace('AccountNumber', '1234567890')
                return JsonResponse({
                    "message": f"{bank.title()} Transfer:\nUSSD: {info['code']}\nFormat: {info['transfer']}\nExample: {example}",
                    "type": "text"
                })
            else:
                return JsonResponse({
                    "message": f"{bank.title()}: Dial {info['code']} for {info['uses']}.",
                    "type": "text"
                })
    
    # General help response
    bank_list = ", ".join([bank.title() for bank in list(banks_detailed.keys())[:6]])
    return JsonResponse({
        "message": f"Nigerian Bank USSD Helper. Available banks: {bank_list}, etc. Ask: 'GTB transfer' or 'Access Bank code'",
        "type": "text"
    })

@csrf_exempt
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        "status": "healthy", 
        "service": "Nigerian Bank USSD AI Agent",
        "ai_provider": "Google Gemini 2.0 Flash"
    })

@csrf_exempt
def simple_test(request):
    """Simple test endpoint without AI"""
    return JsonResponse({
        "message": "Service is working! Ask me about Nigerian bank USSD codes.",
        "type": "text"
    })