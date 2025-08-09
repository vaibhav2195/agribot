import os
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

app = FastAPI()

@app.get("/")
def home():
    return {"status": "WhatsApp bot is running"}

# Webhook verification
@app.get("/webhook")
def verify_webhook(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    return {"error": "Verification failed"}

# Receive messages
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    print("Incoming webhook data:", data)  # Debug log

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        phone_number = message["from"]  # sender's number
        text = message["text"]["body"].strip().lower()

        if text in ["hi", "hello"]:
            send_whatsapp_message(phone_number, "Hello! 👋 How can I help you today?")
        else:
            send_whatsapp_message(phone_number, "Sorry, I didn't understand that.")

    except KeyError:
        print("No valid message in the webhook payload.")

    return {"status": "success"}

# Send message function
def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Send message response:", response.status_code, response.text)
    return response.json()
