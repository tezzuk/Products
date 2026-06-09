"""
WhatsApp AI Bot — Real Twilio Webhook
Receives actual WhatsApp messages via Twilio, replies with Gemini AI.
Deploy on Railway (free). Configure via environment variables.
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import os
import json

app = Flask(__name__)

# ── Business config from environment variables ──
# Set these in Railway dashboard for each client
BUSINESS_NAME     = os.environ.get("BUSINESS_NAME", "Sharma Restaurant")
BUSINESS_TYPE     = os.environ.get("BUSINESS_TYPE", "Restaurant")
BUSINESS_ADDRESS  = os.environ.get("BUSINESS_ADDRESS", "Civil Lines, Kanpur")
BUSINESS_TIMINGS  = os.environ.get("BUSINESS_TIMINGS", "Mon–Sat 10am–10pm")
BUSINESS_PHONE    = os.environ.get("BUSINESS_PHONE", "9876543210")
BUSINESS_SERVICES = os.environ.get("BUSINESS_SERVICES", "Dal Makhani ₹180, Biryani ₹200, Thali ₹150")
BUSINESS_PRICING  = os.environ.get("BUSINESS_PRICING", "")
BUSINESS_EXTRA    = os.environ.get("BUSINESS_EXTRA", "UPI accepted, home delivery available")
GEMINI_API_KEY    = os.environ.get("GEMINI_API_KEY", "")
OWNER_PHONE       = os.environ.get("OWNER_PHONE", "")  # for lead notifications

# In-memory conversation + lead tracking (resets on redeploy — fine for demo)
conversations = {}  # sender -> list of messages
leads = {}          # sender -> {step, name, phone, query}


def get_system_prompt():
    return f"""You are an AI WhatsApp assistant for {BUSINESS_NAME}, a {BUSINESS_TYPE} in Kanpur, India.

BUSINESS INFORMATION:
- Name: {BUSINESS_NAME}
- Type: {BUSINESS_TYPE}
- Address: {BUSINESS_ADDRESS}
- Timings: {BUSINESS_TIMINGS}
- Phone: {BUSINESS_PHONE}
- Services / Menu: {BUSINESS_SERVICES}
- Pricing: {BUSINESS_PRICING}
- Additional info: {BUSINESS_EXTRA}

YOUR RULES:
1. Answer ONLY based on the information above. Never make up facts.
2. Reply in the SAME language the customer uses — Hindi, English, or Hinglish.
3. Keep replies SHORT — this is WhatsApp, not email. Max 3-4 lines.
4. Be warm, friendly, and helpful. Use 1-2 emojis per message naturally.
5. If a customer asks something you don't know, reply ONLY with the word: COLLECT_LEAD
6. Never say you are an AI or a bot unless directly asked.
7. For greetings, welcome them warmly and ask how you can help.
8. End responses with a helpful follow-up where natural.
"""


def call_gemini(sender, user_message):
    """Call Gemini API with conversation history."""
    if not GEMINI_API_KEY:
        return rule_based_reply(user_message)

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Build history (last 8 messages for context)
        history = conversations.get(sender, [])[-8:]
        chat_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=chat_history[:-1] if chat_history else [])
        full_prompt = get_system_prompt() + f"\n\nCustomer message: {user_message}"
        response = chat.send_message(full_prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Gemini error: {e}")
        return rule_based_reply(user_message)


def rule_based_reply(msg):
    """Fallback if no API key or Gemini fails."""
    m = msg.lower()
    if any(w in m for w in ["hello", "hi", "namaste", "hey"]):
        return f"Namaste! 🙏 Welcome to {BUSINESS_NAME}. Kaise help kar sakta hoon aapki?"
    if any(w in m for w in ["timing", "time", "open", "kab", "baje"]):
        return f"Humare timings: {BUSINESS_TIMINGS} 🕐" if BUSINESS_TIMINGS else "COLLECT_LEAD"
    if any(w in m for w in ["address", "location", "kahan", "where"]):
        return f"Hum yahan hain: {BUSINESS_ADDRESS} 📍" if BUSINESS_ADDRESS else "COLLECT_LEAD"
    if any(w in m for w in ["menu", "price", "rate", "kitna", "service", "kya hai"]):
        return f"{BUSINESS_SERVICES} 😊" if BUSINESS_SERVICES else "COLLECT_LEAD"
    if any(w in m for w in ["thanks", "shukriya", "ok", "theek", "done"]):
        return f"Khushi hui! Aur kuch chahiye toh batayein 🙏 — {BUSINESS_NAME}"
    return "COLLECT_LEAD"


def store_message(sender, role, content):
    if sender not in conversations:
        conversations[sender] = []
    conversations[sender].append({"role": role, "content": content})
    # Keep only last 20 messages per sender
    if len(conversations[sender]) > 20:
        conversations[sender] = conversations[sender][-20:]


@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    if not incoming_msg:
        return str(MessagingResponse())

    print(f"Message from {sender}: {incoming_msg}")
    store_message(sender, "user", incoming_msg)

    resp = MessagingResponse()

    # ── Lead collection flow ──
    if sender in leads:
        lead = leads[sender]

        if lead["step"] == 1:
            # Got their name
            lead["name"] = incoming_msg
            lead["step"] = 2
            store_message(sender, "bot", "Aur aapka phone number? 📞")
            resp.message("Aur aapka phone number? 📞")

        elif lead["step"] == 2:
            # Got their number — save and complete
            lead["phone"] = incoming_msg
            name = lead.get("name", "Customer")
            query = lead.get("query", "")
            print(f"NEW LEAD: Name={name}, Phone={incoming_msg}, Query={query}, From={sender}")

            reply = (f"Shukriya {name} ji! ✅\n\n"
                     f"{BUSINESS_NAME} ki taraf se humara staff aapko jald call karega.\n\n"
                     f"Koi aur sawaal? 😊")
            del leads[sender]
            store_message(sender, "bot", reply)
            resp.message(reply)

        return str(resp)

    # ── Normal AI response ──
    ai_response = call_gemini(sender, incoming_msg)

    if "COLLECT_LEAD" in ai_response:
        # Start lead collection
        leads[sender] = {"step": 1, "query": incoming_msg}
        reply = ("Yeh query main owner tak pahunchaata hoon! 😊\n\n"
                 "Aapka naam bata sakte hain? 🙏")
        store_message(sender, "bot", reply)
        resp.message(reply)
    else:
        store_message(sender, "bot", ai_response)
        resp.message(ai_response)

    return str(resp)


@app.route("/", methods=["GET"])
def home():
    return f"""
    <h2>✅ {BUSINESS_NAME} WhatsApp Bot — Running</h2>
    <p>Webhook URL: <code>/webhook</code></p>
    <p>Conversations active: {len(conversations)}</p>
    <p>Leads collected: {len(leads)}</p>
    <p>AI: {'Gemini connected ✅' if GEMINI_API_KEY else '⚠️ No API key set — using rule-based fallback'}</p>
    """


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
