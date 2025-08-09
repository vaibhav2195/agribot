from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_verify_token")  # set in Render environment variables

@app.get("/")
def home():
    return {"status": "FastAPI WhatsApp Bot is running"}

# Webhook verification (GET)
@app.get("/webhook")
async def verify_token(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return JSONResponse(content=int(challenge))
    return JSONResponse(content="Verification failed", status_code=403)

# Handle incoming messages (POST)
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                if messages:
                    from_number = messages[0]["from"]
                    text_body = messages[0]["text"]["body"]

                    print(f"Message from {from_number}: {text_body}")

                    # Greeting logic
                    if text_body.lower() in ["hi", "hello"]:
                        send_whatsapp_message(from_number, "Hello! 👋 How can I help you today?")
                    else:
                        send_whatsapp_message(from_number, f"You said: {text_body}")

        return JSONResponse(content={"status": "success"})
    except Exception as e:
        print("Error:", e)
        return JSONResponse(content={"status": "error"}, status_code=500)


# Send message back via WhatsApp Cloud API
import requests
def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v18.0/{os.getenv('PHONE_NUMBER_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=payload)

