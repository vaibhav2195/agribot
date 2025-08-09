from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import os

VERIFY_TOKEN = "myverifytoken"
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

app = FastAPI()

@app.get("/webhook")
async def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return JSONResponse(status_code=403, content={})

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    print(data)
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]

        # Simple bot logic
        if "hello" in text.lower():
            reply_text = "👋 Hi! How can I help you?"
        else:
            reply_text = "I’m your bot! 😊"

        # Send reply
        url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": from_number,
            "text": {"body": reply_text}
        }
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        requests.post(url, json=payload, headers=headers)

    except Exception as e:
        print("Error:", e)

    return JSONResponse(status_code=200, content={})
