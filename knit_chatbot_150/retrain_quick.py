# retrain_quick.py
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

DATA = {
 "ask_departments": ["how many departments", "departments in knit", "list of departments", "number of departments in knit"],
 "ask_fees": ["what is the fees", "btech fees", "fee structure"],
 "ask_hostel": ["hostel fee", "how are hostels allotted", "hostel allotment"],
 "ask_fullform": ["knit stands for", "full form knit"],
 "greeting": ["hi","hello","hii"],
 "farewell": ["bye","goodbye"]
}

X=[]; y=[]
for label, examples in DATA.items():
    for ex in examples:
        X.append(ex); y.append(label)

pipe = make_pipeline(TfidfVectorizer(ngram_range=(1,2)), LogisticRegression(max_iter=2000))
pipe.fit(X, y)
joblib.dump(pipe, "intent_pipeline.joblib")
print("Retrained intent_pipeline.joblib")
