# Product 4 — Competitor Price Monitor
*Last updated: 2026-06-09*

## What It Does
A tool that automatically monitors competitor product prices on Amazon/Flipkart/Meesho daily and sends WhatsApp/email alerts when:
- A competitor drops their price
- A competitor goes out of stock (opportunity to capture sales)
- Your product's rank changes
- A new competitor appears for your keyword

## Why Kanpur Specifically
Kanpur is India's leather capital with 300+ businesses selling on Amazon/Flipkart.
Leather goods, shoes, bags, belts, wallets, industrial gloves — all highly competitive on these platforms.
Every seller is fighting for the Buy Box. Price monitoring = direct revenue impact.

## Tech Stack
- **Python** scraper (BeautifulSoup + requests / Selenium)
- **Deployed on Railway/Render** with daily cron job
- **WhatsApp alert** via Twilio or plain email via SMTP
- **Streamlit dashboard** to view price history
- Claude builds all of it

## Pricing
- One-time setup: **₹10,000–₹15,000**
- Monthly maintenance (keeps running): **₹1,000/month**

## Delivery Time
2–3 days

## Kanpur Target Customers

### Leather Goods Sellers (PRIMARY)
Search Amazon.in for: "leather wallet Kanpur", "leather bag India", "industrial gloves Kanpur"
→ Each seller is a potential client
- Rukh Enterprises (IndiaMART listed leather seller)
- Kanpur Leather Craft (has Amazon storefront)
- 100s more on TradeIndia/IndiaMART

### Textile & Garment Sellers
Selling on Meesho, Flipkart, Amazon — highly price-sensitive
- Search "textile wholesale Kanpur", "cotton fabric seller Kanpur"

### How to Find Them
1. Search "leather wallet" on Amazon.in
2. Click seller name → "See all products from this seller"
3. Check if they're based in Kanpur / UP (many are)
4. Contact via their seller email or find on IndiaMART

## Dashboard Features
| Feature | Details |
|---|---|
| Product Tracker | Add any Amazon/Flipkart URL to monitor |
| Price History Chart | 30-day price trend per product |
| Competitor Comparison | Your price vs top 5 competitors |
| Stock Alerts | Notify when competitor goes out of stock |
| WhatsApp Alert | Instant message when price drops >5% |
| Rank Tracker | Amazon search rank over time |

## Edge Cases
- Amazon changes HTML structure (scraper breaks) → Claude rebuilds in 30 min
- Client sells on Meesho/Myntra too → extend scraper to those platforms (+₹2,000)
- Client wants to track 50+ products → batch processing included
- Anti-scraping blocks → rotate user-agents + add delays (built in)

## Sales Pitch
```
Namaste Sir! 🙏

Amazon pe sell karte ho? Ek sawaal:

Kya aapko pata chalta hai jab competitor apna price 
galat din kam kar deta hai aur aapki sales girne lagti hain?

Main ek tool banata hoon jo:
• Roz subah competitor prices check karta hai
• Jab koi price girata hai → aapko WhatsApp pe alert aata hai
• Competitor out of stock hua → aapko pata chala, price badhao

Kanpur ke leather/textile sellers ke liye specially useful.
IIT Kanpur student. One-time: ₹10,000.
Demo? 😊
```
