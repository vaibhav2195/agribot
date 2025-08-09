from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

# Must exactly match the token you set in the WhatsApp webhook setup
VERIFY_TOKEN = "my_verify_token"

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Webhook verification endpoint for WhatsApp"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)  # WhatsApp expects this exact number
    return {"error": "Invalid verification token"}

@app.post("/webhook")
async def receive_message(request: Request):
    """Handle incoming WhatsApp messages"""
    data = await request.json()
    print("Received message:", data)
    # You can add reply logic here later
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
