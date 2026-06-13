# BI Dashboard — Business Plan & Strategy

## The Product
A retail analytics dashboard for small shop owners who can't afford or don't need a data analyst.
Deployed on Streamlit Cloud. Clients log in with a password, upload their CSV sales data, and get
instant insights — charts, ML forecasts, stock recommendations, and a plain-English PDF report.

**Positioning:** "Main aapke pichhle saal ka data dekh ke batata hoon — kaunsa din sabse zyada
bikta hai, kaunsa item band karna chahiye, agla mahina kaisa jayega."

Don't say "dashboard" or "SaaS." Sell the answer, not the software.

---

## Pricing (Realistic for Kanpur / Tier-2 India)

| Tier | Price | What's included |
|------|-------|-----------------|
| Basic | ₹499/month | Dashboard, charts, top products, best/worst days |
| Standard | ₹999/month | Basic + ML revenue forecast, PDF report, stock reorder |
| Premium | ₹1,999/month | Everything + Google Sheets sync, WhatsApp daily digest, compare periods |
| One-time Health Report | ₹999 flat | Client sends data → you run it → send PDF report. No login needed. |
| Setup / Onboarding | ₹500 one-time | Column mapping help, first session walkthrough |

**Annual discount:** 2 months free (pay 10 months, get 12). Gets upfront cash + locks client in.

**Why low pricing works better at this stage:**
- ₹499 is cheaper than their monthly tea bill. Zero friction to say yes.
- 100 clients × ₹499 = ₹49,900/month recurring.
- Better than hunting 10 premium clients that take weeks to close.
- Lock volume first → raise price for new signups later.

---

## Fastest Path to ₹50,000 (2 Weeks)

**The "Health Report" hustle:**
1. Walk into shops on Birhana Road, Naveen Market, Mall Road
2. Show them a printed sample report (from demo data)
3. Offer: "₹999 — give me your billing data, I'll give you a full analysis report in 24 hours"
4. Do 20–30 of these = ₹20,000–30,000 in one-time fees
5. 30–40% will convert to monthly ₹499/₹999 plan
6. 20 one-time + 10 monthly clients = ₹20,000 + ₹10,000 MRR in 2 weeks

**Target list already built:** `Kanpur_Retail_Outreach_List.xlsx` — 47 businesses across malls,
clothing, electronics, jewellery, grocery, home decor.

---

## Features by Tier (Current)

### Basic (₹499)
- Dark-theme dashboard
- Total revenue, transactions, avg bill, repeat rate
- Best/worst day of week
- Top selling products
- Daily revenue trend chart
- Revenue by category (donut chart)
- Weekly revenue (last 12 weeks)
- Monthly performance comparison

### Standard (₹999)
- Everything in Basic
- Compare two periods side-by-side
- Staff scheduling recommendation (by day + hour)
- Stock reorder recommendations (fast vs slow movers)
- Payment method split analysis
- Top 5 loyal customers

### Premium (₹1,999)
- Everything in Standard
- ML Revenue Forecast (next 7 & 30 days with confidence range)
- Product Demand Prediction (day-by-day for next 7 days)
- Anomaly Detection (unusual revenue spikes/drops)
- Business Summary Report (plain-English, 8 paragraphs)
- Download as PDF
- Google Sheets auto-sync (client's live data, no CSV upload needed)
- Multi-language: English + Hinglish

---

## Features to Build Next (Revenue Unlocks)

### WhatsApp Daily Digest (add ₹300/month or include in Premium)
Every morning at 9am, client gets:
"Yesterday: Rs 12,400 from 47 bills. Top item: Shirt. Tuesday avg is Rs 15,000 — you were 17% below. Watch out."
**Why:** Most shop owners never open a dashboard. They check WhatsApp 50 times a day.
**How:** Already have WhatsApp bot infrastructure (Product 1). Wire them together.

### Multi-Branch Dashboard (₹1,500/month per extra branch)
One login → dropdown to switch between branches → compare branch performance.
Targets shop owners with 2–3 locations. High willingness to pay.

### GST-Ready Monthly Export (add ₹200/month or include in Standard+)
One-click monthly sales summary formatted for their CA.
Small shops pay CAs ₹2,000–5,000/month just to organize this data. You save them that.

### Custom WhatsApp Alerts (include in Premium)
Client sets thresholds: "If Wednesday revenue < Rs 8,000, WhatsApp me."
Zero ongoing effort after setup. Feels like a premium concierge service.

### Competitor Price Monitoring Bundle (add ₹999/month)
Already built as Product 4. Bundle: "We also track competitor prices so you know when to adjust."
Upsell existing clients, minimal extra work.

### Branded PDF Reports (include in Premium)
Client's shop name + logo on every report page.
They share it with their CA, business partner, investor. Perceived value 10x the effort.

---

## Go-To-Market

### Primary: In-Person Kanpur Outreach
1. Print 2–3 sample reports (use demo data, look polished)
2. Walk into target shops from the outreach Excel sheet
3. Script: "Aapka data dekh ke ek report banata hoon — kaunsa mahina best tha, kya banana chahiye
   agle mahine. ₹999 ka kaam hai, 24 ghante mein deta hoon."
4. Collect WhatsApp number → send sample report on WhatsApp first as hook
5. Close on ₹999 one-time → upsell monthly within a week

### Secondary: WhatsApp Broadcast
Send to existing contacts + shopkeeper WhatsApp groups:
"Kya aap jaanna chahte hain ki aapki dukaan mein sabse zyada sale kab hoti hai?
₹499/mahine mein poora analysis. Pehla mahina free demo available hai."

### Tertiary: Local Facebook/Instagram
Target Kanpur businessmen groups. Post a screenshot of the dashboard with:
"Ye aapki dukaan ka data dekh sakta hai. DM for free demo."

---

## Client Onboarding Workflow

1. Client agrees → collect WhatsApp + email
2. Add them to CLIENTS dict in app.py (takes 2 minutes):
   ```python
   "their_password": {
       "name": "Their Shop Name",
       "tier": "standard",
       "lang": "English",
       "alert_discount": 30,
       # optional: "sheets_url": "their google sheets link"
   }
   ```
3. Push to GitHub → Streamlit auto-deploys in 2–3 min
4. Send them their password on WhatsApp
5. 10-minute video call to help with column mapping (first time only)
6. Done. Recurring revenue starts.

---

## Revenue Projections

| Month | Clients | MRR | One-time | Total |
|-------|---------|-----|----------|-------|
| Month 1 | 20 | ₹10,000 | ₹20,000 | ₹30,000 |
| Month 2 | 40 | ₹22,000 | ₹10,000 | ₹32,000 |
| Month 3 | 65 | ₹38,000 | ₹8,000 | ₹46,000 |
| Month 6 | 120 | ₹72,000 | ₹5,000 | ₹77,000 |

*Assumes avg ₹650/client blended (mix of Basic/Standard/Premium)*

---

## Competitive Moat

- **Language:** Hinglish UI and reports. No English-only SaaS does this.
- **Price:** 10x cheaper than Zoho Analytics or Power BI for SMBs.
- **Setup friction:** Zero IT knowledge needed. Upload CSV → done.
- **Personal service:** You add them to the system yourself. Feels like a managed service, not DIY software.
- **WhatsApp-first:** Every touchpoint on WhatsApp. No app to download, no new habit to form.

---

## Tech Stack
- **Frontend:** Streamlit (Python)
- **ML:** scikit-learn (LinearRegression + day-of-week dummies)
- **PDF:** FPDF2
- **Hosting:** Streamlit Cloud (free tier — upgrade when >5 concurrent users)
- **Code:** GitHub → tezzuk/Products → Product2_BI_Dashboard/
- **Data sync option:** Google Sheets CSV export URL

---

*Last updated: June 2026*
