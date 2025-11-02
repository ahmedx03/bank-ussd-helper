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
        
        # Define complex questions that need AI
        complex_keywords = ['compare', 'which is better', 'difference', 'shortest', 'fastest', 'best', 'recommend', 'fee', 'cost', 'charge']
        
        # Check if this is a complex question that needs AI
        needs_ai = any(keyword in user_message for keyword in complex_keywords)
        
        # For simple bank-specific queries, use rule-based (FASTER)
        if not needs_ai:
            # FIRST: Quick rule-based responses for common queries
            quick_responses = {
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
            
            # Enhanced responses for specific actions
            action_responses = {
                "check my balance": {
                    "uba": "To check your UBA balance, dial *919*6# or use *919# and follow the menu options.",
                    "access bank": "To check your Access Bank balance, dial *901*6# or use *901# and navigate to balance inquiry.",
                    "gtb": "To check your GTB balance, dial *737*6*1# or use *737# and select balance inquiry.",
                    "zenith bank": "To check your Zenith Bank balance, dial *966*6# or use *966# and choose balance check.",
                    "first bank": "To check your First Bank balance, dial *894*6# or use *894# and select balance inquiry."
                },
                "buy airtime": {
                    "access bank": "To buy airtime with Access Bank, dial *901*Amount*PhoneNumber#. Example: *901*100*08012345678#",
                    "uba": "To buy airtime with UBA, dial *919*Amount*PhoneNumber#. Example: *919*500*08012345678#",
                    "gtb": "To buy airtime with GTB, dial *737*Amount*PhoneNumber#. Example: *737*200*08012345678#",
                    "zenith bank": "To buy airtime with Zenith Bank, dial *966*Amount*PhoneNumber#. Example: *966*1000*08012345678#",
                    "first bank": "To buy airtime with First Bank, dial *894*Amount*PhoneNumber#. Example: *894*500*08012345678#"
                }
            }
            
            # Check for specific actions first
            for action, banks in action_responses.items():
                if action in user_message:
                    for bank, response in banks.items():
                        if bank in user_message:
                            return JsonResponse({"message": response, "type": "text"})
            
            # Then check for bank-specific queries
            for bank, response in quick_responses.items():
                if bank in user_message:
                    # Add transfer format if transfer is mentioned
                    if 'transfer' in user_message:
                        transfer_formats = {
                            "access bank": "*901*Amount*AccountNumber#",
                            "gtb": "*737*2*Amount*AccountNumber#",
                            "uba": "*919*Amount*AccountNumber#", 
                            "zenith bank": "*966*Amount*AccountNumber#",
                            "first bank": "*894*Amount*AccountNumber#"
                        }
                        format = transfer_formats.get(bank, "")
                        if format:
                            example = format.replace('Amount', '1000').replace('AccountNumber', '1234567890')
                            return JsonResponse({
                                "message": f"{bank.title()} Transfer:\nUSSD: {response.split('Dial ')[1].split(' ')[0]}\nFormat: {format}\nExample: {example}",
                                "type": "text"
                            })
                    return JsonResponse({"message": response, "type": "text"})
        
        # Use AI for complex questions or when no quick match found
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key and (needs_ai or not any(bank in user_message for bank in BANK_USSD_CODES.keys())):
            try:
                # Better prompt for complex questions
                prompt = f"""User asked: "{user_message}"

Nigerian Bank USSD Database: {BANK_USSD_CODES}

Provide a helpful, accurate response about Nigerian bank USSD codes. If comparing banks or answering complex questions, provide useful insights."""
                
                print("Calling Gemini AI for complex question...")
                model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
                response = model.generate_content(prompt, request_options={"timeout": 10})
                
                if response.text and len(response.text) > 20:
                    print(f"AI Response: {response.text}")
                    return JsonResponse({
                        "message": response.text,
                        "type": "text"
                    })
            except Exception as ai_error:
                print(f"AI Error: {ai_error}")
        
        # Final fallback
        return rule_based_fallback(user_message)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return rule_based_fallback(user_message if 'user_message' in locals() else "")