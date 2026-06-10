# Tool 3: Student Progress Report Generator — Complete Google Sheets Setup Guide

**For:** Coaching Center Owners and Teachers
**Setup Time:** ~1.5 to 2 hours
**Skill Required:** Basic computer use, no coding needed

---

## OVERVIEW

This Google Sheet has 4 tabs:
1. **Setup** — Subject names and student list (configure once)
2. **Marks Entry** — Teacher fills in marks each month
3. **Summary** — Auto-generated performance summary per student
4. **Report Card** — Clean, formatted view for screenshot and WhatsApp sharing

---

## STEP 1: CREATE THE GOOGLE SHEET

1. Go to **sheets.google.com** and sign in
2. Click **+** (Blank spreadsheet)
3. Name it: `Student Progress Reports — [Your Center Name]`
4. Rename the default Sheet1 tab to: `Setup`
5. Add 3 more tabs: `Marks Entry`, `Summary`, `Report Card`

---

## SHEET 1: SETUP

### Tab Name: `Setup`

This sheet is where you configure everything once. You only need to update it when students join/leave or subjects change.

### Section A: Student List (starting at Row 1)

| A | B | C |
|---|---|---|
| Student ID | Student Name | Class/Batch |

Fill from Row 2:
```
S001 | Rahul Sharma    | Class 10
S002 | Priya Gupta     | Class 10
S003 | Amit Verma      | Class 9
```

### Section B: Subject List (starting at Column E, Row 1)

| E | F |
|---|---|
| Subject Code | Subject Name |

Fill from Row 2:
```
SUB1 | Mathematics
SUB2 | Science
SUB3 | English
SUB4 | Hindi
SUB5 | Social Studies
```

Add or remove subjects as needed. Maximum 8 subjects recommended.

### Section C: Scoring Config (Column H)

| H | I |
|---|---|
| Config | Value |
| Max Marks Per Test | 100 |
| Tests Per Month | 2 |
| Green Threshold (%) | 75 |
| Yellow Threshold (%) | 50 |

---

## SHEET 2: MARKS ENTRY

### Tab Name: `Marks Entry`

This is where the teacher fills in marks every month.

### Column Headers (Row 1):

| A | B | C | D | E | F | G | H | I | J | K |
|---|---|---|---|---|---|---|---|---|---|---|
| Month | Student ID | Student Name | Mathematics | Science | English | Hindi | Social Studies | Total | Percentage | Grade |

Adjust subject columns (D onwards) to match whatever subjects you set up in the Setup sheet.

### Step-by-step Instructions:

**Step 1: Link Student Names**

In cell B2, type a Student ID manually (e.g., S001).

In cell C2, type this formula to auto-fill the name:
```
=IFERROR(VLOOKUP(B2,Setup!$A:$B,2,0),"Student Not Found")
```

**Step 2: Enter Marks**

For each subject column (D, E, F, G, H), the teacher manually types the marks out of 100.

**Step 3: Total Formula**

In cell I2 (Total):
```
=SUM(D2:H2)
```

Adjust the range (D2:H2) to include all your subject columns.

**Step 4: Percentage Formula**

In cell J2 (Percentage) — assuming 5 subjects, each out of 100:
```
=IFERROR(ROUND(I2/500*100,1),0)
```

If you have a different number of subjects, change 500 to (number of subjects × 100).

For example: 4 subjects = divide by 400; 6 subjects = divide by 600.

**Step 5: Grade Formula**

In cell K2 (Grade):
```
=IF(J2>=90,"A+",IF(J2>=75,"A",IF(J2>=60,"B+",IF(J2>=50,"B",IF(J2>=35,"C","D")))))
```

**Step 6: Drag All Formulas Down**

Select cells C2 to K2, then drag down for all student rows.

**Step 7: Month Column**

In Column A (Month), type the month for each batch of entries:
```
June 2025
June 2025
June 2025
...
```

All rows for the same month should have the same value — this helps the Summary sheet work correctly.

### Conditional Formatting for Percentage Column:

1. Select all cells in the Percentage column (J2 to J200)
2. Go to **Format > Conditional formatting**
3. Add Rule 1: Greater than or equal to 75 → Fill color: **Light Green**
4. Add Rule 2: Between 50 and 74.9 → Fill color: **Light Yellow**
5. Add Rule 3: Less than 50 → Fill color: **Light Red/Pink**
6. Click **Done**

### Conditional Formatting for Individual Subject Marks:

1. Select all subject mark cells (D2:H200)
2. Add Rule 1: Greater than or equal to 75 → Light Green
3. Add Rule 2: Between 50 and 74 → Light Yellow
4. Add Rule 3: Less than 50 → Light Red

---

## SHEET 3: SUMMARY

### Tab Name: `Summary`

This sheet gives a per-student overview across all months.

### Column Headers (Row 1):

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| Student ID | Student Name | Latest Month | Latest % | Best Month | Best % | Trend |

### Formulas (Row 2 onwards):

**Cell A2:** Type Student ID manually (S001, S002, etc.) — or link from Setup:
```
=Setup!A2
```

**Cell B2 (Student Name):**
```
=IFERROR(VLOOKUP(A2,Setup!$A:$B,2,0),"")
```

**Cell C2 (Latest Month — finds most recent entry):**
```
=IFERROR(INDEX('Marks Entry'!$A:$A,MATCH(2,1/('Marks Entry'!$B:$B=A2),1)),"No data")
```

**Cell D2 (Latest Percentage):**
```
=IFERROR(INDEX('Marks Entry'!$J:$J,MATCH(1,('Marks Entry'!$B:$B=A2)*('Marks Entry'!$A:$A=C2),0)),"—")
```

Note: This is an array formula. After typing it, press **Ctrl+Shift+Enter** instead of just Enter (on Windows), or **Cmd+Shift+Enter** on Mac. You will see curly braces { } around the formula.

**Cell E2 (Best Month):**
```
=IFERROR(INDEX('Marks Entry'!$A:$A,MATCH(MAXIFS('Marks Entry'!$J:$J,'Marks Entry'!$B:$B,A2),'Marks Entry'!$J:$J,0)),"—")
```

**Cell F2 (Best Percentage):**
```
=IFERROR(MAXIFS('Marks Entry'!$J:$J,'Marks Entry'!$B:$B,A2),"—")
```

**Cell G2 (Trend — simple comparison):**
```
=IFERROR(IF(D2>F2-5,"Improving",IF(D2<F2-10,"Declining","Stable")),"—")
```

Drag all formulas down for each student.

### Conditional Formatting on Summary Sheet:

Select column D (Latest %):
- Greater than or equal to 75 → Green
- Between 50 and 74 → Yellow
- Less than 50 → Red

---

## SHEET 4: REPORT CARD

### Tab Name: `Report Card`

This is the "clean display" sheet — format it nicely so the owner can screenshot and share on WhatsApp.

### Layout Design:

**Row 1:** Center Name (large, bold — e.g., "SHARMA CLASSES — STUDENT REPORT CARD")
**Row 2:** Month: [Month Year] | Class: [Batch]
**Row 3:** (blank separator)
**Row 4:** Student Name: _____________
**Row 5:** (blank)
**Row 6 onwards:** Subject-wise marks table

### Suggested Column Layout:

| A | B | C | D |
|---|---|---|---|
| Subject | Marks Obtained | Out of | Grade |

### Setup Instructions:

**Step 1: Create a dropdown to select student**

1. Click on cell B4 (next to "Student Name:")
2. Go to **Data > Data Validation**
3. Under "Criteria", select **List from a range**
4. Enter: `Setup!$B$2:$B$50`
5. Click **Save**

Now cell B4 is a dropdown — you pick the student name and the report fills in automatically.

**Step 2: Create a dropdown to select month**

1. Click on a cell like B2 (next to "Month:")
2. Add Data Validation — List from a range: any column where you've listed months
3. Or just type the month manually each time

**Step 3: Subject marks formulas**

In the report body, for each subject row:

If your subjects are in rows 8–12, and column A has subject names, column B should have this formula to pull marks:

Cell B8 (Marks for Mathematics):
```
=IFERROR(INDEX('Marks Entry'!$D:$D,MATCH(1,('Marks Entry'!$C:$C=$B$4)*('Marks Entry'!$A:$A=$B$2),0)),"—")
```

Press **Ctrl+Shift+Enter** for this array formula.

- For Science (column E in Marks Entry), change `$D:$D` to `$E:$E`
- For English (column F), use `$F:$F`
- And so on for each subject

Cell C8 (Out of): Type `100` manually

Cell D8 (Grade):
```
=IF(B8="—","—",IF(B8>=90,"A+",IF(B8>=75,"A",IF(B8>=60,"B+",IF(B8>=50,"B",IF(B8>=35,"C","D"))))))
```

**Step 4: Overall row at the bottom**

| Total | =SUM(B8:B12) | =SUM(C8:C12) | |
| Percentage | =ROUND(B13/C13*100,1)&"%" | | |
| Overall Grade | =(use grade formula on percentage) | | |

**Step 5: Conditional formatting on marks column (B)**

Select B8:B12:
- Greater than or equal to 75 → Green text or Green fill
- Between 50 and 74 → Yellow fill
- Less than 50 → Red fill

### Making it Screenshot-Friendly:

1. Select all cells of the report card area
2. Go to **Format > Borders** — add thick outer border and thin inner borders
3. Center align all text
4. Make the header row (Row 1) bold and larger font (14–16pt)
5. Set a light blue or white background for the whole table
6. Hide all empty columns outside the report area (right-click column header > Hide column)

### How to Use Report Card Tab:

1. Go to Report Card tab
2. Select the student's name from the dropdown in B4
3. Type the month in B2
4. The marks fill in automatically
5. Take a screenshot (Windows: Win + Shift + S, then crop)
6. Send screenshot to parent on WhatsApp

---

## MONTHLY WORKFLOW FOR TEACHER

### After Each Test (5–10 minutes):
1. Open Google Sheet
2. Go to **Marks Entry** tab
3. Add a new row for each student
4. Fill: Month, Student ID, and all subject marks
5. Total, Percentage, and Grade fill automatically

### For Parent Reports (2 minutes per student):
1. Go to **Report Card** tab
2. Select student name from dropdown
3. Check month is correct
4. Take a screenshot
5. Send to parent via WhatsApp with a short message

---

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| VLOOKUP shows "Student Not Found" | Check that Student ID in Marks Entry matches exactly what's in Setup |
| Summary formulas show errors | Make sure to press Ctrl+Shift+Enter for array formulas |
| Report Card not pulling marks | Verify student name dropdown selection matches exactly what's in Marks Entry |
| Colors not showing | Re-apply conditional formatting; check the range is correct |
| Percentage formula gives wrong result | Count your subjects and adjust the divider (subjects × 100) |

---

## SHEET PROTECTION (OPTIONAL — RECOMMENDED)

To prevent teachers from accidentally editing formulas:

1. Select all formula cells (not the ones teachers fill in)
2. Go to **Data > Protect sheets and ranges**
3. Add a description and set a PIN or restrict to yourself only
4. Teachers can only edit the allowed data-entry columns

---

*Setup guide prepared by Aayushman — for questions, contact via WhatsApp*
