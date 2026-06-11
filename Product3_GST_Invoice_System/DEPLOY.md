# How to Deploy — GST Invoice System
*Get a live URL in ~10 minutes. Free forever.*

---

## What You Need
- A GitHub account (free) — make one at github.com if you don't have one
- A Streamlit account (free) — sign up at share.streamlit.io with your GitHub

---

## Step 1: Put the code on GitHub

On your friend's laptop:

1. Go to github.com → click **New repository**
2. Name it: `gst-invoice-app` → **Create repository**
3. On the next screen, click **uploading an existing file**
4. Upload both files:
   - `app.py`
   - `requirements.txt`
5. Click **Commit changes**

---

## Step 2: Deploy on Streamlit Cloud

1. Go to **share.streamlit.io**
2. Click **New app**
3. Select your GitHub repo: `gst-invoice-app`
4. Branch: `main`
5. Main file path: `app.py`
6. Click **Deploy!**

Wait ~2 minutes. You'll get a live URL like:
**`https://yourname-gst-invoice-app-app-xyz.streamlit.app`**

---

## Step 3: First-time setup (takes 2 minutes)

1. Open your live URL
2. Click **⚙️ Business Settings** in the sidebar
3. Fill in:
   - Your client's business name
   - Their GSTIN
   - Their address, phone, email
   - Bank details for payment
4. Click **Save Settings**

Done! Now go to **➕ Create Invoice** and make your first invoice.

---

## How to Customize Per Client

Each client gets their own deployment. To set up for a new client:
1. Either change the Business Settings to their details
2. Or deploy a separate copy (takes 5 min, same steps above)

**Tip:** Deploy one copy for your demo first. Show it to clients. 
Once they say yes and pay the advance, deploy a fresh one for them.

---

## Sharing the Demo with Prospects

Send them this WhatsApp message:
```
Sir/Ma'am, ek chhota demo bhej raha hoon 😊

Yeh link open karein:
[YOUR STREAMLIT LINK HERE]

Apna naam, ek item aur rate enter karein → 
"Generate Invoice PDF" dabayein → 
Professional PDF ready.

Interested? ₹8,000 one-time setup.
```

---

## If Client Wants Their Own URL (optional upgrade — charge ₹2,000 extra)

1. Create a **custom domain** on Railway/Render
2. Or tell them Streamlit URL is fine (most clients won't care)

---

## Troubleshooting

| Problem | Fix |
|---|---|
| App shows error on load | Check requirements.txt has `streamlit` and `reportlab` |
| PDF download doesn't work | Try a different browser (Chrome works best) |
| Settings not saving | Normal — Streamlit Cloud resets SQLite on restart. For persistent data, upgrade to Railway (see me) |
| App is slow | Free tier — normal. Wakes up in ~30 sec after inactivity |

---

## Important Note on Data Persistence

Streamlit Cloud's free tier resets the database when the app restarts (roughly every day).
**For the demo this is fine** — you just need to show clients the UI and PDF output.

For a paying client who needs permanent storage, deploy on **Railway** instead:
- railway.app → free $5/month credit → enough for 1-2 apps
- Same code, same requirements.txt, just different platform
- Data persists because Railway gives you a proper filesystem

Ask me to help with Railway deployment when you have your first paying client.
