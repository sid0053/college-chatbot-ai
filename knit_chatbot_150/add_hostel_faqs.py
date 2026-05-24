# add_hostel_faqs.py
import sqlite3
conn = sqlite3.connect("faqs.db")
c = conn.cursor()
rows = [
    ("ask_hostel", "What is the hostel fee?", "Hostel fee at KNIT is approximately ₹10,000 per year depending on the hostel and facilities. Mess charges are separate."),
    ("ask_hostel", "What is the hostel fees?", "Hostel fee at KNIT is approximately ₹10,000 per year depending on the hostel and facilities. Mess charges are separate."),
    ("ask_hostel", "How are hostels allotted?", "Hostel rooms are allotted by the hostel office based on first-year allotment rules, seniority, and availability. Freshers usually get allocation during induction based on merit/category and room availability."),
    ("ask_hostel", "How are hostels allotted to students?", "Hostel allotment is done by the student affairs/hostel office, usually during the start of the semester. Priority rules (new joiners, seniors, reserved categories) may apply.")
]
c.executemany("INSERT INTO faqs (intent, question, answer) VALUES (?, ?, ?)", rows)
conn.commit()
conn.close()
print("Inserted hostel FAQs.")
