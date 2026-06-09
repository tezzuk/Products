# Product 1 — AI WhatsApp Business Bot
*Last updated: 2026-06-09*

## What It Does
A 24/7 AI assistant that handles incoming WhatsApp messages for a business.
- Answers FAQs (timings, menu, prices, services)
- Books appointments or takes orders
- When it doesn't know → collects name + number, tells user "owner will call you back"
- Business owner gets a WhatsApp notification with the lead's details

## Tech Stack
- **Twilio WhatsApp Sandbox** (free) or Twilio number (paid, ~₹800/month)
- **Groq API** (free tier, very fast) or Gemini API (free tier) — AI brain
- **Flask** webhook deployed on **Railway** or **Render** (free tier)
- **Python** backend — Claude builds all of it

## Pricing
- One-time setup: **₹8,000–₹12,000**
- Optional hosting fee: **₹500/month** (if client wants you to maintain it)

## Delivery Time
2–3 days per client

## Kanpur Target Customers

### Tier 1 — Restaurants & Cafes (Civil Lines / Naveen Market)
High WhatsApp volume, need to answer menu/order/timing questions constantly
- Three Olives, Civil Lines
- Loco Restaurant, Civil Lines
- Cockpit Cafe, Naveen Market
- Barbeque Nation, Kanpur
- Jo Hukum, Civil Lines
- SD Chaat, Naveen Market
- All small dhabas and fast food joints in Naveen Market lanes

### Tier 2 — Dental & Private Clinics (Swaroop Nagar / Arya Nagar)
34 private hospitals + hundreds of small clinics. Need appointment booking badly.
- Dr. Tandon Dental Clinic, Swaroop Nagar
- Smile Ray Super-Speciality Dental Clinic, Swaroop Nagar
- All private general physician clinics listed on Practo Kanpur
- Homeopathy/Ayurveda clinics (very common in Kanpur)

### Tier 3 — Coaching Centers (already have their numbers)
Upsell from the coaching center list already built.
- Answer fee queries, batch timing, admission questions
- Parents message coaching centers ALL day

## How to Find More Targets
1. Search "restaurant Kanpur" on Google Maps → click each → check if they have WhatsApp
2. Practo.com/kanpur → filter by clinics → find contact numbers
3. Zomato Kanpur → find restaurants not on Swiggy/Zomato (they rely purely on WhatsApp)

## Edge Cases Handled
| Situation | Bot Response |
|---|---|
| Unknown question | "Let me get someone to help — can I get your name and number?" |
| Out of hours | "We're closed right now. Your query is noted — we'll call you tomorrow morning." |
| Multiple languages | Respond in same language as customer (Hindi/English) |
| Abusive messages | Politely ignore and offer to connect to owner |

## What Aayushman Does Per Client
1. Get client's FAQ list (5 min conversation)
2. Paste into Claude → generates bot config
3. Deploy on Railway (15 min)
4. Connect Twilio to client's WhatsApp number (30 min with client on call)
5. Done

## Sales Pitch (WhatsApp message to target businesses)
```
Namaste Sir/Ma'am 🙏

Kya aapko roz WhatsApp pe yahi sawaal aate hain:
"Timings kya hain?" / "Menu bhejo" / "Appointment available hai?"

Main ek AI WhatsApp assistant banata hoon jo yeh sab 
khud handle karta hai — 24/7, bina aapke involvement ke.

Main IIT Kanpur ka student hoon.
One-time setup: ₹8,000
Free demo available.

Interested? 😊
```
