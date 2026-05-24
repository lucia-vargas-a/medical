# Medical Tracker — Setup Guide
### Private health tracking · Python + Flask + MySQL · Hosted on Railway

---

## What this app does

Tracks over time, including:
- Conditions and affected parts
- Symptom
- Treatments
- Appointments
- Doctors
- Timeline

**Privacy by design:** The app blocks emails, phone numbers, URLs and full names from being saved. No personal information is stored.

---

## Files in this project

## STEP 1 — Install Python on your Mac

Open Terminal (press Cmd+Space, type "Terminal", press Enter).

Check if Python is already installed:
```bash
python3 --version
```

If you see a version number (3.10 or higher), skip to Step 2.

If not, install it:
```bash
brew install python
```

If brew is not installed either, first run:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## STEP 2 — Install Git (to upload code to Railway)

Check if git is installed:
```bash
git --version
```

If not:
```bash
brew install git
```

---

## STEP 3 — Install Railway CLI

```bash
brew install railway
```

---

## STEP 4 — Set up a Railway account

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Sign up (you can use your Google account — this is just for Railway's website, not for your app)
4. Verify your email

---

## STEP 5 — Create a new Railway project with MySQL

1. In the Railway dashboard, click **"New Project"**
2. Click **"Empty Project"**
3. Click **"Add a Service"** → select **"Database"** → select **"MySQL"**
4. Wait about 30 seconds for the database to be created
5. Click on the MySQL service → go to the **"Variables"** tab
6. Copy the value of `MYSQL_URL` — you will need it shortly

---

## STEP 6 — Put your project files in a folder

In Terminal, go to where you saved the medical_tracker folder:
```bash
cd ~/Downloads/medical_tracker   # adjust path if needed
```

---

## STEP 7 — Run the privacy unit tests (verify the filter works)

```bash
pip3 install pytest
python3 -m pytest test_privacy.py -v
```

You should see all tests passing (green). If any fail, do not deploy until fixed.

---

## STEP 8 — Deploy to Railway

Log in to Railway from your terminal:
```bash
railway login
```

This opens a browser window — log in with your Railway account.

Initialize the project:
```bash
railway init
```

When asked, select **"Create new project"** and give it a name like `medical-tracker`.

Link your MySQL database:
```bash
railway service
```

Select the MySQL service when prompted.

Deploy your app:
```bash
railway up
```

---

## STEP 9 — Set environment variables (your username, password, secret key)

In the Railway dashboard:
1. Click on your app service (not the MySQL one)
2. Go to **"Variables"** tab
3. Add these three variables:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Paste the MYSQL_URL you copied in Step 5 |
| `APP_USERNAME` | Choose a username (e.g. `myname`) |
| `APP_PASSWORD` | Choose a strong password |
| `SECRET_KEY` | Any long random string (e.g. `x7k2m9q4w1p8`) |

4. Click **"Deploy"** after adding variables

---

## STEP 10 — Open your app

1. In the Railway dashboard, click on your app service
2. Go to **"Settings"** → **"Domains"**
3. Click **"Generate Domain"**
4. You'll get a URL like `medical-tracker-production.up.railway.app`
5. Open that URL in your browser
6. Log in with the username and password you set in Step 9

---

## Doctor code system

When you add a doctor, the app assigns a number automatically (1, 2, 3...).
Keep a **private handwritten note** or a note on your personal phone (NOT in this app):

```
DR-1 = Dr. García — Rheumatology — Hospital La Paz
DR-2 = Dr. Martín — General Practitioner — Clinic Centro
DR-3 = Dr. López — Physiotherapist — Clínica Sport
```

---

## Running the privacy tests again later

Any time you modify the code, re-run:
```bash
python3 -m pytest test_privacy.py -v
```

All tests must pass before deploying updates.

---

## Deploying updates after making changes

Any time you change the code and want to update the live app:
```bash
cd ~/Downloads/medical_tracker
railway up
```

That's it. Railway handles the rest.

---

## Backing up your data

To export your database at any time:
1. Go to Railway dashboard → MySQL service → **"Data"** tab
2. Click **"Export"** to download a full SQL backup

Keep this backup in a safe place (external hard drive or encrypted storage).

---

## Questions, changes, improvements

You can return to this conversation at any time and ask for:
- New fields or tables
- New pages (e.g. a medications summary page)
- Charts and reports
- Export to PDF or CSV
- Any other feature

Just describe what you want and the code will be updated.
