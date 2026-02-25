# Hostinger VPS – terminal-only setup

Run these commands **in the terminal on your Hostinger VPS** (browser terminal in hPanel, or SSH from your Mac). Replace `YOUR_PROJECT_DIR` with the folder where you want the project (e.g. `~/linkedin-bot` or `/root/linkedin-bot`).

---

## 1. Clone the repo and go into the project

```bash
# Pick a folder for the project (e.g. in your home directory)
export PROJECT_DIR=~/linkedin-bot
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Clone the GitHub repo
git clone https://github.com/vipinvishal/inkedin-post-automation.git .
```

---

## 2. Create `.env` and paste your secrets

```bash
# Create empty .env, then open it to paste your content
nano .env
```

- Paste the **full content** of your local `.env` from your Mac (all keys: Gemini, Gmail, LinkedIn).
- Save: **Ctrl+O**, Enter, then exit: **Ctrl+X**.

---

## 3. Python virtual environment and dependencies

```bash
# Make sure you're in the project folder
cd "$PROJECT_DIR"

# Create venv and install dependencies
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Create logs folder
mkdir -p logs
```

---

## 4. Get the full project path (for cron)

```bash
pwd
```

**Copy this path.** You need it for the cron commands below (e.g. `/root/linkedin-bot`).

---

## 5. Test run (optional)

```bash
.venv/bin/python scripts/run_pipeline.py
```

You should see “Draft sent”. Then continue to cron.

---

## 6. Add cron jobs (Mon/Wed/Fri 11:00 and 11:30)

Replace **`/root/linkedin-bot`** with the path you got from `pwd` in step 4.

**Open crontab:**

```bash
crontab -e
```

If asked to choose an editor, pick **nano** (often option 1). Then add these **two lines** at the end of the file:

**11:00 AM server time (pipeline – draft email):**
```cron
0 11 * * 1,3,5 cd /root/linkedin-bot && .venv/bin/python scripts/cron_run.py
```

**Post to LinkedIn as soon as you approve (every 5 min on Mon/Wed/Fri):**
```cron
*/5 * * * 1,3,5 cd /root/linkedin-bot && .venv/bin/python scripts/cron_run.py --approval-only
```
This runs only the approval check (no new draft email). When you reply APPROVE to the draft email, the next run within 5 minutes will post it to LinkedIn.

**For 11:00 AM India (IST)** when server is in UTC, use for the pipeline:
```cron
30 5 * * 1,3,5 cd /root/linkedin-bot && .venv/bin/python scripts/cron_run.py
*/5 * * * 1,3,5 cd /root/linkedin-bot && .venv/bin/python scripts/cron_run.py --approval-only
```

Save: **Ctrl+O**, Enter. Exit: **Ctrl+X**.

**Check that cron was saved:**
```bash
crontab -l
```

You should see your two lines.

---

## One-time copy-paste block (after you set PROJECT_DIR and .env)

Run step 1 yourself (clone + nano .env). Then you can run this block in one go (replace `/root/linkedin-bot` if different):

```bash
cd ~/linkedin-bot
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p logs
echo "Setup done. Run: pwd   (then add that path to crontab -e)"
```

Then do **crontab -e** and add the two cron lines with your real path.
