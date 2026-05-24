# services/search.py
import sqlite3
from pathlib import Path
import difflib

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "faqs.db"

def _fetch_all_rows():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT intent, question, answer FROM faqs")
    rows = c.fetchall()
    conn.close()
    return rows

def lookup_by_intent(intent: str):
    if not intent:
        return None
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT question, answer FROM faqs WHERE intent=?", (intent,))
    row = c.fetchone()
    conn.close()
    return (row[0], row[1]) if row else (None, None)

def keyword_search(query: str):
    """
    Returns best matching (question, answer) or (None, None).
    Steps:
      1) direct LIKE search on question or answer
      2) token overlap scoring (Jaccard-like)
      3) difflib fuzzy matching on questions
    """
    q = (query or "").strip().lower()
    if not q:
        return (None, None)

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    pattern = f"%{q}%"
    c.execute("SELECT question, answer FROM faqs WHERE lower(question) LIKE ? OR lower(answer) LIKE ?", (pattern, pattern))
    rows = c.fetchall()
    if rows:
        conn.close()
        return (rows[0][0], rows[0][1])

    c.execute("SELECT question, answer FROM faqs")
    all_rows = c.fetchall()
    conn.close()

    q_tokens = set(q.split())
    best_score = 0.0
    best_qa = (None, None)
    for question, answer in all_rows:
        text = f"{question} {answer}".lower()
        tkns = set(text.split())
        inter = q_tokens.intersection(tkns)
        union = q_tokens.union(tkns)
        score = len(inter) / (len(union) + 1e-9)
        if score > best_score:
            best_score = score
            best_qa = (question, answer)

    if best_score >= 0.15:
        return best_qa

    # final fallback: fuzzy match on question text
    best_ratio = 0.0
    best_qa = (None, None)
    for question, answer in all_rows:
        ratio = difflib.SequenceMatcher(None, q, question.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_qa = (question, answer)

    if best_ratio >= 0.45:
        return best_qa

    return (None, None)

def token_overlap_score(text_a: str, text_b: str) -> float:
    """Return simple Jaccard-like score (0..1) between two strings."""
    a = set((text_a or "").lower().split())
    b = set((text_b or "").lower().split())
    if not a or not b:
        return 0.0
    inter = a.intersection(b)
    union = a.union(b)
    return len(inter) / (len(union) + 1e-9)
