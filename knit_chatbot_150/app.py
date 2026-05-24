from flask import Flask, render_template
from routes.api import api_bp

app = Flask(__name__, template_folder='templates', static_folder='static')
app.register_blueprint(api_bp, url_prefix="/api")

@app.route("/")
def home():
    return render_template("chat.html")

# <-- ADD THIS ROUTE
@app.route("/chat")
def chat_page():
    return render_template("chat.html")

if __name__ == "__main__":
    app.run(debug=True)
