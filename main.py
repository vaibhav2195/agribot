from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import os

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

app = FastAPI()

@app.get("/webhook")
async def verify_webhook(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    return JSONResponse({"error": "Verification failed"}, status_code=403)

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    print("Incoming webhook:", data)

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]

        # Send reply back to WhatsApp
        url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": from_number,
            "type": "text",
            "text": {"body": f"Hello! You said: {text}"}
        }
        r = requests.post(url, headers=headers, json=payload)
        print("Reply status:", r.status_code, r.text)

    except KeyError:
        print("No messages found in webhook payload.")

    return JSONResponse({"status": "ok"})
