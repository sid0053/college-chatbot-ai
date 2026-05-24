# add_missing_all_faqs.py
import sqlite3

conn = sqlite3.connect("faqs.db")
c = conn.cursor()

rows = [
    ("ask_fullform", "What is the full form of KNIT?", "The full form of KNIT is Kamla Nehru Institute of Technology."),
    ("ask_fees", "What is the fee structure for B.Tech?", "The total B.Tech fee is approximately ₹2.5–3.5 lakhs; check official notices for exact current amounts."),
    ("ask_fees", "What is the btech fees?", "The total B.Tech fee is approximately ₹2.5–3.5 lakhs; check official notices for exact current amounts."),
    ("ask_hostel", "What is the hostel fee?", "Hostel fee at KNIT is approximately ₹20,000–₹30,000 per year. Mess charges are separate."),
    ("ask_hostel", "How are hostels allotted?", "Hostel allotment is managed by the hostel office based on availability, seniority and admission rules."),
    ("ask_departments", "How many departments are there in KNIT?", "KNIT has departments such as CSE, IT, ECE, EE, ME, CE and allied departments. See Academics page for current list."),
    ("ask_director", "Who is the director of KNIT?", "For the current director's name and official contact, please check the KNIT official website or contact director@knit.ac.in."),
    ("ask_founding", "When was KNIT founded?", "Please refer to the KNIT official website's About page for the institute's founding/establishment year."),
    ("ask_contact", "Is KNIT affiliated to a university?", "Yes — KNIT is affiliated to Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow.")
]

for intent, q, a in rows:
    c.execute("SELECT 1 FROM faqs WHERE lower(question)=?", (q.lower(),))
    if not c.fetchone():
        c.execute("INSERT INTO faqs (intent, question, answer) VALUES (?, ?, ?)", (intent, q, a))

conn.commit()
conn.close()
print("Inserted missing FAQs (if absent).")
