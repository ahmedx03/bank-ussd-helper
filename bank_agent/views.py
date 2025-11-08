import json
import google.generativeai as genai
import os
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini AI with API key from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print(" Gemini AI configured successfully!")
else:
    print(" GEMINI_API_KEY not found")

MODEL_NAME = 'gemini-2.0-flash-lite'

# Complete database of Nigerian bank USSD codes
BANK_USSD_CODES = {
    'access bank': {'balance': '*901*00#', 'transfer': '*901*Amount*AccountNumber#', 'airtime': '*901*Amount*PhoneNumber#', 'main': '*901#'},
    'gtb': {'balance': '*737*6*1#', 'transfer': '*737*1*Amount*AccountNumber#', 'airtime': '*737*Amount*PhoneNumber#', 'main': '*737#'},
    'zenith bank': {'balance': '*966*00#', 'transfer': '*966*Amount*AccountNumber#', 'airtime': '*966*Amount*PhoneNumber#', 'main': '*966#'},
    'first bank': {'balance': '*894*00#', 'transfer': '*894*Amount*AccountNumber#', 'airtime': '*894*Amount*PhoneNumber#', 'main': '*894#'},
    'uba': {'balance': '*919*00#', 'transfer': '*919*3*Amount*AccountNumber#', 'airtime': '*919*Amount*PhoneNumber#', 'main': '*919#'},
    'polaris bank': {'balance': '*833*6#', 'transfer': '*833*1*Amount*AccountNumber#', 'airtime': '*833*Amount*PhoneNumber#', 'main': '*833#'},
    'union bank': {'balance': '*826*7#', 'transfer': '*826*4*Amount*AccountNumber#', 'airtime': '*826*3*Amount*PhoneNumber#', 'main': '*826#'},
    'fidelity bank': {'balance': '*770*00#', 'transfer': '*770*Amount*AccountNumber#', 'airtime': '*770*Amount*PhoneNumber#', 'main': '*770#'},
    'ecobank': {'balance': '*326*00#', 'transfer': '*326*3*Amount*AccountNumber#', 'airtime': '*326*Amount*PhoneNumber#', 'main': '*326#'},
    'wema bank': {'balance': '*945*00#', 'transfer': '*945*2*Amount*AccountNumber#', 'airtime': '*945*1*Amount*PhoneNumber#', 'main': '*945#'},
    'sterling bank': {'balance': '*822*5#', 'transfer': '*822*1*Amount*AccountNumber#', 'airtime': '*822*2*Amount*PhoneNumber#', 'main': '*822#'},
    'fcmb': {'balance': '*329*00#', 'transfer': '*329*Amount*AccountNumber#', 'airtime': '*329*Amount*PhoneNumber#', 'main': '*329#'},
    'unity bank': {'balance': '*7799*0#', 'transfer': '*7799*2*Amount*AccountNumber#', 'airtime': '*7799*1*Amount*PhoneNumber#', 'main': '*7799#'},
    'keystone bank': {'balance': '*7111*1#', 'transfer': '*7111*2*Amount*AccountNumber#', 'airtime': '*7111*3*Amount*PhoneNumber#', 'main': '*7111#'},
    'stanbic ibtc': {'balance': '*909*3#', 'transfer': '*909*2*Amount*AccountNumber#', 'airtime': '*909*1*Amount*PhoneNumber#', 'main': '*909#'},
    'jaiz bank': {'balance': '*773*3#', 'transfer': '*773*2*Amount*AccountNumber#', 'airtime': '*773*1*Amount*PhoneNumber#', 'main': '*773#'},
    'heritage bank': {'balance': '*745*0#', 'transfer': '*745*1*Amount*AccountNumber#', 'airtime': '*745*2*Amount*PhoneNumber#', 'main': '*745#'}
}

def generate_ai_response(user_message):
    """
    Generate AI responses for ALL queries using Gemini AI
    """
    try:
        print(f"Generating AI response for: {user_message}")
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Comprehensive prompt for all types of queries
        prompt = f"""You are a helpful Nigerian banking expert. Provide direct, immediate answers about Nigerian bank USSD codes and banking services.

User Question: "{user_message}"

Nigerian Bank USSD Codes Database:
- Access Bank: Balance *901*00#, Transfer *901*Amount*AccountNumber#, Airtime *901*Amount*PhoneNumber#
- GTB: Balance *737*6*1#, Transfer *737*1*Amount*AccountNumber#, Airtime *737*Amount*PhoneNumber#
- UBA: Balance *919*00#, Transfer *919*3*Amount*AccountNumber#, Airtime *919*Amount*PhoneNumber#
- Zenith Bank: Balance *966*00#, Transfer *966*Amount*AccountNumber#, Airtime *966*Amount*PhoneNumber#
- First Bank: Balance *894*00#, Transfer *894*Amount*AccountNumber#, Airtime *894*Amount*PhoneNumber#
- Polaris Bank: Balance *833*6#, Transfer *833*1*Amount*AccountNumber#
- Union Bank: Balance *826*7#, Transfer *826*4*Amount*AccountNumber#
- 10 other major Nigerian banks available

Instructions:
- For USSD code requests: Provide the exact code immediately without introductory phrases
- For security questions: Give direct security advice and best practices
- For comparisons: Provide clear, helpful comparisons between banks
- For general banking questions: Answer directly and informatively
- NEVER use phrases like "fetching", "retrieving", "getting", "looking up", "I'll", "Let me"
- ALWAYS provide immediate, direct answers
- Include relevant USSD codes when applicable
- Keep responses concise but helpful

Examples:
- "UBA balance" → "UBA Balance Check: Dial *919*00#"
- "Is USSD banking safe?" → "USSD banking is secure when you: [direct security tips]"
- "GTB transfer code" → "GTB Transfer: Dial *737*1*Amount*AccountNumber#"
- "Compare Access Bank and GTB" → "Access Bank vs GTB: [direct comparison]" """

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=300,
                temperature=0.7
            )
        )
        
        ai_response = response.text.strip()

        # Ensure response isn't too long
        if len(ai_response) > 1000:
            ai_response = ai_response[:1000] + "..."
        print(f"AI response generated: {ai_response[:100]}...")
        
        return ai_response
        
    except Exception as ai_error:
        print(f"AI Error: {ai_error}")
        # Fallback response if AI fails
        return "I can help with Nigerian bank USSD codes. For balance checks, dial *901*00# for Access Bank, *737*6*1# for GTB, or *919*00# for UBA."

# Main agent endpoint 
@csrf_exempt
@require_http_methods(["POST"])
def ussd_agent(request):
    """
    Main AI agent endpoint for Nigerian Bank USSD codes
    """
    try:
        data = json.loads(request.body)
        print(f" INCOMING REQUEST: {json.dumps(data, indent=2)[:500]}...")
        
        # A2A PROTOCOL PARSING
        user_message = ""
        request_id = data.get('id', '1')
        
        # Handle A2A JSON-RPC format
        if 'method' in data and data.get('method') == 'message/send':
            if 'params' in data and 'message' in data['params']:
                message_obj = data['params']['message']
                
                # Extract text from parts
                if 'parts' in message_obj:
                    for part in message_obj['parts']:
                        if part.get('kind') == 'text':
                            text_content = part.get('text', '').strip()
                            if text_content:
                                user_message = text_content
                                break
                        elif part.get('kind') == 'data':
                            data_parts = part.get('data', [])
                            for data_item in data_parts:
                                if data_item.get('kind') == 'text':
                                    text_content = data_item.get('text', '').strip()
                                    if text_content:
                                        user_message = text_content
                                        break
        
        # Fallback for simple format
        if not user_message:
            user_message = data.get('message', data.get('content', '')).strip()
            
        print(f" EXTRACTED MESSAGE: '{user_message}'")
        
        # Health check endpoint for monitoring
        if not user_message or user_message.lower() in ['health', 'test', 'ping', 'status']:
            response_data = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "message": {
                        "kind": "message", 
                        "role": "assistant",
                        "parts": [
                            {
                                "kind": "text",
                                "text": "Healthy - Nigerian Bank USSD AI Agent"
                            }
                        ]
                    }
                }
            }
            return JsonResponse(response_data)
        
        # Use AI for ALL queries
        if GEMINI_API_KEY:
            try:
                import threading
                
                ai_response = None
                def generate_response():
                    nonlocal ai_response
                    ai_response = generate_ai_response(user_message)
                
                thread = threading.Thread(target=generate_response)
                thread.start()
                thread.join(timeout=10)  # 10 second timeout
                
                if thread.is_alive():
                    # Thread timed out
                    print("AI response timed out")
                    ai_response = "I can help with Nigerian bank USSD codes. For quick codes: Access *901#, GTB *737#, UBA *919#"
                
                if ai_response:
                    response_data = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "message": {
                                "kind": "message", 
                                "role": "assistant",
                                "parts": [
                                    {
                                        "kind": "text",
                                        "text": ai_response
                                    }
                                ]
                            }
                        }
                    }
                    print(f" SENDING A2A RESPONSE: {ai_response}")
                    return JsonResponse(response_data)
                
            except Exception as ai_error:
                print(f"AI processing error: {ai_error}")
        
        response_data = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "message": {
                    "kind": "message", 
                    "role": "assistant",
                    "parts": [
                        {
                            "kind": "text",
                            "text": "I can help with Nigerian bank USSD codes. Try asking about specific banks like UBA, GTB, or Access Bank."
                        }
                    ]
                }
            }
        }
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f" Error in ussd_agent: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        # Error response in A2A format
        error_response = {
            "jsonrpc": "2.0",
            "id": data.get('id', '1') if 'data' in locals() else '1',
            "error": {
                "code": -32000,
                "message": "Internal server error"
            }
        }
        return JsonResponse(error_response, status=500)
    
# A2A protocol health check endpoint
@csrf_exempt
def a2a_health(request):
    """
    Health check endpoint for A2A protocol compliance
    """
    return JsonResponse({
        "status": "healthy",
        "service": "Nigerian Bank USSD AI Agent",
        "a2a_protocol": "supported",
        "ai_available": bool(GEMINI_API_KEY),
        "total_banks": len(BANK_USSD_CODES),
        "mode": "ai-only"
    })

# Test endpoint to verify AI functionality
@csrf_exempt
@require_http_methods(["POST"])
def test_ai(request):
    """Test endpoint to verify Gemini AI is working correctly"""
    if not GEMINI_API_KEY:
        return JsonResponse({"error": "No API key"}, status=500)
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            "What is 2+2? Answer with one number only."
        )
        return JsonResponse({
            "ai_working": True,
            "response": response.text,
            "model": MODEL_NAME
        })
    except Exception as e:
        return JsonResponse({
            "ai_working": False,
            "error": str(e)
        }, status=500)