# Deploy — Competitor Price Monitor
*Demo deploys in ~10 minutes. Free on Streamlit Cloud.*

---

## Step 1: Put Code on GitHub
1. github.com → **New Repository** → name: `price-monitor-demo`
2. Upload:
   - `app.py`
   - `requirements.txt`
3. Commit changes

---

## Step 2: Deploy on Streamlit Cloud
1. **share.streamlit.io** → New app
2. Repo: `price-monitor-demo` | Main file: `app.py`
3. Deploy → live in ~2 min

---

## Demo Walkthrough (what to show clients)
1. "Today's Alerts" — price drops visible at the top, immediate impact
2. Price history chart — 30 days of competitor movement
3. Out-of-stock tracker — "This is an opportunity you'd normally miss"
4. Expand "Sample WhatsApp Alert" — show what they'd get every morning
5. Close: "This whole thing runs automatically. You just read your morning message."

---

## For a Paying Client — Real Scraping Setup (ask me when you have one)

The demo uses sample data. The real product adds Python scrapers:

1. **Client gives you their product URLs** (Amazon/Flipkart)
2. We build a scraper with BeautifulSoup + requests (Claude writes it)
3. Deploy on **Railway** with a daily cron job (runs at 7am every day)
4. WhatsApp alert via Twilio (or email via Gmail SMTP — free)
5. Dashboard shows real scraped data

Time to build real scraper per client: ~2 hours.
Railway free tier: enough for 2-3 clients.

**Important:** Amazon occasionally blocks scrapers. When this happens, Claude rebuilds the scraper in ~30 min. Include this in your service agreement as "maintenance."

---

## Monthly Maintenance Plan (recurring income)

Offer clients: ₹1,000/month
- You check it's running every week (2 min)
- Fix if scraper breaks (rare, Claude fixes it fast)
- 5 clients = ₹5,000/month passive income

**Always offer this. Most will say yes.**
