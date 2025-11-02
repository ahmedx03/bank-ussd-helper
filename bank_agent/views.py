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

# COMPLETE Nigerian Bank USSD Database - ALL 17 BANKS
BANK_USSD_CODES = {
    'access bank': {
        'balance': '*901*00#',
        'transfer': '*901*Amount*AccountNumber#',
        'airtime': '*901*Amount*PhoneNumber#',
        'main': '*901#',
        'data': '*901*11#'
    },
    'gtb': {
        'balance': '*737*6*1#',
        'transfer': '*737*1*Amount*AccountNumber#',
        'airtime': '*737*Amount*PhoneNumber#',
        'main': '*737#',
        'data': '*737*4#'
    },
    'zenith bank': {
        'balance': '*966*00#',
        'transfer': '*966*Amount*AccountNumber#',
        'airtime': '*966*Amount*PhoneNumber#',
        'main': '*966#',
        'data': '*966*13#'
    },
    'first bank': {
        'balance': '*894*00#',
        'transfer': '*894*Amount*AccountNumber#',
        'airtime': '*894*Amount*PhoneNumber#',
        'main': '*894#',
        'data': '*894*14#'
    },
    'uba': {
        'balance': '*919*00#',
        'transfer': '*919*3*Amount*AccountNumber#',
        'airtime': '*919*Amount*PhoneNumber#',
        'main': '*919#',
        'data': '*919*14#'
    },
    'polaris bank': {
        'balance': '*833*6#',
        'transfer': '*833*1*Amount*AccountNumber#',
        'airtime': '*833*Amount*PhoneNumber#',
        'main': '*833#',
        'data': '*833*5#'
    },
    'union bank': {
        'balance': '*826*7#',
        'transfer': '*826*4*Amount*AccountNumber#',
        'airtime': '*826*3*Amount*PhoneNumber#',
        'main': '*826#',
        'data': '*826*6#'
    },
    'fidelity bank': {
        'balance': '*770*00#',
        'transfer': '*770*Amount*AccountNumber#',
        'airtime': '*770*Amount*PhoneNumber#',
        'main': '*770#',
        'data': '*770*9#'
    },
    'ecobank': {
        'balance': '*326*00#',
        'transfer': '*326*3*Amount*AccountNumber#',
        'airtime': '*326*Amount*PhoneNumber#',
        'main': '*326#',
        'data': '*326*7#'
    },
    'wema bank': {
        'balance': '*945*00#',
        'transfer': '*945*2*Amount*AccountNumber#',
        'airtime': '*945*1*Amount*PhoneNumber#',
        'main': '*945#',
        'data': '*945*3#'
    },
    'sterling bank': {
        'balance': '*822*5#',
        'transfer': '*822*1*Amount*AccountNumber#',
        'airtime': '*822*2*Amount*PhoneNumber#',
        'main': '*822#',
        'data': '*822*8#'
    },
    'fcmb': {
        'balance': '*329*00#',
        'transfer': '*329*Amount*AccountNumber#',
        'airtime': '*329*Amount*PhoneNumber#',
        'main': '*329#',
        'data': '*329*6#'
    },
    'unity bank': {
        'balance': '*7799*0#',
        'transfer': '*7799*2*Amount*AccountNumber#',
        'airtime': '*7799*1*Amount*PhoneNumber#',
        'main': '*7799#',
        'data': '*7799*4#'
    },
    'keystone bank': {
        'balance': '*7111*1#',
        'transfer': '*7111*2*Amount*AccountNumber#',
        'airtime': '*7111*3*Amount*PhoneNumber#',
        'main': '*7111#',
        'data': '*7111*5#'
    },
    'stanbic ibtc': {
        'balance': '*909*3#',
        'transfer': '*909*2*Amount*AccountNumber#',
        'airtime': '*909*1*Amount*PhoneNumber#',
        'main': '*909#',
        'data': '*909*5#'
    },
    'jaiz bank': {
        'balance': '*773*3#',
        'transfer': '*773*2*Amount*AccountNumber#',
        'airtime': '*773*1*Amount*PhoneNumber#',
        'main': '*773#',
        'data': '*773*5#'
    },
    'heritage bank': {
        'balance': '*745*0#',
        'transfer': '*745*1*Amount*AccountNumber#',
        'airtime': '*745*2*Amount*PhoneNumber#',
        'main': '*745#',
        'data': '*745*4#'
    }
}

@csrf_exempt
@require_http_methods(["POST"])
def ussd_agent(request):
    """
    Complete Nigerian Bank USSD Agent - All 17 Banks
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        user_lower = user_message.lower()
        
        # DIRECT CODE RESPONSES for all banks
        response = generate_direct_response(user_lower)
        return JsonResponse({
            "message": response,
            "type": "text"
        })
        
    except Exception as e:
        return JsonResponse({
            "message": "Nigerian Bank USSD Helper. Available banks: Access, GTB, UBA, Zenith, First Bank, Polaris, Union, Fidelity, Ecobank, Wema, Sterling, FCMB, Unity, Keystone, Stanbic, Jaiz, Heritage.",
            "type": "text"
        })

def generate_direct_response(user_lower):
    """Generate direct USSD code responses for all banks"""
    
    # Check each bank in the database
    for bank_name, codes in BANK_USSD_CODES.items():
        if bank_name in user_lower:
            if 'balance' in user_lower:
                return f"{bank_name.title()} Balance Check: {codes['balance']}\nDial this code and follow prompts to check your account balance."
            elif 'transfer' in user_lower:
                return f"{bank_name.title()} Transfer: {codes['transfer']}\nReplace Amount and AccountNumber with actual values."
            elif 'airtime' in user_lower:
                return f"{bank_name.title()} Airtime: {codes['airtime']}\nReplace Amount and PhoneNumber with actual values."
            elif 'data' in user_lower:
                return f"{bank_name.title()} Data: {codes['data']}\nDial to buy data bundles."
            else:
                return f"{bank_name.title()} USSD Banking:\nBalance: {codes['balance']}\nTransfer: {codes['transfer']}\nAirtime: {codes['airtime']}\nData: {codes['data']}\nMain Menu: {codes['main']}"
    
    # Bank list queries
    if 'list' in user_lower or 'all bank' in user_lower or 'which bank' in user_lower:
        banks_list = list(BANK_USSD_CODES.keys())
        first_banks = ", ".join([bank.title() for bank in banks_list[:8]])
        remaining_banks = ", ".join([bank.title() for bank in banks_list[8:]])
        return f"All Nigerian Banks Available:\n\nFirst 8: {first_banks}\nOthers: {remaining_banks}\n\nAsk about any specific bank's USSD codes."
    
    # General USSD query
    if 'ussd' in user_lower and 'bank' in user_lower:
        popular_banks = ["UBA", "GTB", "Access Bank", "Zenith Bank", "First Bank"]
        popular_codes = [f"{bank}: {BANK_USSD_CODES[bank.lower().replace(' ', '')]['main']}" for bank in popular_banks if bank.lower().replace(' ', '') in BANK_USSD_CODES]
        return f"Popular Bank USSD Codes:\n" + "\n".join(popular_codes) + "\n\nAsk about any specific Nigerian bank."
    
    # Default response with popular banks
    return "Nigerian Bank USSD Helper - All 17 Banks\n\nPopular Banks:\nUBA: *919#\nGTB: *737#\nAccess Bank: *901#\nZenith Bank: *966#\nFirst Bank: *894#\n\nAsk me about any Nigerian bank's USSD codes for balance, transfers, airtime, or data."

@csrf_exempt
def health_check(request):
    return JsonResponse({
        "status": "healthy", 
        "service": "Complete Nigerian Bank USSD Agent",
        "total_banks": len(BANK_USSD_CODES),
        "banks_covered": list(BANK_USSD_CODES.keys())
    })

# Test all banks endpoint
@csrf_exempt
@require_http_methods(["POST"])
def test_all_banks(request):
    """Test endpoint showing all banks are available"""
    bank_list = "\n".join([f"{bank.title()}: {codes['main']}" for bank, codes in BANK_USSD_CODES.items()])
    return JsonResponse({
        "message": f"All 17 Nigerian Banks Available:\n\n{bank_list}\n\nTotal: {len(BANK_USSD_CODES)} banks covered.",
        "type": "text"
    })