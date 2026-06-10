import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import random

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

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
[data-testid="stMetricValue"] { color: #58a6ff !important; font-size: 26px !important; font-weight: 700 !important; }
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
.month-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.month-table th { background: #21262d; color: #8b949e; padding: 8px 12px; text-align: left; font-weight: 600; }
.month-table td { padding: 8px 12px; border-bottom: 1px solid #21262d; color: #e6edf3; }
.month-table tr:hover td { background: #1f2937; }
.stock-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px 16px; margin: 4px 0; display: flex; justify-content: space-between; align-items: center; }
.stock-name { color: #e6edf3; font-size: 14px; font-weight: 600; }
.stock-vel { color: #ffa657; font-size: 13px; }
.stock-action { background: #1a3a2a; color: #3fb950; border-radius: 6px; padding: 2px 10px; font-size: 12px; font-weight: 600; }
.cmp-card {
    background: #161b22; border: 1px solid #30363d; border-radius: 12px;
    padding: 18px 20px; text-align: center;
}
.cmp-label { color: #8b949e; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.cmp-a { color: #58a6ff; font-size: 22px; font-weight: 700; }
.cmp-b { color: #d2a8ff; font-size: 22px; font-weight: 700; }
.cmp-diff-pos { color: #3fb950; font-size: 13px; margin-top: 4px; }
.cmp-diff-neg { color: #f85149; font-size: 13px; margin-top: 4px; }
.cmp-diff-neu { color: #8b949e; font-size: 13px; margin-top: 4px; }
.loyal-row { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 10px 16px; margin: 4px 0; display: flex; justify-content: space-between; align-items: center; }
.loyal-name { color: #e6edf3; font-size: 14px; font-weight: 600; }
.loyal-visits { color: #8b949e; font-size: 12px; }
.loyal-spend { color: #3fb950; font-size: 14px; font-weight: 700; }
.report-box {
    background: linear-gradient(135deg, #0f2d1a, #161b22);
    border: 1px solid #3fb950; border-radius: 12px;
    padding: 24px 28px; margin: 16px 0;
    font-size: 15px; line-height: 1.9; color: #e6edf3;
}
.report-title { color: #3fb950; font-size: 13px; font-weight: 700; letter-spacing: 1px; margin-bottom: 14px; text-transform: uppercase; }
.report-rec {
    background: rgba(88,166,255,0.08); border-left: 4px solid #58a6ff;
    border-radius: 6px; padding: 12px 16px; margin-top: 14px;
    font-size: 14px; color: #79c0ff;
}
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


# ── COLUMN MAPPING CONFIG ──
REQUIRED_FIELDS = {
    "DateTime":      "Transaction date & time (e.g. 2024-01-15 or 15/01/2024 10:30)",
    "Product":       "Product or item name",
    "Qty":           "Quantity / units sold per transaction",
    "Selling_Price": "Selling price per unit",
}
OPTIONAL_FIELDS = {
    "Category": "Product category or department (e.g. Clothing, Electronics)",
    "Customer": "Customer ID or name",
    "Payment":  "Payment method (UPI, Cash, Card, etc.)",
}
ALL_FIELDS = {**REQUIRED_FIELDS, **OPTIONAL_FIELDS}


def _guess_cols(file_cols):
    lc = {c.lower().strip(): c for c in file_cols}
    hints = {
        "DateTime":      ["datetime","date","timestamp","time","order_time","created_at",
                          "order_date","sale_date","transaction_date","bill_date","txn_date"],
        "Product":       ["product","item","name","product_name","item_name","description",
                          "product_description","item_desc","sku","prod"],
        "Qty":           ["qty","quantity","units","count","pieces","pcs","no_of_units","num_units","sold_qty"],
        "Selling_Price": ["selling_price","price","sp","sale_price","unit_price","rate",
                          "sell_price","sold_price","amount","net_price"],
        "Category":      ["category","cat","type","product_type","segment","dept","department","section","group"],
        "Customer":      ["customer","cust","customer_id","customer_name","buyer","client",
                          "cust_name","cust_id","mobile","phone","contact"],
        "Payment":       ["payment","payment_method","mode","pay_mode","payment_mode","tender","pay_type"],
    }
    guesses = {}
    for field, keywords in hints.items():
        for kw in keywords:
            if kw in lc:
                guesses[field] = lc[kw]
                break
    return guesses


# ────────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Retail Analytics")
    st.markdown("---")
    shop_name = st.text_input("Shop / Mall Name", value="Sharma Retail Store")
    st.markdown("---")
    st.markdown("**Upload Your Sales Data**")
    st.caption("CSV or Excel with your sales records")
    uploaded = st.file_uploader("", type=["csv","xlsx"])
    if uploaded:
        _mkey = "col_mapping_" + uploaded.name
        if _mkey in st.session_state:
            if st.button("🔄 Re-map Columns", use_container_width=True):
                del st.session_state[_mkey]
                st.rerun()
    st.markdown("---")

    compare_mode = st.toggle("📊 Compare Periods", value=False)

    if compare_mode:
        data_max = st.session_state.get("data_max_date", date.today())
        data_min = st.session_state.get("data_min_date", date.today() - timedelta(days=730))
        st.markdown("**Period A**")
        a_start = st.date_input("A — Start", value=data_max - timedelta(days=30),
                                min_value=data_min, max_value=data_max, key="cmp_a_start")
        a_end   = st.date_input("A — End",   value=data_max,
                                min_value=data_min, max_value=data_max, key="cmp_a_end")
        st.markdown("**Period B**")
        b_start = st.date_input("B — Start", value=data_max - timedelta(days=61),
                                min_value=data_min, max_value=data_max, key="cmp_b_start")
        b_end   = st.date_input("B — End",   value=data_max - timedelta(days=31),
                                min_value=data_min, max_value=data_max, key="cmp_b_end")
        days = max((a_end - a_start).days + 1, 1)
    else:
        a_start = a_end = b_start = b_end = None
        period = st.radio("View Period", ["Last 7 Days","Last 30 Days","Last 90 Days","Full Year"])
        days = {"Last 7 Days":7,"Last 30 Days":30,"Last 90 Days":90,"Full Year":365}[period]

    st.markdown("---")
    lang = st.radio("Summary Language", ["English", "Hinglish"])
    st.markdown("---")
    st.caption("Demo mode — upload CSV to see real numbers.")


# ────────────────────────────────────────────
# LOAD DATA
# ────────────────────────────────────────────
if uploaded:
    try:
        df_raw_upload = (pd.read_csv(uploaded) if uploaded.name.endswith(".csv")
                         else pd.read_excel(uploaded))
    except Exception as e:
        st.error("Could not read file: " + str(e))
        st.stop()

    file_cols = list(df_raw_upload.columns)
    mapping_key = "col_mapping_" + uploaded.name

    if mapping_key not in st.session_state:
        st.markdown("## Map Your Data Columns")
        st.caption(
            "Your file has **" + str(len(file_cols)) + " column" +
            ("s" if len(file_cols) != 1 else "") + "**: `" +
            "`, `".join(file_cols) + "`  \n"
            "Match each field below. Required fields are marked **✱**."
        )
        st.markdown("")
        guesses = _guess_cols(file_cols)
        sel = {}
        with st.form("col_mapping_form"):
            col_a, col_b = st.columns(2)
            for i, (field, desc) in enumerate(ALL_FIELDS.items()):
                is_optional = field in OPTIONAL_FIELDS
                null_option = "Not available" if is_optional else "— select —"
                options = [null_option] + file_cols
                default_val = guesses.get(field, null_option)
                default_idx = options.index(default_val) if default_val in options else 0
                target_col = col_a if i % 2 == 0 else col_b
                with target_col:
                    label = field + ("  *(optional)*" if is_optional else "  ✱")
                    sel[field] = st.selectbox(label, options=options, index=default_idx, help=desc)
            st.markdown("")
            submitted = st.form_submit_button("✅  Apply Mapping & Run Dashboard", use_container_width=True)
        if submitted:
            missing = [f for f in REQUIRED_FIELDS if sel.get(f) == "— select —"]
            if missing:
                st.error("Please map all required fields: **" + ", ".join(missing) + "**")
            else:
                st.session_state[mapping_key] = {f: sel[f] for f in ALL_FIELDS}
                st.rerun()
        st.stop()

    mapping = st.session_state[mapping_key]
    rename_dict = {
        mapping[f]: f
        for f in ALL_FIELDS
        if mapping.get(f) not in ("Not available", "— select —", None, "")
        and mapping[f] in df_raw_upload.columns
        and mapping[f] != f
    }
    df_raw = df_raw_upload.rename(columns=rename_dict)

    if "DateTime" in df_raw.columns:
        df_raw["DateTime"] = pd.to_datetime(df_raw["DateTime"], errors="coerce")
        df_raw["Date"]      = df_raw["DateTime"].dt.date
        df_raw["Hour"]      = df_raw["DateTime"].dt.hour
        df_raw["DayOfWeek"] = df_raw["DateTime"].dt.strftime("%A")
        df_raw["DayNum"]    = df_raw["DateTime"].dt.dayofweek

    if "Revenue" not in df_raw.columns:
        if "Selling_Price" in df_raw.columns and "Qty" in df_raw.columns:
            df_raw["Revenue"] = (pd.to_numeric(df_raw["Selling_Price"], errors="coerce") *
                                 pd.to_numeric(df_raw["Qty"], errors="coerce"))
        elif "Selling_Price" in df_raw.columns:
            df_raw["Revenue"] = pd.to_numeric(df_raw["Selling_Price"], errors="coerce")

    using_real = True
else:
    df_raw = make_sample()
    using_real = False

max_date = df_raw["Date"].max()
st.session_state["data_max_date"] = max_date
st.session_state["data_min_date"] = df_raw["Date"].min()


# ────────────────────────────────────────────
# PERIOD FILTERING
# ────────────────────────────────────────────
if compare_mode and a_start and a_end and b_start and b_end:
    df      = df_raw[(df_raw["Date"] >= a_start) & (df_raw["Date"] <= a_end)].copy()
    df_b    = df_raw[(df_raw["Date"] >= b_start) & (df_raw["Date"] <= b_end)].copy()
    df_prev = df_b
else:
    cutoff      = max_date - timedelta(days=days)
    prev_cutoff = cutoff - timedelta(days=days)
    df      = df_raw[df_raw["Date"] >= cutoff].copy()
    df_prev = df_raw[(df_raw["Date"] >= prev_cutoff) & (df_raw["Date"] < cutoff)].copy()
    df_b    = df_prev


# ────────────────────────────────────────────
# HEADER
# ────────────────────────────────────────────
c1, c2 = st.columns([4,1])
with c1:
    st.markdown("# " + shop_name)
    label = "Your real data" if using_real else "Demo - sample retail data"
    st.caption(label + " | Updated: " + datetime.now().strftime("%d %b %Y, %I:%M %p"))
with c2:
    if not using_real:
        st.info("Demo Mode")

st.markdown("---")


# ────────────────────────────────────────────
# COMPARE PERIODS VIEW (when toggle is on)
# ────────────────────────────────────────────
if compare_mode and a_start and b_start:
    label_a = str(a_start.strftime("%d %b")) + " – " + str(a_end.strftime("%d %b %Y"))
    label_b = str(b_start.strftime("%d %b")) + " – " + str(b_end.strftime("%d %b %Y"))

    st.markdown("#### Period Comparison")
    st.caption("**Period A** (blue): " + label_a + "  ·  **Period B** (purple): " + label_b)

    def _cmp_metrics(dfa, dfb):
        def safe(val): return val if val == val else 0
        metrics = {}
        for key, col, fmt in [
            ("Total Revenue",    "Revenue", lambda v: "Rs {:,}".format(int(v))),
            ("Transactions",     None,      lambda v: "{:,}".format(int(v))),
            ("Avg Bill Value",   "Revenue", lambda v: "Rs {:,}".format(int(v))),
            ("Units Sold",       "Qty",     lambda v: "{:,}".format(int(v))),
        ]:
            if key == "Transactions":
                va, vb = len(dfa), len(dfb)
            elif key == "Avg Bill Value":
                va = safe(dfa["Revenue"].mean()) if "Revenue" in dfa.columns else 0
                vb = safe(dfb["Revenue"].mean()) if "Revenue" in dfb.columns else 0
            else:
                va = dfa[col].sum() if col in dfa.columns else 0
                vb = dfb[col].sum() if col in dfb.columns else 0
            diff = va - vb
            pct  = (diff / vb * 100) if vb > 0 else 0
            metrics[key] = (va, vb, diff, pct, fmt)
        return metrics

    cmp_data = _cmp_metrics(df, df_b)
    cols = st.columns(len(cmp_data))
    for col_obj, (metric, (va, vb, diff, pct, fmt)) in zip(cols, cmp_data.items()):
        with col_obj:
            diff_sign = "+" if diff >= 0 else ""
            diff_class = "cmp-diff-pos" if diff >= 0 else "cmp-diff-neg"
            if abs(pct) < 0.05:
                diff_class = "cmp-diff-neu"
            diff_str = diff_sign + str(round(pct, 1)) + "% (" + diff_sign + fmt(abs(diff)) + ")"
            st.markdown(
                "<div class='cmp-card'>"
                "<div class='cmp-label'>" + metric + "</div>"
                "<div class='cmp-a'>A: " + fmt(va) + "</div>"
                "<div class='cmp-b'>B: " + fmt(vb) + "</div>"
                "<div class='" + diff_class + "'>" + diff_str + "</div>"
                "</div>",
                unsafe_allow_html=True
            )

    st.markdown("")

    # Combined revenue trend — day-offset x-axis so periods overlay cleanly
    if "Date" in df.columns and "Date" in df_b.columns:
        daily_a = df.groupby("Date")["Revenue"].sum().reset_index().sort_values("Date")
        daily_a["Day"]    = range(1, len(daily_a) + 1)
        daily_a["Period"] = "Period A (" + label_a + ")"

        daily_b = df_b.groupby("Date")["Revenue"].sum().reset_index().sort_values("Date")
        daily_b["Day"]    = range(1, len(daily_b) + 1)
        daily_b["Period"] = "Period B (" + label_b + ")"

        cmp_daily = pd.concat([daily_a[["Day","Revenue","Period"]], daily_b[["Day","Revenue","Period"]]])

        fig_cmp = px.line(
            cmp_daily, x="Day", y="Revenue", color="Period",
            color_discrete_map={
                "Period A (" + label_a + ")": "#58a6ff",
                "Period B (" + label_b + ")": "#d2a8ff",
            },
            labels={"Day": "Day in Period", "Revenue": "Rs"},
        )
        fig_cmp.update_layout(**DARK, height=280,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(color="#8b949e")))
        fig_cmp.update_traces(line=dict(width=2))
        st.plotly_chart(fig_cmp, use_container_width=True)

    st.markdown("---")


# ────────────────────────────────────────────
# CORE NUMBERS
# ────────────────────────────────────────────
total_rev   = df["Revenue"].sum()
prev_rev    = df_prev["Revenue"].sum()
rev_delta   = ((total_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0
total_orders = len(df)
prev_orders  = len(df_prev)
ord_delta    = ((total_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
avg_order    = df["Revenue"].mean() if len(df) > 0 else 0
uniq_cust    = df["Customer"].nunique() if "Customer" in df.columns else 0
total_units  = int(df["Qty"].sum()) if "Qty" in df.columns else 0

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

# Customer repeat rate
if "Customer" in df.columns and len(df) > 0:
    cust_freq    = df.groupby("Customer").size()
    repeat_count = int((cust_freq > 1).sum())
    total_custs  = len(cust_freq)
    repeat_rate  = repeat_count / total_custs * 100 if total_custs > 0 else 0
    repeat_str   = str(round(repeat_rate, 1)) + "%"
else:
    repeat_rate = None
    repeat_str  = "N/A"


# ══════════════════════════════════════════════
# SECTION 1: PLAIN-ENGLISH / HINGLISH SUMMARY
# ══════════════════════════════════════════════
def build_summary(hinglish=False):
    rev_str       = "Rs {:,}".format(int(total_rev))
    avg_str       = "Rs {:,}".format(int(avg_order))
    trend_word_en = "up" if rev_delta >= 0 else "down"
    trend_word_hi = "zyada" if rev_delta >= 0 else "kam"
    delta_str     = str(abs(round(rev_delta, 1))) + "%"

    if not hinglish:
        lines = []
        lines.append("In the last <b>" + str(days) + " days</b>, your shop made <b>" + rev_str + "</b> from <b>" + str(total_orders) + " bills</b>.")
        lines.append("Your average bill value was <b>" + avg_str + "</b>, and <b>" + str(uniq_cust) + " unique customers</b> visited.")
        lines.append("Your best-selling item was <b>" + top_product + "</b>.")
        if bh is not None:
            lines.append("You were busiest between <b>" + peak_str + "</b> — keep extra staff ready during that time.")
        if prev_rev > 0:
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
        if prev_rev > 0:
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

if len(df_raw) > 0 and "Product" in df_raw.columns:
    ref_cutoff_7   = max_date - timedelta(days=7)
    ref_cutoff_p30 = max_date - timedelta(days=37)
    df_7   = df_raw[df_raw["Date"] >= ref_cutoff_7]
    df_p30 = df_raw[(df_raw["Date"] >= ref_cutoff_p30) & (df_raw["Date"] < ref_cutoff_7)]

    vel_30 = df_p30.groupby("Product")["Qty"].sum() / 30.0
    vel_7  = df_7.groupby("Product")["Qty"].sum() / 7.0
    common = vel_30.index.intersection(vel_7.index)
    slow_products = []
    for prod in common:
        avg_vel, recent_vel = vel_30[prod], vel_7[prod]
        if avg_vel > 0.1 and recent_vel < avg_vel * 0.5:
            slow_products.append((prod, int((1 - recent_vel / avg_vel) * 100)))
    slow_products.sort(key=lambda x: -x[1])
    for prod, drop in slow_products[:3]:
        msg = "<b>" + prod + "</b> — sales dropped <b>" + str(drop) + "%</b> this week vs the prior 30 days."
        if lang == "Hinglish":
            msg = "<b>" + prod + "</b> ki bikri is hafte <b>" + str(drop) + "%</b> giri hai pichle 30 din ke comparison mein."
        alerts.append(("red", msg))

    all_prods    = set(df_raw["Product"].unique())
    recent_prods = set(df_7["Product"].unique()) if len(df_7) > 0 else set()
    dead_prods   = all_prods - recent_prods
    if dead_prods:
        dead_list = ", ".join(sorted(dead_prods)[:3])
        msg = "No sales in last 7 days: <b>" + dead_list + "</b>. Consider discounting or removing from shelf."
        if lang == "Hinglish":
            msg = "Yeh items pichhle 7 din mein bilkul nahi bike: <b>" + dead_list + "</b>. Discount dein ya shelf se hatayein."
        alerts.append(("red", msg))

if "DayOfWeek" in df.columns and len(df) >= 14:
    day_rev     = df.groupby(["Date","DayOfWeek"])["Revenue"].sum().reset_index()
    dow_avg     = day_rev.groupby("DayOfWeek")["Revenue"].mean()
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

disc_col = next((c for c in ["Discount_Pct","Discount","discount_pct"] if c in df.columns), None)
if disc_col and len(df) > 0:
    disc_pct_val = (df[disc_col] > 0).sum() / len(df) * 100
    if disc_pct_val > 35:
        msg = "<b>" + str(int(disc_pct_val)) + "%</b> of your bills had a discount — this is reducing your profit margin."
        if lang == "Hinglish":
            msg = "Aapke <b>" + str(int(disc_pct_val)) + "% bills</b> par discount diya gaya — isse profit kam ho raha hai."
        alerts.append(("yellow", msg))
else:
    disc_pct_val = 0

if rev_delta > 20:
    msg = "Revenue is up <b>" + str(round(rev_delta,1)) + "%</b> vs the previous period. Stock up on fast-moving items!"
    if lang == "Hinglish":
        msg = "Revenue <b>" + str(round(rev_delta,1)) + "% badhi</b> hai pichle period se. Fast-moving items ka stock badhayen!"
    alerts.append(("green", msg))

if not alerts:
    alerts.append(("green", "No issues found. Business is running smoothly!" if lang == "English"
                   else "Koi problem nahi mili. Business theek chal raha hai!"))

for atype, amsg in alerts:
    st.markdown("<div class='alert-box alert-" + atype + "'>" + amsg + "</div>", unsafe_allow_html=True)

st.markdown("---")


# ── KPI METRICS (7 cards) ──
m1,m2,m3,m4,m5,m6,m7 = st.columns(7)
with m1:
    rev_delta_label = (("+" if rev_delta >= 0 else "") + str(round(rev_delta, 1)) + "% vs prev") if prev_rev > 0 else None
    st.metric("Total Revenue", "Rs {:,}".format(int(total_rev)), delta=rev_delta_label)
with m2:
    ord_delta_label = (("+" if ord_delta >= 0 else "") + str(round(ord_delta, 1)) + "% vs prev") if prev_orders > 0 else None
    st.metric("Transactions", "{:,}".format(total_orders), delta=ord_delta_label)
with m3:
    st.metric("Avg Bill Value", "Rs {:,}".format(int(avg_order)))
with m4:
    st.metric("Units Sold", "{:,}".format(total_units))
with m5:
    st.metric("Peak Hour", peak_str)
with m6:
    st.metric("Best Day", best_dow)
with m7:
    st.metric("Repeat Rate", repeat_str,
              help="% of customers who made more than one purchase in this period")

st.markdown("---")


# ── TOP 5 LOYAL CUSTOMERS ──
if "Customer" in df.columns and repeat_rate is not None and len(df) > 0:
    st.markdown("#### Top 5 Loyal Customers")
    top_loyal = (
        df.groupby("Customer")
          .agg(Visits=("Customer","count"), Total_Spend=("Revenue","sum"))
          .sort_values("Visits", ascending=False)
          .head(5)
          .reset_index()
    )
    loy_cols = st.columns(min(len(top_loyal), 5))
    for i, row in top_loyal.iterrows():
        with loy_cols[i]:
            st.markdown(
                "<div class='loyal-row' style='flex-direction:column;align-items:flex-start'>"
                "<div class='loyal-name'>" + str(row["Customer"]) + "</div>"
                "<div class='loyal-visits'>" + str(int(row["Visits"])) + " visits</div>"
                "<div class='loyal-spend'>Rs {:,}</div>".format(int(row["Total_Spend"])) +
                "</div>",
                unsafe_allow_html=True
            )
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
# SECTION 3: STAFF SCHEDULING
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
            st.markdown(
                "<div class='insight-box' style='text-align:center'>"
                "<div class='insight-title'>Keep Extra Staff</div>"
                "<div class='insight-val'>" + str(row["DayOfWeek"])[:3] + " " + fh2(int(row["Hour"])) + "</div>"
                "<div class='insight-sub'>" + str(int(row["Transactions"])) + " avg bills</div>"
                "</div>",
                unsafe_allow_html=True
            )
else:
    st.info("Add DateTime column to get staff scheduling recommendations.")


# ── SECTION 4: STOCK REORDER ──
st.markdown("---")
st.markdown("#### Stock Reorder Recommendations")
st.caption("Based on average daily sales velocity over the selected period")
if "Qty" in df.columns and len(df) > 0:
    vel = df.groupby("Product")["Qty"].sum() / max(days, 1)
    vel = vel.sort_values(ascending=False)
    top_fast    = vel.head(6)
    bottom_slow = vel[vel > 0].tail(5)
    col_fast, col_slow2 = st.columns(2)
    with col_fast:
        st.markdown("**Order More (Fast Movers)**" if lang == "English" else "**Yeh Order Karein (Jaldi Bikne Wale)**")
        for prod, v in top_fast.items():
            st.markdown(
                "<div class='stock-card'>"
                "<div><div class='stock-name'>" + str(prod) + "</div>"
                "<div class='stock-vel'>" + str(round(v,1)) + " units/day &rarr; ~" + str(int(v*7)) + " needed/week</div></div>"
                "<div class='stock-action'>Reorder</div>"
                "</div>", unsafe_allow_html=True
            )
    with col_slow2:
        st.markdown("**Review Stock (Slow Movers)**" if lang == "English" else "**Stock Ghatayen (Dheere Bikne Wale)**")
        for prod, v in bottom_slow.items():
            st.markdown(
                "<div class='stock-card'>"
                "<div><div class='stock-name'>" + str(prod) + "</div>"
                "<div class='stock-vel'>" + str(round(v,2)) + " units/day -- consider discount or less stock</div></div>"
                "<div style='background:#2d1a00;color:#ffa657;border-radius:6px;padding:2px 10px;font-size:12px;font-weight:600'>Review</div>"
                "</div>", unsafe_allow_html=True
            )


# ── PRODUCT TABLES ──
st.markdown("---")
col_prod, col_slow3 = st.columns(2)
with col_prod:
    st.markdown("#### Top Selling Products")
    ps = (df.groupby("Product")
            .agg(Units=("Qty","sum"), Revenue=("Revenue","sum"), Bills=("Product","count"))
            .sort_values("Revenue", ascending=False)
            .head(15).reset_index())
    ps["Revenue"] = ps["Revenue"].apply(lambda x: "Rs {:,}".format(int(x)))
    st.dataframe(ps, use_container_width=True, hide_index=True, height=300)

with col_slow3:
    st.markdown("#### Bottom Sellers by Revenue (Consider Action)")
    slow = (df.groupby("Product")
              .agg(Units=("Qty","sum"), Revenue=("Revenue","sum"))
              .sort_values("Revenue", ascending=True)
              .head(10).reset_index())
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


# ── MONTHLY COMPARISON TABLE ──
st.markdown("---")
st.markdown("#### Monthly Performance Comparison")
if len(df_raw) > 0:
    dm = df_raw.copy()
    dm["Date"] = pd.to_datetime(dm["Date"])
    dm["Month"] = dm["Date"].dt.to_period("M")
    monthly = dm.groupby("Month").agg(Revenue=("Revenue","sum"), Bills=("Revenue","count"), Avg_Bill=("Revenue","mean")).reset_index()
    monthly["Month"] = monthly["Month"].astype(str)
    monthly = monthly.sort_values("Month")
    max_rev_m, min_rev_m = monthly["Revenue"].max(), monthly["Revenue"].min()
    header = "<tr><th>Month</th><th>Total Revenue</th><th>Avg Bill Value</th><th>No. of Bills</th><th>vs Prev Month</th></tr>"
    rows_html = ""
    prev_rev_m = None
    for _, row in monthly.iterrows():
        rev, avg_b, bills = int(row["Revenue"]), int(row["Avg_Bill"]), int(row["Bills"])
        if prev_rev_m is not None and prev_rev_m > 0:
            chg = (rev - prev_rev_m) / prev_rev_m * 100
            chg_str = ("+" if chg >= 0 else "") + str(round(chg,1)) + "%"
            vs_cell = "<span style='color:" + ("#3fb950" if chg >= 0 else "#f85149") + ";font-weight:600'>" + chg_str + "</span>"
        else:
            vs_cell = "<span style='color:#8b949e'>--</span>"
        intensity = int((rev - min_rev_m) / max(max_rev_m - min_rev_m, 1) * 200)
        bg = "rgba(88," + str(100 + intensity) + ",255,0.08)"
        rows_html += ("<tr style='background:" + bg + "'><td>" + str(row["Month"]) + "</td>"
                      "<td><b>Rs {:,}</b></td>".format(rev) +
                      "<td>Rs {:,}</td>".format(avg_b) +
                      "<td>" + str(bills) + "</td><td>" + vs_cell + "</td></tr>")
        prev_rev_m = rev
    st.markdown("<table class='month-table'>" + header + rows_html + "</table>", unsafe_allow_html=True)
    st.caption("Darker blue = higher revenue month")


# ── WEEKLY BAR ──
st.markdown("---")
st.markdown("#### Weekly Revenue (last 12 weeks)")
def _fmt_week(p_str):
    parts = p_str.split("/")
    sd, ed = pd.to_datetime(parts[0]), pd.to_datetime(parts[1])
    if sd.month == ed.month:
        return sd.strftime("%b ") + str(sd.day) + "-" + str(ed.day)
    return sd.strftime("%b ") + str(sd.day) + "-" + ed.strftime("%b ") + str(ed.day)

dw2 = df_raw.copy()
dw2["Date"]    = pd.to_datetime(dw2["Date"])
dw2["_period"] = dw2["Date"].dt.to_period("W").astype(str)
dw2["Week"]    = dw2["_period"].apply(_fmt_week)
wk = dw2.groupby(["_period","Week"])["Revenue"].sum().reset_index().sort_values("_period").tail(12)
fig5 = px.bar(wk, x="Week", y="Revenue", color_discrete_sequence=["#d2a8ff"],
              labels={"Revenue":"Rs","Week":""}, category_orders={"Week": wk["Week"].tolist()})
fig5.update_layout(**DARK, height=220)
fig5.update_traces(marker_line_width=0)
st.plotly_chart(fig5, use_container_width=True)


# ── EXPORT ──
st.markdown("---")
_, col_dl = st.columns([3,1])
with col_dl:
    csv_out = df.to_csv(index=False)
    safe = shop_name.replace(" ","_")
    st.download_button("Export Filtered Data as CSV", data=csv_out,
                       file_name=safe + "_" + str(max_date) + ".csv", mime="text/csv")


# ── SECTION 6: GENERATE SUMMARY REPORT ──
st.markdown("---")
st.markdown("#### Business Summary Report")
st.caption("Generate a plain-English report a shop owner can read and act on immediately.")


def _build_report_text(df_r, df_raw_r, shop_r, days_r):
    parts = []
    rev   = df_r["Revenue"].sum() if "Revenue" in df_r.columns else 0
    bills = len(df_r)
    avg_b = rev / bills if bills > 0 else 0

    parts.append(
        "{shop} generated a total revenue of Rs {rev:,} from {bills:,} transactions "
        "over the last {days} days, with an average bill value of Rs {avg:,}.".format(
            shop=shop_r, rev=int(rev), bills=bills, days=days_r, avg=int(avg_b)
        )
    )

    if len(df_raw_r) > 0 and "Revenue" in df_raw_r.columns:
        dm2 = df_raw_r.copy()
        dm2["Date"] = pd.to_datetime(dm2["Date"])
        dm2["Month"] = dm2["Date"].dt.to_period("M").astype(str)
        mon_rev = dm2.groupby("Month")["Revenue"].sum()
        if len(mon_rev) >= 2:
            bm = mon_rev.idxmax()
            wm = mon_rev.idxmin()
            mdiff = int((mon_rev[bm] - mon_rev[wm]) / mon_rev[wm] * 100)
            parts.append(
                "Looking at monthly performance across your full dataset, your best month was {bm} "
                "and your weakest was {wm} -- a {d}% difference in revenue between the two.".format(
                    bm=bm, wm=wm, d=mdiff
                )
            )

    top_prod_name = None
    if "Product" in df_r.columns and "Revenue" in df_r.columns and len(df_r) > 0:
        pr = df_r.groupby("Product")["Revenue"].sum().sort_values(ascending=False)
        if len(pr) >= 3:
            t, b = pr.head(3), pr.tail(3)
            parts.append(
                "Your top three revenue-generating products were {p1} (Rs {v1:,}), "
                "{p2} (Rs {v2:,}), and {p3} (Rs {v3:,}). "
                "Your three lowest revenue products were {b1}, {b2}, and {b3} -- "
                "consider whether these need a price review, better placement, or a clearance discount.".format(
                    p1=t.index[0], v1=int(t.iloc[0]),
                    p2=t.index[1], v2=int(t.iloc[1]),
                    p3=t.index[2], v3=int(t.iloc[2]),
                    b1=b.index[-1], b2=b.index[-2], b3=b.index[-3],
                )
            )
        top_prod_name = pr.index[0] if len(pr) > 0 else None

    day_part = hour_part = ""
    if "DayOfWeek" in df_r.columns and len(df_r) > 0:
        day_part = "Your busiest day of the week is {d}".format(
            d=df_r.groupby("DayOfWeek")["Revenue"].sum().idxmax()
        )
    if "Hour" in df_r.columns and len(df_r) > 0:
        ph = int(df_r.groupby("Hour")["Revenue"].sum().idxmax())
        hour_part = "your peak selling window is {h}:00 to {h1}:00".format(h=ph, h1=ph+1)
    if day_part and hour_part:
        parts.append(day_part + " and " + hour_part +
                     ". Make sure you have adequate staff and stock available during these times.")
    elif day_part:
        parts.append(day_part + ". Plan your staffing schedule accordingly.")

    pay_col_r = next((c for c in ["Payment","Payment_Method","payment"] if c in df_r.columns), None)
    if pay_col_r and len(df_r) > 0 and "Revenue" in df_r.columns:
        pay_rev = df_r.groupby(pay_col_r)["Revenue"].sum()
        top_pay = pay_rev.idxmax()
        pay_pct = int(pay_rev[top_pay] / pay_rev.sum() * 100)
        parts.append(
            "The most popular payment method is {m}, accounting for roughly {p}% of your revenue. "
            "Make sure your {m} terminal is always working and settlement is checked daily.".format(
                m=top_pay, p=pay_pct
            )
        )

    rr_val = None
    if "Customer" in df_r.columns and len(df_r) > 0:
        cf = df_r.groupby("Customer").size()
        rr_val = (cf > 1).mean() * 100
        tc = df_r.groupby("Customer")["Revenue"].sum()
        top_c, top_c_spend = tc.idxmax(), int(tc.max())
        loyalty_note = (
            "This is a healthy loyalty rate -- your regulars are a strong foundation."
            if rr_val >= 30 else
            "There is room to grow -- a simple loyalty offer or WhatsApp follow-up can bring customers back."
            if rr_val >= 15 else
            "Most customers are visiting only once. A loyalty programme or post-purchase message could significantly improve this."
        )
        parts.append(
            "{r}% of your customers made more than one purchase this period. "
            "{note} Your most valuable customer is {c}, with a total spend of Rs {s:,}.".format(
                r=round(rr_val, 1), note=loyalty_note, c=top_c, s=top_c_spend
            )
        )

    disc_col_r = next((c for c in ["Discount_Pct","Discount","discount_pct"] if c in df_r.columns), None)
    disc_val = ((df_r[disc_col_r] > 0).mean() * 100) if disc_col_r else 0

    if rr_val is not None and rr_val < 20:
        rec = (
            "Focus on customer retention. Only {r}% of customers returned this period. "
            "A simple punch-card loyalty scheme, a 10% discount on the next visit, or a brief "
            "WhatsApp message after purchase can double your repeat rate within weeks. "
            "Keeping an existing customer is five times cheaper than finding a new one.".format(r=round(rr_val,1))
        )
    elif disc_val > 35:
        rec = (
            "Review your discount policy. Over {d}% of bills include a discount, directly cutting your margins. "
            "Try replacing blanket discounts with bundle offers (buy 2 get 10% off) or loyalty rewards -- "
            "you keep more revenue while still giving customers a reason to buy.".format(d=int(disc_val))
        )
    elif top_prod_name:
        rec = (
            "Double down on your best-seller: {p}. Never run out of stock on this item -- "
            "stockouts on top-sellers are one of the most common causes of lost revenue. "
            "Consider placing it at eye level near the entrance or checkout to drive impulse purchases.".format(
                p=top_prod_name
            )
        )
    else:
        rec = (
            "Review your product mix monthly and keep your best-sellers well-stocked. "
            "A clean, clearly priced store with consistent opening hours builds trust and drives repeat visits."
        )

    return parts, rec


if "summary_generated" not in st.session_state:
    st.session_state.summary_generated = False

col_gen, _ = st.columns([1, 3])
with col_gen:
    if st.button("Generate Business Summary Report", use_container_width=True, type="primary"):
        st.session_state.summary_generated = True

if st.session_state.summary_generated:
    paragraphs, recommendation = _build_report_text(df, df_raw, shop_name, days)

    body_html = "".join("<p style='margin:0 0 12px 0'>" + p + "</p>" for p in paragraphs)
    rec_html  = "<div class='report-rec'><b>Key Recommendation:</b> " + recommendation + "</div>"
    report_date = datetime.now().strftime("%d %b %Y")

    st.markdown(
        "<div class='report-box'>"
        "<div class='report-title'>Business Intelligence Report -- " + report_date + "</div>"
        + body_html + rec_html +
        "</div>",
        unsafe_allow_html=True
    )

    if FPDF_AVAILABLE:
        def _build_pdf(paras, rec, sname):
            def clean(t):
                # Reduce to ASCII-safe chars for fpdf built-in fonts
                mapping = {
                    "\u2019": "'", "\u2018": "'",
                    "\u201c": '"', "\u201d": '"',
                    "\u2013": "-", "\u2014": "-",
                    "\u2022": "*", "\u00a0": " ",
                    "\u20b9": "Rs",
                }
                out = []
                for ch in t:
                    if ord(ch) < 128:
                        out.append(ch)
                    else:
                        out.append(mapping.get(ch, ""))
                return "".join(out)

            pdf = FPDF()
            pdf.set_margins(20, 20, 20)
            pdf.add_page()
            # Explicit usable width avoids multi_cell(0,...) width=0 bug
            w = pdf.w - pdf.l_margin - pdf.r_margin

            pdf.set_font("Helvetica", "B", 20)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(w, 12, clean(sname), ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(w, 8, "Business Intelligence Report  |  " + datetime.now().strftime("%d %b %Y"), ln=True)
            pdf.ln(2)
            pdf.set_draw_color(88, 130, 200)
            pdf.set_line_width(0.6)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(8)

            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(40, 40, 40)
            for para in paras:
                pdf.multi_cell(w, 7, clean(para))
                pdf.ln(4)

            # Recommendation — draw filled background rect first, then write text on top
            pdf.ln(2)
            box_x  = pdf.l_margin
            box_y  = pdf.get_y()
            rec_clean = clean(rec)
            # Estimate box height: label row + body rows + padding
            body_lines = max(1, len(rec_clean) // 90 + 1)
            box_h = 7 + body_lines * 7 + 8
            pdf.set_fill_color(235, 243, 255)
            pdf.rect(box_x, box_y, w, box_h, style="F")
            pdf.set_xy(box_x + 3, box_y + 3)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(30, 60, 120)
            pdf.multi_cell(w - 6, 7, "Key Recommendation:")
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(40, 40, 40)
            pdf.set_x(box_x + 3)
            pdf.multi_cell(w - 6, 7, rec_clean)

            pdf.set_y(-20)
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(160, 160, 160)
            pdf.cell(w, 8, "Generated by Retail Analytics Dashboard", align="C")
            return bytes(pdf.output())

        pdf_bytes = _build_pdf(paragraphs, recommendation, shop_name)
        st.download_button(
            "Download as PDF",
            data=pdf_bytes,
            file_name=shop_name.replace(" ","_") + "_report_" + datetime.now().strftime("%Y%m%d") + ".pdf",
            mime="application/pdf",
        )
    else:
        st.caption("Install fpdf2 to enable PDF download: pip install fpdf2")
