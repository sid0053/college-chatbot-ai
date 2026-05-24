# add_department_faqs.py
import sqlite3

conn = sqlite3.connect("faqs.db")
c = conn.cursor()

rows = [
    ("ask_departments", "How many departments are there in KNIT?", "KNIT has departments such as Computer Science & Engineering (CSE), Information Technology (IT), Electronics & Communication (ECE), Electrical (EE), Mechanical (ME), Civil (CE) and allied departments. See the Academics page on the official site for the current list."),
    ("ask_departments", "Departments in KNIT", "KNIT departments include CSE, IT, ECE, EE, ME, CE and other allied departments. For updates, check the Academics page of the official KNIT website."),
    ("ask_departments", "list of departments at knit", "Departments include Computer Science & Engineering, Information Technology, Electronics & Communication, Electrical, Mechanical, Civil and allied departments. Visit the official site for the exact, up-to-date list.")
]

for intent, q, a in rows:
    c.execute("SELECT 1 FROM faqs WHERE lower(question)=?", (q.lower(),))
    if not c.fetchone():
        c.execute("INSERT INTO faqs (intent, question, answer) VALUES (?, ?, ?)", (intent, q, a))

conn.commit()
conn.close()
print("Inserted department FAQs (if missing).")
