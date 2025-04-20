from flask import Flask, request
import openai
import os
import datetime
from supabase import create_client, Client

app = Flask(__name__)

# Environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    phone = request.values.get("From", "").replace("whatsapp:", "")
    msg = request.values.get("Body", "").lower().strip()

    # Fetch user by phone number
    user = supabase.table("users").select("*").eq("phone", phone).single().execute().data
    now = datetime.datetime.utcnow()

    if not user or not user["subscribed"]:
        return _twilio_reply("⛔️ Your access is restricted. Subscribe to unlock slang lessons 👉 https://tryslango.com")

    return _respond_with_gpt(msg)

def _respond_with_gpt(user_input):
    system_prompt = """You are Slango, a Gen Z American AI who teaches real English texting slang.
Be fun, casual, and native-sounding. Use emojis. Give short examples. Respond like a texting buddy, not a teacher."""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    reply = response["choices"][0]["message"]["content"]
    return _twilio_reply(reply)

def _twilio_reply(text):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>{text}</Message>
</Response>"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
