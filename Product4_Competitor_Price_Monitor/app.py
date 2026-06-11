"""
Competitor Price Monitor — Demo App
Shows leather/textile Amazon sellers how their competitors' prices move.
Demo uses realistic sample data. Real product adds live scraping.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta, datetime
import random
import json

st.set_page_config(page_title="Price Monitor", page_icon="🔍", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #f8f9fa; }
.alert-card {
    background: white;
    border-left: 4px solid #e63946;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.alert-card.green { border-left-color: #2d6a4f; }
.alert-card.yellow { border-left-color: #f4a261; }
.price-down { color: #e63946; font-weight: bold; }
.price-up { color: #2d6a4f; font-weight: bold; }
.price-same { color: #888; }
.product-card {
    background: white;
    border-radius: 10px;
    padding: 14px;
    margin: 8px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# ── SAMPLE DATA ──
SAMPLE_PRODUCTS = [
    {
        "id": 1,
        "name": "Leather Wallet — Slim Bifold",
        "your_price": 449,
        "category": "Wallet",
        "url": "https://amazon.in/dp/SAMPLE1",
        "competitors": [
            {"name": "LeatherKing", "prices": []},
            {"name": "KanpurLeather", "prices": []},
            {"name": "PremiumWallets", "prices": []},
        ]
    },
    {
        "id": 2,
        "name": "Genuine Leather Belt — 1.5\"",
        "your_price": 349,
        "category": "Belt",
        "url": "https://amazon.in/dp/SAMPLE2",
        "competitors": [
            {"name": "BeltZone", "prices": []},
            {"name": "ClassicLeather", "prices": []},
            {"name": "FashionBelts", "prices": []},
        ]
    },
    {
        "id": 3,
        "name": "Leather Handbag — Medium",
        "your_price": 1199,
        "category": "Handbag",
        "url": "https://amazon.in/dp/SAMPLE3",
        "competitors": [
            {"name": "BagEmpire", "prices": []},
            {"name": "LuxuryBags", "prices": []},
            {"name": "KanpurCraft", "prices": []},
        ]
    },
    {
        "id": 4,
        "name": "Industrial Safety Gloves — Pair",
        "your_price": 285,
        "category": "Gloves",
        "url": "https://amazon.in/dp/SAMPLE4",
        "competitors": [
            {"name": "SafetyFirst", "prices": []},
            {"name": "IndustrialPro", "prices": []},
            {"name": "GloveMaster", "prices": []},
        ]
    },
]

@st.cache_data
def generate_price_history():
    random.seed(99)
    today = date.today()
    history = {}

    for prod in SAMPLE_PRODUCTS:
        history[prod["id"]] = {}
        for comp in prod["competitors"]:
            base = prod["your_price"] * random.uniform(0.85, 1.25)
            prices = []
            current = base
            for days_ago in range(30, -1, -1):
                d = today - timedelta(days=days_ago)
                change = random.uniform(-0.04, 0.04)
                if random.random() < 0.15:  # big move occasionally
                    change = random.uniform(-0.12, 0.12)
                current = max(current * (1 + change), 50)
                prices.append({"date": str(d), "price": round(current)})
            history[prod["id"]][comp["name"]] = prices

    return history


def get_latest_price(history, prod_id, comp_name):
    prices = history.get(prod_id, {}).get(comp_name, [])
    return prices[-1]["price"] if prices else 0


def get_price_change(history, prod_id, comp_name):
    prices = history.get(prod_id, {}).get(comp_name, [])
    if len(prices) < 2:
        return 0
    return prices[-1]["price"] - prices[-2]["price"]


price_history = generate_price_history()

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## 🔍 Price Monitor")
    st.markdown("---")
    seller_name = st.text_input("Your Business Name", value="My Leather Store")
    alert_threshold = st.slider("Alert me when competitor price drops by",
                                 min_value=2, max_value=25, value=5,
                                 format="%d%%")
    st.markdown("---")
    st.markdown("**Track New Product**")
    new_url = st.text_input("Paste Amazon/Flipkart URL", placeholder="https://amazon.in/dp/...")
    if st.button("+ Add to Tracker"):
        if new_url:
            st.success("Product added! (Demo: scraping simulation)")
        else:
            st.warning("Please enter a URL first.")

    st.markdown("---")
    last_updated = datetime.now().strftime("%d %b %Y, %I:%M %p")
    st.caption(f"🕐 Last checked: {last_updated}")
    if st.button("🔄 Refresh Prices"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("💡 *Demo mode: using realistic sample data. Real product scrapes Amazon/Flipkart daily.*")


# ── HEADER ──
st.markdown(f"## 🔍 {seller_name} — Competitor Price Monitor")
st.caption(f"Tracking {len(SAMPLE_PRODUCTS)} products | {len(SAMPLE_PRODUCTS)*3} competitors | Updated daily at 7am")

# ── ALERTS ──
st.markdown("### 🚨 Today's Alerts")
alerts = []
for prod in SAMPLE_PRODUCTS:
    for comp in prod["competitors"]:
        latest = get_latest_price(price_history, prod["id"], comp["name"])
        change = get_price_change(price_history, prod["id"], comp["name"])
        pct = (change / (latest - change) * 100) if (latest - change) > 0 else 0
        if pct <= -alert_threshold:
            alerts.append({
                "type": "danger",
                "msg": f"⚠️ **{comp['name']}** dropped **{prod['name']}** by ₹{abs(change):.0f} ({abs(pct):.1f}%) → now ₹{latest}",
                "prod": prod["name"],
                "your_price": prod["your_price"]
            })
        elif pct >= alert_threshold:
            alerts.append({
                "type": "good",
                "msg": f"✅ **{comp['name']}** raised **{prod['name']}** by ₹{change:.0f} ({pct:.1f}%) → now ₹{latest}"
            })

if alerts:
    for a in alerts[:6]:
        color = "green" if a["type"] == "good" else ""
        st.markdown(f'<div class="alert-card {color}">{a["msg"]}</div>', unsafe_allow_html=True)
    if alerts[0]["type"] == "danger":
        st.info(f"💡 **Tip:** {alerts[0]['prod']} — your price is ₹{alerts[0]['your_price']}. Consider a ₹10–20 reduction to stay competitive.")
else:
    st.success("✅ No major price movements today. Your prices are competitive!")

st.markdown("---")

# ── PRODUCT OVERVIEW TABLE ──
st.markdown("### 📊 Price Comparison — All Products")

table_rows = []
for prod in SAMPLE_PRODUCTS:
    comp_prices = []
    for comp in prod["competitors"]:
        p = get_latest_price(price_history, prod["id"], comp["name"])
        comp_prices.append(p)
    min_comp = min(comp_prices) if comp_prices else 0
    max_comp = max(comp_prices) if comp_prices else 0
    avg_comp = sum(comp_prices) / len(comp_prices) if comp_prices else 0
    your = prod["your_price"]
    position = "✅ Competitive" if your <= avg_comp else ("⚠️ High" if your > min_comp * 1.1 else "🏆 Cheapest")

    table_rows.append({
        "Product": prod["name"],
        "Your Price": f"₹{your}",
        "Cheapest Comp.": f"₹{min_comp:.0f}",
        "Avg Comp.": f"₹{avg_comp:.0f}",
        "Most Expensive": f"₹{max_comp:.0f}",
        "Position": position,
    })

df_table = pd.DataFrame(table_rows)
st.dataframe(df_table, use_container_width=True, hide_index=True)

st.markdown("---")

# ── PRICE HISTORY CHARTS ──
st.markdown("### 📈 Price History — 30 Days")
selected_product = st.selectbox("Select Product",
    options=[p["name"] for p in SAMPLE_PRODUCTS])

prod_obj = next(p for p in SAMPLE_PRODUCTS if p["name"] == selected_product)

fig = go.Figure()

# Your price line (flat)
dates_all = [(date.today() - timedelta(days=i)) for i in range(30, -1, -1)]
fig.add_trace(go.Scatter(
    x=dates_all,
    y=[prod_obj["your_price"]] * 31,
    name="YOUR PRICE",
    line=dict(color="#4361ee", width=3, dash="dash"),
    mode="lines"
))

# Competitor lines
colors_list = ["#e63946", "#2a9d8f", "#f4a261", "#9d4edd"]
for i, comp in enumerate(prod_obj["competitors"]):
    hist = price_history[prod_obj["id"]][comp["name"]]
    dates = [h["date"] for h in hist]
    prices = [h["price"] for h in hist]
    fig.add_trace(go.Scatter(
        x=dates, y=prices,
        name=comp["name"],
        line=dict(color=colors_list[i % len(colors_list)], width=2),
        mode="lines+markers",
        marker=dict(size=4)
    ))

fig.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=0, r=0, t=20, b=0),
    height=320,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    yaxis=dict(title="Price (₹)", gridcolor="#f0f0f0"),
    xaxis=dict(gridcolor="#f0f0f0"),
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

# ── OUT OF STOCK TRACKER ──
st.markdown("---")
st.markdown("### 🔴 Out-of-Stock Tracker")
st.caption("When a competitor goes out of stock, that's your chance to raise prices or run promotions.")

oos_data = {
    "LeatherKing": {"product": "Leather Wallet — Slim Bifold", "since": "2 days ago", "status": "Out of Stock"},
    "BagEmpire": {"product": "Leather Handbag — Medium", "since": "5 days ago", "status": "Out of Stock"},
}

oos_rows = [{"Competitor": k, "Product": v["product"], "Status": v["status"], "Since": v["since"]}
            for k, v in oos_data.items()]
if oos_rows:
    st.dataframe(pd.DataFrame(oos_rows), use_container_width=True, hide_index=True)
    st.warning("💡 **Opportunity:** LeatherKing is out of stock on Slim Bifold Wallet. You can increase your price by ₹30–50 this week without losing sales.")
else:
    st.success("All competitors currently in stock.")

# ── WhatsApp Alert Preview ──
with st.expander("📱 Sample WhatsApp Alert (what you'd receive daily)"):
    st.code("""
🔔 PRICE ALERT — My Leather Store

⚠️ LeatherKing dropped Leather Wallet price by ₹45 (10.2%)
   Their price: ₹404 | Your price: ₹449

✅ BagEmpire raised Handbag price by ₹80 (6.7%)
   Their price: ₹1,280 | Your price: ₹1,199 ← You're now cheapest!

🔴 IndustrialPro out of stock on Safety Gloves
   Opportunity: raise your price by ₹20

— Sent by Price Monitor Bot at 7:00 AM
""", language=None)
