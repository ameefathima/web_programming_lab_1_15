import os
import sqlite3
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "lab-secret-key-change-in-production"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "contacts.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please fill in your name, email, and message.", "error")
            return redirect(url_for("index"))

        if "@" not in email or "." not in email.split("@")[-1]:
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("index"))

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO contacts (name, email, message, created_at) VALUES (?, ?, ?, ?)",
                    (name, email, message, created_at),
                )
                conn.commit()
            flash(f"Thank you, {name}! Your message has been saved.", "success")
        except sqlite3.Error as exc:
            flash(f"Database error while saving message: {exc}", "error")

        return redirect(url_for("index"))

    with get_db_connection() as conn:
        submissions = conn.execute(
            "SELECT id, name, email, message, created_at FROM contacts ORDER BY id DESC"
        ).fetchall()

    return render_template("index.html", submissions=submissions)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)