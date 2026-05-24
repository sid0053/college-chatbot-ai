# add_placement_faqs.py
import sqlite3

conn = sqlite3.connect("faqs.db")
c = conn.cursor()

rows = [
    ("ask_placements", "What is the placement percentage at KNIT?", "Placement statistics vary by year and branch. Historically, many branches have good placement rates; for exact placement percentage and year-wise reports, check the Training & Placement Cell page on the official KNIT website or contact placements@knit.ac.in."),
    ("ask_placements", "placement percentage", "Placement statistics vary by year and branch. See the official T&P reports on the KNIT website or contact the Placement Cell for exact numbers."),
    ("ask_placements", "placements at knit", "KNIT's Training & Placement Cell coordinates internships and placements. For recent placement percentages and recruiter lists, please consult the official placement report available on the college website or contact placements@knit.ac.in."),
    ("ask_placements", "what is the placement record", "Placement records change each year. Please see the official placement report on KNIT's website or contact the Training & Placement office for the latest numbers.")
]

for intent, q, a in rows:
    c.execute("SELECT 1 FROM faqs WHERE lower(question)=?", (q.lower(),))
    if not c.fetchone():
        c.execute("INSERT INTO faqs (intent, question, answer) VALUES (?, ?, ?)", (intent, q, a))

conn.commit()
conn.close()
print("Inserted placement FAQs (if missing).")
