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

    db = get_db()
    exams = db.execute("SELECT * FROM exams").fetchall()
    db.close()

    return render_template("staff_dashboard.html", exams=exams)


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
            (sid, name, email, sid)
        )
        db.commit()
        db.close()

        flash("Student added successfully")
        return redirect(url_for("view_students"))

    return render_template("add_student.html")


@app.route("/staff/view-students")
def view_students():
    if "staff" not in session:
        return redirect(url_for("staff_login"))

    db = get_db()
    students = db.execute("SELECT * FROM students").fetchall()
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
        description = request.form.get("description")
        duration = request.form.get("duration")
        created_by = session["staff"]

        db = get_db()
        db.execute(
            "INSERT INTO exams (title, description, duration, created_by) VALUES (?, ?, ?, ?)",
            (title, description, duration, created_by)
        )
        db.commit()
        db.close()

        flash("Exam created successfully")
        return redirect(url_for("staff_dashboard"))

    return render_template("create_exam.html")


@app.route("/staff/delete-exam/<int:exam_id>", methods=["POST"])
def delete_exam(exam_id):
    if "staff" not in session:
        return redirect(url_for("staff_login"))

    db = get_db()
    db.execute("DELETE FROM exams WHERE id=?", (exam_id,))
    db.commit()
    db.close()

    flash("Exam deleted")
    return redirect(url_for("staff_dashboard"))


@app.route("/staff/exams/<int:exam_id>/questions")
def view_questions(exam_id):
    if "staff" not in session:
        return redirect(url_for("staff_login"))

    db = get_db()
    exam = db.execute("SELECT * FROM exams WHERE id=?", (exam_id,)).fetchone()
    questions = db.execute(
        "SELECT * FROM questions WHERE exam_id=?",
        (exam_id,)
    ).fetchall()
    db.close()

    return render_template("view_questions.html", exam=exam, questions=questions)


@app.route("/staff/exams/<int:exam_id>/add-question", methods=["GET", "POST"])
def add_question(exam_id):
    if "staff" not in session:
        return redirect(url_for("staff_login"))

    if request.method == "POST":
        db = get_db()
        db.execute(
            """
            INSERT INTO questions
            (exam_id, question, option_a, option_b, option_c, option_d, correct_option)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                exam_id,
                request.form["question"],
                request.form["option_a"],
                request.form["option_b"],
                request.form["option_c"],
                request.form["option_d"],
                request.form["correct_option"],
            )
        )
        db.commit()
        db.close()

        flash("Question added")
        return redirect(url_for("view_questions", exam_id=exam_id))

    return render_template("add_question.html", exam_id=exam_id)


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

        flash("Wrong credentials")

    return render_template("student_login.html")


@app.route("/student/dashboard")
def student_dashboard():
    if "student" not in session:
        return redirect(url_for("student_login"))

    db = get_db()
    student = db.execute(
        "SELECT name FROM students WHERE id=?",
        (session["student"],)
    ).fetchone()
    db.close()

    return render_template("student_dashboard.html", student_name=student["name"])


@app.route("/student/exams")
def student_exams():
    if "student" not in session:
        return redirect(url_for("student_login"))

    db = get_db()
    exams = db.execute("SELECT * FROM exams").fetchall()
    db.close()

    return render_template("student_exams.html", exams=exams)


@app.route("/student/result/<int:exam_id>")
def result(exam_id):
    if "student" not in session:
        return redirect(url_for("student_login"))

    db = get_db()
    result = db.execute(
        """
        SELECT * FROM results
        WHERE student_id=? AND exam_id=?
        ORDER BY id DESC LIMIT 1
        """,
        (session["student"], exam_id)
    ).fetchone()
    db.close()

    return render_template("result.html", result=result)


@app.route("/student/change-password", methods=["GET", "POST"])
def change_student_password():
    if "student" not in session:
        return redirect(url_for("student_login"))

    if request.method == "POST":
        if request.form["new_password"] != request.form["confirm_password"]:
            flash("Passwords do not match")
            return redirect(url_for("change_student_password"))

        db = get_db()
        db.execute(
            "UPDATE students SET password=? WHERE id=?",
            (request.form["new_password"], session["student"])
        )
        db.commit()
        db.close()

        session.clear()
        flash("Password changed")
        return redirect(url_for("student_login"))

    return render_template("change_student_password.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
