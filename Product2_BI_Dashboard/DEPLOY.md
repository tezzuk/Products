# Deploy — BI Dashboard
*Deploys in ~10 minutes. Free on Streamlit Cloud.*

---

## Step 1: Put Code on GitHub
1. github.com → **New Repository** → name: `bi-dashboard-demo`
2. Upload both files:
   - `app.py`
   - `requirements.txt`
3. Commit changes

---

## Step 2: Deploy on Streamlit Cloud
1. **share.streamlit.io** → New app
2. Repo: `bi-dashboard-demo` | Main file: `app.py`
3. Click Deploy — live in ~2 min

---

## For the Demo
- The app loads with **sample restaurant data instantly** — no setup needed
- Change the "Business Type" dropdown to match your prospect's industry
- The charts update immediately
- Show the CSV upload: "Give me your Excel, I load it in 30 seconds"

---

## For a Paying Client
1. Get their sales data (Excel/CSV export from wherever they track)
2. Clean it if needed (Claude can do this)
3. Upload into the dashboard — they see their real numbers immediately
4. Show them how to do it themselves going forward
5. Hand off the live URL

For **persistent data + their own login**: deploy on **Railway** instead of Streamlit
(same code, ask me for help — adds 1 hour setup time, charge ₹2,000 extra).

---

## Sample CSV Format (send this to clients)
```
Date,Product,Qty,Price,Customer
2026-06-01,Dal Makhani,3,180,Rahul Sharma
2026-06-01,Biryani,2,200,Priya Singh
2026-06-02,Thali,5,150,Walk-in
```
Date format: YYYY-MM-DD (or DD/MM/YYYY also works)
