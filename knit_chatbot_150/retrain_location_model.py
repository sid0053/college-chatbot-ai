# retrain_location_model.py
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

DATA = {
 "ask_fullform": ["knit stands for", "full form of knit"],
 "ask_location": ["location of knit", "where is knit located", "where is knit situated", "knit location", "knit address"],
 "ask_departments": ["how many departments", "departments in knit"],
 "ask_fees": ["btech fees", "fee structure", "what is the fees"],
 "ask_hostel": ["hostel fee", "hostel charge", "how are hostels allotted"],
 "greeting": ["hi", "hello", "hey"],
 "farewell": ["bye", "goodbye"]
}

X=[]; y=[]
for label, texts in DATA.items():
    for t in texts: X.append(t); y.append(label)

pipe = make_pipeline(
    TfidfVectorizer(ngram_range=(1,2)),
    LogisticRegression(max_iter=2000)
)

pipe.fit(X, y)
joblib.dump(pipe, "intent_pipeline.joblib")
print("Updated location-aware intent model saved.")
