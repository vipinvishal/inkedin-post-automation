# Final hosting on Hostinger VPS – step by step

Use this guide when your Hostinger VPS is ready and you want to host the LinkedIn post automation. Do each step in order. Your repo is: **https://github.com/vipinvishal/inkedin-post-automation**

---

## Step 1: Log in to Hostinger and open your VPS

1. Open your browser and go to **https://www.hostinger.com**
2. Click **Log in** (top right) and sign in with your email and password.
3. You will see **hPanel** (Hostinger control panel).
4. In the **Hosting** or **VPS** section, find your **VPS** (it may show your server IP or a name like “VPS 1”).
5. Click **Manage** (or **Open**) next to that VPS.  
   You should now see the management screen for this server (with a left sidebar menu).

**What you need:** You must be inside the panel for **this** VPS, not a different product.

---

## Step 2: Find Git and add your GitHub repo

1. In the **left sidebar** of the VPS management page, look for **Git** (it may be under a section like “Advanced” or “Development”).
2. Click **Git**.
3. On the Git page, find the option to **Create a New Repository** or **Add repository** and click it.
4. A form will appear. Fill it in **exactly** as below:

   | Field | What to enter |
   |-------|----------------|
   | **Repository address** | `https://github.com/vipinvishal/inkedin-post-automation.git` |
   | **Branch** | `main` |
   | **Install path** | Leave **empty** (so code goes to the root folder, usually `public_html`). Or type `linkedin-bot` if you want the project in a subfolder. |

5. Click **Create** or **Add** to save the repository.
6. After the repo appears in the list, click the **Deploy** button so Hostinger clones the code from GitHub.
7. Wait until the deployment finishes (you may see a success message or “Build complete”).
8. **Write down where the code is:**
   - If Install path was **empty:** code is in **`public_html`** (full path often like `.../public_html`).
   - If you used **`linkedin-bot`:** code is in **`public_html/linkedin-bot`**.

You will need this path for creating `.env`, SSH, and cron.

---

## Step 3: Create the `.env` file on the server

The app needs your secrets (Gemini, Gmail, LinkedIn) in a file named `.env`. You will create it in the same folder where the code was deployed.

1. In the **left sidebar**, open **Files** (or **File Manager**). If you don’t see it, look under **Advanced** or **Management**.
2. In File Manager, navigate to the folder where the code was deployed:
   - Often: **domains** → **yourdomain.com** (or your main domain) → **public_html**.
   - If you used Install path **linkedin-bot**, open the **linkedin-bot** folder inside **public_html**.
   - You should see project files (e.g. `scripts`, `src`, `requirements.txt`, `README.md`).
3. Click **+ File** or **New file**.
4. When asked for the file name, type exactly: **`.env`** (including the dot at the start). Then Create/Save.
5. **Edit** the new `.env` file (right‑click → Edit, or select it and click Edit).
6. On your **Mac**, open your project folder and open the **`.env`** file in a text editor. Select **all** the text and copy it.
7. Back in Hostinger File Manager, in the `.env` editor, **paste** that full content (replace any placeholder text). Do not leave any of your real keys on your Mac out of the paste.
8. Click **Save** or **Update** to save `.env` on the server.

Your server now has the same environment variables as your Mac (Gemini API, Gmail, LinkedIn, etc.).

---

## Step 4: Turn on SSH and get your SSH details

1. In the **left sidebar**, go to **Advanced** → **SSH Access** (or search for “SSH” in the panel).
2. Turn **SSH Access** **ON** if it is not already on.
3. Note and **copy** these somewhere safe:
   - **Username** (e.g. `root` or `u123456789`)
   - **Host / Server address** (e.g. `server123.hostinger.com` or an IP)
   - **Password** (if shown; otherwise use the one you set when creating the VPS).  
   You will use these to connect from your Mac in the next step.

---

## Step 5: Connect from your Mac via SSH and find the project path

1. On your **Mac**, open **Terminal** (Applications → Utilities → Terminal, or search “Terminal” in Spotlight).
2. Connect to the server (replace with your actual username and host):

   ```bash
   ssh root@YOUR_SERVER_HOST
   ```

   Example: if the host is `123.45.67.89`, then:

   ```bash
   ssh root@123.45.67.89
   ```

   If your username is not `root`, use that instead, e.g. `ssh u123456789@server123.hostinger.com`.
3. When prompted **“Are you sure you want to continue connecting?”**, type **yes** and press Enter.
4. When prompted for a **password**, paste or type your SSH password (nothing will appear as you type). Press Enter.
5. When you are in, your prompt will change (e.g. `root@vps:~#`). You are now on the **server**.
6. Go to the folder where the project was deployed. Try (adjust domain if yours is different):

   ```bash
   cd /root/domains/yourdomain.com/public_html
   ```

   If that folder does not exist, try:

   ```bash
   cd ~/public_html
   ```

   Or list directories to find it:

   ```bash
   ls -la
   ls -la ~/domains/
   ```

   Once you are in the project folder, you must see `scripts`, `src`, `requirements.txt`. If you used Install path **linkedin-bot**, then:

   ```bash
   cd /root/domains/yourdomain.com/public_html/linkedin-bot
   ```

7. When you are in the **project folder**, run:

   ```bash
   pwd
   ```

   **Copy the full path** that is printed (e.g. `/root/domains/yourdomain.com/public_html`). You will use this **exact path** in the cron jobs later.

---

## Step 6: Install Python virtual environment and dependencies

Stay in the **same SSH session** and in the **project folder** (the path you got from `pwd`).

1. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

   If you see **“command not found: python3”**, try:

   ```bash
   python -m venv .venv
   ```

   On Ubuntu you can install Python with: `apt update && apt install -y python3 python3-venv python3-pip`

2. Activate the venv and install dependencies:

   ```bash
   .venv/bin/pip install -r requirements.txt
   ```

   Wait until all packages are installed (no errors).

3. Create the `logs` folder (used by the cron script):

   ```bash
   mkdir -p logs
   ```

4. **Optional test:** Run the pipeline once to confirm everything works:

   ```bash
   .venv/bin/python scripts/run_pipeline.py
   ```

   You should see something like “Draft sent” (and receive the draft email). If you see an error, fix it before setting cron (e.g. missing `.env` or wrong path).

5. When finished, type **exit** and press Enter to disconnect from SSH.

---

## Step 7: Add the first cron job (send draft email at 11:00 AM)

This cron runs the pipeline every **Monday, Wednesday, and Friday** at **11:00 AM** (server time) and sends you the draft email.

1. In **Hostinger**, in the **left sidebar**, go to **Advanced** → **Cron Jobs** (or search “Cron”).
2. Click **Create** or **Add cron job**.
3. Set the **schedule**:
   - If your server time is **already in your timezone** (e.g. India): use **`0 11 * * 1,3,5`** (11:00 AM Mon/Wed/Fri).
   - If the server uses **UTC** and you want **11:00 AM India (IST)** use **`30 5 * * 1,3,5`** (5:30 UTC = 11:00 IST).
4. In the **Command** field, enter **one** line (replace `FULL_PROJECT_PATH` with the path you copied from `pwd` in Step 5):

   ```bash
   cd FULL_PROJECT_PATH && .venv/bin/python scripts/cron_run.py
   ```

   Example (if `pwd` was `/root/domains/yourdomain.com/public_html`):

   ```bash
   cd /root/domains/yourdomain.com/public_html && .venv/bin/python scripts/cron_run.py
   ```

   If you used Install path **linkedin-bot**:

   ```bash
   cd /root/domains/yourdomain.com/public_html/linkedin-bot && .venv/bin/python scripts/cron_run.py
   ```

5. Click **Save** or **Create**.

The first cron is done. At 11:00 (in the schedule you chose) you will receive the draft email.

---

## Step 8: Add the second cron job (post approved drafts at 11:30 AM)

This cron checks your email for **APPROVE-&lt;id&gt;** replies and posts those drafts to LinkedIn.

1. Again go to **Advanced** → **Cron Jobs** and click **Create** / **Add cron job**.
2. Set the **schedule** (30 minutes after the first one):
   - Same timezone as Step 7, 11:30: **`30 11 * * 1,3,5`**
   - Server UTC, 11:30 AM IST: **`0 6 * * 1,3,5`**
3. **Command:** same as in Step 7, but add **`--approval`** at the end:

   ```bash
   cd FULL_PROJECT_PATH && .venv/bin/python scripts/cron_run.py --approval
   ```

   Example:

   ```bash
   cd /root/domains/yourdomain.com/public_html && .venv/bin/python scripts/cron_run.py --approval
   ```

4. Click **Save** or **Create**.

---

## You’re done

- **11:00 (Mon/Wed/Fri):** The server runs the pipeline and sends you the draft email.
- **You:** Reply to that email with **APPROVE-&lt;id&gt;** (the `&lt;id&gt;` is in the email).
- **11:30 (same days):** The server runs the approval check and posts that draft to LinkedIn.

No manual posting on LinkedIn needed.

**Useful paths:**

- Repo: https://github.com/vipinvishal/inkedin-post-automation  
- To update code on the server: in Hostinger Git page, click **Deploy** again, or set up Auto-Deployment with the webhook in GitHub (repo → Settings → Webhooks).  
- To see logs on the server: SSH in, go to the project folder, then run: `cat logs/cron.log`
