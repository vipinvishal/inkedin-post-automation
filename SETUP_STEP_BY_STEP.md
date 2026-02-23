# Step-by-step: GitHub repo + Hostinger hosting

Two parts: **Part A** = set up GitHub and push your code. **Part B** = log in to Hostinger and host the app using that GitHub repo.

---

# Part A: Set up the GitHub repo

## A1. Create a GitHub account (if you don’t have one)

1. Open a browser and go to **https://github.com**
2. Click **Sign up** (top right).
3. Enter email, password, username; verify email.
4. Skip “tailored experience” if you like; you can complete setup later.

---

## A2. Create a new repository

1. Log in to GitHub.
2. Click the **+** icon (top right) → **New repository**.
   - Or go directly: **https://github.com/new**
3. Fill in:
   - **Repository name:** e.g. `linkedin-post-automation` (no spaces).
   - **Description:** optional (e.g. “LinkedIn draft automation”).
   - **Public** (recommended).
   - **Do not** check “Add a README file”.
   - **Do not** add .gitignore or license yet (your project already has them).
4. Click **Create repository**.

You’ll see a page like “Quick setup — if you’ve pushed before…”. Keep this page open; you’ll need the repo URL (e.g. `https://github.com/YOUR_USERNAME/linkedin-post-automation.git`).

---

## A3. Push your project from your Mac

Do this in **Terminal** on your Mac (in your project folder).

**Step 3.1 – Go to the project folder**

```bash
cd "/Users/vipinvishal/Desktop/Vipin Codes/LinkedIN post automation"
```

**Step 3.2 – Initialize Git and first commit**

```bash
git init
git add .
git status
```

Check that **`.env`** and **`.venv`** do **not** appear in the list (they are in `.gitignore`). Then:

```bash
git commit -m "Initial commit"
```

**Step 3.3 – Connect to GitHub and push**

Replace `YOUR_USERNAME` with your GitHub username and `YOUR_REPO` with the repo name (e.g. `linkedin-post-automation`):

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

- If it asks for login: use your **GitHub username** and a **Personal Access Token** (not your GitHub password).  
  To create a token: GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Generate new token** → enable **repo** → copy the token and paste it when Terminal asks for password.

**Step 3.4 – Verify**

- Open **https://github.com/YOUR_USERNAME/YOUR_REPO** in the browser. You should see your files (no `.env`, no `.venv`).

---

Part A is done. Your code is on GitHub. Next: Hostinger.

---

# Part B: Host on Hostinger using GitHub

## B1. Log in to Hostinger

1. Go to **https://www.hostinger.com**
2. Click **Log in** (top right).
3. Enter your email and password (or use Google).
4. You’ll land in **hPanel** (Hostinger control panel).

---

## B2. Open your website and Git

1. In hPanel, find the **website** you want to use (e.g. your domain).
2. Click **Manage** (or **Open**) for that website.
3. In the **left sidebar**, click **Git** (under “Advanced” or similar).

If you don’t see **Git**, your plan might not include it; check Hostinger’s plan features or support.

---

## B3. Connect the GitHub repo

1. On the Git page, click **Create a New Repository** (or **Add repository**).
2. Fill in:
   - **Repository address:**  
     `https://github.com/YOUR_USERNAME/YOUR_REPO.git`  
     (same URL as in Part A; replace YOUR_USERNAME and YOUR_REPO).
   - **Branch:** `main`
   - **Install path:**  
     - Leave **empty** → code will go to `public_html`.  
     - Or type e.g. `linkedin-bot` → code will go to `public_html/linkedin-bot`.
3. Click **Create** (or **Add**).
4. After the repo is added, click **Deploy** so Hostinger downloads the code from GitHub.
5. Wait until deployment finishes. Note the **path** where the code is (e.g. `public_html` or `public_html/linkedin-bot`).

**Optional – auto-update on push:**  
Turn on **Auto-Deployment** and copy the webhook URL. In GitHub: go to your repo → **Settings** → **Webhooks** → **Add webhook** → paste the URL → Save. After that, every `git push` will update the server.

---

## B4. Create the `.env` file on the server

1. In Hostinger (same website), open **Files** → **File Manager** (or **Manage** → **Files**).
2. Navigate to the folder where the code was deployed (e.g. `domains → yourdomain.com → public_html`, or `public_html → linkedin-bot`).
3. Click **+ File** (or **New file**).
4. Name the file: `.env`
5. Click **Create**.
6. **Edit** the file and **paste the full contents** of your local `.env` from your Mac (all your keys: Gemini, Gmail, LinkedIn, etc.).
7. **Save**.

---

## B5. Enable SSH and install Python (venv + dependencies)

**B5.1 – Enable SSH**

1. In Hostinger, go to **Advanced** → **SSH Access**.
2. Turn **SSH Access** **ON**.
3. Note the **username** and **host** (e.g. `u123456789@server123.hostinger.com`). You may need to set or view a password.

**B5.2 – Connect via SSH from your Mac**

1. Open **Terminal** on your Mac.
2. Run (use the username and host from Hostinger):

   ```bash
   ssh YOUR_USER@YOUR_HOST
   ```

   Example: `ssh u123456789@server123.hostinger.com`  
   Enter the password when asked.

**B5.3 – Go to project folder and create venv**

Replace the path with yours (use the path you noted in B3). Common pattern:

```bash
cd ~/domains/yourdomain.com/public_html
```

If you used Install path `linkedin-bot`:

```bash
cd ~/domains/yourdomain.com/public_html/linkedin-bot
```

To see your exact path after SSH, run `pwd` once you’re in the project folder.

Then run:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p logs
```

**B5.4 – Quick test (optional)**

```bash
.venv/bin/python scripts/run_pipeline.py
```

You should see something like “Draft sent”. Then type `exit` to leave SSH.

If you get `python3: command not found`, your Hostinger plan may not include Python (e.g. some shared plans); you may need a VPS plan.

---

## B6. Add cron jobs (Mon / Wed / Fri 11:00 and 11:30)

**B6.1 – Open Cron Jobs**

1. In Hostinger, go to **Advanced** → **Cron Jobs**.
2. Click **Create** (or **Add cron job**).

**B6.2 – First cron: send draft email (11:00)**

1. **Schedule:**  
   - Server in your country (e.g. 11:00 local): `0 11 * * 1,3,5`  
   - If server is in UTC and you want **11:00 AM India (IST)**: `30 5 * * 1,3,5`
2. **Command:** use the **full path** to your project and run the pipeline (replace with your actual path):

   ```bash
   cd /home/YOUR_USER/domains/yourdomain.com/public_html && .venv/bin/python scripts/cron_run.py
   ```

   If you used `linkedin-bot`, use:

   ```bash
   cd /home/YOUR_USER/domains/yourdomain.com/public_html/linkedin-bot && .venv/bin/python scripts/cron_run.py
   ```

   To get the exact path: SSH in, `cd` to the project folder, run `pwd`, and use that path before `&&`.
3. **Save.**

**B6.3 – Second cron: post approved drafts to LinkedIn (11:30)**

1. **Create** another cron job.
2. **Schedule:**  
   - 11:30 local: `30 11 * * 1,3,5`  
   - 11:30 AM IST (server UTC): `0 6 * * 1,3,5`
3. **Command:** same as above, but with `--approval` at the end:

   ```bash
   cd /home/YOUR_USER/domains/yourdomain.com/public_html && .venv/bin/python scripts/cron_run.py --approval
   ```

4. **Save.**

---

## You’re done

- **Part A:** Code is on GitHub; you can push updates with `git add . && git commit -m "message" && git push`.
- **Part B:** Hostinger runs the pipeline every Mon/Wed/Fri at 11:00 (draft email) and at 11:30 (post approved drafts to LinkedIn).

You only reply to the draft email with **APPROVE-&lt;id&gt;**; the 11:30 cron does the LinkedIn posting for you.
