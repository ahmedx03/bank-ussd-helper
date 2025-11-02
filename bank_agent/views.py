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
        user_message = data.get('message', '').strip()
        print(f"Received message: {user_message}")  # Debug print
        
        # AI Prompt with bank data context
        prompt = f"""
        You are a helpful Nigerian Bank USSD Assistant. Your role is to provide accurate USSD codes and helpful banking information.

        BANK USSD DATABASE:
        {json.dumps(BANK_USSD_CODES, indent=2)}

        INSTRUCTIONS:
        1. Provide accurate USSD codes from the database above
        2. Explain what each USSD code can be used for (transfers, airtime, balance checks, bills payment)
        3. Be conversational, helpful, and friendly
        4. Keep responses clear and practical

        USER'S QUESTION: {user_message}

        Provide a helpful, accurate response:
        """
        
        # Use the correct model name
        print("Calling Gemini AI...")  # Debug print
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        response = model.generate_content(prompt)
        print(f"AI Response: {response.text}")  # Debug print
        
        # Telex.im A2A protocol response
        telex_response = {
            "message": response.text,
            "type": "text"
        }
        
        return JsonResponse(telex_response)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")  # Debug print
        # Fallback to simple response if AI fails
        error_response = {
            "message": "I'm here to help with Nigerian bank USSD codes! Ask me about GTB, UBA, Zenith, Access Bank, First Bank, etc.",
            "type": "text"
        }
        return JsonResponse(error_response)

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