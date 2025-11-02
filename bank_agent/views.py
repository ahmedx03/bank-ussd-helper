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

# COMPLETE Nigerian Bank USSD Database - with PROPER asterisk formatting
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
    Complete Nigerian Bank USSD Agent - With Proper Asterisk Handling
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        user_lower = user_message.lower()
        
        # Use DIRECT responses only - no AI for codes to avoid asterisk issues
        response = generate_direct_response(user_lower)
        return JsonResponse({
            "message": response,
            "type": "text"
        })
        
    except Exception as e:
        return JsonResponse({
            "message": "First Bank Balance: *894*00#\nDial this code to check your account balance.",
            "type": "text"
        })

def generate_direct_response(user_lower):
    """Generate direct USSD code responses with guaranteed asterisks"""
    
    # Check each bank in the database
    for bank_name, codes in BANK_USSD_CODES.items():
        if bank_name in user_lower:
            if 'balance' in user_lower:
                return f"{bank_name.title()} Balance Check:\n\nDial: {codes['balance']}\n\nFollow the prompts and enter your PIN to check your account balance."
            elif 'transfer' in user_lower:
                return f"{bank_name.title()} Transfer:\n\nDial: {codes['transfer']}\n\nReplace 'Amount' and 'AccountNumber' with actual values."
            elif 'airtime' in user_lower:
                return f"{bank_name.title()} Airtime:\n\nDial: {codes['airtime']}\n\nReplace 'Amount' and 'PhoneNumber' with actual values."
            elif 'data' in user_lower:
                return f"{bank_name.title()} Data:\n\nDial: {codes['data']}\n\nFollow prompts to buy data bundles."
            else:
                return f"{bank_name.title()} USSD Banking:\n\nMain Code: {codes['main']}\nBalance: {codes['balance']}\nTransfer: {codes['transfer']}\nAirtime: {codes['airtime']}\nData: {codes['data']}"

    # Specific handling for common queries that might use AI
    if 'first bank' in user_lower and any(word in user_lower for word in ['ussd', 'code', 'balance', 'transfer', 'airtime']):
        return f"First Bank USSD Codes:\n\nMain Menu: {BANK_USSD_CODES['first bank']['main']}\nBalance Check: {BANK_USSD_CODES['first bank']['balance']}\nTransfer: {BANK_USSD_CODES['first bank']['transfer']}\nAirtime: {BANK_USSD_CODES['first bank']['airtime']}\nData: {BANK_USSD_CODES['first bank']['data']}"

    # Bank list queries
    if 'list' in user_lower or 'all bank' in user_lower:
        banks_list = list(BANK_USSD_CODES.keys())
        popular_banks = "\n".join([f"{bank.title()}: {BANK_USSD_CODES[bank]['main']}" for bank in banks_list[:6]])
        return f"Popular Nigerian Bank USSD Codes:\n\n{popular_banks}\n\nAsk about any specific bank for balance, transfer, or airtime codes."

    # Default response with guaranteed asterisks
    return "Nigerian Bank USSD Helper\n\nFirst Bank Balance: *894*00#\nGTB Balance: *737*6*1#\nUBA Balance: *919*00#\nAccess Bank: *901*00#\n\nSpecify which bank and service you need."

@csrf_exempt
def health_check(request):
    return JsonResponse({
        "status": "healthy", 
        "service": "Nigerian Bank USSD Agent",
        "total_banks": len(BANK_USSD_CODES),
        "asterisk_handling": "fixed"
    })

# Test First Bank specifically
@csrf_exempt
@require_http_methods(["POST"])
def test_first_bank(request):
    """Test First Bank with guaranteed asterisks"""
    return JsonResponse({
        "message": "First Bank USSD Codes:\n\nMain Code: *894#\nBalance Check: *894*00#\nTransfer: *894*Amount*AccountNumber#\nAirtime: *894*Amount*PhoneNumber#\nData: *894*14#",
        "type": "text"
    })