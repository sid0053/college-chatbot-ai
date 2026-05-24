# routes/api.py
from flask import Blueprint, request, jsonify
import joblib, re, logging, os
from pathlib import Path
from services.search import lookup_by_intent, keyword_search, token_overlap_score

api_bp = Blueprint("api", __name__)
MODEL_PATH = Path(__file__).resolve().parent.parent / "intent_pipeline.joblib"
try:
    MODEL = joblib.load(MODEL_PATH)
except Exception:
    logging.exception("Failed to load intent model")
    MODEL = None

# Rule-based patterns (more comprehensive)
GREETING = re.compile(r"\b(hi|hello|hey|hii|good\s?(morning|afternoon|evening))\b", re.I)
FAREWELL = re.compile(r"\b(bye|goodbye|see you|see ya|take care|good night|gn)\b", re.I)
THANKS = re.compile(r"\b(thanks?|thank you|thx)\b", re.I)

# Smalltalk / chit-chat (detect non-KNIT conversational queries)
SMALLTALK = re.compile(
    r"\b(how are you|who are you|what can you do|how's it going|are you there|tell me about yourself|what is your name|who made you)\b",
    re.I
)

CONF_THRESHOLD = 0.45   # require at least 45% prob to trust model

# ensure logs directory exists
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
UNMATCHED_FILE = LOG_DIR / "unmatched_queries.txt"

def log_unmatched(q_norm):
    try:
        with open(UNMATCHED_FILE, "a", encoding="utf-8") as f:
            f.write(q_norm.replace("\n", " ") + "\n")
    except Exception:
        logging.exception("Failed to write unmatched query")

@api_bp.post("/ask")
def ask():
    # Read JSON safely and accept several field names
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "expected JSON body (Content-Type: application/json)", "reply": None}), 400

    # accept message/question/q/text/query
    q = (
        (payload.get("message") or
         payload.get("question") or
         payload.get("q") or
         payload.get("text") or
         payload.get("query") or
         "")
    ).strip()

    if not q:
        return jsonify({"error": "missing question text (message/query/question/q/text)", "reply": None}), 400

    # Keep raw and normalized versions
    q_raw = q
    # Normalize: lowercase + remove punctuation (keep a-z, 0-9, whitespace)
    q_norm = re.sub(r"[^a-z0-9\s]", "", q_raw.lower()).strip()

    if not q_norm:
        return jsonify({"reply": "Please type a question.", "meta": {"error": "empty_after_normalize"}}), 400

    # 0) deterministic rule-based intents
    if GREETING.search(q_norm):
        if re.search(r"good\s?morning", q_norm):
            return jsonify({"reply": "Good morning! How can I help you today?", "meta": {"intent": "greeting.morning"}})
        return jsonify({"reply": "Hello! How can I help you today?", "meta": {"intent": "greeting"}})

    # 0.5) Smalltalk (short conversational queries)
    if SMALLTALK.search(q_norm):
        return jsonify({
            "reply": "I'm doing well — thanks! I'm here to help with KNIT-related questions. How can I help you today?",
            "meta": {"intent": "smalltalk"}
        })

    if THANKS.search(q_norm):
        return jsonify({"reply": "You're welcome! Anything else I can help with?", "meta": {"intent": "thanks"}})

    if FAREWELL.search(q_norm):
        return jsonify({"reply": "Goodbye — have a great day!", "meta": {"intent": "farewell"}})

    # --- Runtime-like deterministic rules (mock/live-looking responses) ---
    # College timings / timetable
    if re.search(r"\b(timing|timetable|time table|schedule|college hours|college timing|class timings|class timing|college timings)\b", q_norm):
        return jsonify({
            "reply": "College hours are typically from 9:30 AM to 5:00 PM. For branch-wise timetables, check the Academics page or ask for a specific branch/semester.",
            "meta": {"intent": "runtime_info", "source": "rule"}
        })

    # Placement stats (mock/live-looking)
    if re.search(r"\b(placement|placement rate|highest package|packages|placements)\b", q_norm):
        return jsonify({
            "reply": "As of this semester the placement rate is around 82% with the highest reported package of ₹15 LPA. For official placement reports, see the Training & Placement cell.",
            "meta": {"intent": "placements", "source": "rule"}
        })

    # Hostel seat availability / allotment
    if "hostel" in q_norm and re.search(r"\b(seat|available|vacant|availability|allotment|allocate)\b", q_norm):
        return jsonify({
            "reply": "Currently, hostel seats are limited. First-year allotment is prioritized during induction; afterwards rooms are allotted based on seniority and availability. Contact the Hostel Office for exact availability.",
            "meta": {"intent": "hostel_live", "source": "rule"}
        })

    # Attendance related (mock)
    if re.search(r"\b(attendance|present|absent|attendance percentage|attendance percent)\b", q_norm):
        return jsonify({
            "reply": "Attendance is maintained by each department. Typically, minimum attendance required is 75% for eligibility in exams. For your exact attendance, check the Student Portal or contact the Academic Office.",
            "meta": {"intent": "attendance", "source": "rule"}
        })

    # Exam dates / results release (mock)
    if re.search(r"\b(exam date|exam dates|result|results|exam schedule|semester exam|semester exams)\b", q_norm):
        return jsonify({
            "reply": "Exam schedules and result release dates are published on the official website under the 'Examinations' section. If you ask for a specific exam (e.g., 'When are B.Tech semester exams?'), I can provide a mock example.",
            "meta": {"intent": "exams", "source": "rule"}
        })

    # Contact info / office hours
    if re.search(r"\b(contact|phone|email|office hours|office timing|contact number)\b", q_norm):
        return jsonify({
            "reply": "For administrative queries contact the college office at +91-12345-67890 or email admin@knit.ac.in. For placements, contact placement@knit.ac.in. (These are sample contacts for demo.)",
            "meta": {"intent": "contact_info", "source": "rule"}
        })

    # Results / grade related
    if re.search(r"\b(result|marks|grades|gpa|cgpa)\b", q_norm):
        return jsonify({
            "reply": "Results are usually published on the official student portal. If you need help finding them, provide your roll number and I'll show the endpoint (demo only).",
            "meta": {"intent": "results", "source": "rule"}
        })

    # --- End runtime deterministic rules ---

    # 1) Model prediction (if available)
    intent = None
    conf = None
    if MODEL is not None:
        try:
            if hasattr(MODEL, "predict_proba"):
                probs = MODEL.predict_proba([q_norm])[0]
                classes = MODEL.classes_
                top_idx = int(probs.argmax())
                intent = classes[top_idx]
                conf = float(probs[top_idx])
                if conf < CONF_THRESHOLD:
                    intent = None  # ignore low-confidence intent
            else:
                intent = MODEL.predict([q_norm])[0]
                conf = None
        except Exception:
            logging.exception("Model predict failed")
            intent = None

    # 2) If confident intent, lookup
    if intent:
        try:
            faq_q, faq_ans = lookup_by_intent(intent)
        except Exception:
            logging.exception("lookup_by_intent failed")
            faq_q, faq_ans = None, None

        if faq_ans:
            try:
                overlap = token_overlap_score(q_norm, f"{faq_q} {faq_ans}")
            except Exception:
                logging.exception("token_overlap_score failed")
                overlap = 0.0

            if overlap >= 0.08:
                return jsonify({"reply": faq_ans, "meta": {"intent": intent, "confidence": conf, "overlap": overlap}})

            # else fall through to keyword search

    # 3) Keyword/fuzzy search (operate on normalized text)
    try:
        kw_q, kw_ans = keyword_search(q_norm)
    except Exception:
        logging.exception("keyword_search failed")
        kw_q, kw_ans = None, None

    if kw_ans:
        return jsonify({"reply": kw_ans, "meta": {"intent": intent or "keyword_search"}})

    # 4) final fallback: log unmatched then respond
    try:
        log_unmatched(q_norm)
    except Exception:
        logging.exception("failed to log unmatched query")

    return jsonify({"reply": "Sorry, I couldn't find that. Please contact the admin office.", "meta": {"intent": intent, "confidence": conf}})
