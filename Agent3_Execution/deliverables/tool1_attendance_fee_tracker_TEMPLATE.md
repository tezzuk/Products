# Tool 1: Attendance + Fee Tracker — Complete Google Sheets Setup Guide

**For:** Coaching Center Owners
**Setup Time:** ~1.5 to 2 hours
**Skill Required:** Basic computer use, no coding needed

---

## OVERVIEW

This Google Sheet has 3 tabs:
1. **Students** — Master list of all students and their fee details
2. **Attendance** — Daily attendance marking
3. **Fees** — Fee collection tracker with automatic due calculations

---

## STEP 1: CREATE THE GOOGLE SHEET

1. Go to **sheets.google.com** and sign in with your Google account
2. Click the **+** button (Blank spreadsheet)
3. Name it: `Coaching Center Tracker — [Your Center Name]`
4. You will see "Sheet1" at the bottom — right-click it, select **Rename**, type: `Students`
5. Click the **+** icon at the bottom to add a new sheet — name it: `Attendance`
6. Add one more sheet — name it: `Fees`

---

## SHEET 1: STUDENTS

### Tab Name: `Students`

### Column Headers (Row 1):

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| Student ID | Student Name | Parent Name | Parent WhatsApp | Class/Batch | Monthly Fee (₹) | Admission Date | Status |

### How to Fill:

- **Row 1** = Headers (bold these — select row 1, press Ctrl+B)
- **Row 2 onwards** = One student per row
- **Student ID**: Use S001, S002, S003... for each student
- **Status**: Type "Active" or "Inactive"

### Example Data (Row 2):

```
S001 | Rahul Sharma | Rajesh Sharma | 9876543210 | Class 10 | 1500 | 01/06/2025 | Active
```

### Freeze Header Row:

1. Click on Row 1 (the header row)
2. Go to **View > Freeze > 1 row**
   Now the header stays visible when you scroll down.

---

## SHEET 2: ATTENDANCE

### Tab Name: `Attendance`

### Column Headers (Row 1):

| A | B | C | D | E | F | ... |
|---|---|---|---|---|---|-----|
| Student ID | Student Name | 01-Jun | 02-Jun | 03-Jun | 04-Jun | (continue for each date) |

### Setup Instructions:

**Step 1: Copy student names from the Students sheet**

In cell A2, type this formula and drag it down for all students:
```
=Students!A2
```

In cell B2, type this formula and drag it down:
```
=Students!B2
```

Drag both formulas down for as many rows as you have students (e.g., if you have 40 students, drag to row 41).

**Step 2: Add dates across the top**

- Cell C1: Type `01-Jun` (or the first date of the month)
- Cell D1: `=C1+1` — then drag this formula right across all columns for the whole month (30 or 31 columns)
- Format the date row: Select C1 to AF1 (or however many days), right-click > Format Cells > Number > Custom date format: `dd-mmm`

**Step 3: Mark attendance daily**

Each day, go to the column for that date and type:
- `P` = Present
- `A` = Absent
- `L` = Late
- Leave blank = Not marked yet

**Step 4: Add Attendance Count Columns (at the end of the month)**

After all date columns, add these headers:

| Column | Header | Formula (for Row 2) |
|--------|--------|---------------------|
| Next empty column | Total Present | `=COUNTIF(C2:AG2,"P")` |
| Next column | Total Absent | `=COUNTIF(C2:AG2,"A")` |
| Next column | Attendance % | `=IFERROR(ROUND((C2:AG column for Present)/31*100,1)&"%","")` |

Simpler formula for Attendance %:
```
=IFERROR(ROUND(COUNTIF(C2:AG2,"P")/COUNTA(C1:AG1)*100,1)&"%","")
```

Note: Replace `AG` with whichever column is the last date column in your sheet.

Drag all three formulas down for every student row.

### Conditional Formatting for Attendance:

1. Select all the date cells (C2 to last date, last student row)
2. Go to **Format > Conditional formatting**
3. Add Rule 1: "Text is exactly" = `P` → Background color: Light Green
4. Add Rule 2: "Text is exactly" = `A` → Background color: Light Red/Pink
5. Add Rule 3: "Text is exactly" = `L` → Background color: Light Yellow
6. Click **Done**

---

## SHEET 3: FEES

### Tab Name: `Fees`

### Column Headers (Row 1):

| A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|
| Student ID | Student Name | Monthly Fee (₹) | Month | Due Date | Amount Paid (₹) | Date Paid | Payment Mode | Status |

### Setup Instructions:

**Step 1: Link Student ID and Name**

In cell A2:
```
=Students!A2
```

In cell B2:
```
=Students!B2
```

In cell C2 (Monthly Fee — pulls automatically from Students sheet):
```
=Students!F2
```

Drag all three formulas down for all students.

**Step 2: Fill in each month's data**

For each student, each month gets one row:
- **D2 (Month):** Type `June 2025` (or whatever month)
- **E2 (Due Date):** Type the date fees are due, e.g., `05/06/2025`
- **F2 (Amount Paid):** Fill this when payment is received
- **G2 (Date Paid):** Fill the actual payment date
- **H2 (Payment Mode):** Cash / UPI / Bank Transfer
- **I2 (Status):** Use the formula below

**Step 3: Auto-Status Formula**

In cell I2, paste this formula:
```
=IF(F2=C2,"Paid",IF(AND(F2<C2,F2>0),"Partial",IF(AND(ISBLANK(F2),TODAY()>E2),"Overdue","Pending")))
```

This formula automatically shows:
- **Paid** — if amount paid equals the monthly fee
- **Partial** — if some amount is paid but not full
- **Overdue** — if no payment made and due date has passed
- **Pending** — if due date has not yet passed

Drag this formula down for all rows.

**Step 4: Days Overdue Column**

Add one more column after Status:

| Column | Header | Formula |
|--------|--------|---------|
| J | Days Overdue | `=IF(I2="Paid",0,IF(TODAY()>E2,TODAY()-E2,0))` |

This shows how many days overdue the payment is.

**Step 5: Total Pending Dues (Summary)**

At the top of the sheet (or in a separate summary area), you can add:

In a blank cell, type this label: `Total Fees Pending This Month:`
Next to it:
```
=SUMIF(I2:I200,"Overdue",C2:C200)+SUMIF(I2:I200,"Pending",C2:C200)
```

---

## CONDITIONAL FORMATTING FOR FEES SHEET

### Red Highlighting (Fee overdue more than 15 days):

1. Select the entire data range (A2 to J200)
2. Go to **Format > Conditional formatting**
3. Set range to: `A2:J200`
4. Under "Format cells if", select: **Custom formula is**
5. Enter:
   ```
   =$J2>15
   ```
6. Set fill color to: **Red (or light red)**
7. Click **Done**

### Green Highlighting (Fee paid):

1. Add another rule for the same range
2. Custom formula:
   ```
   =$I2="Paid"
   ```
3. Set fill color to: **Light Green**
4. Click **Done**

### Yellow Highlighting (Due within 5 days — upcoming reminder):

1. Add another rule
2. Custom formula:
   ```
   =AND($I2="Pending",$E2-TODAY()<=5,$E2-TODAY()>=0)
   ```
3. Set fill color to: **Light Yellow**

---

## QUICK DAILY WORKFLOW FOR OWNER

### Every Morning (2 minutes):
1. Open the sheet on phone or laptop
2. Go to **Attendance** tab
3. Find today's date column
4. Mark P/A/L for each student

### When a Parent Pays Fees (1 minute):
1. Go to **Fees** tab
2. Find the student's row for the current month
3. Fill in: Amount Paid, Date Paid, Payment Mode
4. Status column updates automatically

### At Month End (5 minutes):
1. Go to **Fees** tab
2. All red rows = overdue fees to follow up
3. Note down the "Days Overdue" column
4. Use the WhatsApp templates (Tool 2) to send reminders

---

## TIPS FOR THE OWNER

- **Backup:** Go to File > Download > Microsoft Excel (.xlsx) once a month
- **Mobile Access:** Install the Google Sheets app — you can mark attendance from your phone
- **Add New Students:** Just add a new row in the Students sheet; the other sheets will include them when you drag the formulas down
- **New Month:** For the Fees sheet, copy last month's rows, update the Month and Due Date columns, and clear the payment columns

---

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Formula shows #REF! error | You may have deleted a row — re-enter the formula |
| Status not updating | Check that Due Date column (E) has a proper date, not text |
| Attendance % shows error | Make sure date headers in row 1 are actual dates, not text |
| Red/Green color not showing | Re-check conditional formatting range includes your data rows |

---

*Setup guide prepared by Aayushman — for questions, contact via WhatsApp*
