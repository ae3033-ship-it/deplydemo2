from pathlib import Path

from flask import Flask, jsonify, send_from_directory

import db

app = Flask(__name__)
FRONTEND = Path(__file__).parent / "frontend"


@app.route("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.route("/api/students")
def students():
    return jsonify(db.get_student_names())


if __name__ == "__main__":
    app.run(debug=True)
