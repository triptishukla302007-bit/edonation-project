import os
import sqlite3
import smtplib
from email.message import EmailMessage

print("APP FOLDER:", os.getcwd())

from flask import Flask, render_template, request
from database import create_database

app = Flask(__name__)
create_database()


def get_db_connection():
    conn = sqlite3.connect("edonation.db")
    conn.row_factory = sqlite3.Row
    return conn


def send_email(subject, message):
    email_user = os.environ.get("EMAIL_USER")
    email_password = os.environ.get("EMAIL_PASSWORD")
    admin_email = os.environ.get("ADMIN_EMAIL")

    if not email_user or not email_password or not admin_email:
        print("Email settings are missing.")
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = email_user
        msg["To"] = admin_email
        msg.set_content(message)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)

        print("Email notification sent successfully.")

    except Exception as e:
        print("Email notification failed:", e)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/donate", methods=["GET", "POST"])
def donate():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        mobile = request.form.get("mobile")
        item = request.form.get("item")
        category = request.form.get("category")
        condition = request.form.get("condition")
        location = request.form.get("location")
        description = request.form.get("description")

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO donations
            (name, email, mobile, item, category, item_condition, location, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            mobile,
            item,
            category,
            condition,
            location,
            description
        ))

        conn.commit()
        conn.close()

        send_email(
            "New Donation Received - Don't Dump",
            f"""A new donation has been submitted.

Donor Name: {name}
Email: {email}
Mobile: {mobile}
Item: {item}
Category: {category}
Condition: {condition}
Location: {location}
Description: {description}

Status: Pending
"""
        )

        return f"""
        <h1>Donation Submitted Successfully ❤️</h1>
        <p>Thank you, {name}!</p>
        <p>Your donation has been saved successfully.</p>
        <p>Item: {item}</p>
        <p>Category: {category}</p>
        <p>Condition: {condition}</p>
        <p>Location: {location}</p>
        <p>Description: {description}</p>
        <p><a href="/">← Back to Home</a></p>
        """

    return render_template("donate.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        mobile = request.form.get("mobile")
        password = request.form.get("password")

        conn = get_db_connection()

        try:
            conn.execute("""
                INSERT INTO users (name, email, mobile, password)
                VALUES (?, ?, ?, ?)
            """, (name, email, mobile, password))

            conn.commit()
            conn.close()

            send_email(
                "New User Registration - Don't Dump",
                f"""A new user has registered.

Name: {name}
Email: {email}
Mobile: {mobile}
"""
            )

            return f"""
            <h1>Registration Successful ❤️</h1>
            <p>Welcome, {name}!</p>
            <p>Your account has been saved successfully.</p>
            <p>Email: {email}</p>
            <p>Mobile: {mobile}</p>
            <p><a href="/login">Go to Login</a></p>
            <p><a href="/">← Back to Home</a></p>
            """

        except sqlite3.IntegrityError:
            conn.close()

            return """
            <h1>Registration Failed</h1>
            <p>This email is already registered.</p>
            <p><a href="/register">← Try Again</a></p>
            """

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()

        user = conn.execute("""
            SELECT * FROM users
            WHERE email = ? AND password = ?
        """, (email, password)).fetchone()

        conn.close()

        if user:
            return f"""
            <h1>Login Successful ❤️</h1>
            <p>Welcome back, {user["name"]}!</p>
            <p>Email: {user["email"]}</p>
            <p>You are now logged in.</p>
            <p><a href="/">← Back to Home</a></p>
            """

        return """
        <h1>Login Failed ❌</h1>
        <p>Invalid email or password.</p>
        <p><a href="/login">← Try Again</a></p>
        """

    return render_template("login.html")


@app.route("/update_status/<int:donation_id>", methods=["POST"])
def update_status(donation_id):
    status = request.form.get("status")

    conn = get_db_connection()

    conn.execute(
        "UPDATE donations SET status = ? WHERE id = ?",
        (status, donation_id)
    )

    conn.commit()
    conn.close()

    return """
    <script>
        window.location.href = "/admin";
    </script>
    """


@app.route("/admin")
def admin():
    conn = get_db_connection()

    total_users = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    total_donations = conn.execute(
        "SELECT COUNT(*) FROM donations"
    ).fetchone()[0]

    donations = conn.execute(
        "SELECT * FROM donations ORDER BY id DESC"
    ).fetchall()

    users = conn.execute(
        "SELECT * FROM users ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_donations=total_donations,
        donations=donations,
        users=users
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
