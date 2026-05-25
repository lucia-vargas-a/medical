import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from models import db, Condition, Entry, Activity, DietItem, Attachment
from privacy import validate_fields

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "change-this-in-production-please")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///medical_tracker.db")
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

APP_USERNAME = os.environ.get("APP_USERNAME", "admin")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "changeme123")

db.init_app(app)
with app.app_context():
    db.create_all()


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


@app.route("/")
@login_required
def dashboard():
    conditions = Condition.query.order_by(Condition.created_at.desc()).all()
    for c in conditions:
        c.latest = Entry.query.filter_by(condition_id=c.id).order_by(Entry.entry_at.desc()).first()
    return render_template("dashboard.html", conditions=conditions)


@app.route("/conditions/add", methods=["GET", "POST"])
@login_required
def add_condition():
    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        notes = request.form.get("notes", "").strip()
        if not name:
            flash("Condition name is required.", "danger")
            return render_template("add_condition.html")
        check = validate_fields({"name": name, "notes": notes})
        if not check["ok"]:
            for err in check["errors"]:
                flash(err, "danger")
            return render_template("add_condition.html")
        condition = Condition(name=name, notes=notes or None)
        db.session.add(condition)
        db.session.commit()
        flash(f'Condition "{condition.name}" created.', "success")
        return redirect(url_for("condition_detail", condition_id=condition.id))
    return render_template("add_condition.html")


@app.route("/conditions/<int:condition_id>")
@login_required
def condition_detail(condition_id):
    condition = Condition.query.get_or_404(condition_id)
    entries = Entry.query.filter_by(condition_id=condition_id).order_by(Entry.entry_at.desc()).all()
    return render_template("condition_detail.html", condition=condition, entries=entries)


@app.route("/conditions/<int:condition_id>/delete", methods=["POST"])
@login_required
def delete_condition(condition_id):
    condition = Condition.query.get_or_404(condition_id)
    db.session.delete(condition)
    db.session.commit()
    flash("Condition deleted.", "success")
    return redirect(url_for("dashboard"))


@app.route("/conditions/<int:condition_id>/entries/add", methods=["GET", "POST"])
@login_required
def add_entry(condition_id):
    condition = Condition.query.get_or_404(condition_id)
    if request.method == "POST":
        text_fields = {
            "symptoms":     request.form.get("symptoms", ""),
            "events":       request.form.get("events", ""),
            "context":      request.form.get("context", ""),
            "observations": request.form.get("observations", ""),
            "doctor":       request.form.get("doctor", ""),
            "medications":  request.form.get("medications", ""),
        }
        check = validate_fields(text_fields)
        if not check["ok"]:
            for err in check["errors"]:
                flash(err, "danger")
            return render_template("add_entry.html", condition=condition,
                                   now_date=request.form.get("entry_date"),
                                   now_time=request.form.get("entry_time"))
        entry_date = request.form.get("entry_date", "")
        entry_time = request.form.get("entry_time", "00:00")
        try:
            entry_at = datetime.strptime(f"{entry_date} {entry_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            entry_at = datetime.utcnow()
        entry = Entry(
            condition_id = condition_id,
            entry_at     = entry_at,
            symptoms     = text_fields["symptoms"]     or None,
            events       = text_fields["events"]       or None,
            context      = text_fields["context"]      or None,
            observations = text_fields["observations"] or None,
            doctor       = text_fields["doctor"]       or None,
            medications  = text_fields["medications"]  or None,
        )
        db.session.add(entry)
        db.session.flush()

        for name, feeling in zip(request.form.getlist("activity_name[]"),
                                  request.form.getlist("activity_feeling[]")):
            if name.strip():
                db.session.add(Activity(entry_id=entry.id, name=name.strip(),
                                        feeling_after=feeling.strip() or None))

        for food, feeling in zip(request.form.getlist("diet_food[]"),
                                  request.form.getlist("diet_feeling[]")):
            if food.strip():
                db.session.add(DietItem(entry_id=entry.id, food=food.strip(),
                                        feeling=feeling.strip() or None))

        att_labels = request.form.getlist("att_label[]")
        att_urls   = request.form.getlist("att_url[]")
        att_imgs   = request.form.getlist("att_is_image[]")
        for i, url in enumerate(att_urls):
            if url.strip():
                label    = att_labels[i].strip() if i < len(att_labels) else ""
                is_image = (att_imgs[i] == "1") if i < len(att_imgs) else False
                db.session.add(Attachment(entry_id=entry.id, label=label or None,
                                          url=url.strip(), is_image=is_image))

        db.session.commit()
        flash("Entry saved.", "success")
        return redirect(url_for("condition_detail", condition_id=condition_id))

    now = datetime.now()
    return render_template("add_entry.html", condition=condition,
                           now_date=now.strftime("%Y-%m-%d"),
                           now_time=now.strftime("%H:%M"))


@app.route("/entries/<int:entry_id>")
@login_required
def entry_detail(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    return render_template("entry_detail.html", entry=entry)


@app.route("/entries/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    cid = entry.condition_id
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted.", "success")
    return redirect(url_for("condition_detail", condition_id=cid))


if __name__ == "__main__":
    app.run(debug=True)
