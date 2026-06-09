"""
AI WhatsApp Business Bot — Demo App
Shows clients exactly how their bot will behave.
Uses Google Gemini API (free: 1500 requests/day, no credit card).
Get API key at: https://aistudio.google.com/app/apikey
"""

import streamlit as st
import json
import re
from datetime import datetime

# ── Try to import Gemini ──
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

st.set_page_config(
    page_title="WhatsApp AI Bot Demo",
    page_icon="💬",
    layout="wide"
)

# ── CSS: WhatsApp look ──
st.markdown("""
<style>
.stApp { background-color: #ece5dd; }
.main .block-container { padding-top: 1.5rem; max-width: 1100px; }

.chat-bubble-bot {
    background: white;
    border-radius: 0 12px 12px 12px;
    padding: 10px 14px;
    margin: 6px 0;
    max-width: 75%;
    display: inline-block;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    font-size: 14px;
    color: #111;
}
.chat-bubble-user {
    background: #dcf8c6;
    border-radius: 12px 0 12px 12px;
    padding: 10px 14px;
    margin: 6px 0;
    max-width: 75%;
    display: inline-block;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    font-size: 14px;
    color: #111;
    float: right;
    clear: both;
}
.chat-time { font-size: 10px; color: #999; margin-top: 2px; }
.chat-container {
    background: #e5ddd5 url("data:image/svg+xml,%3Csvg...%3E") repeat;
    border-radius: 12px;
    padding: 16px;
    min-height: 400px;
    max-height: 500px;
    overflow-y: auto;
}
.wa-header {
    background: #075e54;
    color: white;
    padding: 12px 16px;
    border-radius: 12px 12px 0 0;
    font-weight: bold;
    font-size: 15px;
}
.lead-card {
    background: white;
    border-left: 4px solid #25d366;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 8px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.section-box {
    background: white;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "leads" not in st.session_state:
    st.session_state.leads = []
if "collecting_lead" not in st.session_state:
    st.session_state.collecting_lead = False
if "lead_step" not in st.session_state:
    st.session_state.lead_step = 0
if "pending_lead" not in st.session_state:
    st.session_state.pending_lead = {}


def build_system_prompt(cfg):
    return f"""You are an AI assistant for {cfg['business_name']}, a {cfg['business_type']} in Kanpur.

BUSINESS INFO:
- Name: {cfg['business_name']}
- Type: {cfg['business_type']}
- Address: {cfg['address']}
- Timings: {cfg['timings']}
- Phone: {cfg['phone']}
- Services/Menu: {cfg['services']}
- Pricing: {cfg['pricing']}
- Special info: {cfg['extra']}

INSTRUCTIONS:
1. Answer customer questions ONLY based on the above info. Be friendly, brief, warm.
2. Respond in the SAME language the customer uses (Hindi or English or Hinglish).
3. If asked something you don't know → say: "COLLECT_LEAD" (just those two words, nothing else)
4. For greetings → warmly welcome and ask how you can help.
5. Keep replies short — this is WhatsApp, not email.
6. Never make up information not provided above.
7. End responses with a helpful follow-up question when appropriate.
"""


def get_ai_response(user_msg, cfg, api_key):
    if not GEMINI_AVAILABLE or not api_key:
        return rule_based_response(user_msg, cfg)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        history = []
        for m in st.session_state.messages[-10:]:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [m["content"]]})

        chat = model.start_chat(history=history[:-1] if history else [])
        system = build_system_prompt(cfg)
        response = chat.send_message(system + "\n\nCustomer: " + user_msg)
        return response.text.strip()
    except Exception as e:
        return rule_based_response(user_msg, cfg)


def rule_based_response(user_msg, cfg):
    msg = user_msg.lower()
    name = cfg["business_name"]

    if any(w in msg for w in ["hello", "hi", "namaste", "helo", "hey", "hii"]):
        return f"Namaste! 🙏 Welcome to {name}. Main aapki kaise madad kar sakta hoon?"

    if any(w in msg for w in ["timing", "time", "open", "close", "hours", "baje", "kab"]):
        if cfg["timings"]:
            return f"Humare timings hain: {cfg['timings']} 🕐"
        return "COLLECT_LEAD"

    if any(w in msg for w in ["address", "location", "kahan", "where", "jagah"]):
        if cfg["address"]:
            return f"Hum yahan hain: {cfg['address']} 📍\nGoogle Maps pe '{name}' search karein!"
        return "COLLECT_LEAD"

    if any(w in msg for w in ["price", "cost", "rate", "kitna", "fees", "charge", "menu", "service"]):
        if cfg["pricing"] or cfg["services"]:
            info = cfg["services"] + ("\n\n" + cfg["pricing"] if cfg["pricing"] else "")
            return f"Yeh hai humari services/pricing:\n\n{info} 😊"
        return "COLLECT_LEAD"

    if any(w in msg for w in ["phone", "number", "contact", "call", "baat"]):
        if cfg["phone"]:
            return f"Aap hume directly call kar sakte hain: {cfg['phone']} 📞"
        return "COLLECT_LEAD"

    if any(w in msg for w in ["book", "appointment", "slot", "available", "kab", "milenge"]):
        return "COLLECT_LEAD"

    if any(w in msg for w in ["thanks", "thank", "shukriya", "dhanyawad", "ok", "theek"]):
        return f"Khushi hui aapki help karke! Aur kuch chahiye toh batayein. {name} mein aapka swagat hai 🙏"

    return "COLLECT_LEAD"


def add_message(role, content):
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "time": datetime.now().strftime("%H:%M")
    })


# ── LAYOUT ──
st.markdown("## 💬 WhatsApp AI Bot — Live Demo")
st.caption("Show this to your client. They type questions as their customer would → bot responds instantly.")

col_setup, col_chat = st.columns([1, 1.2])

# ── LEFT: Setup ──
with col_setup:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("### 🏪 Business Setup")
    st.caption("Fill in your client's details. The bot learns from this.")

    business_name = st.text_input("Business Name", value="Sharma Restaurant")
    business_type = st.selectbox("Business Type",
        ["Restaurant / Dhaba", "Dental Clinic", "Coaching Center",
         "Medical Clinic", "Pharmacy", "Gym / Fitness", "Other"])
    address = st.text_input("Address", value="Civil Lines, Kanpur")
    timings = st.text_input("Timings", value="Mon–Sat 10am–10pm, Sun 11am–9pm")
    phone = st.text_input("Phone", value="9876543210")
    services = st.text_area("Services / Menu", height=80,
        value="Dal Makhani ₹180, Paneer Butter Masala ₹220, Thali ₹150, Biryani ₹200")
    pricing = st.text_area("Extra Pricing Info (optional)", height=60, placeholder="Home delivery min ₹100...")
    extra = st.text_area("Other Info (optional)", height=60,
        placeholder="Parking available, AC seating, accepts UPI...")

    api_key = st.text_input("🔑 Gemini API Key (optional — for real AI)",
        type="password",
        help="Free at aistudio.google.com/app/apikey — 1500 requests/day, no card needed")

    if st.button("🚀 Start / Reset Demo Chat", type="primary"):
        st.session_state.messages = []
        st.session_state.leads = []
        st.session_state.collecting_lead = False
        st.session_state.lead_step = 0
        st.session_state.pending_lead = {}
        add_message("bot",
            f"Namaste! 🙏 Welcome to {business_name}. Main aapki kaise help kar sakta hoon?\n\n"
            "_(Type as if you're a customer messaging this business)_")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Leads Panel
    if st.session_state.leads:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown(f"### 📋 Collected Leads ({len(st.session_state.leads)})")
        st.caption("These are customers who had queries the bot couldn't answer — owner must call back.")
        for lead in reversed(st.session_state.leads):
            st.markdown(f"""
            <div class="lead-card">
            👤 <b>{lead.get('name', 'Unknown')}</b><br/>
            📞 {lead.get('phone', '—')}<br/>
            💬 <i>"{lead.get('query', '')}"</i><br/>
            🕐 {lead.get('time', '')}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── RIGHT: Chat ──
with col_chat:
    cfg = {
        "business_name": business_name,
        "business_type": business_type,
        "address": address,
        "timings": timings,
        "phone": phone,
        "services": services,
        "pricing": pricing,
        "extra": extra,
    }

    # WhatsApp header
    st.markdown(f"""
    <div class="wa-header">
        <span>🟢</span> &nbsp; {business_name} &nbsp;
        <span style="font-size:11px; opacity:0.8">online</span>
    </div>
    """, unsafe_allow_html=True)

    # Chat window
    chat_html = '<div class="chat-container" id="chat-box">'
    if not st.session_state.messages:
        chat_html += '<p style="color:#888; text-align:center; padding:40px 0;">Press "Start Demo Chat" to begin 👆</p>'

    for msg in st.session_state.messages:
        if msg["role"] == "bot":
            text = msg["content"].replace("\n", "<br/>")
            chat_html += f'<div style="clear:both;"><div class="chat-bubble-bot">{text}<br/><span class="chat-time">{msg["time"]} ✓✓</span></div></div>'
        else:
            text = msg["content"].replace("\n", "<br/>")
            chat_html += f'<div style="clear:both;"><div class="chat-bubble-user">{text}<br/><span class="chat-time">{msg["time"]}</span></div></div>'

    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # Input
    user_input = st.chat_input("Type a customer message...")

    if user_input and st.session_state.messages:
        add_message("user", user_input)

        # Lead collection flow
        if st.session_state.collecting_lead:
            step = st.session_state.lead_step
            if step == 1:
                st.session_state.pending_lead["name"] = user_input
                st.session_state.lead_step = 2
                add_message("bot", "Aur aapka phone number? 📞")
            elif step == 2:
                st.session_state.pending_lead["phone"] = user_input
                st.session_state.pending_lead["time"] = datetime.now().strftime("%H:%M")
                st.session_state.leads.append(st.session_state.pending_lead.copy())
                st.session_state.collecting_lead = False
                st.session_state.lead_step = 0
                st.session_state.pending_lead = {}
                add_message("bot",
                    f"Shukriya! ✅ {business_name} ki taraf se humara staff aapko jald call karega.\n\n"
                    "Aur koi sawaal? 😊")
        else:
            response = get_ai_response(user_input, cfg, api_key)

            if "COLLECT_LEAD" in response:
                st.session_state.collecting_lead = True
                st.session_state.lead_step = 1
                st.session_state.pending_lead = {"query": user_input}
                add_message("bot",
                    "Yeh query main aapke liye owner tak pahunchaata hoon! 😊\n\n"
                    "Aapka naam bata sakte hain? 🙏")
            else:
                add_message("bot", response)

        st.rerun()

    if not st.session_state.messages:
        st.info('👆 Click "Start / Reset Demo Chat" first, then type customer questions below.')

# ── Try these messages hint ──
with st.expander("💡 Try typing these as a customer (demo suggestions)"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - `Hello`
        - `Timings kya hain?`
        - `Menu bhejo`
        - `Price kya hai?`
        """)
    with col2:
        st.markdown("""
        - `Address kya hai?`
        - `Appointment book karna hai`
        - `Home delivery hai?`
        - `Thank you`
        """)
