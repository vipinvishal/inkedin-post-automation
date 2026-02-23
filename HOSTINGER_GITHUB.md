# Host on Hostinger using GitHub (simplest)

**Full walkthrough:** For detailed step-by-step from GitHub signup and repo creation through Hostinger login to cron, see **[SETUP_STEP_BY_STEP.md](SETUP_STEP_BY_STEP.md)**.

4 steps: push to GitHub → connect repo in Hostinger → add .env and Python → add cron.

---

## Step 1: Push project to GitHub

1. Open **Terminal** on your Mac and go to the project folder:
   ```bash
   cd "/Users/vipinvishal/Desktop/Vipin Codes/LinkedIN post automation"
   git init
   git add .
   git commit -m "Initial commit"
   ```
2. On **GitHub**: [github.com/new](https://github.com/new) → create a new repo (e.g. `linkedin-post-automation`). Do **not** add README or .gitignore.
3. Push (use your GitHub username and repo name):
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main
   ```
   Your `.env` and `.venv` are already in `.gitignore`, so they **won’t** be uploaded.

---

## Step 2: Connect repo in Hostinger

1. Log in to **Hostinger** → **hPanel** → select your **website** → **Manage**.
2. In the left menu, click **Git**.
3. **Create a New Repository:**
   - **Repository address:** `https://github.com/YOUR_USERNAME/YOUR_REPO.git`
   - **Branch:** `main`
   - **Install path:** leave **empty** (code goes to `public_html`) or type `linkedin-bot` to use a subfolder.
4. Click **Create** (or **Add**), then click **Deploy** so Hostinger clones the code.
5. Optional: turn on **Auto-Deployment** and add the webhook URL in GitHub (Repo → Settings → Webhooks) so every future `git push` updates the server.

Remember where the code is (e.g. `public_html` or `public_html/linkedin-bot`) for the next steps.

---

## Step 3: Add .env and install Python on the server

**3a. Create .env**

1. Hostinger → **Files** → **File Manager** → open the folder where the code was deployed.
2. **+ File** → name: `.env` → Create.
3. Open `.env` → paste the **full content** of your local `.env` from your Mac → Save.

**3b. Install Python (SSH)**

1. Hostinger → **Advanced** → **SSH Access** → turn **ON**. Note the **username** and **host**.
2. On your Mac, in Terminal:
   ```bash
   ssh YOUR_USER@YOUR_HOST
   ```
3. On the server, go to the project folder and run (change the path if you used an Install path like `linkedin-bot`):
   ```bash
   cd ~/domains/yourdomain.com/public_html
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   mkdir -p logs
   ```
4. Optional test: run `.venv/bin/python scripts/run_pipeline.py` — you should see “Draft sent”. Then type `exit`.

If you see `python3: command not found`, you need a **VPS** plan on Hostinger (shared hosting often has no Python).

---

## Step 4: Add cron job (Mon / Wed / Fri 11:00 AM)

1. Hostinger → **Advanced** → **Cron Jobs** → **Create**.
2. **Schedule:** `0 11 * * 1,3,5` (11:00 AM Mon/Wed/Fri in **server** time).  
   For **11:00 AM India (IST)** use: `30 5 * * 1,3,5`.
3. **Command** (replace with your real path; use `pwd` in SSH to see it):
   ```bash
   cd /home/YOUR_USER/domains/yourdomain.com/public_html && .venv/bin/python scripts/cron_run.py
   ```
   If you used Install path `linkedin-bot`, use `public_html/linkedin-bot` before `&&`.
4. Save.

**Optional – post approved drafts at 11:30:** Add a **second** cron: schedule `30 11 * * 1,3,5`, same command but end with `scripts/cron_run.py --approval`.

---

Done. Every Mon/Wed/Fri at 11:00 you get the draft email; reply **APPROVE-&lt;id&gt;** and the 11:30 run will post to LinkedIn.
