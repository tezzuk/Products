# Deploy — WhatsApp AI Bot
*This demo deploys in ~10 minutes. Free on Streamlit Cloud.*

---

## Step 1: Get a Free Gemini API Key (2 min)
1. Go to: **https://aistudio.google.com/app/apikey**
2. Sign in with Google
3. Click **Create API Key**
4. Copy it — you'll paste it into the app later

Free tier: 1,500 requests/day. More than enough.

---

## Step 2: Put Code on GitHub
1. github.com → **New Repository** → name: `whatsapp-bot-demo`
2. **uploading an existing file** → upload:
   - `app.py`
   - `requirements.txt`
3. Commit changes

---

## Step 3: Deploy on Streamlit Cloud
1. **share.streamlit.io** → New app
2. Select repo: `whatsapp-bot-demo`
3. Main file: `app.py`
4. Click **Deploy**

Live URL in ~2 minutes.

---

## Step 4: Demo Setup
1. Open your live URL
2. Paste your Gemini API key into the field
3. Fill in the client's business details on the left
4. Press "Start / Reset Demo Chat"
5. Type: "Hello", "Menu bhejo", "Appointment book karna hai"
6. Client sees it working in real time

---

## For a Paying Client (actual WhatsApp integration)

The above is the DEMO. For a real WhatsApp bot on a client's actual phone:
1. They need a **Twilio account** (twilio.com) — ask me to help set this up
2. Cost: ~₹800/month for a Twilio WhatsApp number (client pays this)
3. We deploy a Flask webhook on **Railway** (free tier)
4. Twilio routes messages to the webhook → AI responds → Twilio delivers

**Time to set up for a paying client: ~3 hours. Ask me when you have one.**

---

## Troubleshooting
| Problem | Fix |
|---|---|
| "No module named google" | requirements.txt must have `google-generativeai` |
| Bot says wrong things | Update the Business Setup fields on the left, restart chat |
| API key error | Double-check key at aistudio.google.com, key must start with "AIza..." |
| App slow to load | Normal on Streamlit free tier — warn clients it's a demo environment |
