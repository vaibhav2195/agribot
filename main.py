import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")  # Your verify token from Meta Webhook setup
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")  # Permanent or temporary access token
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")  # From WhatsApp Cloud API

# Root route (optional)
@app.get("/")
def home():
    return {"status": "WhatsApp bot running"}


# Webhook verification (GET)
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            return PlainTextResponse(content="Verification token mismatch", status_code=403)
    return PlainTextResponse(content="Invalid request", status_code=400)


# Webhook for incoming messages (POST)
@app.post("/webhook")
async def webhook_handler(request: Request):
    try:
        data = await request.json()
        print("Incoming:", data)  # Log incoming request

        if "entry" in data:
            for entry in data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        value = change.get("value", {})
                        messages = value.get("messages", [])
                        if messages:
                            for msg in messages:
                                from_number = msg["from"]  # sender's WhatsApp number
                                text = msg.get("text", {}).get("body", "").strip().lower()

                                if text in ["hi", "hello", "hey"]:
                                    reply = "Hello! 👋 How can I help you today?"
                                else:
                                    reply = f"You said: {text}"

                                send_whatsapp_message(from_number, reply)
        return JSONResponse(content={"status": "success"}, status_code=200)

    except Exception as e:
        print("Error:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Function to send WhatsApp message
def send_whatsapp_message(to_number: str, message: str):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Send response:", response.status_code, response.text)
    return response.json()
