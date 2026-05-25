"""
models.py
---------
Medical Tracker — redesigned schema.

Core concept: you track CONDITIONS over time via ENTRIES (each entry is a date/time snapshot).
Each entry can have multiple activities, diet items, and links/images attached.
No personal info stored.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Condition(db.Model):
    """A health condition the user is tracking."""
    __tablename__ = "conditions"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(200), nullable=False)
    notes        = db.Column(db.Text, nullable=True)      # optional initial notes
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    entries = db.relationship("Entry", backref="condition", lazy=True,
                              cascade="all, delete-orphan",
                              order_by="Entry.entry_at.desc()")


class Entry(db.Model):
    """
    A journal entry for a condition at a specific date/time.
    All fields are optional open text — the user fills in what is relevant.
    """
    __tablename__ = "entries"

    id           = db.Column(db.Integer, primary_key=True)
    condition_id = db.Column(db.Integer, db.ForeignKey("conditions.id"), nullable=False)
    entry_at     = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # user-chosen date+time

    # --- Open text fields (all optional) ---
    symptoms     = db.Column(db.Text, nullable=True)   # what you feel / physical symptoms
    events       = db.Column(db.Text, nullable=True)   # what happened (triggers, incidents)
    context      = db.Column(db.Text, nullable=True)   # environment / what you were doing
    observations = db.Column(db.Text, nullable=True)   # your own observations / patterns noticed
    doctor       = db.Column(db.Text, nullable=True)   # doctor visited, what was said (no names)
    medications  = db.Column(db.Text, nullable=True)   # meds taken, dosage, timing

    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Related rows ---
    activities   = db.relationship("Activity",  backref="entry", lazy=True,
                                   cascade="all, delete-orphan")
    diet_items   = db.relationship("DietItem",  backref="entry", lazy=True,
                                   cascade="all, delete-orphan")
    attachments  = db.relationship("Attachment", backref="entry", lazy=True,
                                   cascade="all, delete-orphan")


class Activity(db.Model):
    """One physical / mental activity logged within an entry, with how you felt after."""
    __tablename__ = "activities"

    id          = db.Column(db.Integer, primary_key=True)
    entry_id    = db.Column(db.Integer, db.ForeignKey("entries.id"), nullable=False)
    name        = db.Column(db.Text, nullable=False)   # e.g. "30 min walk", "yoga"
    feeling_after = db.Column(db.Text, nullable=True)  # how you felt after


class DietItem(db.Model):
    """One food/drink item logged within an entry, with how you felt."""
    __tablename__ = "diet_items"

    id          = db.Column(db.Integer, primary_key=True)
    entry_id    = db.Column(db.Integer, db.ForeignKey("entries.id"), nullable=False)
    food        = db.Column(db.Text, nullable=False)   # what you ate/drank
    feeling     = db.Column(db.Text, nullable=True)    # how you felt with it


class Attachment(db.Model):
    """A link or image reference attached to an entry."""
    __tablename__ = "attachments"

    id          = db.Column(db.Integer, primary_key=True)
    entry_id    = db.Column(db.Integer, db.ForeignKey("entries.id"), nullable=False)
    label       = db.Column(db.String(200), nullable=True)   # optional description
    url         = db.Column(db.Text, nullable=True)          # external URL or image path
    is_image    = db.Column(db.Boolean, default=False)
