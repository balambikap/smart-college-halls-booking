from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret_key"

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("timetable"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            session["is_admin"] = user["is_admin"]
            flash("Login successful!")
            return redirect(url_for("timetable"))
        else:
            flash("Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))
        except:
            flash("Username already exists")
        conn.close()
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out")
    return redirect(url_for("login"))

@app.route("/timetable")
def timetable():
    hall_id = request.args.get("hall_id", 1, type=int)
    conn = get_db()
    halls = conn.execute("SELECT * FROM halls").fetchall()
    subjects = conn.execute("SELECT * FROM subjects").fetchall()
    bookings = conn.execute("SELECT b.*, u.username, s.name as subject, h.name as hall FROM bookings b                              JOIN users u ON b.user_id=u.id                              JOIN subjects s ON b.subject_id=s.id                              JOIN halls h ON b.hall_id=h.id                              WHERE b.hall_id=?", (hall_id,)).fetchall()
    conn.close()

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    periods = ["Period 1", "Period 2", "Period 3", "Period 4", "Period 5"]

    return render_template("timetable.html", halls=halls, selected_hall_id=hall_id,
                           bookings=bookings, days=days, periods=periods, subjects=subjects)

@app.route("/book", methods=["GET", "POST"])
def book():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    halls = conn.execute("SELECT * FROM halls").fetchall()
    subjects = conn.execute("SELECT * FROM subjects").fetchall()

    if request.method == "POST":
        hall_id = request.form["hall_id"]
        day = request.form["day"]
        period = request.form["period"]
        subject_id = request.form["subject_id"]
        user_id = session["user_id"]

        # Check conflict
        conflict = conn.execute("SELECT * FROM bookings WHERE hall_id=? AND day=? AND period=?",
                                (hall_id, day, period)).fetchone()
        if conflict:
            flash("Slot already booked!")
        else:
            conn.execute("INSERT INTO bookings (user_id, hall_id, day, period, subject_id) VALUES (?, ?, ?, ?, ?)",
                         (user_id, hall_id, day, period, subject_id))
            conn.commit()
            flash("Booking successful!")
            return redirect(url_for("timetable"))

    conn.close()
    return render_template("book.html", halls=halls, subjects=subjects)

@app.route("/cancel/<int:booking_id>")
def cancel(booking_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    booking = conn.execute("SELECT * FROM bookings WHERE id=?", (booking_id,)).fetchone()

    if booking and booking["user_id"] == session["user_id"]:
        conn.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
        conn.commit()
        flash("Booking cancelled.")
    else:
        flash("You can only cancel your own bookings.")
    conn.close()
    return redirect(url_for("timetable"))


@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        cur.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
        conn.commit()
        flash("Subject added successfully!", "success")
        return redirect(url_for("subjects"))

    cur.execute("SELECT * FROM subjects")
    subjects = cur.fetchall()
    conn.close()
    return render_template("subjects.html", subjects=subjects)


@app.route("/subjects/edit/<int:subject_id>", methods=["GET", "POST"])
def edit_subject(subject_id):
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        name = request.form["name"]
        cur.execute("UPDATE subjects SET name = ? WHERE id = ?", (name, subject_id))
        conn.commit()
        conn.close()
        flash("Subject updated successfully!", "success")
        return redirect(url_for("subjects"))

    cur.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
    subject = cur.fetchone()
    conn.close()
    return render_template("edit_subject.html", subject=subject)


@app.route("/subjects/delete/<int:subject_id>")
def delete_subject(subject_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    conn.commit()
    conn.close()
    flash("Subject deleted successfully!", "success")
    return redirect(url_for("subjects"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0",port=port)
