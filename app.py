from pathlib import Path

from flask import Flask, jsonify, send_from_directory

import db
from models import CompetencyAverages

app = Flask(__name__)
FRONTEND = Path(__file__).parent / "frontend"


@app.route("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.route("/api/students")
def students():
    names = [student["name"] for student in db.get_students()]
    return jsonify(names)


@app.route("/api/competency-averages")
def competency_averages():
    averages = CompetencyAverages.from_students(db.get_students())
    return jsonify(averages.to_dict())


if __name__ == "__main__":
    app.run(debug=True)
