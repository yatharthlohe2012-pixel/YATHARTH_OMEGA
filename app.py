
from flask import Flask, request, jsonify, render_template, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key-before-deployment"
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///leads.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Admin credentials
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-me")

db = SQLAlchemy(app)


# --------------------------------------------------
# DATABASE MODEL
# --------------------------------------------------

class Lead(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(200), nullable=False)

    revenue = db.Column(db.String(100))
    phone = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(200), nullable=False)

    website = db.Column(db.String(300))
    location = db.Column(db.String(150))

    project_type = db.Column(db.String(100))
    work = db.Column(db.String(500))

    budget = db.Column(db.String(100))
    timeline = db.Column(db.String(100))

    details = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# --------------------------------------------------
# CREATE DATABASE
# --------------------------------------------------

with app.app_context():
    db.create_all()


# --------------------------------------------------
# PUBLIC WEBSITE
# --------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------------------------
# SUBMIT LEAD
# --------------------------------------------------

@app.route("/api/leads", methods=["POST"])
def create_lead():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400

    name = str(data.get("name", "")).strip()
    company = str(data.get("company", "")).strip()
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip()

    if not name or not company or not phone or not email:

        return jsonify({
            "success": False,
            "message": "Please complete all required fields."
        }), 400

    lead = Lead(

        name=name,
        company=company,

        revenue=str(data.get("revenue", "")).strip(),
        phone=phone,
        email=email,

        website=str(data.get("website", "")).strip(),
        location=str(data.get("location", "")).strip(),

        project_type=str(
            data.get("projectType", "")
        ).strip(),

        work=str(
            data.get("work", "")
        ).strip(),

        budget=str(
            data.get("budget", "")
        ).strip(),

        timeline=str(
            data.get("timeline", "")
        ).strip(),

        details=str(
            data.get("details", "")
        ).strip()
    )

    db.session.add(lead)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Lead received successfully."
    })


# --------------------------------------------------
# ADMIN LOGIN PAGE
# --------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            session["admin_logged_in"] = True

            return redirect("/admin")

        return render_template(
            "admin.html",
            login_error="Invalid username or password.",
            logged_in=False
        )

    return render_template(
        "admin.html",
        logged_in=False
    )


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):

        return redirect("/admin/login")

    leads = Lead.query.order_by(
        Lead.created_at.desc()
    ).all()

    return render_template(
        "admin.html",
        logged_in=True,
        leads=leads
    )


# --------------------------------------------------
# DELETE LEAD
# --------------------------------------------------

@app.route("/admin/delete/<int:lead_id>", methods=["POST"])
def delete_lead(lead_id):

    if not session.get("admin_logged_in"):

        return redirect("/admin/login")

    lead = db.session.get(Lead, lead_id)

    if lead:

        db.session.delete(lead)
        db.session.commit()

    return redirect("/admin")


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/admin/logout")
def logout():

    session.clear()

    return redirect("/admin/login")


# --------------------------------------------------
# RUN SERVER
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get("PORT", 5000)
        ),
        debug=True
    )
