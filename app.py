"""
app.py
------
Medical Tracker — Flask application.
Tracks conditions, symptoms, treatments, appointments and doctors.
"""

import os
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from models import db, Condition, Doctor, Appointment, Treatment, TreatmentResponse, SymptomLog, BodyPartAffected
from privacy import validate_fields

app = Flask(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
app.secret_key = os.environ.get("SECRET_KEY", "change-this-in-production-please")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///medical_tracker.db")

# Railway provides MySQL URL as mysql://... — SQLAlchemy needs mysql+pymysql://
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

APP_USERNAME = os.environ.get("APP_USERNAME", "admin")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "changeme123")

db.init_app(app)
with app.app_context():
    db.create_all()

# ── Auth ──────────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] == APP_USERNAME and request.form["password"] == APP_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.route("/")
@login_required
def dashboard():
    conditions = Condition.query.order_by(Condition.created_at.desc()).all()
    recent_logs = SymptomLog.query.order_by(SymptomLog.logged_at.desc()).limit(5).all()
    recent_appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).limit(5).all()
    return render_template("dashboard.html",
                           conditions=conditions,
                           recent_logs=recent_logs,
                           recent_appointments=recent_appointments
                           )

# ── Conditions ────────────────────────────────────────────────────────────────
@app.route("/conditions")
@login_required
def conditions():
    all_conditions = Condition.query.order_by(Condition.created_at.desc()).all()
    return render_template("conditions.html", conditions=all_conditions)

@app.route("/conditions/add", methods=["GET", "POST"])
@login_required
def add_condition():
    if request.method == "POST":
        check = validate_fields({
            "name":  request.form.get("name", ""),
            "notes": request.form.get("notes", ""),
        })
        if not check["ok"]:
            for err in check["errors"]:
                flash(err, "danger")
            return render_template("add_condition.html", form=request.form)

        diagnosed_str = request.form.get("diagnosed_date")
        diagnosed = datetime.strptime(diagnosed_str, "%Y-%m-%d").date() if diagnosed_str else None

        condition = Condition(
            name=request.form["name"],
            diagnosed_date=diagnosed,
            icd_code=request.form.get("icd_code"),
            status=request.form.get("status", "active"),
            notes=request.form.get("notes"),
        )
        db.session.add(condition)
        db.session.flush()

        parts = request.form.getlist("body_parts")
        for part in parts:
            if part.strip():
                bp = BodyPartAffected(
                    condition_id=condition.id,
                    body_part=part,
                    severity=int(request.form.get(f"severity_{part}", 5)),
                )
                db.session.add(bp)

        db.session.commit()
        flash(f"Condition #{condition.id} added successfully.", "success")
        return redirect(url_for("condition_detail", condition_id=condition.id))

    return render_template("add_condition.html", form={})

@app.route("/conditions/<int:condition_id>")
@login_required
def condition_detail(condition_id):
    condition = Condition.query.get_or_404(condition_id)
    logs = SymptomLog.query.filter_by(condition_id=condition_id).order_by(SymptomLog.logged_at.desc()).all()
    treatments = Treatment.query.filter_by(condition_id=condition_id).order_by(Treatment.start_date.desc()).all()
    appointments = Appointment.query.filter_by(condition_id=condition_id).order_by(Appointment.appointment_date.desc()).all()
    return render_template("condition_detail.html",
                           condition=condition,
                           logs=logs,
                           treatments=treatments,
                           appointments=appointments
                           )

@app.route("/conditions/<int:condition_id>/history")
@login_required
def condition_history(condition_id):
    """Full timeline / medical history for a condition."""
    condition = Condition.query.get_or_404(condition_id)
    appointments = Appointment.query.filter_by(condition_id=condition_id).order_by(Appointment.appointment_date).all()
    treatments = Treatment.query.filter_by(condition_id=condition_id).order_by(Treatment.start_date).all()
    logs = SymptomLog.query.filter_by(condition_id=condition_id).order_by(SymptomLog.logged_at).all()
    return render_template("history.html",
                           condition=condition,
                           appointments=appointments,
                           treatments=treatments,
                           logs=logs
                           )

# ── Doctors ───────────────────────────────────────────────────────────────────
@app.route("/doctors")
@login_required
def doctors():
    all_doctors = Doctor.query.order_by(Doctor.id).all()
    return render_template("doctors.html", doctors=all_doctors)

@app.route("/doctors/add", methods=["GET", "POST"])
@login_required
def add_doctor():
    if request.method == "POST":
        check = validate_fields({
            "specialty": request.form.get("specialty", ""),
            "city":      request.form.get("city", ""),
            "country":   request.form.get("country", ""),
            "notes":     request.form.get("notes", ""),
        })
        if not check["ok"]:
            for err in check["errors"]:
                flash(err, "danger")
            return render_template("add_doctor.html", form=request.form)

        doctor = Doctor(
            specialty=request.form["specialty"],
            city=request.form.get("city"),
            country=request.form.get("country"),
            notes=request.form.get("notes"),
        )
        db.session.add(doctor)
        db.session.commit()
        flash(f"Doctor {doctor.id} added.", "success")
        return redirect(url_for("doctors"))

    return render_template("add_doctor.html", form={})

# ── Appointments ──────────────────────────────────────────────────────────────
@app.route("/appointments/add", methods=["GET", "POST"])
@login_required
def add_appointment():
    conditions = Condition.query.order_by(Condition.name).all()
    doctors = Doctor.query.order_by(Doctor.id).all()

    if request.method == "POST":
        check = validate_fields({
            "reason":  request.form.get("reason", ""),
            "outcome": request.form.get("outcome", ""),
        })
        if not check["ok"]:
            for err in check["errors"]:
                flash(err, "danger")
            return render_template("add_appointment.html", conditions=conditions, doctors=doctors, form=request.form)

        appt_date = datetime.strptime(request.form["appointment_date"], "%Y-%m-%d").date()
        req_str   = request.form.get("requested_date")
        req_date  = datetime.strptime(req_str, "%Y-%m-%d").date() if req_str else None
        waiting   = (appt_date - req_date).days if req_date else None

        appt = Appointment(
            condition_id=request.form["condition_id"],
            doctor_id=request.form.get("doctor_id") or None,
            requested_date=req_date,
            appointment_date=appt_date,
            waiting_days=waiting,
            reason=request.form.get("reason"),
            outcome=request.form.get("outcome"),
            follow_up_needed=bool(request.form.get("follow_up_needed")),
        )
        db.session.add(appt)
        db.session.commit()
        flash("Appointment logged.", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_appointment.html", conditions=conditions, doctors=doctors, form={})

# ── Treatments ────────────────────────────────────────────────────────────────
@app.route("/treatments/add", methods=["GET", "POST"])
@login_required
def add_treatment():
    conditions   = Condition.query.order_by(Condition.name).all()
    doctors      = Doctor.query.order_by(Doctor.id).all()
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()

    if request.method == "POST":
        check = validate_fields({
            "name":            request.form.get("name", ""),
            "dosage_details":  request.form.get("dosage_details", ""),
            "side_effects":    request.form.get("side_effects", ""),
            "notes":           request.form.get("notes", ""),
        })
        if not check["ok"]:
            for err in check["errors"]:
                flash(err, "danger")
            return render_template("add_treatment.html", conditions=conditions, doctors=doctors, appointments=appointments, form=request.form)

        start_str = request.form.get("start_date")
        end_str   = request.form.get("end_date")

        treatment = Treatment(
            condition_id=request.form["condition_id"],
            appointment_id=request.form.get("appointment_id") or None,
            doctor_id=request.form.get("doctor_id") or None,
            treatment_type=request.form["treatment_type"],
            name=request.form["name"],
            dosage_details=request.form.get("dosage_details"),
            start_date=datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None,
            end_date=datetime.strptime(end_str,   "%Y-%m-%d").date() if end_str   else None,
            still_ongoing=bool(request.form.get("still_ongoing")),
            outcome=request.form.get("outcome"),
            side_effects=request.form.get("side_effects"),
            active_ingredient=request.form.get("active_ingredient"),
            notes=request.form.get("notes"),
        )
        db.session.add(treatment)
        db.session.commit()
        flash("Treatment logged.", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_treatment.html", conditions=conditions, doctors=doctors, appointments=appointments, form={})

# ── Symptom Logs ──────────────────────────────────────────────────────────────
BODY_PARTS = [
    "Hand (L)", "Hand (R)", "Wrist (L)", "Wrist (R)",
    "Elbow (L)", "Elbow (R)", "Shoulder (L)", "Shoulder (R)",
    "Neck", "Upper Back", "Lower Back",
    "Hip (L)", "Hip (R)", "Knee (L)", "Knee (R)",
    "Ankle (L)", "Ankle (R)", "Foot (L)", "Foot (R)",
    "Jaw", "Chest", "Abdomen", "Other"
]

@app.route("/log/add", methods=["GET", "POST"])
@login_required
def add_log():
    conditions = Condition.query.order_by(Condition.name).all()

    if request.method == "POST":
        check = validate_fields({"notes": request.form.get("notes", "")})
        if not check["ok"]:
            for err in check["errors"]:
                flash(err, "danger")
            return render_template("add_log.html", conditions=conditions, form=request.form)

        temp_str = request.form.get("temperature")

        def opt_int(key, default=None):
            v = request.form.get(key)
            return int(v) if v not in (None, "") else default

        log = SymptomLog(
            condition_id=request.form["condition_id"],
            body_part=request.form.get("body_part"),
            pain_level=int(request.form.get("pain_level", 0)),
            heat_level=int(request.form.get("heat_level", 0)),
            swelling_level=int(request.form.get("swelling_level", 0)),
            redness_level=int(request.form.get("redness_level", 0)),
            inflammation_level=int(request.form.get("inflammation_level", 0)),
            mobility_level=int(request.form.get("mobility_level", 10)),
            fatigue_level=int(request.form.get("fatigue_level", 0)),
            sleep_quality=int(request.form.get("sleep_quality", 5)),
            daily_life_impact=int(request.form.get("daily_life_impact", 0)),
            work_impact=int(request.form.get("work_impact", 0)),
            has_fever=bool(request.form.get("has_fever")),
            temperature=float(temp_str) if temp_str else None,
            sensitivity_cold=opt_int("sensitivity_cold"),
            sensitivity_hot=opt_int("sensitivity_hot"),
            sensitivity_pressure=opt_int("sensitivity_pressure"),
            sensitivity_sweet=opt_int("sensitivity_sweet"),
            gum_bleeding=opt_int("gum_bleeding"),
            tooth_mobility=opt_int("tooth_mobility"),
            bad_taste_odor=True if request.form.get("bad_taste_odor") == "1" else (False if request.form.get("bad_taste_odor") == "0" else None),
            photo_reference=request.form.get("photo_reference"),
            notes=request.form.get("notes"),
        )
        db.session.add(log)
        db.session.commit()
        flash("Symptom log saved.", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_log.html", conditions=conditions, form={})

# ── API: chart data ───────────────────────────────────────────────────────────
@app.route("/api/symptom_chart/<int:condition_id>")
@login_required
def symptom_chart_data(condition_id):
    logs = SymptomLog.query.filter_by(condition_id=condition_id).order_by(SymptomLog.logged_at).all()
    data = [{
        "date":     log.logged_at.strftime("%Y-%m-%d %H:%M"),
        "pain":     log.pain_level,
        "heat":     log.heat_level,
        "swelling": log.swelling_level,
        "mobility": log.mobility_level,
        "fatigue":  log.fatigue_level,
    } for log in logs]
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
