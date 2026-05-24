"""
models.py
---------
Database schema for the Medical Tracker app.
All tables use plain integer IDs. No personal information fields.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Condition(db.Model):
    __tablename__ = "conditions"

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(200), nullable=False)
    diagnosed_date = db.Column(db.Date, nullable=True)
    icd_code       = db.Column(db.String(20), nullable=True)
    status         = db.Column(db.String(50), default="active")  # active / resolved / monitoring
    notes          = db.Column(db.Text, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    symptom_logs  = db.relationship("SymptomLog", backref="condition", lazy=True, cascade="all, delete-orphan")
    treatments    = db.relationship("Treatment", backref="condition", lazy=True, cascade="all, delete-orphan")
    appointments  = db.relationship("Appointment", backref="condition", lazy=True, cascade="all, delete-orphan")
    body_parts    = db.relationship("BodyPartAffected", backref="condition", lazy=True, cascade="all, delete-orphan")


class BodyPartAffected(db.Model):
    __tablename__ = "body_parts_affected"

    id           = db.Column(db.Integer, primary_key=True)
    condition_id = db.Column(db.Integer, db.ForeignKey("conditions.id"), nullable=False)
    body_part    = db.Column(db.String(100), nullable=False)
    severity     = db.Column(db.Integer, default=5)  # 0-10
    notes        = db.Column(db.Text, nullable=True)


class Doctor(db.Model):
    __tablename__ = "doctors"

    id        = db.Column(db.Integer, primary_key=True)
    specialty = db.Column(db.String(150), nullable=False)
    city      = db.Column(db.String(100), nullable=True)
    country   = db.Column(db.String(100), nullable=True)
    notes     = db.Column(db.Text, nullable=True)

    appointments = db.relationship("Appointment", backref="doctor", lazy=True)
    treatments   = db.relationship("Treatment", backref="prescribing_doctor", lazy=True)


class Appointment(db.Model):
    __tablename__ = "appointments"

    id               = db.Column(db.Integer, primary_key=True)
    condition_id     = db.Column(db.Integer, db.ForeignKey("conditions.id"), nullable=False)
    doctor_id        = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=True)
    requested_date   = db.Column(db.Date, nullable=True)
    appointment_date = db.Column(db.Date, nullable=False)
    waiting_days     = db.Column(db.Integer, nullable=True)  # auto-calculated
    reason           = db.Column(db.String(300), nullable=True)
    outcome          = db.Column(db.Text, nullable=True)
    follow_up_needed = db.Column(db.Boolean, default=False)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    treatments = db.relationship("Treatment", backref="appointment", lazy=True)


class Treatment(db.Model):
    __tablename__ = "treatments"

    id             = db.Column(db.Integer, primary_key=True)
    condition_id   = db.Column(db.Integer, db.ForeignKey("conditions.id"), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True)
    doctor_id      = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=True)

    treatment_type = db.Column(db.String(50), nullable=False)
    # medication / physiotherapy / injection / surgery / massage /
    # acupuncture / lifestyle / rest /
    # dental_cleaning / filling / root_canal / crown /
    # extraction / implant / brace_aligner / other

    name           = db.Column(db.String(200), nullable=False)
    dosage_details = db.Column(db.String(300), nullable=True)
    start_date     = db.Column(db.Date, nullable=True)
    end_date       = db.Column(db.Date, nullable=True)
    still_ongoing  = db.Column(db.Boolean, default=False)

    outcome        = db.Column(db.String(50), nullable=True)
    # helped / partial_relief / no_relief / made_worse / stopped_side_effects / ongoing

    side_effects      = db.Column(db.Text, nullable=True)
    active_ingredient = db.Column(db.String(300), nullable=True)  # e.g. Naproxen sodium 500mg
    notes             = db.Column(db.Text, nullable=True)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    responses = db.relationship("TreatmentResponse", backref="treatment", lazy=True, cascade="all, delete-orphan")


class TreatmentResponse(db.Model):
    """Tracks how a treatment is working over time — can be logged multiple times."""
    __tablename__ = "treatment_responses"

    id            = db.Column(db.Integer, primary_key=True)
    treatment_id  = db.Column(db.Integer, db.ForeignKey("treatments.id"), nullable=False)
    logged_at     = db.Column(db.DateTime, default=datetime.utcnow)
    pain_before   = db.Column(db.Integer, nullable=True)  # 0-10
    pain_after    = db.Column(db.Integer, nullable=True)  # 0-10
    relief_pct    = db.Column(db.Integer, nullable=True)  # 0-100%
    still_taking  = db.Column(db.Boolean, default=True)
    stopped_reason = db.Column(db.Text, nullable=True)
    notes         = db.Column(db.Text, nullable=True)


class SymptomLog(db.Model):
    """
    Core regular tracking table.
    Covers general inflammation signs + dental-specific indicators.
    Temperature always stored in Celsius.
    """
    __tablename__ = "symptom_logs"

    id           = db.Column(db.Integer, primary_key=True)
    condition_id = db.Column(db.Integer, db.ForeignKey("conditions.id"), nullable=False)
    body_part    = db.Column(db.String(100), nullable=True)
    logged_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # ── Four classic signs of inflammation ───────────────────────────────────
    pain_level     = db.Column(db.Integer, default=0)   # Dolor   0-10
    heat_level     = db.Column(db.Integer, default=0)   # Calor   0-10
    swelling_level = db.Column(db.Integer, default=0)   # Tumor   0-10
    redness_level  = db.Column(db.Integer, default=0)   # Rubor   0-10

    # ── General indicators ────────────────────────────────────────────────────
    inflammation_level = db.Column(db.Integer, default=0)   # 0-10
    mobility_level     = db.Column(db.Integer, default=10)  # 10=full, 0=none
    fatigue_level      = db.Column(db.Integer, default=0)   # 0-10
    sleep_quality      = db.Column(db.Integer, default=5)   # 0-10
    daily_life_impact  = db.Column(db.Integer, default=0)   # 0-10
    work_impact        = db.Column(db.Integer, default=0)   # 0-10

    # ── Fever (Celsius only) ──────────────────────────────────────────────────
    has_fever    = db.Column(db.Boolean, default=False)
    temperature  = db.Column(db.Float, nullable=True)   # °C

    # ── Dental-specific indicators ────────────────────────────────────────────
    sensitivity_cold     = db.Column(db.Integer, nullable=True)  # 0-10
    sensitivity_hot      = db.Column(db.Integer, nullable=True)  # 0-10
    sensitivity_pressure = db.Column(db.Integer, nullable=True)  # 0-10
    sensitivity_sweet    = db.Column(db.Integer, nullable=True)  # 0-10
    gum_bleeding         = db.Column(db.Integer, nullable=True)  # 0-10
    tooth_mobility       = db.Column(db.Integer, nullable=True)  # 0-3 (dental scale)
    bad_taste_odor       = db.Column(db.Boolean, nullable=True)  # yes/no

    # ── Photo reference (photo stored privately by user, this is just a label) ──
    photo_reference = db.Column(db.String(300), nullable=True)  # e.g. knee swelling — 24 May 2026 — album: Medical

    notes = db.Column(db.Text, nullable=True)
