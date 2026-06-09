# Product 3 — GST Invoice Automation System
*Last updated: 2026-06-09*

## What It Does
A web app where a business fills in client name + items + amounts → system instantly generates:
- A professional, GST-compliant PDF invoice
- Auto-calculates CGST + SGST / IGST
- Saves invoice history (never lose a record)
- Tracks who has paid and who hasn't
- Sends payment reminders (optional)

Solves all 3 pain points:
✅ Making invoices is slow → done in 60 seconds
✅ Invoices look amateur → professional PDF with logo
✅ Can't track payments → live payment status dashboard

## Tech Stack
- **Streamlit** or plain **Flask** web app
- **ReportLab** (Python) → PDF generation
- **SQLite** → invoice storage (no server DB needed)
- **Deployed on Render/Railway** (free)
- Claude builds all of it

## Pricing
- One-time setup: **₹8,000–₹12,000**
- With custom logo + letterhead: **₹12,000**

## Delivery Time
2 days

## Kanpur Target Customers

### Leather & Textile Manufacturers
Issue B2B invoices constantly. Many still use Word templates.
High volume = high pain = high willingness to pay.
- Find on IndiaMART, TradeIndia, Google Maps "leather manufacturer Kanpur"

### Freelance Professionals (CAs, Consultants, Architects)
They bill clients monthly. Need professional invoices with GST.
- Search "CA office Kanpur", "consultant Kanpur"

### Small Factories & Workshops (Panki Industrial Area, Fazalganj)
Kanpur has a large industrial belt. Small units issue invoices daily.
- Google Maps: "factory Panki industrial area Kanpur"

### Home-Based Businesses (Tiffin, Catering, Boutique)
Rising segment. They send WhatsApp invoices or paper receipts. Easy upsell.

### Medical Stores / Diagnostics Labs
Issue bills constantly, need GST compliance.

## Key Features
| Feature | Details |
|---|---|
| Invoice Generator | Fill form → get PDF in 10 seconds |
| GST Calculator | Auto CGST/SGST (same state) or IGST (other state) |
| Invoice History | Search by client, date, amount |
| Payment Tracker | Mark as Paid / Pending / Partial |
| Reminder Button | One click → copies WhatsApp reminder message |
| Custom Branding | Business name, logo, address, GSTIN |
| Invoice Numbering | Auto-increments (INV-001, INV-002...) |

## Edge Cases
- Client doesn't have GST number yet → system works without it, marks "non-GST invoice"
- Multiple tax rates on one invoice (5%, 12%, 18%) → handled per line item
- Credit notes / cancellations → included as a feature
- Client wants to email invoice → PDF download button, they send manually

## Sales Pitch
```
Namaste Sir! 🙏

Abhi invoice kaise banate hain? Word file? Excel?

Main ek web tool banata hoon:
• Client ka naam daliye → PDF invoice 10 seconds mein ready
• GST automatically calculate hoti hai
• Kaun paid hai, kaun nahi — sab track hota hai
• Professional look — clients impress honge

IIT Kanpur student. One-time: ₹8,000
Interested? Free demo de sakta hoon.
```
