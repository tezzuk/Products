# Coaching Centre — Railway Variables Template
*Copy this, fill in the blanks, paste into Railway Variables tab*

---

## REQUIRED VARIABLES

```
BUSINESS_NAME     = [Centre Name] e.g. Omega Career Institute

BUSINESS_TYPE     = Coaching Centre

BUSINESS_ADDRESS  = [Full address] e.g. Shop 12, Kalyanpur Main Road, Kanpur

BUSINESS_TIMINGS  = [All batch timings] e.g. Morning: 6AM-8AM | Evening: 4PM-7PM | Sun: 9AM-12PM

BUSINESS_PHONE    = [Owner's number] e.g. 9876543210

BUSINESS_SERVICES = [Subjects/Batches offered]
e.g. JEE Mains+Advanced | NEET | Class 10 (Math+Science) | Class 12 (PCM) | Foundation (Class 8-9)

BUSINESS_PRICING  = [Fee structure]
e.g. JEE/NEET: Rs 2500/month | Class 10-12: Rs 1500/month | Registration fee: Rs 500 one-time

BUSINESS_EXTRA    = [Anything else useful]
e.g. Free demo class available | Small batches (max 20 students) | Study material included | Online classes also available

ENABLE_APPOINTMENTS = true

ENABLE_ORDERS     = false

DASHBOARD_KEY     = [Set a password] e.g. omega2024
```

---

## CUSTOM_FAQ (paste as one line in Railway)

```
CUSTOM_FAQ = {"Admission kaise hogi?":"Pehle ek free demo class attend karein, phir form fill karein. Demo ke liye apna naam aur number dein.","Results kaisa hai?":"Hamare 2024 batch mein 12 students ne JEE clear kiya aur 8 ne NEET. Results hamare centre pe dekh sakte hain.","Faculty kaun hai?":"Hamare teachers IIT aur NIT qualified hain with 5-10 years experience.","Online classes hain?":"Haan, recorded lectures available hain after each class at no extra cost.","Demo class milega?":"Bilkul! First class free hai. Apna naam aur number dein, hum schedule karenge.","Books included hain?":"Study material included hai fees mein. External books ki zarurat nahi.","Exam hota hai?":"Haan, weekly tests aur monthly exams hote hain with detailed feedback.","Hostel hai?":"Abhi hostel facility nahi hai. Nearby PG ki list de sakte hain."}
```

---

## HOW TO FILL THIS FOR A NEW CLIENT

**Step 1** — Call the coaching centre and ask:
- Kaunse subjects/batches hain?
- Fees kya hain?
- Timings kya hain?
- Koi special feature? (small batch, IIT faculty, free demo etc.)
- Kitne students ne result diya last year?

**Step 2** — Fill the template above with their answers

**Step 3** — Railway → your service → Variables tab → paste all values

**Step 4** — Railway auto-redeploys in 30 seconds → bot is live for that centre

---

## SAMPLE — PRE-FILLED (use this as demo)

```
BUSINESS_NAME     = Omega Career Institute
BUSINESS_TYPE     = Coaching Centre
BUSINESS_ADDRESS  = Kakadeo, Kanpur (near Civil Hospital)
BUSINESS_TIMINGS  = Morning Batch: 6AM-8AM | Evening Batch: 4PM-7PM | Weekend: 9AM-1PM
BUSINESS_PHONE    = 9876543210
BUSINESS_SERVICES = JEE Mains+Advanced | NEET UG | Class 10 (Math+Science) | Class 12 (PCM+PCB) | Foundation Batch (Class 8-9)
BUSINESS_PRICING  = JEE/NEET Batch: Rs 2500/month | Class 10-12: Rs 1800/month | Foundation: Rs 1200/month | One-time registration: Rs 500
BUSINESS_EXTRA    = First demo class FREE | Small batches max 20 students | Study material included | IIT-qualified faculty | 10+ years experience | Weekly tests included
ENABLE_APPOINTMENTS = true
ENABLE_ORDERS     = false
DASHBOARD_KEY     = omega2024
CUSTOM_FAQ        = {"Admission kaise hogi?":"Pehle ek free demo class attend karein. Demo ke liye apna naam aur number dein, hum schedule karenge.","Results kaisa hai?":"2024 mein 12 JEE aur 8 NEET qualifiers. Details centre pe milenge.","Faculty kaun hai?":"IIT aur NIT qualified teachers, 10+ years experience.","Demo class free hai?":"Bilkul! Pehli class FREE hai. Apna naam aur number dein.","Books milti hain?":"Haan, study material fees mein included hai.","Batch size kitna hai?":"Max 20 students per batch — personal attention guaranteed."}
GEMINI_API_KEY    = [your key]
```

---

## WHAT THE BOT HANDLES AUTOMATICALLY

| Parent asks | Bot replies |
|---|---|
| "Admission kaise hogi?" | Free demo class ka process explain karta hai |
| "Fees kya hain?" | Full fee structure bata deta hai |
| "Timings kya hain?" | Sabhi batch timings deta hai |
| "Demo class chahiye" | Appointment flow start → naam → number → date → confirm |
| "JEE ke liye best hai?" | Haan, resources aur results bata deta hai |
| "Hostel hai?" | Custom FAQ se answer (ya lead collect karta hai) |
| Koi unknown sawaal | Naam + number collect → owner call karega |

---

## OUTREACH MESSAGE (send to coaching centres from your list)

```
Namaste Sir/Ma'am

Main Aayushman hoon, IIT Kanpur ka student.

Aapke coaching centre ke liye ek AI WhatsApp assistant
banata hoon jo roz ke sawaal khud handle kare:
- "Fees kya hain?" 
- "Demo class milega?"
- "Admission kaise hogi?"
- "Timings kya hain?"

Parents 24/7 message kar sakte hain, bot turant reply karta hai.
Jab bot na jaane - parent ka naam+number collect karke
aapko bhej deta hai.

IIT Kanpur se hoon. Setup: Rs 8,000 one-time.
Free demo de sakta hoon - aap khud WhatsApp karke test karein.

Interest hai?
— Aayushman, IIT Kanpur
```
