# add_location_faqs.py
import sqlite3

conn = sqlite3.connect("faqs.db")
c = conn.cursor()

rows = [
    ("ask_location", "Where is KNIT located?", "KNIT is located in Sultanpur, Uttar Pradesh."),
    ("ask_location", "Location of KNIT", "KNIT is located in Sultanpur, Uttar Pradesh."),
    ("ask_location", "Where is knit situated?", "KNIT is situated in Sultanpur, Uttar Pradesh."),
    ("ask_location", "KNIT address", "KNIT, Sultanpur – 228118, Uttar Pradesh.")
]

for intent, q, a in rows:
    c.execute("SELECT 1 FROM faqs WHERE lower(question)=?", (q.lower(),))
    if not c.fetchone():
        c.execute("INSERT INTO faqs (intent,question,answer) VALUES (?,?,?)", (intent, q, a))

conn.commit()
conn.close()
print("Location FAQs inserted if missing.")
