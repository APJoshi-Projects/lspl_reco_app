import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from db import init_db, SessionLocal
from recommender import Recommender, InputSchema
from models import Ticket

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "devkey")

# Initialize DB
init_db()

# Initialize recommender (loads vector index lazily on first call)
reco = Recommender()

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        payload = request.get_json(force=True)
        data = InputSchema(**payload)
        result = reco.recommend(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Simple route to list last 10 tickets
@app.route("/api/tickets", methods=["GET"])
def list_tickets():
    db = SessionLocal()
    try:
        rows = db.query(Ticket).order_by(Ticket.id.desc()).limit(10).all()
        return jsonify([t.to_dict() for t in rows])
    finally:
        db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
