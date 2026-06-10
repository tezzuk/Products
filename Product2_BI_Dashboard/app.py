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
.insight-box { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 14px 18px; margin: 6px 0; }
.insight-title { color: #58a6ff; font-size: 13px; font-weight: 600; margin-bottom: 4px; }
.insight-val { color: #e6edf3; font-size: 22px; font-weight: 700; }
.insight-sub { color: #8b949e; font-size: 12px; margin-top: 2px; }
.badge-green { background: #1a3a2a; color: #3fb950; border-radius: 6px; padding: 2px 8px; font-size: 12px; }
.badge-red { background: #3a1a1a; color: #f85149; border-radius: 6px; padding: 2px 8px; font-size: 12px; }
.warn-box { background: #2d2000; border: 1px solid #f85149; border-radius: 8px; padding: 10px 14px; margin: 4px 0; font-size: 13px; color: #ffa657; }
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


# SIDEBAR
with st.sidebar:
    st.markdown("## Retail Analytics")
    st.markdown("---")
    shop_name = st.text_input("Shop / Mall Name", value="Sharma Retail Store")
    st.markdown("---")
    st.markdown("**Upload Your Sales Data**")
    st.caption("CSV columns needed: DateTime, Product, Category, Qty, Selling_Price, Customer, Payment")
    uploaded = st.file_uploader("", type=["csv","xlsx"])
    st.markdown("---")
    period = st.radio("View Period", ["Last 7 Days","Last 30 Days","Last 90 Days","Full Year"])
    days_map = {"Last 7 Days":7,"Last 30 Days":30,"Last 90 Days":90,"Full Year":365}
    days = days_map[period]
    st.markdown("---")
    st.caption("Demo mode — using sample retail data. Upload your CSV to see real numbers.")


# LOAD DATA
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


# HEADER
c1, c2 = st.columns([4,1])
with c1:
    st.markdown("# " + shop_name)
    label = "Your real data" if using_real else "Demo - sample retail data"
    st.caption(label + " | " + period + " | Updated: " + datetime.now().strftime("%d %b %Y, %I:%M %p"))
with c2:
    if not using_real:
        st.info("Demo Mode")

st.markdown("---")

# KPIs
total_rev = df["Revenue"].sum()
prev_rev = df_prev["Revenue"].sum()
rev_delta = ((total_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0
total_orders = len(df)
prev_orders = len(df_prev)
ord_delta = ((total_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
avg_order = df["Revenue"].mean() if len(df) > 0 else 0
uniq_cust = df["Customer"].nunique() if "Customer" in df.columns else 0
total_units = df["Qty"].sum() if "Qty" in df.columns else 0

if "Hour" in df.columns and len(df) > 0:
    bh = int(df.groupby("Hour")["Revenue"].sum().idxmax())
    peak_str = str(bh).zfill(2) + ":00-" + str(bh+1).zfill(2) + ":00"
else:
    peak_str = "N/A"

if "DayOfWeek" in df.columns and len(df) > 0:
    best_dow = str(df.groupby("DayOfWeek")["Revenue"].sum().idxmax())
else:
    best_dow = "N/A"

m1,m2,m3,m4,m5,m6 = st.columns(6)
with m1:
    st.metric("Total Revenue", "Rs {:,}".format(int(total_rev)), delta=("+" if rev_delta>=0 else "")+str(round(rev_delta,1))+"% vs prev")
with m2:
    st.metric("Transactions", "{:,}".format(total_orders), delta=("+" if ord_delta>=0 else "")+str(round(ord_delta,1))+"% vs prev")
with m3:
    st.metric("Avg Bill Value", "Rs {:,}".format(int(avg_order)))
with m4:
    st.metric("Units Sold", "{:,}".format(int(total_units)))
with m5:
    st.metric("Peak Hour", peak_str)
with m6:
    st.metric("Best Day", best_dow)

st.markdown("---")

# ROW 1: Revenue trend + Category split
col_trend, col_pie = st.columns([3,2])
with col_trend:
    st.markdown("#### Daily Revenue Trend")
    daily = df.groupby("Date")["Revenue"].sum().reset_index().sort_values("Date")
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
        prod_rev = df.groupby("Product")["Revenue"].sum().nlargest(6).reset_index()
        fig2 = px.pie(prod_rev, values="Revenue", names="Product", color_discrete_sequence=COLORS, hole=0.45)
    fig2.update_layout(**DARK_NO_AX, height=280, showlegend=True, legend=dict(font=dict(color="#8b949e",size=11)))
    fig2.update_traces(textposition="inside", textinfo="percent", textfont=dict(color="white"))
    st.plotly_chart(fig2, use_container_width=True)


# ROW 2: Hour + Day of week
st.markdown("---")
col_hour, col_dow = st.columns(2)
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

with col_dow:
    st.markdown("#### Best Days of the Week")
    if "DayOfWeek" in df.columns:
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = df.groupby("DayOfWeek")["Revenue"].sum().reindex(day_order).reset_index()
        fig4 = px.bar(dow, x="DayOfWeek", y="Revenue", color="Revenue",
            color_continuous_scale=["#21262d","#3fb950"], labels={"Revenue":"Rs","DayOfWeek":""})
        fig4.update_layout(**DARK, height=250, coloraxis_showscale=False)
        fig4.update_traces(marker_line_width=0)
        st.plotly_chart(fig4, use_container_width=True)


# ROW 3: Product table + Dead stock alert
st.markdown("---")
col_prod, col_slow = st.columns(2)
with col_prod:
    st.markdown("#### Top Selling Products")
    ps = df.groupby("Product").agg(
        Units=("Qty","sum"), Revenue=("Revenue","sum"), Bills=("Product","count")
    ).sort_values("Revenue", ascending=False).head(15).reset_index()
    ps["Revenue"] = ps["Revenue"].apply(lambda x: "Rs {:,}".format(int(x)))
    st.dataframe(ps, use_container_width=True, hide_index=True, height=350)

with col_slow:
    st.markdown("#### Slow Movers (Bottom 10)")
    slow = df.groupby("Product").agg(Units=("Qty","sum"), Revenue=("Revenue","sum")).sort_values("Units").head(10).reset_index()
    slow["Revenue"] = slow["Revenue"].apply(lambda x: "Rs {:,}".format(int(x)))
    st.dataframe(slow, use_container_width=True, hide_index=True, height=250)
    st.markdown("These products sold least — consider discounting or replacing them.", unsafe_allow_html=False)


# ROW 4: Payment + Customer
st.markdown("---")
col_pay, col_cust = st.columns(2)
with col_pay:
    st.markdown("#### Payment Method Split")
    pay_col = next((c for c in ["Payment","Payment_Method","payment"] if c in df.columns), None)
    if pay_col:
        pay = df.groupby(pay_col)["Revenue"].sum().reset_index()
        fig6 = px.pie(pay, values="Revenue", names=pay_col, color_discrete_sequence=COLORS, hole=0.4)
        fig6.update_layout(**DARK_NO_AX, height=250, showlegend=True, legend=dict(font=dict(color="#8b949e")))
        fig6.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(color="white"))
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("Add a Payment column to see payment split.")

with col_cust:
    st.markdown("#### Top Customers")
    if "Customer" in df.columns:
        cs = df.groupby("Customer").agg(
            Bills=("Customer","count"), Spent=("Revenue","sum")
        ).sort_values("Spent", ascending=False).head(10).reset_index()
        cs["Spent"] = cs["Spent"].apply(lambda x: "Rs {:,}".format(int(x)))
        st.dataframe(cs, use_container_width=True, hide_index=True, height=250)


# ROW 5: Weekly + Discount analysis
st.markdown("---")
col_wk, col_disc = st.columns(2)
with col_wk:
    st.markdown("#### Weekly Revenue (last 12 weeks)")
    dw = df_raw.copy()
    dw["Date"] = pd.to_datetime(dw["Date"])
    dw["Week"] = dw["Date"].dt.to_period("W").astype(str)
    wk = dw.groupby("Week")["Revenue"].sum().reset_index().tail(12)
    fig5 = px.bar(wk, x="Week", y="Revenue", color_discrete_sequence=["#d2a8ff"], labels={"Revenue":"Rs","Week":""})
    fig5.update_layout(**DARK, height=250)
    fig5.update_traces(marker_line_width=0)
    st.plotly_chart(fig5, use_container_width=True)

with col_disc:
    st.markdown("#### Discount Impact")
    disc_col = next((c for c in ["Discount_Pct","Discount","discount_pct"] if c in df.columns), None)
    if disc_col:
        disc_grp = df.groupby(disc_col).agg(Transactions=("Revenue","count"), Revenue=("Revenue","sum")).reset_index()
        fig7 = px.bar(disc_grp, x=disc_col, y="Revenue", color="Transactions",
            color_continuous_scale=["#21262d","#ffa657"],
            labels={"Revenue":"Rs","Transactions":"No. of Bills", disc_col:"Discount %"})
        fig7.update_layout(**DARK, height=250, coloraxis_showscale=False)
        fig7.update_traces(marker_line_width=0)
        st.plotly_chart(fig7, use_container_width=True)
    else:
        st.info("Add a Discount_Pct column to see discount impact.")


# SMART INSIGHTS
st.markdown("---")
st.markdown("#### Smart Insights")
if len(df) > 0 and len(daily) > 0:
    best_day_row = daily.loc[daily["Revenue"].idxmax()]
    top_prod = str(df.groupby("Product")["Revenue"].sum().idxmax())
    i1,i2,i3,i4 = st.columns(4)
    with i1:
        st.markdown("<div class='insight-box'><div class='insight-title'>Best Sales Day</div><div class='insight-val'>"+str(best_day_row["Date"])+"</div><div class='insight-sub'>Rs {:,} in one day</div></div>".format(int(best_day_row["Revenue"])), unsafe_allow_html=True)
    with i2:
        st.markdown("<div class='insight-box'><div class='insight-title'>Top Product</div><div class='insight-val'>"+top_prod+"</div><div class='insight-sub'>Highest revenue this period</div></div>", unsafe_allow_html=True)
    with i3:
        st.markdown("<div class='insight-box'><div class='insight-title'>Peak Shopping Hour</div><div class='insight-val'>"+peak_str+"</div><div class='insight-sub'>Staff extra here</div></div>", unsafe_allow_html=True)
    with i4:
        badge = "<span class='badge-green'>+" + str(round(rev_delta,1)) + "%</span>" if rev_delta >= 0 else "<span class='badge-red'>" + str(round(rev_delta,1)) + "%</span>"
        st.markdown("<div class='insight-box'><div class='insight-title'>Revenue vs Prev Period</div><div class='insight-val'>"+badge+"</div><div class='insight-sub'>"+("Growing" if rev_delta>=0 else "Declining")+"</div></div>", unsafe_allow_html=True)


# EXPORT
st.markdown("---")
_, col_dl = st.columns([3,1])
with col_dl:
    csv_out = df.to_csv(index=False)
    safe = shop_name.replace(" ","_")
    fname = safe + "_" + str(max_date) + ".csv"
    st.download_button("Export Filtered Data as CSV", data=csv_out, file_name=fname, mime="text/csv")
