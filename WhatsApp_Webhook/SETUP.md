# Setup Guide — Real WhatsApp Bot via Twilio Sandbox

## Step 1: Twilio Account (free)
1. Go to **twilio.com** → Sign up free
2. After signup → go to **Console Dashboard**
3. Note your **Account SID** and **Auth Token** (you'll need these later)
4. Left sidebar → **Messaging** → **Try it out** → **Send a WhatsApp message**
5. You'll see the sandbox number: **+1 415 523 8886**
6. And a join keyword like: **join example-word**

## Step 2: Join the Sandbox (you test this first)
On your WhatsApp, message **+1 415 523 8886**:
```
join example-word
```
(use your actual keyword from Twilio dashboard)
You'll get a confirmation. Now you can chat with the bot.

For a client demo — ask the prospect to send that same join message before the demo call.

## Step 3: Deploy on Railway (free)
1. Go to **railway.app** → Sign up with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `Products` repo
4. Railway asks which folder → type: `WhatsApp_Webhook`
5. Click **Deploy**
6. Wait ~2 min → you get a URL like: `https://products-production-xxxx.up.railway.app`

## Step 4: Set Environment Variables on Railway
In your Railway project → **Variables** tab → add these:

| Variable | Value |
|---|---|
| `GEMINI_API_KEY` | Your Gemini API key (AIzaSy...) |
| `BUSINESS_NAME` | e.g. Sharma Restaurant |
| `BUSINESS_TYPE` | e.g. Restaurant |
| `BUSINESS_ADDRESS` | e.g. Civil Lines, Kanpur |
| `BUSINESS_TIMINGS` | e.g. Mon–Sat 10am–10pm |
| `BUSINESS_PHONE` | e.g. 9876543210 |
| `BUSINESS_SERVICES` | e.g. Dal Makhani ₹180, Biryani ₹200 |
| `BUSINESS_EXTRA` | e.g. UPI accepted, home delivery |

Railway redeploys automatically after you save variables.

## Step 5: Connect Twilio to Railway
1. Twilio Console → **Messaging** → **Try it out** → **WhatsApp**
2. Scroll to **Sandbox Settings**
3. In **"When a message comes in"** field, paste:
```
https://your-railway-url.up.railway.app/webhook
```
4. Method: **HTTP POST**
5. Click **Save**

## Step 6: Test It
WhatsApp the sandbox number → type anything → you get a real AI reply!

---

## For Each New Client
Just change the environment variables in Railway to that client's business info.
Redeploys in 30 seconds. No code changes needed.

---

## The Demo Flow with a Prospect
1. Before the call: ask them to WhatsApp `join [keyword]` to +1 415 523 8886
2. On the call: "Now send any message you'd normally get from a customer"
3. They see the AI reply instantly in their actual WhatsApp
4. That's the close.
