# Gmail setup for LinkedIn post automation

We’ll use **one Gmail account** to:
- **Send** draft emails to you (post text + Approve / Re-write).
- **Receive** your replies (Approve or Re-write) so the app can act on them.

The simplest way is an **App Password** (no Google Cloud project needed).

---

## Step 1: Use a Gmail account

- Use the Gmail address you want for this automation (e.g. `you@gmail.com`).
- This account will **send** the draft emails and **receive** your replies.
- You can use a separate Gmail just for this, or your main one.

---

## Step 2: Turn on 2-Step Verification

App Passwords only work when 2-Step Verification is on.

1. Go to [Google Account](https://myaccount.google.com/).
2. Click **Security** (left menu).
3. Under **“How you sign in to Google”**, click **2-Step Verification**.
4. If it’s off, click **Get started** and follow the steps (phone number, code, etc.) until 2-Step Verification is **On**.

---

## Step 3: Create an App Password

1. Still in [Google Account → Security](https://myaccount.google.com/security).
2. Under **“How you sign in to Google”**, find **2-Step Verification** and click it.
3. Scroll to the bottom to **“App passwords”** and click it.
   - If you don’t see “App passwords”, make sure 2-Step Verification is really on and you’re not in a workspace that blocks it.
4. Click **Select app** → choose **Mail** (or **Other** and type e.g. “LinkedIn automation”).
5. Click **Select device** → choose **Other** and type e.g. “LinkedIn post automation”.
6. Click **Generate**.
7. Google shows a **16-character password** (like `abcd efgh ijkl mnop`).
8. **Copy it** and store it somewhere safe (we’ll put it in `.env` in the next step). You won’t see it again.

---

## Step 4: Add the credentials to this project

1. Open the file **`.env`** in this project (create it from `.env.example` if needed).
2. Set these two (use your real Gmail and the 16-character app password **without spaces**):

```env
GMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

Example: if your Gmail is `jane@gmail.com` and the app password is `abcd efgh ijkl mnop`, use:

```env
GMAIL_ADDRESS=jane@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

3. Save `.env`. Don’t commit it to git (it’s already in `.gitignore`).

---

## Step 5: Confirm IMAP is allowed (for reading replies)

Gmail usually has IMAP on by default. To check:

1. Open [Gmail](https://mail.google.com/) in the browser.
2. Click the gear → **See all settings**.
3. Go to **Forwarding and POP/IMAP**.
4. Under **IMAP access**, select **Enable IMAP** if it isn’t already.
5. Save changes.

---

## What we need from you

Once you’ve done the steps above, you don’t need to send your password to anyone. You only add it in your own `.env` on your machine.

For the code to work, we need you to have set in **your** `.env`:

| Variable              | Example              | Description                          |
|-----------------------|----------------------|--------------------------------------|
| `GMAIL_ADDRESS`       | `you@gmail.com`      | Gmail that sends and receives drafts |
| `GMAIL_APP_PASSWORD`  | `abcdefghijklmnop`   | 16-character app password (no spaces) |

After that, we’ll use:
- **SMTP** (with this app password) to send the draft email to you.
- **IMAP** (same app password) to read your replies and detect Approve / Re-write.

---

## Optional: Use a label for draft replies

Later we can add a Gmail label (e.g. `linkedin-drafts`) and have the script only look at emails with that label, so your inbox stays clean. For the first version we’ll look at recent mail from you to this address.

---

## Troubleshooting

- **“App passwords” not visible**  
  Make sure 2-Step Verification is really turned on. Some work or school accounts don’t allow App Passwords.

- **Login / security errors when sending**  
  Double-check:
  - `GMAIL_ADDRESS` is the full address.
  - `GMAIL_APP_PASSWORD` is the 16-character app password with **no spaces**.

- **Can’t read replies**  
  Confirm IMAP is enabled in Gmail settings (Step 5).

When your `.env` has `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` set, tell me and we’ll wire up the send and receive flow next.
