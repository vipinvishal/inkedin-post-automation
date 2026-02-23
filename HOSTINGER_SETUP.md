# Hosting on Hostinger – scheduled runs (Mon / Wed / Fri 11:00 AM)

**Easiest setup:** use **GitHub + Hostinger Git** → see **[HOSTINGER_GITHUB.md](HOSTINGER_GITHUB.md)** (4 steps: push repo → connect in Hostinger → .env + venv → cron).

---

## Alternative: Zip upload (5 steps)

### Step 1: Upload the project

1. On your Mac, zip the project **without** `.env` and without `.venv`:
   - In Finder, right‑click the project folder → **Compress** (or zip everything except `.env` and `.venv`).
2. In Hostinger: **hPanel** → **Files** → **File Manager**. Go to your home or `domains/yourdomain.com` (or `public_html`’s parent).
3. **Upload** the zip, then **Extract** it. You should get a folder like `LinkedIN post automation` or `linkedin-automation`. Rename it to something simple, e.g. `linkedin-bot`.

### Step 2: Create `.env` on the server

1. In File Manager, open the project folder (e.g. `linkedin-bot`).
2. Click **+ File** → name: `.env`
3. Open `.env` in the editor and **paste the full contents** of your local `.env` (from your Mac). Save.

### Step 3: Enable SSH and install Python dependencies

1. In Hostinger: **Advanced** → **SSH Access** – turn it **ON** and note the username/host (e.g. `u123456789@server.hostinger.com`).
2. On your Mac, open Terminal and connect (use the password or SSH key Hostinger shows):
   ```bash
   ssh u123456789@server.hostinger.com
   ```
3. Go to the project folder (path might be like `~/domains/yourdomain.com/linkedin-bot` or `~/public_html/linkedin-bot` – list with `ls` and `pwd`):
   ```bash
   cd ~/domains/yourdomain.com/linkedin-bot
   # or:  cd ~/public_html/linkedin-bot
   ```
4. Create a virtualenv and install dependencies:
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   mkdir -p logs
   ```
5. Test once (optional):
   ```bash
   .venv/bin/python scripts/run_pipeline.py
   ```
   If that runs and you get “Draft sent”, you’re good. Type `exit` to leave SSH.

**If `python3` is not found:** Hostinger shared hosting sometimes has no Python. Then you need a **VPS** plan from Hostinger and follow the same steps there (Python is preinstalled on VPS).

### Step 4: Add the cron job

1. In Hostinger: **Advanced** → **Cron Jobs**.
2. **Create new cron job:**
   - **Schedule:** `0 11 * * 1,3,5` (11:00 AM every Mon, Wed, Fri – in **server time**; Hostinger often uses UTC).
   - **Command:** (use **your** project path from Step 3; replace the path below with the one you got from `pwd`):
   ```bash
   cd /home/u123456789/domains/yourdomain.com/linkedin-bot && .venv/bin/python scripts/cron_run.py
   ```
3. Save.

**If you want 11:00 AM India time (IST):** Server is often UTC. 11:00 IST = 05:30 UTC. Use schedule `30 5 * * 1,3,5` and the same command.

### Step 5: (Optional) Approval check at 11:30

So that when you reply **APPROVE** to the email, the script can post to LinkedIn without another manual run:

- Add a **second** cron job:
  - **Schedule:** `30 11 * * 1,3,5` (11:30 AM; or for IST use `0 6 * * 1,3,5`).
  - **Command:** same as above but add `--approval` at the end:
  ```bash
  cd /home/u123456789/domains/yourdomain.com/linkedin-bot && .venv/bin/python scripts/cron_run.py --approval
  ```

Done. On Mon/Wed/Fri at 11:00 you’ll get the draft email; reply **APPROVE-&lt;id&gt;** and the 11:30 run will post it to LinkedIn (or run approval check manually anytime).

---

## Detailed reference (if you need it)

### Deploy the project (alternatives)

- **Option A – Git (if you use a repo)**  
  SSH into the server (or use Hostinger’s “SSH Access” / terminal), then:
  ```bash
  cd /home/your_user/domains/your_domain  # or your preferred path
  git clone https://github.com/YOUR_USER/YOUR_REPO.git linkedin-automation
  cd linkedin-automation
  ```
- **Option B – Upload**  
  Upload the whole project (e.g. via File Manager or FTP) to a folder like `linkedin-automation`. Do **not** upload `.env` or `.venv` (you’ll create `.env` on the server and install deps there).

---

## 2. Create `.env` on the server

Create a file `.env` in the project root with the same variables as on your Mac. You can copy from your local `.env` and paste (e.g. in File Manager “Create file” → `.env`), or create it via SSH:

```bash
cd /path/to/linkedin-automation
nano .env
```

Paste your values (GEMINI_API_KEY, GMAIL_*, LINKEDIN_*, etc.). Save and exit.  
**Important:** Do not commit `.env` to git. Keep it only on the server.

---

## 3. Python and dependencies on the server

Hostinger shared hosting may have a limited Python. Prefer **VPS** or a plan that allows Python 3 and pip.

**If you have SSH and Python 3:**

```bash
cd /path/to/linkedin-automation
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# Test
.venv/bin/python scripts/run_pipeline.py
```

If `python3` or `pip` are not available, use Hostinger’s “Setup Python App” (or similar) to create an app and install dependencies there; then in the cron command below use the path to that app’s Python instead of `.venv/bin/python`.

---

## 4. Cron jobs (Mon / Wed / Fri 11:00 AM)

In Hostinger: **Advanced** → **Cron Jobs** (or **Scheduled tasks**).  
Use **server timezone** (Hostinger often uses UTC; set 11:00 in the timezone shown in the panel).

### Pipeline – Monday, Wednesday, Friday at 11:00 AM

Runs research, generates draft, sends email to your Gmail.

| Field        | Value |
|-------------|--------|
| **Schedule** | `0 11 * * 1,3,5` (11:00 AM on Mon, Wed, Fri) |
| **Command**   | See below |

**Command (replace with your real path):**

```bash
cd /home/your_user/domains/your_domain/linkedin-automation && .venv/bin/python scripts/cron_run.py >> logs/cron.log 2>&1
```

If you don’t have a venv:

```bash
cd /path/to/linkedin-automation && python3 scripts/cron_run.py >> logs/cron.log 2>&1
```

Create the `logs` folder if needed: `mkdir -p /path/to/linkedin-automation/logs`.

### Approval check (optional) – same days at 11:30 AM

Picks up APPROVE replies and posts to LinkedIn. Gives you ~30 minutes to reply after the 11:00 email.

| Field        | Value |
|-------------|--------|
| **Schedule** | `30 11 * * 1,3,5` |
| **Command**   | Same as above but with `--approval`: |

```bash
cd /path/to/linkedin-automation && .venv/bin/python scripts/cron_run.py --approval >> logs/cron.log 2>&1
```

**Cron schedule reference (server time):**

- `0 11 * * 1,3,5` → 11:00 AM Monday, Wednesday, Friday  
- `30 11 * * 1,3,5` → 11:30 AM Monday, Wednesday, Friday  

If Hostinger uses UTC and you want 11:00 AM **India Standard Time (IST, UTC+5:30)**:

- 11:00 IST = 05:30 UTC → use `30 5 * * 1,3,5` for pipeline and `0 6 * * 1,3,5` for approval (or adjust to your timezone).

---

## 5. Check that it runs

- After the first scheduled run, open `logs/cron.log` on the server. You should see “Running pipeline…” and “Pipeline OK.” (and approval output if you use `--approval`).
- Check your Gmail for the draft email on the next Mon/Wed/Fri at 11:00 (server time).
- Reply **APPROVE-&lt;draft_id&gt;**; the 11:30 run (or the next run with `--approval`) will post to LinkedIn.

---

## 6. Troubleshooting

- **Cron not running**  
  Confirm the path in the cron command is correct and that the job is saved. Check Hostinger’s cron log or email notifications if enabled.

- **“Permission denied” or “No such file”**  
  Use full paths in the cron command (e.g. `/home/.../linkedin-automation`). Ensure `logs` exists and is writable: `mkdir -p logs && chmod 755 logs`.

- **Pipeline fails in cron but works in SSH**  
  Cron has a minimal environment. The script loads `.env` from the project directory, so as long as `cd` to the project root is in the command, it should work. If you use a custom Python path from “Setup Python App”, use that full path in the cron command.

- **Timezone**  
  Set the cron schedule to the server’s timezone (e.g. UTC). Convert your desired local time (e.g. 11:00 AM IST) to that timezone when choosing the minute/hour.
