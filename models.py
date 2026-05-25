from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Condition(db.Model):
    __tablename__ = "conditions"
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(200), nullable=False)
    notes      = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    entries    = db.relationship("Entry", backref="condition", lazy=True,
                                 cascade="all, delete-orphan",
                                 order_by="Entry.entry_at.desc()")


class Entry(db.Model):
    __tablename__ = "entries"
    id           = db.Column(db.Integer, primary_key=True)
    condition_id = db.Column(db.Integer, db.ForeignKey("conditions.id"), nullable=False)
    entry_at     = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    symptoms     = db.Column(db.Text, nullable=True)
    events       = db.Column(db.Text, nullable=True)
    context      = db.Column(db.Text, nullable=True)
    observations = db.Column(db.Text, nullable=True)
    doctor       = db.Column(db.Text, nullable=True)
    medications  = db.Column(db.Text, nullable=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    activities   = db.relationship("Activity",   backref="entry", lazy=True, cascade="all, delete-orphan")
    diet_items   = db.relationship("DietItem",   backref="entry", lazy=True, cascade="all, delete-orphan")
    attachments  = db.relationship("Attachment", backref="entry", lazy=True, cascade="all, delete-orphan")


class Activity(db.Model):
    __tablename__ = "activities"
    id            = db.Column(db.Integer, primary_key=True)
    entry_id      = db.Column(db.Integer, db.ForeignKey("entries.id"), nullable=False)
    name          = db.Column(db.Text, nullable=False)
    feeling_after = db.Column(db.Text, nullable=True)


class DietItem(db.Model):
    __tablename__ = "diet_items"
    id       = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey("entries.id"), nullable=False)
    food     = db.Column(db.Text, nullable=False)
    feeling  = db.Column(db.Text, nullable=True)


class Attachment(db.Model):
    __tablename__ = "attachments"
    id       = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey("entries.id"), nullable=False)
    label    = db.Column(db.String(200), nullable=True)
    url      = db.Column(db.Text, nullable=True)
    is_image = db.Column(db.Boolean, default=False)
