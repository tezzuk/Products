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


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def sheets_to_csv_url(url: str) -> str:
    """Convert any Google Sheets share/edit URL to a direct CSV export URL."""
    import re as _re
    m = _re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
    if not m:
        return url  # not recognised, pass through
    sheet_id = m.group(1)
    gid_m = _re.search(r"[#&?]gid=([0-9]+)", url)
    gid = gid_m.group(1) if gid_m else "0"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


# ══════════════════════════════════════════════════════
# CLIENT CONFIG — add a new client by adding one entry
# tier: "basic" | "standard" | "premium"
# ══════════════════════════════════════════════════════
CLIENTS = {
    "demo": {
        "name": "Demo Store",
        "tier": "premium",
        "lang": "English",
        "alert_discount": 30,
    },
    "sharma123": {
        "name": "Sharma Retail Store",
        "tier": "premium",
        "lang": "English",
        "alert_discount": 30,
    },
    # Add more clients here:
    # "rajelectronics": {"name": "Raj Electronics", "tier": "standard", "lang": "English", "alert_discount": 25},
    # To auto-load from Google Sheets, add a sheets_url field:
    # "gupta567": {
    #     "name": "Gupta Traders",
    #     "tier": "premium",
    #     "lang": "English",
    #     "alert_discount": 30,
    #     "sheets_url": "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0",
    # },
}

TIER_LABEL = {"basic": "Basic", "standard": "Standard", "premium": "Premium"}

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



# ── LOGIN GATE ──
if "client_config" not in st.session_state:
    st.markdown("""
    <style>
    .login-wrap { max-width: 400px; margin: 80px auto 0; }
    .login-title { font-size: 32px; font-weight: 700; color: #e6edf3; margin-bottom: 4px; }
    .login-sub { color: #8b949e; font-size: 15px; margin-bottom: 32px; }
    </style>
    <div class='login-wrap'>
      <div class='login-title'>Retail Analytics</div>
      <div class='login-sub'>Business Intelligence Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        pwd = st.text_input("Enter your password", type="password", placeholder="Password provided by your administrator")
        if st.button("Login", use_container_width=True, type="primary"):
            if pwd in CLIENTS:
                st.session_state.client_config = CLIENTS[pwd]
                st.rerun()
            else:
                st.error("Invalid password. Please contact your administrator.")
        st.caption("Need access? Contact: vanshtripathi2007@gmail.com")
    st.stop()

# ── LOAD CLIENT CONFIG ──
_cfg   = st.session_state.client_config
_tier  = _cfg["tier"]        # "basic" | "standard" | "premium"
_cname = _cfg["name"]
_clang = _cfg.get("lang", "English")
_calert_disc = _cfg.get("alert_discount", 30)

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
    shop_name = _cname
    st.markdown(
        "<div style='background:#21262d;border-radius:8px;padding:10px 14px;margin-bottom:8px'>"
        "<div style='color:#8b949e;font-size:11px;font-weight:600;letter-spacing:1px;text-transform:uppercase'>Logged in as</div>"
        "<div style='color:#e6edf3;font-size:15px;font-weight:600;margin-top:2px'>" + _cname + "</div>"
        "<div style='color:#58a6ff;font-size:11px;margin-top:2px'>" + TIER_LABEL[_tier] + " plan</div>"
        "</div>",
        unsafe_allow_html=True
    )
    if st.button("Logout", use_container_width=True):
        del st.session_state.client_config
        st.rerun()
    st.markdown("---")
    _sheets_url = _cfg.get("sheets_url", "")
    if _sheets_url:
        # ── Google Sheets mode ──
        st.markdown("**📊 Data Source**")
        st.markdown(
            "<div style='background:#1c2d3a;border:1px solid #1f6feb;border-radius:8px;"
            "padding:8px 12px;margin-bottom:8px'>"
            "<div style='color:#58a6ff;font-size:12px;font-weight:600'>✅ Connected to Google Sheets</div>"
            "<div style='color:#8b949e;font-size:11px;margin-top:2px'>Auto-syncs when you refresh</div>"
            "</div>",
            unsafe_allow_html=True
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                _sk = "sheets_df_" + _cname
                for k in list(st.session_state.keys()):
                    if k == _sk or k == "col_mapping__sheets_auto_.csv":
                        del st.session_state[k]
                st.rerun()
        with col2:
            if st.button("🔗 Open Sheet", use_container_width=True):
                st.markdown(
                    f'<a href="{_sheets_url}" target="_blank" style="display:none">open</a>',
                    unsafe_allow_html=True
                )
                st.info("Link copied — open in browser")
        with st.expander("⬆ Override with CSV", expanded=False):
            uploaded = st.file_uploader("Upload CSV/Excel to override", type=["csv","xlsx"], key="csv_override")
            if uploaded and "col_mapping_" + uploaded.name in st.session_state:
                if st.button("🔄 Re-map Columns", use_container_width=True):
                    del st.session_state["col_mapping_" + uploaded.name]
                    st.rerun()
    else:
        # ── Manual upload mode ──
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

    if _tier in ("standard", "premium"):
        compare_mode = st.toggle("📊 Compare Periods", value=False)
    else:
        compare_mode = False
        st.caption("🔒 Compare Periods — Standard plan")

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
    lang = st.radio("Summary Language", ["English", "Hinglish"], index=0 if _clang == "English" else 1)
    st.markdown("---")
    if not _sheets_url:
        st.caption("Demo mode — upload CSV to see real numbers.")


# ────────────────────────────────────────────
# LOAD DATA
# ────────────────────────────────────────────
# Auto-load from Google Sheets if configured and no CSV override
_sheets_cfg_url = _cfg.get("sheets_url", "")
_SHEETS_KEY = "sheets_df_" + _cname
if _sheets_cfg_url and _SHEETS_KEY not in st.session_state and not uploaded:
    with st.spinner("Loading data from Google Sheets…"):
        try:
            _csv_url = sheets_to_csv_url(_sheets_cfg_url)
            st.session_state[_SHEETS_KEY] = pd.read_csv(_csv_url)
        except Exception as _se:
            st.warning(f"⚠️ Could not load Google Sheets data: {_se}  \nPlease upload a CSV file.")

# If sheets data loaded and no CSV override, use sheets data as the upload
if not uploaded and _SHEETS_KEY in st.session_state:
    import io as _io
    _fake_buf = _io.BytesIO()
    st.session_state[_SHEETS_KEY].to_csv(_fake_buf, index=False)
    _fake_buf.seek(0)
    _fake_buf.name = "_sheets_auto_.csv"
    uploaded = _fake_buf

if uploaded:
    try:
        _fname = getattr(uploaded, "name", "file.csv")
        if _fname.endswith(".xlsx") or _fname.endswith(".xls"):
            df_raw_upload = pd.read_excel(uploaded)
        else:
            df_raw_upload = pd.read_csv(uploaded)
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
        # If all hours are 0, the source has no time component — drop Hour so
        # downstream sections show "No data available" instead of just "12am"
        if df_raw["Hour"].nunique() == 1 and df_raw["Hour"].iloc[0] == 0:
            df_raw = df_raw.drop(columns=["Hour"])

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
    if not using_real and _cfg.get("name") == "Demo Store":
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
    else:
        st.info("⏰ No time data available — upload a file with a DateTime column to see hourly trends.")

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


if _tier in ('standard', 'premium'):
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
    
    
else:
    st.markdown('---')
    st.info('🔒 Staff Scheduling is available on Standard and Premium plans.')
if _tier in ('standard', 'premium'):
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
    
    
else:
    st.markdown('---')
    st.info('🔒 Stock Reorder Recommendations are available on Standard and Premium plans.')
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


if _tier in ('standard', 'premium'):
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
    
    
else:
    st.markdown('---')
    st.info('🔒 Payment Method Analysis is available on Standard and Premium plans.')
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
dw2 = df_raw.copy()
dw2["Date"] = pd.to_datetime(dw2["Date"])
dw2["WeekStart"] = dw2["Date"].dt.to_period("W").apply(lambda p: p.start_time.date())
wk = dw2.groupby("WeekStart")["Revenue"].sum().reset_index().sort_values("WeekStart").tail(12)
wk["Label"] = wk["WeekStart"].apply(lambda d: d.strftime("%d %b %Y"))
fig5 = px.bar(wk, x="Label", y="Revenue", color_discrete_sequence=["#d2a8ff"],
              labels={"Revenue":"Rs","Label":""}, category_orders={"Label": wk["Label"].tolist()})
fig5.update_layout(**DARK, height=220)
fig5.update_traces(marker_line_width=0)
st.plotly_chart(fig5, use_container_width=True)



# ══════════════════════════════════════════════════════
if _tier == 'premium':
    # SECTION ML: FORECASTING, DEMAND, ANOMALY DETECTION
    # ══════════════════════════════════════════════════════
    import numpy as np
    from sklearn.linear_model import LinearRegression
    
    st.markdown("---")
    st.markdown("## ML Analytics & Predictions")
    st.caption("Powered by machine learning on your historical data. Requires at least 60 days of data for accuracy.")
    
    ml_tab1, ml_tab2, ml_tab3 = st.tabs(["Revenue Forecast", "Product Demand", "Anomaly Detection"])
    
    
    # ──────────────────────────────────────────────────────
    # TAB 1: REVENUE FORECAST
    # ──────────────────────────────────────────────────────
    with ml_tab1:
        st.markdown("#### Revenue Forecast — Next 30 Days")
        st.caption("Uses linear trend + day-of-week seasonality learned from your historical data")
    
        # Need at least 60 days
        all_daily = df_raw.groupby("Date")["Revenue"].sum().reset_index().sort_values("Date")
        all_daily["Date"] = pd.to_datetime(all_daily["Date"])
        all_daily = all_daily.sort_values("Date").reset_index(drop=True)
    
        if len(all_daily) < 30:
            st.warning("Need at least 30 days of data for forecasting. Upload more historical data.")
        else:
            # Feature engineering: day index + day of week dummies
            all_daily["DayIndex"] = range(len(all_daily))
            all_daily["DOW"] = all_daily["Date"].dt.dayofweek
    
            # Build feature matrix: trend + 6 day-of-week dummies (drop Monday as base)
            dow_dummies = pd.get_dummies(all_daily["DOW"], prefix="dow", drop_first=True)
            X = pd.concat([all_daily[["DayIndex"]], dow_dummies], axis=1).values
            y = all_daily["Revenue"].values
    
            model = LinearRegression()
            model.fit(X, y)
    
            # Residuals for confidence interval
            y_pred_train = model.predict(X)
            residuals = y - y_pred_train
            std_resid = np.std(residuals)
            z80 = 1.28  # 80% confidence interval
    
            # Build future dates
            last_idx = all_daily["DayIndex"].max()
            last_date = all_daily["Date"].max()
            future_dates = [last_date + timedelta(days=i+1) for i in range(30)]
            future_rows = []
            for i, fd in enumerate(future_dates):
                row = {"DayIndex": last_idx + i + 1, "DOW": fd.dayofweek}
                future_rows.append(row)
            future_df = pd.DataFrame(future_rows)
            dow_fut = pd.get_dummies(future_df["DOW"], prefix="dow")
            for col in dow_dummies.columns:
                if col not in dow_fut.columns:
                    dow_fut[col] = 0
            dow_fut = dow_fut[dow_dummies.columns]
            X_fut = pd.concat([future_df[["DayIndex"]], dow_fut], axis=1).values
            y_fut = model.predict(X_fut)
            y_fut = np.maximum(y_fut, 0)
            y_upper = y_fut + z80 * std_resid
            y_lower = np.maximum(y_fut - z80 * std_resid, 0)
    
            # Plot: historical + forecast + confidence band
            fig_fc = go.Figure()
    
            # Historical (last 90 days only for readability)
            hist_plot = all_daily.tail(90)
            fig_fc.add_trace(go.Scatter(
                x=hist_plot["Date"], y=hist_plot["Revenue"],
                name="Historical", mode="lines",
                line=dict(color="#58a6ff", width=1.5)
            ))
    
            # Confidence band
            fig_fc.add_trace(go.Scatter(
                x=future_dates + future_dates[::-1],
                y=list(y_upper) + list(y_lower[::-1]),
                fill="toself", fillcolor="rgba(255,166,87,0.12)",
                line=dict(color="rgba(0,0,0,0)"),
                name="80% Confidence Range", showlegend=True
            ))
    
            # Forecast line
            fig_fc.add_trace(go.Scatter(
                x=future_dates, y=y_fut,
                name="Forecast", mode="lines",
                line=dict(color="#ffa657", width=2.5, dash="dot")
            ))
    
            fig_fc.update_layout(**DARK, height=340,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#8b949e")),
                shapes=[dict(type="line", x0=last_date, x1=last_date, y0=0, y1=1, xref="x", yref="paper",
                             line=dict(color="#30363d", width=1, dash="dash"))]
            )
            st.plotly_chart(fig_fc, use_container_width=True)
    
            # Summary cards
            fc_7  = int(np.sum(y_fut[:7]))
            fc_30 = int(np.sum(y_fut))
            lo_7  = int(np.sum(y_lower[:7]))
            hi_7  = int(np.sum(y_upper[:7]))
            lo_30 = int(np.sum(y_lower))
            hi_30 = int(np.sum(y_upper))
    
            # Month-end projection
            today_date = max_date
            days_passed = today_date.day
            days_in_month = 30
            month_start = today_date.replace(day=1)
            mtd_rev = int(df_raw[df_raw["Date"] >= month_start]["Revenue"].sum()) if len(df_raw) > 0 else 0
            projected_month = int(mtd_rev / max(days_passed, 1) * days_in_month) if days_passed > 0 else 0
    
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                st.markdown(
                    "<div class='insight-box'>"
                    "<div class='insight-title'>Next 7 Days (Forecast)</div>"
                    "<div class='insight-val'>Rs {:,}</div>".format(fc_7) +
                    "<div class='insight-sub'>Range: Rs {:,} - Rs {:,}</div>".format(lo_7, hi_7) +
                    "</div>", unsafe_allow_html=True
                )
            with fc2:
                st.markdown(
                    "<div class='insight-box'>"
                    "<div class='insight-title'>Next 30 Days (Forecast)</div>"
                    "<div class='insight-val'>Rs {:,}</div>".format(fc_30) +
                    "<div class='insight-sub'>Range: Rs {:,} - Rs {:,}</div>".format(lo_30, hi_30) +
                    "</div>", unsafe_allow_html=True
                )
            with fc3:
                st.markdown(
                    "<div class='insight-box'>"
                    "<div class='insight-title'>This Month Projection</div>"
                    "<div class='insight-val'>Rs {:,}</div>".format(projected_month) +
                    "<div class='insight-sub'>Based on Rs {:,} earned so far ({} days)</div>".format(mtd_rev, days_passed) +
                    "</div>", unsafe_allow_html=True
                )
    
            if lang == "Hinglish":
                st.info("Agli 7 din mein estimated revenue: Rs {:,} se Rs {:,} ke beech (80% probability)".format(lo_7, hi_7))
            else:
                st.info("Next 7 days: Rs {:,} to Rs {:,} with 80% confidence. Plan your stock and staff accordingly.".format(lo_7, hi_7))
    
    
    # ──────────────────────────────────────────────────────
    # TAB 2: PRODUCT DEMAND PREDICTION
    # ──────────────────────────────────────────────────────
    with ml_tab2:
        st.markdown("#### Product Demand Prediction — Next 7 Days")
        st.caption("Predicts units to sell per product based on day-of-week patterns from historical data")
    
        if "Product" not in df_raw.columns or "Qty" not in df_raw.columns:
            st.warning("Need Product and Qty columns in your data.")
        elif len(df_raw) < 30:
            st.warning("Need at least 30 days of data.")
        else:
            # For each product: average units per day-of-week
            df_raw2 = df_raw.copy()
            df_raw2["Date"] = pd.to_datetime(df_raw2["Date"])
            df_raw2["DOW"] = df_raw2["Date"].dt.dayofweek
            df_raw2["DOWName"] = df_raw2["Date"].dt.strftime("%A")
    
            prod_dow = df_raw2.groupby(["Product","DOW"])["Qty"].mean().reset_index()
            prod_dow.columns = ["Product","DOW","AvgQty"]
    
            # Next 7 days
            next7 = [(max_date + timedelta(days=i+1)) for i in range(7)]
            next7_dow = [d.weekday() for d in next7]
            next7_names = [d.strftime("%a %d %b") for d in next7]
    
            # For each product, predict next 7 days
            products_list = df_raw2["Product"].unique()
            demand_rows = []
            for prod in products_list:
                pdata = prod_dow[prod_dow["Product"] == prod].set_index("DOW")["AvgQty"]
                weekly_pred = 0
                for dow in next7_dow:
                    avg = pdata.get(dow, pdata.mean() if len(pdata) > 0 else 0)
                    weekly_pred += avg
                demand_rows.append({"Product": prod, "Predicted_Units_Next_7d": round(weekly_pred, 1)})
    
            demand_df = pd.DataFrame(demand_rows).sort_values("Predicted_Units_Next_7d", ascending=False)
    
            # Show top and bottom
            col_dem1, col_dem2 = st.columns(2)
            with col_dem1:
                st.markdown("**Top 8 — Stock Up This Week**")
                top8 = demand_df.head(8).reset_index(drop=True)
                fig_dem = px.bar(top8, x="Predicted_Units_Next_7d", y="Product",
                    orientation="h", color="Predicted_Units_Next_7d",
                    color_continuous_scale=["#21262d","#3fb950"],
                    labels={"Predicted_Units_Next_7d": "Predicted Units", "Product": ""})
                fig_dem.update_layout(**DARK, height=320, coloraxis_showscale=False)
                fig_dem.update_traces(marker_line_width=0)
                st.plotly_chart(fig_dem, use_container_width=True)
    
            with col_dem2:
                st.markdown("**Day-by-Day Prediction (Top 5 Products)**")
                top5_prods = demand_df.head(5)["Product"].tolist()
                day_pred_rows = []
                for prod in top5_prods:
                    pdata = prod_dow[prod_dow["Product"] == prod].set_index("DOW")["AvgQty"]
                    row = {"Product": prod}
                    for j, (d, dname) in enumerate(zip(next7_dow, next7_names)):
                        avg = pdata.get(d, pdata.mean() if len(pdata) > 0 else 0)
                        row[dname] = round(avg, 1)
                    day_pred_rows.append(row)
    
                day_pred_df = pd.DataFrame(day_pred_rows).set_index("Product")
                st.dataframe(day_pred_df, use_container_width=True, height=220)
                st.caption("Numbers = predicted units to sell each day")
    
            # Plain-English recommendation
            top_prod_dem = demand_df.iloc[0]["Product"] if len(demand_df) > 0 else "N/A"
            top_units = demand_df.iloc[0]["Predicted_Units_Next_7d"] if len(demand_df) > 0 else 0
            if lang == "Hinglish":
                st.success("Is hafte sabse zyada bikne wala item: **" + str(top_prod_dem) + "** (~" + str(int(top_units)) + " units). Stock ready rakhein!")
            else:
                st.success("Top predicted seller this week: **" + str(top_prod_dem) + "** (~" + str(int(top_units)) + " units). Make sure you have enough stock!")
    
    
    # ──────────────────────────────────────────────────────
    # TAB 3: ANOMALY DETECTION
    # ──────────────────────────────────────────────────────
    with ml_tab3:
        st.markdown("#### Anomaly Detection — Unusual Revenue Days")
        st.caption("Flags days where revenue was statistically unusual (more than 2 standard deviations from rolling average)")
    
        all_daily2 = df_raw.groupby("Date")["Revenue"].sum().reset_index().sort_values("Date")
        all_daily2["Date"] = pd.to_datetime(all_daily2["Date"])
    
        if len(all_daily2) < 14:
            st.warning("Need at least 14 days of data for anomaly detection.")
        else:
            # Rolling 30-day mean and std
            all_daily2["Roll_Mean"] = all_daily2["Revenue"].rolling(30, min_periods=7, center=True).mean()
            all_daily2["Roll_Std"]  = all_daily2["Revenue"].rolling(30, min_periods=7, center=True).std()
            all_daily2["Roll_Mean"] = all_daily2["Roll_Mean"].fillna(all_daily2["Revenue"].mean())
            all_daily2["Roll_Std"]  = all_daily2["Roll_Std"].fillna(all_daily2["Revenue"].std())
            all_daily2["ZScore"]    = (all_daily2["Revenue"] - all_daily2["Roll_Mean"]) / all_daily2["Roll_Std"].replace(0, 1)
            all_daily2["Anomaly"]   = all_daily2["ZScore"].abs() > 2.0
            all_daily2["Spike"]     = all_daily2["ZScore"] > 2.0
            all_daily2["Drop"]      = all_daily2["ZScore"] < -2.0
    
            spikes = all_daily2[all_daily2["Spike"]]
            drops  = all_daily2[all_daily2["Drop"]]
    
            # Chart
            fig_an = go.Figure()
    
            # Normal days
            normal = all_daily2[~all_daily2["Anomaly"]]
            fig_an.add_trace(go.Scatter(
                x=normal["Date"], y=normal["Revenue"],
                mode="lines", name="Normal",
                line=dict(color="#58a6ff", width=1.5)
            ))
    
            # Rolling mean band
            fig_an.add_trace(go.Scatter(
                x=list(all_daily2["Date"]) + list(all_daily2["Date"])[::-1],
                y=list(all_daily2["Roll_Mean"] + 2*all_daily2["Roll_Std"]) + list((all_daily2["Roll_Mean"] - 2*all_daily2["Roll_Std"]).clip(0))[::-1],
                fill="toself", fillcolor="rgba(88,166,255,0.06)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Normal Range", showlegend=True
            ))
    
            fig_an.add_trace(go.Scatter(
                x=all_daily2["Date"], y=all_daily2["Roll_Mean"],
                mode="lines", name="Rolling Avg",
                line=dict(color="#8b949e", width=1, dash="dot")
            ))
    
            # Spike markers
            if len(spikes) > 0:
                fig_an.add_trace(go.Scatter(
                    x=spikes["Date"], y=spikes["Revenue"],
                    mode="markers", name="Spike",
                    marker=dict(color="#3fb950", size=10, symbol="triangle-up")
                ))
    
            # Drop markers
            if len(drops) > 0:
                fig_an.add_trace(go.Scatter(
                    x=drops["Date"], y=drops["Revenue"],
                    mode="markers", name="Drop",
                    marker=dict(color="#f85149", size=10, symbol="triangle-down")
                ))
    
            fig_an.update_layout(**DARK, height=350,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#8b949e"))
            )
            st.plotly_chart(fig_an, use_container_width=True)
    
            # Anomaly table
            an_col1, an_col2 = st.columns(2)
            with an_col1:
                st.markdown("**Revenue Spikes (unusually HIGH)**")
                if len(spikes) > 0:
                    sp_show = spikes[["Date","Revenue","ZScore"]].copy()
                    sp_show["Revenue"] = sp_show["Revenue"].apply(lambda x: "Rs {:,}".format(int(x)))
                    sp_show["ZScore"]  = sp_show["ZScore"].apply(lambda x: "+" + str(round(x,1)) + " SD")
                    sp_show["Date"] = sp_show["Date"].dt.strftime("%d %b %Y")
                    st.dataframe(sp_show, use_container_width=True, hide_index=True)
                    if lang == "Hinglish":
                        st.caption("In dino mein kuch special tha — sale, festival, ya zyada customers. Analyze karein aur dobara karein!")
                    else:
                        st.caption("Something special happened on these days — sale event, festival, or unusual footfall. Try to replicate it!")
                else:
                    st.info("No unusual spikes found.")
    
            with an_col2:
                st.markdown("**Revenue Drops (unusually LOW)**")
                if len(drops) > 0:
                    dr_show = drops[["Date","Revenue","ZScore"]].copy()
                    dr_show["Revenue"] = dr_show["Revenue"].apply(lambda x: "Rs {:,}".format(int(x)))
                    dr_show["ZScore"]  = dr_show["ZScore"].apply(lambda x: str(round(x,1)) + " SD")
                    dr_show["Date"] = dr_show["Date"].dt.strftime("%d %b %Y")
                    st.dataframe(dr_show, use_container_width=True, hide_index=True)
                    if lang == "Hinglish":
                        st.caption("In dino mein kuch galat tha — band dukan, power cut, ya aur kuch. Wajah dhundhein.")
                    else:
                        st.caption("Something went wrong on these days — shop closure, power cut, billing issue. Investigate the cause.")
                else:
                    st.info("No unusual drops found.")
    
            # Summary
            total_anomalies = len(spikes) + len(drops)
            anomaly_pct = round(total_anomalies / len(all_daily2) * 100, 1)
            if lang == "Hinglish":
                st.info("Kul " + str(total_anomalies) + " anomaly mile (" + str(anomaly_pct) + "% din). " +
                    str(len(spikes)) + " spike aur " + str(len(drops)) + " drop.")
            else:
                st.info("Found " + str(total_anomalies) + " anomalous days (" + str(anomaly_pct) + "% of all days): " +
                    str(len(spikes)) + " spikes and " + str(len(drops)) + " drops.")
    
else:
    st.markdown('---')
    st.info('🔒 ML Analytics (Revenue Forecast, Demand Prediction, Anomaly Detection) is available on the Premium plan.')
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
    import numpy as _np
    from sklearn.linear_model import LinearRegression as _LR

    parts = []
    rev   = df_r["Revenue"].sum() if "Revenue" in df_r.columns else 0
    bills = len(df_r)
    avg_b = rev / bills if bills > 0 else 0

    # ── Para 1: Revenue overview + growth ──
    growth_note = ""
    if len(df_raw_r) > 0 and "Revenue" in df_raw_r.columns:
        dr = df_raw_r.copy()
        dr["Date"] = pd.to_datetime(dr["Date"])
        dr = dr.sort_values("Date")
        max_d = dr["Date"].max()
        split = max_d - pd.Timedelta(days=days_r)
        split_prev = split - pd.Timedelta(days=days_r)
        this_p = dr[dr["Date"] > split]["Revenue"].sum()
        prev_p = dr[(dr["Date"] > split_prev) & (dr["Date"] <= split)]["Revenue"].sum()
        if prev_p > 0:
            g = (this_p - prev_p) / prev_p * 100
            direction = "up" if g >= 0 else "down"
            growth_note = " Revenue is <b>{d} {p}%</b> compared to the equivalent previous period.".format(
                d=direction, p=abs(round(g, 1))
            )
    parts.append(
        "<b>{shop}</b> generated a total revenue of <b>Rs {rev:,}</b> from <b>{bills:,} transactions</b> "
        "over the last {days} days, with an average bill value of <b>Rs {avg:,}</b>.{g}".format(
            shop=shop_r, rev=int(rev), bills=bills, days=days_r, avg=int(avg_b), g=growth_note
        )
    )

    # ── Para 2: Seasonal patterns ──
    if len(df_raw_r) > 0 and "Revenue" in df_raw_r.columns:
        dm2 = df_raw_r.copy()
        dm2["Date"] = pd.to_datetime(dm2["Date"])
        dm2["Month"] = dm2["Date"].dt.to_period("M").astype(str)
        mon_rev = dm2.groupby("Month")["Revenue"].sum()
        if len(mon_rev) >= 2:
            bm = mon_rev.idxmax()
            wm = mon_rev.idxmin()
            mdiff = int((mon_rev[bm] - mon_rev[wm]) / mon_rev[wm] * 100)
            dm2["MonthNum"] = dm2["Date"].dt.month
            month_avg = dm2.groupby("MonthNum")["Revenue"].mean()
            top_months = month_avg.nlargest(3).index.tolist()
            month_names = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
                          7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
            peak_season = ", ".join([month_names[m] for m in sorted(top_months)])
            parts.append(
                "Your best month on record was <b>{bm}</b> (Rs {brev:,}) and your weakest was <b>{wm}</b> -- "
                "a <b>{d}% difference</b>. Historically your peak revenue months are <b>{ps}</b>. "
                "Stock up and schedule extra staff before these months begin to avoid lost sales.".format(
                    bm=bm, wm=wm, d=mdiff, ps=peak_season,
                    brev=int(mon_rev[bm])
                )
            )

    # ── Para 3: Category + product breakdown ──
    top_prod_name = None
    if "Product" in df_r.columns and "Revenue" in df_r.columns and len(df_r) > 0:
        pr = df_r.groupby("Product")["Revenue"].sum().sort_values(ascending=False)
        if len(pr) >= 3:
            t, b = pr.head(3), pr.tail(3)
            cat_note = ""
            if "Category" in df_r.columns:
                cat_rev = df_r.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
                top_cat = cat_rev.index[0]
                top_cat_pct = int(cat_rev.iloc[0] / cat_rev.sum() * 100)
                second_cat = cat_rev.index[1] if len(cat_rev) > 1 else None
                second_cat_pct = int(cat_rev.iloc[1] / cat_rev.sum() * 100) if second_cat else 0
                cat_note = " <b>{cat}</b> leads your categories at {pct}% of revenue, followed by <b>{c2}</b> at {p2}%.".format(
                    cat=top_cat, pct=top_cat_pct, c2=second_cat, p2=second_cat_pct
                )
            parts.append(
                "Your top three products by revenue are <b>{p1}</b> (Rs {v1:,}), "
                "<b>{p2}</b> (Rs {v2:,}), and <b>{p3}</b> (Rs {v3:,}).{cat} "
                "Your slowest movers are <b>{b1}, {b2}, and {b3}</b> -- consider a clearance bundle "
                "or positioning them next to a fast-seller to move stock.".format(
                    p1=t.index[0], v1=int(t.iloc[0]),
                    p2=t.index[1], v2=int(t.iloc[1]),
                    p3=t.index[2], v3=int(t.iloc[2]),
                    b1=b.index[-1], b2=b.index[-2], b3=b.index[-3],
                    cat=cat_note
                )
            )
        top_prod_name = pr.index[0] if len(pr) > 0 else None

    # ── Para 4: Day + hour traffic ──
    if "DayOfWeek" in df_r.columns and "Hour" in df_r.columns and len(df_r) > 0:
        dow_rev = df_r.groupby("DayOfWeek")["Revenue"].sum()
        best_dow = dow_rev.idxmax()
        worst_dow = dow_rev.idxmin()
        hr_rev = df_r.groupby("Hour")["Revenue"].sum()
        ph = int(hr_rev.idxmax())
        top3h = hr_rev.nlargest(3).index.tolist()
        if len(top3h) >= 2:
            second_hour_txt = ", with strong traffic also at {h2}:00-{h3}:00".format(
                h2=top3h[1], h3=top3h[1]+1)
        else:
            second_hour_txt = ""
        parts.append(
            "<b>{d}</b> is your highest-revenue day; <b>{wd}</b> is your slowest -- "
            "consider a mid-week flash sale or a small discount on {wd} to even out footfall. "
            "Your peak selling window is <b>{h}:00-{h1}:00</b>{sht}. "
            "Never be understaffed during these windows.".format(
                d=best_dow, wd=worst_dow,
                h=ph, h1=ph+1,
                sht=second_hour_txt
            )
        )

    # ── Para 5: Payment methods ──
    pay_col_r = next((c for c in ["Payment","Payment_Method","payment"] if c in df_r.columns), None)
    if pay_col_r and len(df_r) > 0 and "Revenue" in df_r.columns:
        pay_rev = df_r.groupby(pay_col_r)["Revenue"].sum().sort_values(ascending=False)
        top_pay = pay_rev.index[0]
        pay_pct = int(pay_rev.iloc[0] / pay_rev.sum() * 100)
        second_pay = pay_rev.index[1] if len(pay_rev) > 1 else None
        second_pct = int(pay_rev.iloc[1] / pay_rev.sum() * 100) if second_pay else 0
        cash_val = pay_rev.get("Cash", 0)
        cash_pct = int(cash_val / pay_rev.sum() * 100)
        cash_note = ""
        if cash_pct > 25:
            cash_note = " Cash still makes up {c}% of transactions -- a small UPI incentive (5 Rs cashback) can shift customers digital and make reconciliation faster.".format(c=cash_pct)
        parts.append(
            "<b>{m}</b> is your top payment method at <b>{p}%</b>, followed by <b>{m2}</b> at {p2}%.{cn} "
            "Keep all terminals charged and reconcile settlements daily.".format(
                m=top_pay, p=pay_pct, m2=second_pay, p2=second_pct, cn=cash_note
            )
        )

    # ── Para 6: Customer loyalty ──
    rr_val = None
    if "Customer" in df_r.columns and len(df_r) > 0:
        cf = df_r.groupby("Customer").size()
        rr_val = (cf > 1).mean() * 100
        avg_visits = round(cf.mean(), 1)
        tc = df_r.groupby("Customer")["Revenue"].sum()
        top_c_spend = int(tc.max())
        loyalty_note = (
            "Your repeat rate is excellent -- regulars are your strongest asset."
            if rr_val >= 50 else
            "A healthy share of customers return. A loyalty programme could push this further."
            if rr_val >= 30 else
            "There is room to grow -- a simple loyalty card or post-purchase WhatsApp message can bring customers back."
            if rr_val >= 15 else
            "Most customers visit only once. A loyalty programme or follow-up message could significantly improve this."
        )
        parts.append(
            "<b>{r}%</b> of customers made more than one purchase, averaging <b>{av} visits</b> each. "
            "{note} Your top customer spent <b>Rs {s:,}</b> -- "
            "consider a VIP tier with early access to new stock to retain your highest-value buyers.".format(
                r=round(rr_val, 1), av=avg_visits, note=loyalty_note, s=top_c_spend
            )
        )

    # ── Para 7: ML Revenue Forecast ──
    forecast_7 = forecast_30 = forecast_lo = forecast_hi = None
    if len(df_raw_r) >= 60 and "Revenue" in df_raw_r.columns:
        try:
            fd = df_raw_r.copy()
            fd["Date"] = pd.to_datetime(fd["Date"])
            all_d = fd.groupby("Date")["Revenue"].sum().reset_index().sort_values("Date").reset_index(drop=True)
            all_d["DayIndex"] = range(len(all_d))
            all_d["DOW"] = all_d["Date"].dt.dayofweek
            dummies = pd.get_dummies(all_d["DOW"], prefix="dow", drop_first=True)
            Xm = pd.concat([all_d[["DayIndex"]], dummies], axis=1).values
            ym = all_d["Revenue"].values
            mdl = _LR().fit(Xm, ym)
            resid_std = _np.std(ym - mdl.predict(Xm))
            last_idx = all_d["DayIndex"].max()
            last_date = all_d["Date"].max()
            fut_dates = [last_date + timedelta(days=i+1) for i in range(30)]
            fut_rows = [{"DayIndex": last_idx+i+1, "DOW": d.dayofweek} for i, d in enumerate(fut_dates)]
            fut_df = pd.DataFrame(fut_rows)
            dow_fut = pd.get_dummies(fut_df["DOW"], prefix="dow")
            for col in dummies.columns:
                if col not in dow_fut.columns:
                    dow_fut[col] = 0
            dow_fut = dow_fut[dummies.columns]
            X_fut = pd.concat([fut_df[["DayIndex"]], dow_fut], axis=1).values
            y_fut = _np.maximum(mdl.predict(X_fut), 0)
            forecast_7  = int(y_fut[:7].sum())
            forecast_30 = int(y_fut.sum())
            forecast_lo = int(max(forecast_30 - 1.28 * resid_std * 30, 0))
            forecast_hi = int(forecast_30 + 1.28 * resid_std * 30)
        except Exception:
            pass

    if forecast_7 is not None:
        parts.append(
            "Based on your historical sales patterns, the <b>next 7 days are forecast to generate "
            "Rs {s7:,}</b>, and the <b>next 30 days Rs {s30:,}</b> "
            "(80% confidence range: Rs {lo:,} to Rs {hi:,}). "
            "Use these figures to plan your procurement budget and staff roster.".format(
                s7=forecast_7, s30=forecast_30, lo=forecast_lo, hi=forecast_hi
            )
        )

    # ── Para 8: Discount health ──
    disc_col_r = next((c for c in ["Discount_Pct","Discount","discount_pct"] if c in df_r.columns), None)
    disc_val = ((df_r[disc_col_r] > 0).mean() * 100) if disc_col_r else 0
    if disc_val > 15:
        avg_disc = round(df_r[disc_col_r].mean(), 1) if disc_col_r else 0
        parts.append(
            "<b>{d}%</b> of your bills included a discount with an average of <b>{ad}% off</b>. "
            "Blanket discounts on every sale quietly erode margins. "
            "Reserve discounts for bundles, slow movers, or loyalty customers -- "
            "this keeps your average bill value healthy without losing footfall.".format(
                d=int(disc_val), ad=avg_disc
            )
        )

    # ── Key Recommendation ──
    if rr_val is not None and rr_val < 20:
        rec = (
            "Focus on customer retention. Only {r}% of customers returned this period. "
            "A simple punch-card scheme, a 10% next-visit discount, or a brief WhatsApp message "
            "after purchase can double your repeat rate within weeks. "
            "Keeping an existing customer costs five times less than acquiring a new one.".format(r=round(rr_val,1))
        )
    elif disc_val > 35:
        rec = (
            "Review your discount policy urgently. Over {d}% of bills include a discount. "
            "Replace blanket discounts with bundle offers (buy 2 get 10% off) or a loyalty rewards card. "
            "You keep more revenue per sale while still giving customers a reason to buy.".format(d=int(disc_val))
        )
    elif forecast_7 is not None and top_prod_name:
        rec = (
            "Your next 7-day forecast is Rs {s7:,}. Lead with <b>{p}</b> -- your top seller. "
            "Make sure it is always in stock and at eye level. "
            "A single stockout on a peak Sunday can cost more revenue than an entire slow weekday.".format(
                s7=forecast_7, p=top_prod_name
            )
        )
    elif top_prod_name:
        rec = (
            "Double down on {p} -- your best-seller. Never run out of stock on this item. "
            "Place it near the entrance or checkout counter to drive impulse purchases.".format(p=top_prod_name)
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

    if FPDF_AVAILABLE and _tier == "premium":
        def _build_pdf(paras, rec, sname):
            import re as _re
            def clean(t):
                # Strip HTML tags first
                t = _re.sub(r"<[^>]+>", "", t)
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
    elif _tier != "premium":
        st.info("🔒 PDF report download is available on the Premium plan.")
    else:
        st.caption("Install fpdf2 to enable PDF download: pip install fpdf2")
