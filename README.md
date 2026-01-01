# Nigerian Bank USSD AI Agent

A pure AI-powered assistant that provides USSD codes for Nigerian banks using Google Gemini AI.

## Features
- Pure AI implementation using Google Gemini
- USSD codes for 17 Nigerian banks
- Natural language understanding
- Fast response times
- Telex.im A2A integration

## Live Demo
**Endpoint:** `https://web-production-f7377.up.railway.app/a2a/agent/ussd-helper`

## Usage
```bash
curl -X POST https://web-production-f7377.up.railway.app/a2a/agent/ussd-helper \
  -H "Content-Type: application/json" \
  -d '{"content": "UBA balance"}'
```

## Example Queries
- "UBA balance" → Returns *919*00#
- "GTB transfer code" → Returns *737*1*Amount*AccountNumber#
- "Access Bank airtime" → Returns *901*Amount*PhoneNumber#
- "Is USSD banking safe?" → AI-powered security analysis

## Supported Banks
Access Bank, GTB, UBA, Zenith Bank, First Bank, Polaris Bank, Union Bank, Fidelity Bank, Ecobank, Wema Bank, Sterling Bank, FCMB, Unity Bank, Keystone Bank, Stanbic IBTC, Jaiz Bank, Heritage Bank

## Technology
- Backend: Django + Python
- AI: Google Gemini API
- Deployment: Railway
- Protocol: JSON-RPC 2.0

## Health Check
`GET https://web-production-f7377.up.railway.app/a2a/health`

Built for HNG Internship Stage 3 Backend Task.