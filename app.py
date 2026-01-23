from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "exam-secret-key"

DATABASE = "database/exam.db"


# ------------------ DB CONNECTION ------------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ------------------ HOME ------------------
@app.route("/")
def index():
    return render_template("index.html")


# ==================================================
# ================= STAFF SECTION ==================
# ==================================================

@app.route("/staff/login", methods=["GET", "POST"])
def staff_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        staff = db.execute(
            "SELECT * FROM staff WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        db.close()

        if staff:
            session["staff"] = username
            return redirect(url_for("staff_dashboard"))

        flash("Invalid staff credentials")

    return render_template("staff_login.html")


@app.route("/staff/dashboard")
def staff_dashboard():
    if "staff" not in session:
        return redirect(url_for("staff_login"))

    return render_template("staff_dashboard.html")


@app.route("/staff/add-student", methods=["GET", "POST"])
def add_student():
    if "staff" not in session:
        return redirect(url_for("staff_login"))

    if request.method == "POST":
        sid = request.form.get("student_id")
        name = request.form.get("student_name")
        email = request.form.get("student_email")

        db = get_db()
        exists = db.execute(
            "SELECT * FROM students WHERE id=? OR email=?",
            (sid, email)
        ).fetchone()

        if exists:
            db.close()
            flash("Student ID or Email already exists")
            return redirect(url_for("add_student"))

        db.execute(
            "INSERT INTO students (id, name, email, password) VALUES (?, ?, ?, ?)",
            (sid, name, email, sid)  # default password = student ID
        )
        db.commit()
        db.close()

        flash("Student added successfully (password = student ID)")
        return redirect(url_for("view_students"))

    return render_template("add_student.html")


@app.route("/staff/view-students")
def view_students():
    if "staff" not in session:
        return redirect(url_for("staff_login"))

    db = get_db()
    students = db.execute("SELECT id, name, email FROM students").fetchall()
    db.close()

    return render_template("view_students.html", students=students)


@app.route("/staff/edit-student/<sid>", methods=["GET", "POST"])
def edit_student(sid):
    if "staff" not in session:
        return redirect(url_for("staff_login"))

    db = get_db()

    if request.method == "POST":
        name = request.form.get("student_name")
        email = request.form.get("student_email")

        exists = db.execute(
            "SELECT * FROM students WHERE email=? AND id!=?",
            (email, sid)
        ).fetchone()

        if exists:
            db.close()
            flash("Email already exists")
            return redirect(url_for("edit_student", sid=sid))

        db.execute(
            "UPDATE students SET name=?, email=? WHERE id=?",
            (name, email, sid)
        )
        db.commit()
        db.close()

        flash("Student updated successfully")
        return redirect(url_for("view_students"))

    student = db.execute(
        "SELECT * FROM students WHERE id=?",
        (sid,)
    ).fetchone()
    db.close()

    return render_template("edit_student.html", student=student)


@app.route("/staff/delete-student/<sid>", methods=["POST"])
def delete_student(sid):
    if "staff" not in session:
        return redirect(url_for("staff_login"))

    db = get_db()
    db.execute("DELETE FROM students WHERE id=?", (sid,))
    db.commit()
    db.close()

    flash("Student deleted")
    return redirect(url_for("view_students"))


@app.route("/staff/delete-all-students", methods=["POST"])
def delete_all_students():
    if "staff" not in session:
        return redirect(url_for("staff_login"))

    db = get_db()
    db.execute("DELETE FROM students")
    db.commit()
    db.close()

    flash("All students deleted")
    return redirect(url_for("view_students"))


@app.route("/staff/create-exam", methods=["GET", "POST"])
def create_exam():
    if "staff" not in session:
        return redirect(url_for("staff_login"))

    if request.method == "POST":
        title = request.form.get("title")

        db = get_db()
        db.execute("INSERT INTO exams (title) VALUES (?)", (title,))
        db.commit()
        db.close()

        flash("Exam created successfully")

    return render_template("create_exam.html")


# ==================================================
# ================= STUDENT SECTION =================
# ==================================================

@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        sid = request.form.get("student_id")
        password = request.form.get("password")

        db = get_db()
        student = db.execute(
            "SELECT * FROM students WHERE id=? AND password=?",
            (sid, password)
        ).fetchone()
        db.close()

        if student:
            session["student"] = sid
            return redirect(url_for("student_dashboard"))

        flash("Wrong student credentials")

    return render_template("student_login.html")


@app.route("/student/dashboard")
def student_dashboard():
    if "student" not in session:
        return redirect(url_for("student_login"))

    return render_template("student_dashboard.html")


# ✅ THIS ROUTE WAS MISSING (ROOT CAUSE)
@app.route("/student/change-password", methods=["GET", "POST"])
def change_student_password():
    if "student" not in session:
        return redirect(url_for("student_login"))

    if request.method == "POST":
        old = request.form.get("old_password")
        new = request.form.get("new_password")
        confirm = request.form.get("confirm_password")

        if new != confirm:
            flash("Passwords do not match")
            return redirect(url_for("change_student_password"))

        db = get_db()
        student = db.execute(
            "SELECT * FROM students WHERE id=? AND password=?",
            (session["student"], old)
        ).fetchone()

        if not student:
            db.close()
            flash("Old password is incorrect")
            return redirect(url_for("change_student_password"))

        db.execute(
            "UPDATE students SET password=? WHERE id=?",
            (new, session["student"])
        )
        db.commit()
        db.close()

        session.clear()
        flash("Password changed successfully. Login again.")
        return redirect(url_for("student_login"))

    return render_template("change_student_password.html")


@app.route("/student/exams")
def student_exams():
    if "student" not in session:
        return redirect(url_for("student_login"))

    db = get_db()
    exams = db.execute("SELECT * FROM exams").fetchall()
    db.close()

    return render_template("student_exams.html", exams=exams)


# ------------------ LOGOUT ------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(debug=True)
