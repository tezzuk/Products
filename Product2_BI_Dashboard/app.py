"""
Business Intelligence Dashboard — Demo App
Pre-loaded with sample data so clients immediately see value.
CSV upload to load their real data.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import random
import io

st.set_page_config(page_title="Business Dashboard", page_icon="📊", layout="wide")

# ── Custom CSS ──
st.markdown("""
<style>
.stApp { background-color: #f0f2f6; }
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    text-align: center;
}
.metric-value { font-size: 28px; font-weight: 700; color: #4361ee; }
.metric-label { font-size: 13px; color: #666; margin-top: 4px; }
.metric-delta-pos { color: #2d6a4f; font-size: 13px; }
.metric-delta-neg { color: #c0392b; font-size: 13px; }
.section-header { font-size: 17px; font-weight: 600; color: #1a1a2e; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ── SAMPLE DATA GENERATOR ──
@st.cache_data
def generate_sample_data(business_type="Restaurant"):
    random.seed(42)
    today = date.today()

    if business_type == "Restaurant":
        products = ["Dal Makhani", "Paneer Butter Masala", "Biryani", "Thali",
                    "Naan", "Lassi", "Gulab Jamun", "Butter Chicken"]
        prices = [180, 220, 200, 150, 40, 60, 80, 250]
    elif business_type == "Coaching Center":
        products = ["JEE Batch", "NEET Batch", "Class 10 Math", "Class 10 Science",
                    "Class 12 Physics", "Class 12 Chemistry", "SSC Prep", "Foundation"]
        prices = [2500, 2500, 1200, 1200, 1500, 1500, 1800, 1000]
    elif business_type == "Medical Store":
        products = ["Paracetamol", "Vitamin D3", "Cough Syrup", "Antacid",
                    "BP Tablets", "Diabetes Kit", "Bandage", "Antiseptic"]
        prices = [25, 180, 85, 60, 120, 350, 40, 90]
    else:  # Leather/Textile
        products = ["Wallet", "Belt", "Handbag", "Laptop Bag",
                    "Card Holder", "Key Chain", "Shoes", "Gloves"]
        prices = [450, 350, 1200, 1800, 200, 120, 800, 300]

    records = []
    customers = [f"Customer {chr(65+i)}" for i in range(20)]

    for days_ago in range(60):
        d = today - timedelta(days=days_ago)
        n_orders = random.randint(3, 18)
        for _ in range(n_orders):
            idx = random.choices(range(len(products)),
                                  weights=[10,8,9,12,6,5,4,7][:len(products)], k=1)[0]
            qty = random.randint(1, 4)
            records.append({
                "Date": d,
                "Product": products[idx],
                "Qty": qty,
                "Price": prices[idx],
                "Revenue": prices[idx] * qty,
                "Customer": random.choice(customers),
            })

    return pd.DataFrame(records)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## 📊 Business Dashboard")
    st.markdown("---")

    biz_name = st.text_input("Business Name", value="Sharma Enterprises")
    biz_type = st.selectbox("Business Type",
        ["Restaurant", "Coaching Center", "Medical Store", "Leather/Textile Shop"])

    st.markdown("---")
    st.markdown("**Upload Your Data**")
    st.caption("CSV with columns: Date, Product, Qty, Price, Customer")
    uploaded = st.file_uploader("", type=["csv", "xlsx"])

    st.markdown("---")
    period = st.radio("Time Period", ["Last 7 Days", "Last 30 Days", "Last 60 Days"])
    days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 60 Days": 60}
    days = days_map[period]

    st.markdown("---")
    st.caption("💡 *This is a live demo — using sample data. Upload your real CSV to see your actual numbers.*")


# ── LOAD DATA ──
if uploaded:
    try:
        if uploaded.name.endswith(".csv"):
            df_raw = pd.read_csv(uploaded)
        else:
            df_raw = pd.read_excel(uploaded)
        df_raw["Date"] = pd.to_datetime(df_raw["Date"]).dt.date
        df_raw["Revenue"] = df_raw["Qty"] * df_raw["Price"]
        using_real = True
    except Exception as e:
        st.error(f"Error reading file: {e}")
        df_raw = generate_sample_data(biz_type)
        using_real = False
else:
    df_raw = generate_sample_data(biz_type)
    using_real = False

# Filter by period
cutoff = date.today() - timedelta(days=days)
prev_cutoff = cutoff - timedelta(days=days)
df = df_raw[df_raw["Date"] >= cutoff].copy()
df_prev = df_raw[(df_raw["Date"] >= prev_cutoff) & (df_raw["Date"] < cutoff)].copy()


# ── HEADER ──
col_title, col_badge = st.columns([4, 1])
with col_title:
    st.markdown(f"## 📊 {biz_name}")
    st.caption(f"{'📂 Your real data' if using_real else '📋 Demo — sample data'} | {period}")
with col_badge:
    if not using_real:
        st.info("Demo Mode")


# ── KPI METRICS ──
total_rev = df["Revenue"].sum()
prev_rev = df_prev["Revenue"].sum()
rev_delta = ((total_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0

total_orders = len(df)
prev_orders = len(df_prev)
ord_delta = ((total_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0

avg_order = df["Revenue"].mean() if len(df) > 0 else 0
unique_customers = df["Customer"].nunique() if "Customer" in df.columns else 0

m1, m2, m3, m4 = st.columns(4)

def delta_arrow(val):
    return f"{'▲' if val >= 0 else '▼'} {abs(val):.1f}% vs prev period"

with m1:
    st.metric("💰 Total Revenue", f"₹{total_rev:,.0f}", delta=f"{delta_arrow(rev_delta)}")
with m2:
    st.metric("🧾 Total Orders", f"{total_orders:,}", delta=f"{delta_arrow(ord_delta)}")
with m3:
    st.metric("📦 Avg Order Value", f"₹{avg_order:,.0f}")
with m4:
    st.metric("👥 Unique Customers", f"{unique_customers}")

st.markdown("---")

# ── REVENUE TREND ──
col_trend, col_pie = st.columns([3, 2])

with col_trend:
    st.markdown("#### 📈 Daily Revenue Trend")
    daily = df.groupby("Date")["Revenue"].sum().reset_index()
    daily = daily.sort_values("Date")

    fig = px.area(daily, x="Date", y="Revenue",
                  color_discrete_sequence=["#4361ee"],
                  labels={"Revenue": "Revenue (₹)", "Date": ""})
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=10, b=0),
        height=260,
        yaxis=dict(gridcolor="#f0f0f0"),
        xaxis=dict(gridcolor="#f0f0f0"),
    )
    fig.update_traces(line_width=2, fill="tozeroy", fillcolor="rgba(67,97,238,0.1)")
    st.plotly_chart(fig, use_container_width=True)

with col_pie:
    st.markdown("#### 🏆 Top Products")
    prod_rev = df.groupby("Product")["Revenue"].sum().nlargest(6).reset_index()
    fig2 = px.pie(prod_rev, values="Revenue", names="Product",
                  color_discrete_sequence=px.colors.sequential.Blues_r,
                  hole=0.4)
    fig2.update_layout(
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=10, b=0),
        height=260,
        showlegend=True,
        legend=dict(font=dict(size=11))
    )
    fig2.update_traces(textposition="inside", textinfo="percent")
    st.plotly_chart(fig2, use_container_width=True)

# ── PRODUCTS TABLE + CUSTOMERS ──
col_prod, col_cust = st.columns(2)

with col_prod:
    st.markdown("#### 📦 Product Performance")
    prod_summary = df.groupby("Product").agg(
        Units_Sold=("Qty", "sum"),
        Revenue=("Revenue", "sum"),
        Orders=("Product", "count")
    ).sort_values("Revenue", ascending=False).reset_index()
    prod_summary["Revenue"] = prod_summary["Revenue"].apply(lambda x: f"₹{x:,.0f}")

    st.dataframe(prod_summary, use_container_width=True, hide_index=True, height=220)

with col_cust:
    st.markdown("#### 👥 Top Customers")
    if "Customer" in df.columns:
        cust_summary = df.groupby("Customer").agg(
            Orders=("Customer", "count"),
            Total_Spent=("Revenue", "sum")
        ).sort_values("Total_Spent", ascending=False).head(10).reset_index()
        cust_summary["Total_Spent"] = cust_summary["Total_Spent"].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(cust_summary, use_container_width=True, hide_index=True, height=220)
    else:
        st.info("Add a 'Customer' column to your CSV to see customer analytics.")

# ── DAILY REVENUE BAR (last 14 days) ──
st.markdown("---")
st.markdown("#### 📅 Revenue — Last 14 Days")
last14 = df[df["Date"] >= (date.today() - timedelta(days=14))]
bar_data = last14.groupby("Date")["Revenue"].sum().reset_index().sort_values("Date")

fig3 = px.bar(bar_data, x="Date", y="Revenue",
              color_discrete_sequence=["#4cc9f0"],
              labels={"Revenue": "Revenue (₹)", "Date": ""})
fig3.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=0, r=0, t=10, b=0),
    height=220,
    yaxis=dict(gridcolor="#f0f0f0"),
)
st.plotly_chart(fig3, use_container_width=True)

# ── DOWNLOAD ──
st.markdown("---")
col_dl1, col_dl2 = st.columns([2, 1])
with col_dl2:
    csv_data = df.to_csv(index=False)
    st.download_button(
        "⬇️ Export Data as CSV",
        data=csv_data,
        file_name=f"{biz_name.replace(' ', '_')}_data_{date.today()}.csv",
        mime="text/csv"
    )

# ── INSIGHT BOX ──
if len(df) > 0:
    best_day = daily.loc[daily["Revenue"].idxmax()]
    best_prod = prod_rev.iloc[0]["Product"] if len(prod_rev) > 0 else "N/A"
    with st.expander("🔍 Quick Insights"):
        st.success(f"📈 Best day this period: **{best_day['Date']}** with ₹{best_day['Revenue']:,.0f}")
        st.success(f"🏆 Top product: **{best_prod}**")
        if rev_delta > 0:
            st.success(f"✅ Revenue is UP **{rev_delta:.1f}%** compared to the previous period.")
        else:
            st.warning(f"⚠️ Revenue is DOWN **{abs(rev_delta):.1f}%** vs previous period. Time to review strategy.")
