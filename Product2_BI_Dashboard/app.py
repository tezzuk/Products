import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import random

st.set_page_config(page_title="Business Dashboard", page_icon="📊", layout="wide")

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
def make_sample(btype):
    random.seed(42)
    today = date.today()
    if btype == "Restaurant":
        prods = ["Dal Makhani","Paneer Butter Masala","Biryani","Thali","Naan","Lassi","Gulab Jamun","Butter Chicken"]
        prices = [180,220,200,150,40,60,80,250]; peak=[12,13,14,19,20,21]
    elif btype == "Coaching Center":
        prods = ["JEE Batch","NEET Batch","Class 10 Math","Class 10 Science","Class 12 Physics","Class 12 Chemistry","SSC Prep","Foundation"]
        prices = [2500,2500,1200,1200,1500,1500,1800,1000]; peak=[6,7,16,17,18,19]
    elif btype == "Medical Store":
        prods = ["Paracetamol","Vitamin D3","Cough Syrup","Antacid","BP Tablets","Diabetes Kit","Bandage","Antiseptic"]
        prices = [25,180,85,60,120,350,40,90]; peak=[9,10,11,17,18,19]
    else:
        prods = ["Wallet","Belt","Handbag","Laptop Bag","Card Holder","Key Chain","Shoes","Gloves"]
        prices = [450,350,1200,1800,200,120,800,300]; peak=[10,11,14,15,16,17]
    custs = ["Customer " + chr(65+i) for i in range(20)]
    hrs = list(range(8,22)); hw = [5 if h in peak else 1 for h in hrs]
    rows = []
    for ago in range(90):
        d = today - timedelta(days=ago)
        for _ in range(random.randint(3,18)):
            idx = random.choices(range(len(prods)), weights=[10,8,9,12,6,5,4,7][:len(prods)], k=1)[0]
            qty = random.randint(1,4)
            h = random.choices(hrs, weights=hw, k=1)[0]
            dt = datetime(d.year, d.month, d.day, h, random.randint(0,59))
            rows.append({"DateTime":dt,"Date":d,"Hour":h,"DayOfWeek":dt.strftime("%A"),"DayNum":dt.weekday(),
                         "Product":prods[idx],"Qty":qty,"Price":prices[idx],"Revenue":prices[idx]*qty,"Customer":random.choice(custs)})
    return pd.DataFrame(rows)


with st.sidebar:
    st.markdown("## Business Dashboard")
    st.markdown("---")
    biz_name = st.text_input("Business Name", value="Sharma Enterprises")
    biz_type = st.selectbox("Business Type", ["Restaurant","Coaching Center","Medical Store","Leather/Textile Shop"])
    st.markdown("---")
    st.markdown("**Upload Your Data**")
    st.caption("CSV with: DateTime, Product, Qty, Price, Customer")
    uploaded = st.file_uploader("", type=["csv","xlsx"])
    st.markdown("---")
    period = st.radio("Time Period", ["Last 7 Days","Last 30 Days","Last 90 Days"])
    days = {"Last 7 Days":7,"Last 30 Days":30,"Last 90 Days":90}[period]
    st.markdown("---")
    st.caption("Demo mode — upload CSV to see real numbers.")


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
        if "Revenue" not in df_raw.columns and "Qty" in df_raw.columns:
            price_col = "Selling_Price" if "Selling_Price" in df_raw.columns else "Price" if "Price" in df_raw.columns else None
            if price_col:
                df_raw["Revenue"] = df_raw["Qty"] * df_raw[price_col]
        using_real = True
    except Exception as e:
        st.error("Error: " + str(e))
        df_raw = make_sample(biz_type)
        using_real = False
else:
    df_raw = make_sample(biz_type)
    using_real = False

# Use data's own max date so historical uploads work correctly
max_date = df_raw["Date"].max()
cutoff = max_date - timedelta(days=days)
prev_cutoff = cutoff - timedelta(days=days)
df = df_raw[df_raw["Date"] >= cutoff].copy()
df_prev = df_raw[(df_raw["Date"] >= prev_cutoff) & (df_raw["Date"] < cutoff)].copy()


c1, c2 = st.columns([4,1])
with c1:
    st.markdown("# " + biz_name)
    label = "Your real data" if using_real else "Demo - sample data"
    st.caption(label + " | " + period + " | Updated: " + datetime.now().strftime("%d %b %Y, %I:%M %p"))
with c2:
    if not using_real:
        st.info("Demo Mode")

st.markdown("---")

total_rev = df["Revenue"].sum()
prev_rev = df_prev["Revenue"].sum()
rev_delta = ((total_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0
total_orders = len(df)
prev_orders = len(df_prev)
ord_delta = ((total_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
avg_order = df["Revenue"].mean() if len(df) > 0 else 0
uniq_cust = df["Customer"].nunique() if "Customer" in df.columns else 0

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
    st.metric("Revenue", "Rs " + "{:,}".format(int(total_rev)), delta=("+" if rev_delta>=0 else "")+str(round(rev_delta,1))+"% vs prev")
with m2:
    st.metric("Orders", str(total_orders), delta=("+" if ord_delta>=0 else "")+str(round(ord_delta,1))+"% vs prev")
with m3:
    st.metric("Avg Order", "Rs " + "{:,}".format(int(avg_order)))
with m4:
    st.metric("Customers", str(uniq_cust))
with m5:
    st.metric("Peak Hour", peak_str)
with m6:
    st.metric("Best Day", best_dow)

st.markdown("---")

col_trend, col_pie = st.columns([3,2])
with col_trend:
    st.markdown("#### Daily Revenue Trend")
    daily = df.groupby("Date")["Revenue"].sum().reset_index().sort_values("Date")
    daily["MA7"] = daily["Revenue"].rolling(7, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Revenue"], name="Daily", mode="lines",
        line=dict(color="#58a6ff", width=1.5), fill="tozeroy", fillcolor="rgba(88,166,255,0.08)"))
    fig.add_trace(go.Scatter(x=daily["Date"], y=daily["MA7"], name="7-Day Avg", mode="lines",
        line=dict(color="#ffa657", width=2, dash="dot")))
    fig.update_layout(**DARK, height=280, legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(color="#8b949e")))
    st.plotly_chart(fig, use_container_width=True)

with col_pie:
    st.markdown("#### Top Products")
    prod_rev = df.groupby("Product")["Revenue"].sum().nlargest(6).reset_index()
    fig2 = px.pie(prod_rev, values="Revenue", names="Product", color_discrete_sequence=COLORS, hole=0.45)
    fig2.update_layout(**DARK_NO_AX, height=280, showlegend=True, legend=dict(font=dict(color="#8b949e",size=11)))
    fig2.update_traces(textposition="inside", textinfo="percent", textfont=dict(color="white"))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
col_hour, col_dow = st.columns(2)
with col_hour:
    st.markdown("#### Revenue by Hour of Day")
    if "Hour" in df.columns:
        hourly = df.groupby("Hour")["Revenue"].sum().reset_index()
        def fh(h):
            if h == 0: return "12am"
            if h < 12: return str(h)+"am"
            if h == 12: return "12pm"
            return str(h-12)+"pm"
        hourly["Label"] = hourly["Hour"].apply(fh)
        fig3 = px.bar(hourly, x="Label", y="Revenue", color="Revenue",
            color_continuous_scale=["#21262d","#58a6ff"], labels={"Revenue":"Rs","Label":"Hour"})
        fig3.update_layout(**DARK, height=250, coloraxis_showscale=False)
        fig3.update_traces(marker_line_width=0)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No time data in CSV.")

with col_dow:
    st.markdown("#### Revenue by Day of Week")
    if "DayOfWeek" in df.columns:
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = df.groupby("DayOfWeek")["Revenue"].sum().reindex(day_order).reset_index()
        fig4 = px.bar(dow, x="DayOfWeek", y="Revenue", color="Revenue",
            color_continuous_scale=["#21262d","#3fb950"], labels={"Revenue":"Rs","DayOfWeek":""})
        fig4.update_layout(**DARK, height=250, coloraxis_showscale=False)
        fig4.update_traces(marker_line_width=0)
        st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
col_prod, col_cust = st.columns(2)
with col_prod:
    st.markdown("#### Product Performance")
    ps = df.groupby("Product").agg(Units_Sold=("Qty","sum"),Revenue=("Revenue","sum"),Orders=("Product","count")).sort_values("Revenue",ascending=False).reset_index()
    ps["Revenue"] = ps["Revenue"].apply(lambda x: "Rs {:,}".format(int(x)))
    st.dataframe(ps, use_container_width=True, hide_index=True, height=230)

with col_cust:
    st.markdown("#### Top Customers")
    if "Customer" in df.columns:
        cs = df.groupby("Customer").agg(Orders=("Customer","count"),Total_Spent=("Revenue","sum")).sort_values("Total_Spent",ascending=False).head(10).reset_index()
        cs["Total_Spent"] = cs["Total_Spent"].apply(lambda x: "Rs {:,}".format(int(x)))
        st.dataframe(cs, use_container_width=True, hide_index=True, height=230)
    else:
        st.info("Add Customer column to CSV.")

st.markdown("---")
st.markdown("#### Weekly Revenue (last 8 weeks)")
if len(df_raw) > 0:
    dw = df_raw.copy()
    dw["Date"] = pd.to_datetime(dw["Date"])
    dw["Week"] = dw["Date"].dt.to_period("W").astype(str)
    wk = dw.groupby("Week")["Revenue"].sum().reset_index().tail(8)
    fig5 = px.bar(wk, x="Week", y="Revenue", color_discrete_sequence=["#d2a8ff"], labels={"Revenue":"Rs","Week":""})
    fig5.update_layout(**DARK, height=220)
    fig5.update_traces(marker_line_width=0)
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.markdown("#### Smart Insights")
if len(df) > 0 and len(daily) > 0:
    best_day = daily.loc[daily["Revenue"].idxmax()]
    best_prod = str(prod_rev.iloc[0]["Product"]) if len(prod_rev) > 0 else "N/A"
    i1,i2,i3,i4 = st.columns(4)
    with i1:
        st.markdown("<div class='insight-box'><div class='insight-title'>Best Day</div><div class='insight-val'>"+str(best_day["Date"])+"</div><div class='insight-sub'>Rs {:,} revenue</div></div>".format(int(best_day["Revenue"])), unsafe_allow_html=True)
    with i2:
        st.markdown("<div class='insight-box'><div class='insight-title'>Top Product</div><div class='insight-val'>"+best_prod+"</div><div class='insight-sub'>Highest revenue item</div></div>", unsafe_allow_html=True)
    with i3:
        st.markdown("<div class='insight-box'><div class='insight-title'>Peak Hour</div><div class='insight-val'>"+peak_str+"</div><div class='insight-sub'>Most orders this period</div></div>", unsafe_allow_html=True)
    with i4:
        badge = "<span class='badge-green'>+"+str(round(rev_delta,1))+"%</span>" if rev_delta >= 0 else "<span class='badge-red'>"+str(round(rev_delta,1))+"%</span>"
        st.markdown("<div class='insight-box'><div class='insight-title'>Revenue Trend</div><div class='insight-val'>"+badge+"</div><div class='insight-sub'>vs prev "+str(days)+"-day period</div></div>", unsafe_allow_html=True)

st.markdown("---")
_, col_dl = st.columns([3,1])
with col_dl:
    csv_out = df.to_csv(index=False)
    safe = biz_name.replace(" ","_")
    fname = safe + "_" + str(max_date) + ".csv"
    st.download_button("Export Data as CSV", data=csv_out, file_name=fname, mime="text/csv")
