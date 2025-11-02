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
        
        # SIMPLE RULE-BASED RESPONSES FIRST 
        bank_responses = {
            "access bank": "Access Bank: Dial *901# for transfers, airtime, bills, balance checks.",
            "gtb": "GTB: Dial *737# for transfers, airtime, banking services.", 
            "uba": "UBA: Dial *919# for transfers, airtime, balance checks.",
            "zenith bank": "Zenith Bank: Dial *966# for transfers, airtime, bills.",
            "first bank": "First Bank: Dial *894# for transfers, airtime, balance checks.",
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
        
        # Check for specific bank queries
        for bank, response in bank_responses.items():
            if bank in user_message:
                # Enhanced responses for specific actions
                if 'check my balance' in user_message or 'balance' in user_message:
                    balance_codes = {
                        "uba": "To check UBA balance: Dial *919*6# or use *919# menu",
                        "access bank": "To check Access Bank balance: Dial *901*6# or use *901# menu",
                        "gtb": "To check GTB balance: Dial *737*6*1# or use *737# menu",
                        "zenith bank": "To check Zenith Bank balance: Dial *966*6# or use *966# menu",
                        "first bank": "To check First Bank balance: Dial *894*6# or use *894# menu"
                    }
                    balance_response = balance_codes.get(bank, f"To check balance, dial {response.split('Dial ')[1].split(' ')[0]} and follow balance inquiry options")
                    return JsonResponse({"message": balance_response, "type": "text"})
                
                elif 'buy airtime' in user_message or 'airtime' in user_message:
                    airtime_formats = {
                        "access bank": "Buy airtime with Access Bank: Dial *901*Amount*PhoneNumber#",
                        "uba": "Buy airtime with UBA: Dial *919*Amount*PhoneNumber#",
                        "gtb": "Buy airtime with GTB: Dial *737*Amount*PhoneNumber#",
                        "zenith bank": "Buy airtime with Zenith Bank: Dial *966*Amount*PhoneNumber#",
                        "first bank": "Buy airtime with First Bank: Dial *894*Amount*PhoneNumber#"
                    }
                    airtime_response = airtime_formats.get(bank, f"To buy airtime, dial {response.split('Dial ')[1].split(' ')[0]} and follow airtime purchase options")
                    return JsonResponse({"message": airtime_response, "type": "text"})
                
                elif 'transfer' in user_message:
                    transfer_formats = {
                        "access bank": "Access Bank transfer: Dial *901*Amount*AccountNumber#",
                        "gtb": "GTB transfer: Dial *737*2*Amount*AccountNumber#",
                        "uba": "UBA transfer: Dial *919*Amount*AccountNumber#",
                        "zenith bank": "Zenith Bank transfer: Dial *966*Amount*AccountNumber#",
                        "first bank": "First Bank transfer: Dial *894*Amount*AccountNumber#"
                    }
                    transfer_response = transfer_formats.get(bank, f"To transfer, dial {response.split('Dial ')[1].split(' ')[0]} and follow transfer options")
                    return JsonResponse({"message": transfer_response, "type": "text"})
                
                else:
                    return JsonResponse({"message": response, "type": "text"})
        
        # COMPLEX QUESTIONS - USE AI
        complex_questions = ['compare', 'which is better', 'difference', 'shortest', 'fastest', 'best', 'recommend', 'fee', 'cost', 'charge']
        
        if any(keyword in user_message for keyword in complex_questions):
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                try:
                    prompt = f"""User asked: "{user_message}"

Nigerian Bank USSD Codes: {BANK_USSD_CODES}

Provide a helpful, accurate response about Nigerian bank USSD codes."""
                    
                    print("Calling Gemini AI for complex question...")
                    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
                    response = model.generate_content(prompt, request_options={"timeout": 10})
                    
                    if response.text:
                        return JsonResponse({"message": response.text, "type": "text"})
                except Exception as ai_error:
                    print(f"AI Error: {ai_error}")
                    # Fall through to general help
        
        # GENERAL HELP RESPONSE
        bank_list = ", ".join([bank.title() for bank in list(bank_responses.keys())[:6]])
        help_response = f"Nigerian Bank USSD Helper. Available banks: {bank_list}, etc. Ask specific questions like 'UBA balance check' or 'GTB transfer'."
        
        return JsonResponse({"message": help_response, "type": "text"})
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        # Simple fallback response
        return JsonResponse({
            "message": "Nigerian Bank USSD Helper - Ask me about any Nigerian bank USSD codes.",
            "type": "text"
        })