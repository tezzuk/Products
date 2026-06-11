import streamlit as st
import sqlite3
import os
from datetime import date, datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────

DB_PATH = "invoices.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE,
            client_name TEXT,
            client_gstin TEXT,
            client_address TEXT,
            invoice_date TEXT,
            due_date TEXT,
            items TEXT,
            subtotal REAL,
            total_gst REAL,
            grand_total REAL,
            status TEXT DEFAULT 'Pending',
            notes TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_setting(key, default=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def save_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_next_invoice_number():
    prefix = get_setting("invoice_prefix", "INV")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM invoices")
    count = c.fetchone()[0]
    conn.close()
    return f"{prefix}-{str(count + 1).zfill(3)}"

def save_invoice(inv_number, client_name, client_gstin, client_address,
                 inv_date, due_date, items_str, subtotal, total_gst,
                 grand_total, status, notes):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO invoices
        (invoice_number, client_name, client_gstin, client_address,
         invoice_date, due_date, items, subtotal, total_gst, grand_total,
         status, notes, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (inv_number, client_name, client_gstin, client_address,
          str(inv_date), str(due_date), items_str, subtotal, total_gst,
          grand_total, status, notes, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_invoices():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM invoices ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def update_invoice_status(inv_id, new_status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE invoices SET status=? WHERE id=?", (new_status, inv_id))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# PDF GENERATOR
# ─────────────────────────────────────────────

def generate_pdf(inv_number, inv_date, due_date,
                 biz_name, biz_gstin, biz_address, biz_phone, biz_email, biz_bank,
                 client_name, client_gstin, client_address,
                 items, notes, same_state=True):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=15*mm, leftMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)

    styles = getSampleStyleSheet()
    DARK = colors.HexColor("#1a1a2e")
    ACCENT = colors.HexColor("#4361ee")
    LIGHT = colors.HexColor("#f8f9fa")
    MID = colors.HexColor("#e9ecef")

    h1 = ParagraphStyle("h1", fontSize=22, textColor=ACCENT, spaceAfter=2, leading=26)
    h2 = ParagraphStyle("h2", fontSize=11, textColor=DARK, spaceAfter=2, leading=14, fontName="Helvetica-Bold")
    small = ParagraphStyle("small", fontSize=9, textColor=colors.HexColor("#555555"), leading=13)
    small_bold = ParagraphStyle("small_bold", fontSize=9, textColor=DARK, leading=13, fontName="Helvetica-Bold")
    right_bold = ParagraphStyle("right_bold", fontSize=10, textColor=DARK, alignment=TA_RIGHT, fontName="Helvetica-Bold")
    right = ParagraphStyle("right", fontSize=9, textColor=DARK, alignment=TA_RIGHT)
    center = ParagraphStyle("center", fontSize=9, textColor=colors.HexColor("#555555"), alignment=TA_CENTER)

    story = []

    # ── Header: Business name + TAX INVOICE label ──
    header_data = [
        [Paragraph(biz_name, h1), Paragraph("TAX INVOICE", ParagraphStyle("ti", fontSize=18, textColor=DARK, alignment=TA_RIGHT, fontName="Helvetica-Bold"))]
    ]
    header_table = Table(header_data, colWidths=[95*mm, 85*mm])
    header_table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=6))

    # ── Business info + Invoice meta ──
    biz_lines = f"<b>{biz_name}</b><br/>{biz_address}<br/>GSTIN: {biz_gstin}<br/>Ph: {biz_phone} | {biz_email}"
    inv_meta = f"<b>Invoice No:</b> {inv_number}<br/><b>Date:</b> {inv_date}<br/><b>Due Date:</b> {due_date}"
    meta_table = Table(
        [[Paragraph(biz_lines, small), Paragraph(inv_meta, ParagraphStyle("meta", fontSize=9, alignment=TA_RIGHT, leading=14))]],
        colWidths=[95*mm, 85*mm]
    )
    story.append(meta_table)
    story.append(Spacer(1, 8*mm))

    # ── Bill To ──
    story.append(Paragraph("Bill To", ParagraphStyle("bt", fontSize=9, textColor=ACCENT, fontName="Helvetica-Bold")))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID, spaceBefore=2, spaceAfter=4))
    bill_to = f"<b>{client_name}</b><br/>{client_address}"
    if client_gstin:
        bill_to += f"<br/>GSTIN: {client_gstin}"
    story.append(Paragraph(bill_to, small))
    story.append(Spacer(1, 6*mm))

    # ── Items Table ──
    if same_state:
        col_headers = ["#", "Description", "Qty", "Rate (₹)", "GST%", "CGST (₹)", "SGST (₹)", "Amount (₹)"]
        col_widths = [8*mm, 52*mm, 12*mm, 18*mm, 10*mm, 15*mm, 15*mm, 20*mm]
    else:
        col_headers = ["#", "Description", "Qty", "Rate (₹)", "GST%", "IGST (₹)", "Amount (₹)"]
        col_widths = [8*mm, 60*mm, 12*mm, 18*mm, 10*mm, 18*mm, 24*mm]

    table_data = [col_headers]
    subtotal = 0
    total_cgst = 0
    total_sgst = 0
    total_igst = 0

    for i, item in enumerate(items, 1):
        desc, qty, rate, gst_pct = item["desc"], item["qty"], item["rate"], item["gst"]
        taxable = qty * rate
        subtotal += taxable
        if same_state:
            cgst = round(taxable * gst_pct / 200, 2)
            sgst = round(taxable * gst_pct / 200, 2)
            total_cgst += cgst
            total_sgst += sgst
            row_total = taxable + cgst + sgst
            row = [str(i), desc, str(qty), f"{rate:.2f}", f"{gst_pct}%", f"{cgst:.2f}", f"{sgst:.2f}", f"{row_total:.2f}"]
        else:
            igst = round(taxable * gst_pct / 100, 2)
            total_igst += igst
            row_total = taxable + igst
            row = [str(i), desc, str(qty), f"{rate:.2f}", f"{gst_pct}%", f"{igst:.2f}", f"{row_total:.2f}"]
        table_data.append(row)

    items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("ALIGN", (1,1), (1,-1), "LEFT"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#dee2e6")),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 4*mm))

    # ── Totals ──
    if same_state:
        total_gst = total_cgst + total_sgst
        totals_data = [
            ["Subtotal:", f"₹{subtotal:.2f}"],
            [f"CGST:", f"₹{total_cgst:.2f}"],
            [f"SGST:", f"₹{total_sgst:.2f}"],
            ["", ""],
            ["GRAND TOTAL:", f"₹{subtotal + total_gst:.2f}"],
        ]
    else:
        total_gst = total_igst
        totals_data = [
            ["Subtotal:", f"₹{subtotal:.2f}"],
            [f"IGST:", f"₹{total_igst:.2f}"],
            ["", ""],
            ["GRAND TOTAL:", f"₹{subtotal + total_gst:.2f}"],
        ]

    totals_table = Table(totals_data, colWidths=[85*mm, 35*mm],
                         hAlign="RIGHT")
    totals_table.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "RIGHT"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,-1), (-1,-1), 11),
        ("TEXTCOLOR", (0,-1), (-1,-1), ACCENT),
        ("LINEABOVE", (0,-1), (-1,-1), 1, ACCENT),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(totals_table)

    # ── Bank Details + Notes ──
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID, spaceAfter=4))
    footer_data = [
        [Paragraph(f"<b>Bank Details:</b><br/>{biz_bank}", small),
         Paragraph(f"<b>Notes:</b><br/>{notes or 'Thank you for your business!'}", small)]
    ]
    footer_table = Table(footer_data, colWidths=[95*mm, 85*mm])
    story.append(footer_table)

    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("This is a computer-generated invoice.", center))

    doc.build(story)
    buffer.seek(0)

    grand_total = subtotal + total_gst
    return buffer, subtotal, total_gst, grand_total


# ─────────────────────────────────────────────
# STREAMLIT APP
# ─────────────────────────────────────────────

st.set_page_config(page_title="GST Invoice Manager", page_icon="🧾", layout="wide")
init_db()

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .main .block-container { padding-top: 2rem; }
    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
    }
    .status-paid { color: #2d6a4f; background: #d8f3dc; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .status-pending { color: #9d4edd; background: #f3d9fa; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .status-partial { color: #e76f51; background: #fde8dc; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("# 🧾 GST Invoice")
    st.markdown("---")
    page = st.radio("", ["➕ Create Invoice", "📋 Invoice History", "⚙️ Business Settings"], label_visibility="collapsed")
    st.markdown("---")
    # Quick stats
    all_inv = get_all_invoices()
    total_billed = sum(r[10] for r in all_inv)
    paid_total = sum(r[10] for r in all_inv if r[11] == "Paid")
    pending_total = sum(r[10] for r in all_inv if r[11] == "Pending")
    st.metric("Total Billed", f"₹{total_billed:,.0f}")
    st.metric("Collected", f"₹{paid_total:,.0f}")
    st.metric("Outstanding", f"₹{pending_total:,.0f}")


# ── PAGE: Business Settings ──
if "Settings" in page:
    st.title("⚙️ Business Settings")
    st.caption("This info appears on every invoice.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        biz_name = st.text_input("Business Name *", value=get_setting("biz_name"))
        biz_gstin = st.text_input("GSTIN", value=get_setting("biz_gstin"), placeholder="22AAAAA0000A1Z5")
        biz_phone = st.text_input("Phone", value=get_setting("biz_phone"))
        biz_email = st.text_input("Email", value=get_setting("biz_email"))
    with col2:
        biz_address = st.text_area("Address *", value=get_setting("biz_address"), height=100)
        biz_bank = st.text_area("Bank Details", value=get_setting("biz_bank"),
                                placeholder="Bank: HDFC Bank\nA/C No: 1234567890\nIFSC: HDFC0001234",
                                height=100)
        inv_prefix = st.text_input("Invoice Prefix", value=get_setting("invoice_prefix", "INV"),
                                   help="e.g. INV → INV-001, INV-002...")

    if st.button("💾 Save Settings", type="primary"):
        for k, v in [("biz_name", biz_name), ("biz_gstin", biz_gstin),
                     ("biz_phone", biz_phone), ("biz_email", biz_email),
                     ("biz_address", biz_address), ("biz_bank", biz_bank),
                     ("invoice_prefix", inv_prefix)]:
            save_setting(k, v)
        st.success("Settings saved!")


# ── PAGE: Invoice History ──
elif "History" in page:
    st.title("📋 Invoice History")
    all_inv = get_all_invoices()

    if not all_inv:
        st.info("No invoices yet. Create your first one!")
    else:
        # Filter
        col1, col2 = st.columns([2, 1])
        with col2:
            status_filter = st.selectbox("Filter by status", ["All", "Pending", "Paid", "Partial"])

        filtered = all_inv if status_filter == "All" else [r for r in all_inv if r[11] == status_filter]

        for row in filtered:
            inv_id, inv_num, client, _, _, inv_date, due_date, _, subtotal, gst, total, status, notes, created = row
            status_color = {"Paid": "🟢", "Pending": "🟡", "Partial": "🟠"}.get(status, "⚪")

            with st.expander(f"{status_color} {inv_num}  |  {client}  |  ₹{total:,.0f}  |  {inv_date}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Grand Total", f"₹{total:,.0f}")
                c2.metric("GST", f"₹{gst:,.0f}")
                c3.metric("Status", status)

                new_status = st.selectbox("Update Status", ["Pending", "Partial", "Paid"],
                                          index=["Pending", "Partial", "Paid"].index(status),
                                          key=f"status_{inv_id}")
                if st.button("Update", key=f"upd_{inv_id}"):
                    update_invoice_status(inv_id, new_status)
                    st.success(f"Status updated to {new_status}")
                    st.rerun()

                if notes:
                    st.caption(f"Notes: {notes}")

                # WhatsApp reminder
                if status != "Paid":
                    biz = get_setting("biz_name", "We")
                    reminder = (f"Namaste {client} ji 🙏\n\n"
                                f"Aapka {inv_num} invoice dated {inv_date} ke liye "
                                f"₹{total:,.0f} outstanding hai.\n\n"
                                f"Please payment kar dein. Shukriya!\n\n— {biz}")
                    st.text_area("📱 WhatsApp Reminder (copy this)", value=reminder, height=120, key=f"wa_{inv_id}")


# ── PAGE: Create Invoice ──
else:
    st.title("➕ Create New Invoice")

    biz_name = get_setting("biz_name")
    if not biz_name:
        st.warning("⚠️ Please fill in Business Settings first.")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Client Details")
        client_name = st.text_input("Client Name *")
        client_address = st.text_area("Client Address", height=80)
        client_gstin = st.text_input("Client GSTIN (optional)")

    with col2:
        st.subheader("Invoice Details")
        inv_number = st.text_input("Invoice Number", value=get_next_invoice_number())
        inv_date = st.date_input("Invoice Date", value=date.today())
        due_date = st.date_input("Due Date")
        same_state = st.toggle("Same State (CGST + SGST)", value=True,
                               help="Turn OFF for inter-state transactions (IGST applies)")
        notes = st.text_input("Notes (optional)", placeholder="Payment via UPI / cheque / NEFT")

    st.markdown("---")
    st.subheader("Line Items")

    # Dynamic line items
    if "item_count" not in st.session_state:
        st.session_state.item_count = 1

    col_a, col_b = st.columns([5, 1])
    with col_b:
        if st.button("➕ Add Row"):
            st.session_state.item_count += 1

    items = []
    subtotal_preview = 0
    total_gst_preview = 0

    header = st.columns([4, 1, 1.5, 1.5])
    header[0].markdown("**Description**")
    header[1].markdown("**Qty**")
    header[2].markdown("**Rate (₹)**")
    header[3].markdown("**GST %**")

    for i in range(st.session_state.item_count):
        c1, c2, c3, c4 = st.columns([4, 1, 1.5, 1.5])
        desc = c1.text_input("", placeholder="Product / Service name", key=f"desc_{i}", label_visibility="collapsed")
        qty = c2.number_input("", min_value=1, value=1, key=f"qty_{i}", label_visibility="collapsed")
        rate = c3.number_input("", min_value=0.0, value=0.0, step=100.0, key=f"rate_{i}", label_visibility="collapsed")
        gst_pct = c4.selectbox("", [0, 5, 12, 18, 28], index=2, key=f"gst_{i}", label_visibility="collapsed")

        if desc and rate > 0:
            taxable = qty * rate
            gst_amt = taxable * gst_pct / 100
            items.append({"desc": desc, "qty": qty, "rate": rate, "gst": gst_pct})
            subtotal_preview += taxable
            total_gst_preview += gst_amt

    # Live preview totals
    if items:
        st.markdown("---")
        pc1, pc2, pc3 = st.columns(3)
        pc1.metric("Subtotal", f"₹{subtotal_preview:,.2f}")
        pc2.metric("Total GST", f"₹{total_gst_preview:,.2f}")
        pc3.metric("Grand Total", f"₹{subtotal_preview + total_gst_preview:,.2f}")

    st.markdown("---")
    if st.button("🧾 Generate Invoice PDF", type="primary", disabled=not (client_name and items)):
        import json
        pdf_buf, subtotal, total_gst, grand_total = generate_pdf(
            inv_number=inv_number,
            inv_date=inv_date,
            due_date=due_date,
            biz_name=get_setting("biz_name"),
            biz_gstin=get_setting("biz_gstin"),
            biz_address=get_setting("biz_address"),
            biz_phone=get_setting("biz_phone"),
            biz_email=get_setting("biz_email"),
            biz_bank=get_setting("biz_bank"),
            client_name=client_name,
            client_gstin=client_gstin,
            client_address=client_address,
            items=items,
            notes=notes,
            same_state=same_state
        )

        # Save to DB
        save_invoice(inv_number, client_name, client_gstin, client_address,
                     inv_date, due_date, json.dumps(items),
                     subtotal, total_gst, grand_total, "Pending", notes)

        st.success(f"✅ Invoice {inv_number} created! Grand Total: ₹{grand_total:,.2f}")
        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_buf,
            file_name=f"{inv_number}_{client_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
