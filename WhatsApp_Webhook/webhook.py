from flask import Flask, request, Response, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import sqlite3, os, json, csv, io
from datetime import datetime

app = Flask(__name__)

BUSINESS_NAME     = os.environ.get("BUSINESS_NAME", "My Business")
BUSINESS_TYPE     = os.environ.get("BUSINESS_TYPE", "Business")
BUSINESS_ADDRESS  = os.environ.get("BUSINESS_ADDRESS", "")
BUSINESS_TIMINGS  = os.environ.get("BUSINESS_TIMINGS", "")
BUSINESS_PHONE    = os.environ.get("BUSINESS_PHONE", "")
BUSINESS_SERVICES = os.environ.get("BUSINESS_SERVICES", "")
BUSINESS_PRICING  = os.environ.get("BUSINESS_PRICING", "")
BUSINESS_EXTRA    = os.environ.get("BUSINESS_EXTRA", "")
GEMINI_API_KEY    = os.environ.get("GEMINI_API_KEY", "")
DASHBOARD_KEY     = os.environ.get("DASHBOARD_KEY", "admin123")
ENABLE_ORDERS     = os.environ.get("ENABLE_ORDERS", "false").lower() == "true"
ENABLE_APPOINTMENTS = os.environ.get("ENABLE_APPOINTMENTS", "true").lower() == "true"
try:
    CUSTOM_FAQ = json.loads(os.environ.get("CUSTOM_FAQ", "{}"))
except:
    CUSTOM_FAQ = {}

DB_PATH = "/tmp/bot_data.db"
states = {}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT, name TEXT, phone TEXT,
        query TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT, name TEXT, phone TEXT,
        preferred_date TEXT, preferred_time TEXT,
        notes TEXT, status TEXT DEFAULT 'Pending', created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT, name TEXT, phone TEXT,
        items TEXT, total TEXT, status TEXT DEFAULT 'New', created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT, role TEXT, message TEXT, created_at TEXT)""")
    conn.commit()
    conn.close()

def db():
    return sqlite3.connect(DB_PATH)

def log_message(sender, role, message):
    conn = db()
    conn.execute("INSERT INTO conversations (sender,role,message,created_at) VALUES (?,?,?,?)",
                 (sender, role, message, datetime.now().isoformat()))
    conn.commit(); conn.close()

def save_lead(sender, name, phone, query):
    conn = db()
    conn.execute("INSERT INTO leads (sender,name,phone,query,created_at) VALUES (?,?,?,?,?)",
                 (sender, name, phone, query, datetime.now().isoformat()))
    conn.commit(); conn.close()

def save_appointment(sender, name, phone, date, time, notes):
    conn = db()
    conn.execute("INSERT INTO appointments (sender,name,phone,preferred_date,preferred_time,notes,created_at) VALUES (?,?,?,?,?,?,?)",
                 (sender, name, phone, date, time, notes, datetime.now().isoformat()))
    conn.commit(); conn.close()

def save_order(sender, name, phone, items, total):
    conn = db()
    conn.execute("INSERT INTO orders (sender,name,phone,items,total,created_at) VALUES (?,?,?,?,?,?)",
                 (sender, name, phone, items, total, datetime.now().isoformat()))
    conn.commit(); conn.close()

def get_history(sender, limit=8):
    conn = db()
    rows = conn.execute(
        "SELECT role,message FROM conversations WHERE sender=? ORDER BY created_at DESC LIMIT ?",
        (sender, limit)).fetchall()
    conn.close()
    return list(reversed(rows))

def build_prompt():
    faq = ""
    if CUSTOM_FAQ:
        faq = "\n\nCUSTOM FAQ:\n" + "\n".join(f"Q: {q}\nA: {a}" for q,a in CUSTOM_FAQ.items())
    appt_rule = "\n- If customer wants appointment/visit -> reply only: BOOK_APPOINTMENT" if ENABLE_APPOINTMENTS else ""
    order_rule = "\n- If customer wants to order -> reply only: TAKE_ORDER" if ENABLE_ORDERS else ""
    return f"""You are a WhatsApp assistant for {BUSINESS_NAME} ({BUSINESS_TYPE}).
BUSINESS INFO:
Name: {BUSINESS_NAME} | Type: {BUSINESS_TYPE} | Address: {BUSINESS_ADDRESS}
Timings: {BUSINESS_TIMINGS} | Phone: {BUSINESS_PHONE}
Services/Menu: {BUSINESS_SERVICES} | Pricing: {BUSINESS_PRICING}
Extra: {BUSINESS_EXTRA}
{faq}
RULES:
1. Answer ONLY using info above. Never make things up.
2. Always reply in English by default. ONLY switch to Hinglish if the customer explicitly asks for Hindi (e.g. "Hindi mein baat karo", "hindi me batao"). Never switch based on the language they message in.
3. Keep replies SHORT - max 4 lines. This is WhatsApp.
4. Be warm and friendly.
5. If asked something you do not know -> reply only: COLLECT_LEAD
6. Never reveal you are an AI unless directly asked.{appt_rule}{order_rule}
7. For greetings -> welcome warmly and ask how you can help."""

def get_ai_reply(sender, user_msg):
    if not GEMINI_API_KEY:
        return fallback_reply(user_msg)
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        history = get_history(sender)
        chat_history = [{"role": "user" if r=="user" else "model","parts":[m]} for r,m in history[:-1]]
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(build_prompt() + f"\n\nCustomer: {user_msg}")
        return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return fallback_reply(user_msg)

def fallback_reply(msg):
    m = msg.lower()
    if any(w in m for w in ["hello","hi","namaste","hey","hii"]):
        return f"Hello! Welcome to {BUSINESS_NAME}. How can I help you today?"
    if any(w in m for w in ["timing","time","open","kab","baje","hours"]):
        return f"Timings: {BUSINESS_TIMINGS}" if BUSINESS_TIMINGS else "COLLECT_LEAD"
    if any(w in m for w in ["address","location","kahan","where"]):
        return f"Address: {BUSINESS_ADDRESS}" if BUSINESS_ADDRESS else "COLLECT_LEAD"
    if any(w in m for w in ["price","rate","fees","menu","service","kitna"]):
        return f"{BUSINESS_SERVICES}" if BUSINESS_SERVICES else "COLLECT_LEAD"
    if any(w in m for w in ["book","appointment","slot","milna","visit"]):
        return "BOOK_APPOINTMENT" if ENABLE_APPOINTMENTS else "COLLECT_LEAD"
    if any(w in m for w in ["order","lena","chahiye","delivery"]):
        return "TAKE_ORDER" if ENABLE_ORDERS else "COLLECT_LEAD"
    if any(w in m for w in ["thanks","shukriya","ok","theek","done","bye"]):
        return "Thank you! Feel free to ask if you need anything else."
    return "COLLECT_LEAD"

def handle_lead_flow(sender, msg, state):
    if state["step"] == 1:
        state["data"]["name"] = msg; state["step"] = 2
        return "And your phone number?"
    elif state["step"] == 2:
        save_lead(sender, state["data"]["name"], msg, state["data"].get("query",""))
        name = state["data"]["name"]
        del states[sender]
        return f"Thank you {name}! Someone from {BUSINESS_NAME} will call you shortly."

def handle_appointment_flow(sender, msg, state):
    step = state["step"]
    if step == 1:
        state["data"]["name"] = msg; state["step"] = 2
        return "And your phone number?"
    elif step == 2:
        state["data"]["phone"] = msg; state["step"] = 3
        return "What date works for you? (e.g. 15 June)"
    elif step == 3:
        state["data"]["date"] = msg; state["step"] = 4
        return "What time works best? (e.g. 11am, 3pm)"
    elif step == 4:
        state["data"]["time"] = msg; state["step"] = 5
        return "Any special notes? (or type 'no')"
    elif step == 5:
        notes = "" if msg.lower() in ["no","nahi","na","n"] else msg
        d = state["data"]
        save_appointment(sender, d["name"], d["phone"], d["date"], d["time"], notes)
        del states[sender]
        return f"Appointment confirmed! {d['name']} | {d['date']} at {d['time']}. We will confirm shortly."

def handle_order_flow(sender, msg, state):
    step = state["step"]
    if step == 1:
        state["data"]["items"] = msg; state["step"] = 2
        return "Your name please?"
    elif step == 2:
        state["data"]["name"] = msg; state["step"] = 3
        return "Your phone number?"
    elif step == 3:
        d = state["data"]
        save_order(sender, d["name"], msg, d["items"], "")
        del states[sender]
        return f"Order received! Items: {d['items']}. We will call you on {msg} to confirm."

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.values.get("Body","").strip()
    sender = request.values.get("From","")
    resp = MessagingResponse()
    if not body:
        return str(resp)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {sender}: {body}")
    log_message(sender, "user", body)

    if sender in states:
        state = states[sender]
        flow = state["flow"]
        if flow == "lead": reply = handle_lead_flow(sender, body, state)
        elif flow == "appointment": reply = handle_appointment_flow(sender, body, state)
        elif flow == "order": reply = handle_order_flow(sender, body, state)
        else: reply = "COLLECT_LEAD"
    else:
        reply = get_ai_reply(sender, body)
        if "COLLECT_LEAD" in reply:
            states[sender] = {"flow":"lead","step":1,"data":{"query":body}}
            reply = "Let me connect you with our team! May I know your name?"
        elif "BOOK_APPOINTMENT" in reply:
            if ENABLE_APPOINTMENTS:
                states[sender] = {"flow":"appointment","step":1,"data":{}}
                reply = "Sure! Let me book an appointment for you. Your name please?"
            else:
                states[sender] = {"flow":"lead","step":1,"data":{"query":body}}
                reply = "Let me arrange a callback. Your name please?"
        elif "TAKE_ORDER" in reply:
            if ENABLE_ORDERS:
                states[sender] = {"flow":"order","step":1,"data":{}}
                reply = f"Kya order karna chahenge?\n{BUSINESS_SERVICES}"
            else:
                states[sender] = {"flow":"lead","step":1,"data":{"query":body}}
                reply = "Let me note your order. Your name please?"

    log_message(sender, "bot", reply)
    resp.message(reply)
    return str(resp)

DASH_HTML = """<!DOCTYPE html><html>
<head><title>{{ biz }} Dashboard</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:-apple-system,sans-serif;background:#f0f2f5;margin:0}
.hdr{background:#075e54;color:white;padding:14px 20px;font-size:16px;font-weight:bold}
.stats{display:flex;gap:10px;padding:14px;flex-wrap:wrap}
.stat{background:white;border-radius:10px;padding:14px;flex:1;min-width:120px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.n{font-size:26px;font-weight:700;color:#075e54}.l{font-size:11px;color:#888}
.sec{margin:0 14px 16px}.sec h2{font-size:12px;color:#555;text-transform:uppercase;margin-bottom:8px}
.card{background:white;border-radius:8px;padding:12px;margin-bottom:6px;border-left:4px solid #25d366;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.card.a{border-left-color:#4361ee}.card.o{border-left-color:#f4a261}
.name{font-weight:600;font-size:13px}.meta{font-size:11px;color:#888;margin-top:3px}
.q{font-size:12px;color:#444;margin-top:4px;font-style:italic}
a.btn{display:inline-block;background:#25d366;color:white;padding:8px 16px;border-radius:8px;text-decoration:none;font-size:13px;margin:0 14px 14px}
</style></head><body>
<div class="hdr">{{ biz }} &mdash; Bot Dashboard <small style="opacity:.7;font-size:12px">{{ now }}</small></div>
<div class="stats">
<div class="stat"><div class="n">{{ lc }}</div><div class="l">Leads</div></div>
<div class="stat"><div class="n">{{ ac }}</div><div class="l">Appointments</div></div>
<div class="stat"><div class="n">{{ oc }}</div><div class="l">Orders</div></div>
<div class="stat"><div class="n">{{ cc }}</div><div class="l">Msgs Today</div></div>
</div>
<a href="/export?key={{ key }}" class="btn">Export CSV</a>
<div class="sec"><h2>Leads ({{ lc }})</h2>
{% for l in leads %}<div class="card">
<div class="name">{{ l[2] or 'Unknown' }}</div>
<div class="meta">{{ l[3] }} | {{ l[5][:16] }}</div>
<div class="q">"{{ l[4] }}"</div>
</div>{% else %}<p style="color:#aaa;font-size:13px">No leads yet.</p>{% endfor %}</div>
<div class="sec"><h2>Appointments ({{ ac }})</h2>
{% for a in appts %}<div class="card a">
<div class="name">{{ a[2] or 'Unknown' }}</div>
<div class="meta">{{ a[3] }} | {{ a[4] }} at {{ a[5] }}</div>
{% if a[6] %}<div class="q">{{ a[6] }}</div>{% endif %}
</div>{% else %}<p style="color:#aaa;font-size:13px">No appointments yet.</p>{% endfor %}</div>
{% if orders %}<div class="sec"><h2>Orders ({{ oc }})</h2>
{% for o in orders %}<div class="card o">
<div class="name">{{ o[2] or 'Unknown' }}</div>
<div class="meta">{{ o[3] }} | {{ o[7][:16] }}</div>
<div class="q">{{ o[4] }}</div>
</div>{% endfor %}</div>{% endif %}
</body></html>"""

@app.route("/dashboard")
def dashboard():
    key = request.args.get("key","")
    if key != DASHBOARD_KEY:
        return Response("Access denied. Use ?key=YOUR_DASHBOARD_KEY", status=403)
    conn = db()
    leads = conn.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT 50").fetchall()
    appts = conn.execute("SELECT * FROM appointments ORDER BY created_at DESC LIMIT 50").fetchall()
    orders = conn.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 50").fetchall()
    today = datetime.now().strftime("%Y-%m-%d")
    cc = conn.execute("SELECT COUNT(*) FROM conversations WHERE created_at LIKE ?", (f"{today}%",)).fetchone()[0]
    conn.close()
    html = render_template_string(DASH_HTML, biz=BUSINESS_NAME,
        now=datetime.now().strftime("%d %b %Y, %I:%M %p"),
        leads=leads, appts=appts, orders=orders,
        lc=len(leads), ac=len(appts), oc=len(orders), cc=cc, key=key)
    return html

@app.route("/export")
def export_csv():
    key = request.args.get("key","")
    if key != DASHBOARD_KEY:
        return Response("Access denied.", status=403)
    out = io.StringIO()
    w = csv.writer(out)
    conn = db()
    w.writerow(["=== LEADS ==="])
    w.writerow(["ID","Sender","Name","Phone","Query","Time"])
    for r in conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall(): w.writerow(r)
    w.writerow([])
    w.writerow(["=== APPOINTMENTS ==="])
    w.writerow(["ID","Sender","Name","Phone","Date","Time","Notes","Status","Created"])
    for r in conn.execute("SELECT * FROM appointments ORDER BY created_at DESC").fetchall(): w.writerow(r)
    w.writerow([])
    w.writerow(["=== ORDERS ==="])
    w.writerow(["ID","Sender","Name","Phone","Items","Total","Status","Created"])
    for r in conn.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall(): w.writerow(r)
    conn.close()
    out.seek(0)
    return Response(out.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={BUSINESS_NAME}_data.csv"})

@app.route("/")
def home():
    conn = db()
    lc = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    ac = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    conn.close()
    return (f"<h2>{BUSINESS_NAME} WhatsApp Bot - Running</h2>"
            f"<p>Leads: {lc} | Appointments: {ac}</p>"
            f"<p><a href='/dashboard?key={DASHBOARD_KEY}'>Owner Dashboard</a></p>")

init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
