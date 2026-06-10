import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import random

st.set_page_config(page_title="Retail Analytics Dashboard", page_icon="📊", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #e6edf3; }
[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
[data-testid="stSidebar"] * { color: #e6edf3 !important; }
[data-testid="metric-container"] {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 12px; padding: 16px !important;
}
[data-testid="stMetricValue"] { color: #58a6ff !important; font-size: 28px !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; }
h1, h2, h3, h4 { color: #e6edf3 !important; }
hr { border-color: #30363d !important; }
.summary-box {
    background: linear-gradient(135deg, #1a2744, #161b22);
    border: 1px solid #58a6ff;
    border-radius: 12px; padding: 20px 24px; margin: 12px 0;
    font-size: 16px; line-height: 1.8; color: #e6edf3;
}
.summary-title { color: #58a6ff; font-size: 13px; font-weight: 700; letter-spacing: 1px; margin-bottom: 10px; text-transform: uppercase; }
.alert-box {
    border-radius: 8px; padding: 10px 14px; margin: 5px 0;
    font-size: 14px; display: flex; align-items: flex-start; gap: 8px;
}
.alert-red { background: #2d0f0f; border-left: 4px solid #f85149; color: #ffa0a0; }
.alert-yellow { background: #2d2000; border-left: 4px solid #ffa657; color: #ffd9a0; }
.alert-green { background: #0f2d1a; border-left: 4px solid #3fb950; color: #a0ffc0; }
.insight-box { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 14px 18px; margin: 6px 0; }
.insight-title { color: #58a6ff; font-size: 13px; font-weight: 600; margin-bottom: 4px; }
.insight-val { color: #e6edf3; font-size: 22px; font-weight: 700; }
.insight-sub { color: #8b949e; font-size: 12px; margin-top: 2px; }
.badge-green { background: #1a3a2a; color: #3fb950; border-radius: 6px; padding: 2px 8px; font-size: 12px; }
.badge-red { background: #3a1a1a; color: #f85149; border-radius: 6px; padding: 2px 8px; font-size: 12px; }
.month-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.month-table th { background: #21262d; color: #8b949e; padding: 8px 12px; text-align: left; font-weight: 600; }
.month-table td { padding: 8px 12px; border-bottom: 1px solid #21262d; color: #e6edf3; }
.month-table tr:hover td { background: #1f2937; }
.stock-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px 16px; margin: 4px 0; display: flex; justify-content: space-between; align-items: center; }
.stock-name { color: #e6edf3; font-size: 14px; font-weight: 600; }
.stock-vel { color: #ffa657; font-size: 13px; }
.stock-action { background: #1a3a2a; color: #3fb950; border-radius: 6px; padding: 2px 10px; font-size: 12px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

DARK = dict(
    plot_bgcolor="#161b22", paper_bgcolor="#0d1117", font_color="#e6edf3",
    xaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
    yaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
    margin=dict(l=10, r=10, t=30, b=10),
)
DARK_NO_AX = dict(plot_bgcolor="#161b22", paper_bgcolor="#0d1117", font_color="#e6edf3", margin=dict(l=10,r=10,t=30,b=10))
COLORS = ["#58a6ff","#3fb950","#d2a8ff","#ffa657","#f85149","#79c0ff","#56d364","#ff7b72"]


@st.cache_data
def make_sample():
    random.seed(42)
    today = date.today()
    products = [
        ("Men's T-Shirt",599,"Clothing"),("Women's Kurti",799,"Clothing"),("Jeans",1299,"Clothing"),
        ("Sports Shoes",2499,"Footwear"),("Sandals",899,"Footwear"),("Kids Dress",699,"Clothing"),
        ("Saree",1899,"Clothing"),("Jacket",2999,"Clothing"),("Handbag",1499,"Accessories"),
        ("Sunglasses",649,"Accessories"),("Watch",3499,"Accessories"),("Perfume",1199,"Beauty"),
        ("Face Cream",399,"Beauty"),("Lipstick",499,"Beauty"),("Earrings",349,"Accessories"),
        ("Backpack",1099,"Bags"),("Wallet",749,"Bags"),("Cap",299,"Accessories"),
        ("Headphones",1999,"Electronics"),("Phone Cover",249,"Electronics"),
        ("Chocolate Box",599,"Gifts"),("Toy Car",449,"Toys"),
    ]
    custs = ["CUST" + str(i).zfill(4) for i in range(1,151)]
    payments = ["UPI","Cash","Credit Card","Debit Card"]
    pw = [45,20,20,15]
    hrs = list(range(9,22))
    peak = [11,12,13,14,15,16,17,18,19]
    hw = [6 if h in peak else 1 for h in hrs]
    seasonal = {1:0.8,2:0.75,3:0.9,4:0.95,5:0.85,6:0.8,7:0.9,8:0.95,9:0.9,10:1.1,11:1.3,12:1.8}
    rows = []
    for ago in range(365):
        d = today - timedelta(days=ago)
        is_wk = d.weekday() >= 5
        base = random.randint(40,80) if is_wk else random.randint(20,50)
        n = int(base * seasonal[d.month])
        for _ in range(n):
            name,price,cat = random.choice(products)
            qty = random.choices([1,2,3,4], weights=[70,20,7,3])[0]
            disc = random.choices([0,5,10,15,20], weights=[50,20,15,10,5])[0]
            sp = int(price * (1 - disc/100) / 10) * 10
            h = random.choices(hrs, weights=hw, k=1)[0]
            dt = datetime(d.year, d.month, d.day, h, random.randint(0,59))
            rows.append({
                "DateTime": dt, "Date": d, "Hour": h,
                "DayOfWeek": dt.strftime("%A"), "DayNum": dt.weekday(),
                "Product": name, "Category": cat, "Qty": qty,
                "MRP": price, "Discount_Pct": disc, "Selling_Price": sp,
                "Revenue": sp * qty, "Customer": random.choice(custs),
                "Payment": random.choices(payments, weights=pw)[0],
            })
    return pd.DataFrame(rows)


# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## Retail Analytics")
    st.markdown("---")
    shop_name = st.text_input("Shop / Mall Name", value="Sharma Retail Store")
    st.markdown("---")
    st.markdown("**Upload Your Sales Data**")
    st.caption("CSV: DateTime, Product, Category, Qty, Selling_Price, Customer, Payment")
    uploaded = st.file_uploader("", type=["csv","xlsx"])
    st.markdown("---")
    period = st.radio("View Period", ["Last 7 Days","Last 30 Days","Last 90 Days","Full Year"])
    days = {"Last 7 Days":7,"Last 30 Days":30,"Last 90 Days":90,"Full Year":365}[period]
    st.markdown("---")
    lang = st.radio("Summary Language", ["English", "Hinglish"])
    st.markdown("---")
    st.caption("Demo mode — upload CSV to see real numbers.")


# ── LOAD DATA ──
if uploaded:
    try:
        df_raw = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
        for col in df_raw.columns:
            if col.lower() in ["datetime","date","timestamp","time","order_time","created_at"]:
                df_raw["DateTime"] = pd.to_datetime(df_raw[col])
                df_raw["Date"] = df_raw["DateTime"].dt.date
                df_raw["Hour"] = df_raw["DateTime"].dt.hour
                df_raw["DayOfWeek"] = df_raw["DateTime"].dt.strftime("%A")
                df_raw["DayNum"] = df_raw["DateTime"].dt.dayofweek
                break
        if "Revenue" not in df_raw.columns:
            price_col = next((c for c in ["Selling_Price","Price","MRP"] if c in df_raw.columns), None)
            if price_col and "Qty" in df_raw.columns:
                df_raw["Revenue"] = df_raw["Qty"] * df_raw[price_col]
        using_real = True
    except Exception as e:
        st.error("Error loading file: " + str(e))
        df_raw = make_sample()
        using_real = False
else:
    df_raw = make_sample()
    using_real = False

max_date = df_raw["Date"].max()
cutoff = max_date - timedelta(days=days)
prev_cutoff = cutoff - timedelta(days=days)
df = df_raw[df_raw["Date"] >= cutoff].copy()
df_prev = df_raw[(df_raw["Date"] >= prev_cutoff) & (df_raw["Date"] < cutoff)].copy()


# ── HEADER ──
c1, c2 = st.columns([4,1])
with c1:
    st.markdown("# " + shop_name)
    label = "Your real data" if using_real else "Demo - sample retail data"
    st.caption(label + " | " + period + " | Updated: " + datetime.now().strftime("%d %b %Y, %I:%M %p"))
with c2:
    if not using_real:
        st.info("Demo Mode")

st.markdown("---")

# ── CORE NUMBERS ──
total_rev = df["Revenue"].sum()
prev_rev = df_prev["Revenue"].sum()
rev_delta = ((total_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0
total_orders = len(df)
prev_orders = len(df_prev)
ord_delta = ((total_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
avg_order = df["Revenue"].mean() if len(df) > 0 else 0
uniq_cust = df["Customer"].nunique() if "Customer" in df.columns else 0
total_units = int(df["Qty"].sum()) if "Qty" in df.columns else 0

if "Hour" in df.columns and len(df) > 0:
    bh = int(df.groupby("Hour")["Revenue"].sum().idxmax())
    peak_str = str(bh).zfill(2) + ":00-" + str(bh+1).zfill(2) + ":00"
else:
    bh = None
    peak_str = "N/A"

if "DayOfWeek" in df.columns and len(df) > 0:
    best_dow = str(df.groupby("DayOfWeek")["Revenue"].sum().idxmax())
else:
    best_dow = "N/A"

top_product = str(df.groupby("Product")["Revenue"].sum().idxmax()) if len(df) > 0 else "N/A"
daily = df.groupby("Date")["Revenue"].sum().reset_index().sort_values("Date")


# ══════════════════════════════════════════════
# SECTION 1: PLAIN-ENGLISH / HINGLISH SUMMARY
# ══════════════════════════════════════════════
def build_summary(hinglish=False):
    rev_str = "Rs {:,}".format(int(total_rev))
    avg_str = "Rs {:,}".format(int(avg_order))
    trend_word_en = "up" if rev_delta >= 0 else "down"
    trend_word_hi = "zyada" if rev_delta >= 0 else "kam"
    delta_str = str(abs(round(rev_delta, 1))) + "%"

    if not hinglish:
        lines = []
        lines.append("In the last <b>" + str(days) + " days</b>, your shop made <b>" + rev_str + "</b> from <b>" + str(total_orders) + " bills</b>.")
        lines.append("Your average bill value was <b>" + avg_str + "</b>, and <b>" + str(uniq_cust) + " unique customers</b> visited.")
        lines.append("Your best-selling item was <b>" + top_product + "</b>.")
        if bh is not None:
            lines.append("You were busiest between <b>" + peak_str + "</b> — keep extra staff ready during that time.")
        lines.append("Compared to the previous period, revenue is <b>" + trend_word_en + " " + delta_str + "</b>.")
        if rev_delta < -15:
            lines.append("<span style='color:#f85149'>Revenue has dropped significantly — check if any products stopped selling or if footfall reduced.</span>")
        elif rev_delta > 15:
            lines.append("<span style='color:#3fb950'>Great performance! Revenue is growing well.</span>")
        return " ".join(lines)
    else:
        lines = []
        lines.append("Pichhle <b>" + str(days) + " dino mein</b> aapki dukaan ne <b>" + rev_str + "</b> kamaye <b>" + str(total_orders) + " bills</b> se.")
        lines.append("Har bill ka average <b>" + avg_str + "</b> tha aur <b>" + str(uniq_cust) + " alag customers</b> aaye.")
        lines.append("Sabse zyada bikne wala item tha <b>" + top_product + "</b>.")
        if bh is not None:
            lines.append("<b>" + peak_str + "</b> ke beech sabse zyada bheed thi — us waqt extra staff rakhein.")
        lines.append("Pichle period se compare karein toh revenue <b>" + delta_str + " " + trend_word_hi + "</b> hai.")
        if rev_delta < -15:
            lines.append("<span style='color:#f85149'>Revenue bahut gir gayi hai — dekhein kaunsa item bikna band ho gaya ya kam log aa rahe hain.</span>")
        elif rev_delta > 15:
            lines.append("<span style='color:#3fb950'>Bahut achha! Revenue achhi tarah badh rahi hai.</span>")
        return " ".join(lines)

title_label = "TODAY'S BUSINESS SUMMARY" if lang == "English" else "AAJ KA BUSINESS SUMMARY"
st.markdown(
    "<div class='summary-box'><div class='summary-title'>" + title_label + "</div>" +
    build_summary(lang == "Hinglish") + "</div>",
    unsafe_allow_html=True
)

st.markdown("---")


# ══════════════════════════════════════════════
# SECTION 2: SMART ALERTS
# ══════════════════════════════════════════════
st.markdown("#### Alerts & Warnings")

alerts = []

# Alert 1: Smart slow-mover — compare each product's last-7-day velocity to its own 30-day average
if len(df_raw) > 0 and "Product" in df_raw.columns:
    ref_cutoff_30 = max_date - timedelta(days=30)
    ref_cutoff_7  = max_date - timedelta(days=7)
    df_30 = df_raw[df_raw["Date"] >= ref_cutoff_30]
    df_7  = df_raw[df_raw["Date"] >= ref_cutoff_7]

    vel_30 = df_30.groupby("Product")["Qty"].sum() / 30.0
    vel_7  = df_7.groupby("Product")["Qty"].sum() / 7.0

    common = vel_30.index.intersection(vel_7.index)
    slow_products = []
    for prod in common:
        avg_vel = vel_30[prod]
        recent_vel = vel_7[prod]
        if avg_vel > 0.1 and recent_vel < avg_vel * 0.5:
            drop_pct = int((1 - recent_vel / avg_vel) * 100)
            slow_products.append((prod, drop_pct))
    slow_products.sort(key=lambda x: -x[1])
    for prod, drop in slow_products[:3]:
        msg = "<b>" + prod + "</b> — sales dropped <b>" + str(drop) + "%</b> this week vs its 30-day average."
        if lang == "Hinglish":
            msg = "<b>" + prod + "</b> ki bikri is hafte <b>" + str(drop) + "%</b> giri hai — dhyan dein."
        alerts.append(("red", msg))

# Alert 2: Products that have not sold at all in last 7 days but sold before
if len(df_raw) > 0:
    all_prods = set(df_raw["Product"].unique())
    recent_prods = set(df_7["Product"].unique()) if len(df_7) > 0 else set()
    dead_prods = all_prods - recent_prods
    if dead_prods:
        dead_list = ", ".join(list(dead_prods)[:3])
        msg = "No sales in last 7 days: <b>" + dead_list + "</b>. Consider discounting or removing from shelf."
        if lang == "Hinglish":
            msg = "Yeh items pichhle 7 din mein bilkul nahi bike: <b>" + dead_list + "</b>. Discount dein ya shelf se hatayein."
        alerts.append(("red", msg))

# Alert 3: Revenue dip on specific days compared to that day's own average
if "DayOfWeek" in df.columns and len(df) >= 14:
    day_rev = df.groupby(["Date","DayOfWeek"])["Revenue"].sum().reset_index()
    dow_avg = day_rev.groupby("DayOfWeek")["Revenue"].mean()
    recent_days = day_rev.sort_values("Date").tail(7)
    for _, row in recent_days.iterrows():
        dow = row["DayOfWeek"]
        if dow in dow_avg.index and dow_avg[dow] > 0:
            drop = (dow_avg[dow] - row["Revenue"]) / dow_avg[dow] * 100
            if drop > 40:
                msg = "Last <b>" + dow + "</b> revenue was <b>" + str(int(drop)) + "%</b> below your usual " + dow + " average."
                if lang == "Hinglish":
                    msg = "Pichhle <b>" + dow + "</b> ki kamai <b>" + str(int(drop)) + "%</b> kam thi aapke normal " + dow + " se."
                alerts.append(("yellow", msg))
                break

# Alert 4: Discount overuse
disc_col = next((c for c in ["Discount_Pct","Discount","discount_pct"] if c in df.columns), None)
if disc_col and len(df) > 0:
    disc_bills = (df[disc_col] > 0).sum()
    disc_pct = disc_bills / len(df) * 100
    if disc_pct > 35:
        msg = "<b>" + str(int(disc_pct)) + "%</b> of your bills had a discount — this is reducing your profit margin. Review your discount policy."
        if lang == "Hinglish":
            msg = "Aapke <b>" + str(int(disc_pct)) + "% bills</b> par discount diya gaya — isse profit kam ho raha hai. Discount policy check karein."
        alerts.append(("yellow", msg))

# Alert 5: Revenue growing — positive alert
if rev_delta > 20:
    msg = "Revenue is up <b>" + str(round(rev_delta,1)) + "%</b> vs the previous period. Stock up on fast-moving items!"
    if lang == "Hinglish":
        msg = "Revenue <b>" + str(round(rev_delta,1)) + "% badhi</b> hai pichle period se. Jo items zyada bik rahe hain unka stock badhayen!"
    alerts.append(("green", msg))

if not alerts:
    no_alert = "No issues found. Business is running smoothly!" if lang == "English" else "Koi problem nahi mili. Business theek chal raha hai!"
    alerts.append(("green", no_alert))

for atype, amsg in alerts:
    st.markdown("<div class='alert-box alert-" + atype + "'>" + amsg + "</div>", unsafe_allow_html=True)

st.markdown("---")


# ── KPI METRICS ──
m1,m2,m3,m4,m5,m6 = st.columns(6)
with m1:
    st.metric("Total Revenue", "Rs {:,}".format(int(total_rev)), delta=("+" if rev_delta>=0 else "")+str(round(rev_delta,1))+"% vs prev")
with m2:
    st.metric("Transactions", "{:,}".format(total_orders), delta=("+" if ord_delta>=0 else "")+str(round(ord_delta,1))+"% vs prev")
with m3:
    st.metric("Avg Bill Value", "Rs {:,}".format(int(avg_order)))
with m4:
    st.metric("Units Sold", "{:,}".format(total_units))
with m5:
    st.metric("Peak Hour", peak_str)
with m6:
    st.metric("Best Day", best_dow)

st.markdown("---")


# ── REVENUE TREND + CATEGORY ──
col_trend, col_pie = st.columns([3,2])
with col_trend:
    st.markdown("#### Daily Revenue Trend")
    daily["MA7"] = daily["Revenue"].rolling(7, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Revenue"], name="Daily Revenue", mode="lines",
        line=dict(color="#58a6ff", width=1.5), fill="tozeroy", fillcolor="rgba(88,166,255,0.08)"))
    fig.add_trace(go.Scatter(x=daily["Date"], y=daily["MA7"], name="7-Day Avg", mode="lines",
        line=dict(color="#ffa657", width=2, dash="dot")))
    fig.update_layout(**DARK, height=280, legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(color="#8b949e")))
    st.plotly_chart(fig, use_container_width=True)

with col_pie:
    st.markdown("#### Revenue by Category")
    if "Category" in df.columns:
        cat_rev = df.groupby("Category")["Revenue"].sum().reset_index()
        fig2 = px.pie(cat_rev, values="Revenue", names="Category", color_discrete_sequence=COLORS, hole=0.45)
    else:
        prod_rev2 = df.groupby("Product")["Revenue"].sum().nlargest(6).reset_index()
        fig2 = px.pie(prod_rev2, values="Revenue", names="Product", color_discrete_sequence=COLORS, hole=0.45)
    fig2.update_layout(**DARK_NO_AX, height=280, showlegend=True, legend=dict(font=dict(color="#8b949e",size=11)))
    fig2.update_traces(textposition="inside", textinfo="percent", textfont=dict(color="white"))
    st.plotly_chart(fig2, use_container_width=True)


# ── HOUR + DAY ──
st.markdown("---")
col_hour, col_dow2 = st.columns(2)
with col_hour:
    st.markdown("#### Footfall by Hour")
    if "Hour" in df.columns:
        hourly = df.groupby("Hour").agg(Transactions=("Revenue","count"), Revenue=("Revenue","sum")).reset_index()
        def fh(h):
            if h == 0: return "12am"
            if h < 12: return str(h)+"am"
            if h == 12: return "12pm"
            return str(h-12)+"pm"
        hourly["Label"] = hourly["Hour"].apply(fh)
        fig3 = px.bar(hourly, x="Label", y="Transactions", color="Revenue",
            color_continuous_scale=["#21262d","#58a6ff"], labels={"Transactions":"No. of Bills","Label":"Hour"})
        fig3.update_layout(**DARK, height=250, coloraxis_showscale=False)
        fig3.update_traces(marker_line_width=0)
        st.plotly_chart(fig3, use_container_width=True)

with col_dow2:
    st.markdown("#### Best Days of the Week")
    if "DayOfWeek" in df.columns:
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow_chart = df.groupby("DayOfWeek")["Revenue"].sum().reindex(day_order).reset_index()
        fig4 = px.bar(dow_chart, x="DayOfWeek", y="Revenue", color="Revenue",
            color_continuous_scale=["#21262d","#3fb950"], labels={"Revenue":"Rs","DayOfWeek":""})
        fig4.update_layout(**DARK, height=250, coloraxis_showscale=False)
        fig4.update_traces(marker_line_width=0)
        st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════
# SECTION 3: STAFF SCHEDULING RECOMMENDATION
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown("#### Staff Scheduling Recommendation")

if "Hour" in df.columns and "DayOfWeek" in df.columns and len(df) > 0:
    hd = df.groupby(["DayOfWeek","Hour"])["Revenue"].agg(["sum","count"]).reset_index()
    hd.columns = ["DayOfWeek","Hour","Revenue","Transactions"]
    hd = hd.sort_values("Transactions", ascending=False).head(5)

    def fh2(h):
        if h == 0: return "12am"
        if h < 12: return str(h)+"am"
        if h == 12: return "12pm"
        return str(h-12)+"pm"

    staff_cols = st.columns(len(hd))
    for i, (_, row) in enumerate(hd.iterrows()):
        with staff_cols[i]:
            day = str(row["DayOfWeek"])[:3]
            hour_label = fh2(int(row["Hour"]))
            txn = int(row["Transactions"])
            if lang == "English":
                sub = str(txn) + " avg bills"
            else:
                sub = str(txn) + " bills average"
            st.markdown(
                "<div class='insight-box' style='text-align:center'>"
                "<div class='insight-title'>Keep Extra Staff</div>"
                "<div class='insight-val'>" + day + " " + hour_label + "</div>"
                "<div class='insight-sub'>" + sub + "</div>"
                "</div>",
                unsafe_allow_html=True
            )
else:
    st.info("Add DateTime column to get staff scheduling recommendations.")


# ══════════════════════════════════════════════
# SECTION 4: STOCK REORDER RECOMMENDATIONS
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown("#### Stock Reorder Recommendations")
st.caption("Based on average daily sales velocity over the selected period")

if "Qty" in df.columns and len(df) > 0:
    vel = df.groupby("Product")["Qty"].sum() / max(days, 1)
    vel = vel.sort_values(ascending=False)
    top_fast = vel.head(6)
    bottom_slow = vel[vel > 0].tail(5)

    col_fast, col_slow2 = st.columns(2)
    with col_fast:
        if lang == "English":
            st.markdown("**Order More (Fast Movers)**")
        else:
            st.markdown("**Yeh Order Karein (Jaldi Bikne Wale)**")
        for prod, v in top_fast.items():
            daily_units = round(v, 1)
            weekly_need = int(v * 7)
            st.markdown(
                "<div class='stock-card'>"
                "<div><div class='stock-name'>" + str(prod) + "</div>"
                "<div class='stock-vel'>" + str(daily_units) + " units/day &rarr; ~" + str(weekly_need) + " needed/week</div></div>"
                "<div class='stock-action'>Reorder</div>"
                "</div>",
                unsafe_allow_html=True
            )

    with col_slow2:
        if lang == "English":
            st.markdown("**Review Stock (Slow Movers)**")
        else:
            st.markdown("**Stock Ghatayen (Dheere Bikne Wale)**")
        for prod, v in bottom_slow.items():
            daily_units = round(v, 2)
            st.markdown(
                "<div class='stock-card'>"
                "<div><div class='stock-name'>" + str(prod) + "</div>"
                "<div class='stock-vel'>" + str(daily_units) + " units/day — consider discount or less stock</div></div>"
                "<div style='background:#2d1a00;color:#ffa657;border-radius:6px;padding:2px 10px;font-size:12px;font-weight:600'>Review</div>"
                "</div>",
                unsafe_allow_html=True
            )


# ── PRODUCT TABLE + SLOW MOVERS ──
st.markdown("---")
col_prod, col_slow3 = st.columns(2)
with col_prod:
    st.markdown("#### Top Selling Products")
    ps = df.groupby("Product").agg(Units=("Qty","sum"),Revenue=("Revenue","sum"),Bills=("Product","count")).sort_values("Revenue",ascending=False).head(15).reset_index()
    ps["Revenue"] = ps["Revenue"].apply(lambda x: "Rs {:,}".format(int(x)))
    st.dataframe(ps, use_container_width=True, hide_index=True, height=300)

with col_slow3:
    st.markdown("#### Bottom Sellers (Consider Action)")
    slow = df.groupby("Product").agg(Units=("Qty","sum"),Revenue=("Revenue","sum")).sort_values("Units").head(10).reset_index()
    slow["Revenue"] = slow["Revenue"].apply(lambda x: "Rs {:,}".format(int(x)))
    st.dataframe(slow, use_container_width=True, hide_index=True, height=300)


# ── PAYMENT SPLIT ──
st.markdown("---")
pay_col2 = next((c for c in ["Payment","Payment_Method","payment"] if c in df.columns), None)
if pay_col2:
    col_pay, col_dummy = st.columns(2)
    with col_pay:
        st.markdown("#### Payment Method Split")
        pay = df.groupby(pay_col2)["Revenue"].sum().reset_index()
        fig6 = px.pie(pay, values="Revenue", names=pay_col2, color_discrete_sequence=COLORS, hole=0.4)
        fig6.update_layout(**DARK_NO_AX, height=250, showlegend=True, legend=dict(font=dict(color="#8b949e")))
        fig6.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(color="white"))
        st.plotly_chart(fig6, use_container_width=True)


# ══════════════════════════════════════════════
# SECTION 5: MONTHLY COMPARISON TABLE
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown("#### Monthly Performance Comparison")

if len(df_raw) > 0:
    dm = df_raw.copy()
    dm["Date"] = pd.to_datetime(dm["Date"])
    dm["Month"] = dm["Date"].dt.to_period("M")
    monthly = dm.groupby("Month").agg(
        Revenue=("Revenue","sum"),
        Bills=("Revenue","count"),
        Avg_Bill=("Revenue","mean"),
    ).reset_index()
    monthly["Month"] = monthly["Month"].astype(str)
    monthly = monthly.sort_values("Month")

    # Color-code revenue column
    max_rev = monthly["Revenue"].max()
    min_rev = monthly["Revenue"].min()

    header = "<tr><th>Month</th><th>Total Revenue</th><th>Avg Bill Value</th><th>No. of Bills</th><th>vs Prev Month</th></tr>"
    rows_html = ""
    prev_rev_m = None
    for _, row in monthly.iterrows():
        rev = int(row["Revenue"])
        avg_b = int(row["Avg_Bill"])
        bills = int(row["Bills"])
        month_str = str(row["Month"])

        # vs prev month
        if prev_rev_m is not None and prev_rev_m > 0:
            chg = (rev - prev_rev_m) / prev_rev_m * 100
            chg_str = ("+" if chg >= 0 else "") + str(round(chg,1)) + "%"
            chg_color = "#3fb950" if chg >= 0 else "#f85149"
            vs_cell = "<span style='color:" + chg_color + ";font-weight:600'>" + chg_str + "</span>"
        else:
            vs_cell = "<span style='color:#8b949e'>—</span>"

        # Revenue bar colour based on value
        intensity = int((rev - min_rev) / max(max_rev - min_rev, 1) * 200)
        bg = "rgba(88," + str(100 + intensity) + ",255,0.08)"

        rows_html += (
            "<tr style='background:" + bg + "'>"
            "<td>" + month_str + "</td>"
            "<td><b>Rs {:,}</b></td>".format(rev) +
            "<td>Rs {:,}</td>".format(avg_b) +
            "<td>" + str(bills) + "</td>"
            "<td>" + vs_cell + "</td>"
            "</tr>"
        )
        prev_rev_m = rev

    st.markdown(
        "<table class='month-table'>" + header + rows_html + "</table>",
        unsafe_allow_html=True
    )
    st.caption("Darker blue = higher revenue month")

# ── WEEKLY BAR ──
st.markdown("---")
st.markdown("#### Weekly Revenue (last 12 weeks)")
dw2 = df_raw.copy()
dw2["Date"] = pd.to_datetime(dw2["Date"])
dw2["Week"] = dw2["Date"].dt.to_period("W").astype(str)
wk = dw2.groupby("Week")["Revenue"].sum().reset_index().tail(12)
fig5 = px.bar(wk, x="Week", y="Revenue", color_discrete_sequence=["#d2a8ff"], labels={"Revenue":"Rs","Week":""})
fig5.update_layout(**DARK, height=220)
fig5.update_traces(marker_line_width=0)
st.plotly_chart(fig5, use_container_width=True)

# ── EXPORT ──
st.markdown("---")
_, col_dl = st.columns([3,1])
with col_dl:
    csv_out = df.to_csv(index=False)
    safe = shop_name.replace(" ","_")
    fname = safe + "_" + str(max_date) + ".csv"
    st.download_button("Export Filtered Data as CSV", data=csv_out, file_name=fname, mime="text/csv")
