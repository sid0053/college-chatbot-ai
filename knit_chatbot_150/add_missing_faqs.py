# add_missing_faqs.py
import sqlite3

conn = sqlite3.connect("faqs.db")
c = conn.cursor()
rows = [
 ("ask_fees", "What is the fee structure for B.Tech?", "The total B.Tech fee is approximately ₹2.5–3.5 lakhs for the entire course; exact amounts vary each year—check official notices for the latest figure."),
 ("ask_fees", "What is the fees of BTech?", "The total B.Tech fee is approximately ₹2.5–3.5 lakhs for the entire course; exact amounts vary each year—check official notices for the latest figure."),
 ("ask_fees", "What is the fees?", "The total B.Tech fee is approximately ₹2.5–3.5 lakhs for the entire course; exact amounts vary each year—check official notices for the latest figure."),
 ("ask_general", "How many departments are there in KNIT?", "KNIT has departments such as Computer Science & Engineering, Information Technology, Electronics & Communication, Electrical, Mechanical, Civil and allied departments. For the exact current list, check the Academics page on the official site.")
]
c.executemany("INSERT INTO faqs (intent, question, answer) VALUES (?, ?, ?)", rows)
conn.commit()
conn.close()
print("Inserted missing FAQ variants.")
