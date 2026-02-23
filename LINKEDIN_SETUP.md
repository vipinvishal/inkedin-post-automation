# LinkedIn setup for posting

When you **Approve** a draft (reply with `APPROVE-<id>`), the script posts that text to your LinkedIn profile. To enable that, do a one-time OAuth and add credentials to `.env`.

---

## Final steps (you already added both products)

If you have **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect** in your app’s Products:

1. **Get a new token (with person URN)**  
   From the project root, with your venv activated:
   ```bash
   python scripts/linkedin_oauth.py
   ```
2. **In the browser**  
   Open the URL the script prints → sign in → click **Allow**.  
   The next page will show **two lines** (e.g. `LINKEDIN_ACCESS_TOKEN=...` and `LINKEDIN_PERSON_URN=urn:li:person:...`).
3. **Update `.env`**  
   Copy both lines from that page into your `.env` (replace any existing `LINKEDIN_ACCESS_TOKEN` and add `LINKEDIN_PERSON_URN` if missing).
4. **Verify**  
   ```bash
   python scripts/check_integration.py --post
   ```  
   You should see “Integration OK” and a test post on LinkedIn.

If the auth page shows **“Scope openid is not authorized”**, wait a few minutes after adding the product and try again, or confirm both products appear under your app’s **Products** tab.

---

## Step 1: Create a LinkedIn app

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps) and sign in.
2. Click **Create app**.
3. Fill in:
   - **App name**: e.g. "LinkedIn Post Automation"
   - **LinkedIn Page**: create or pick a company page (required; can be your own).
   - **Privacy policy URL**: any valid URL (e.g. your site or `https://example.com`).
   - **App logo**: optional.
4. Create the app.

---

## Step 2: Add redirect URL and products

1. In your app, open the **Auth** tab.
2. Under **OAuth 2.0 settings**, add **Authorized redirect URLs**:
   - `http://localhost:8080/callback`
3. Open the **Products** tab and add **both** of these (click “Add product” for each):
   - **Sign In with LinkedIn** (or “Sign In with LinkedIn using OpenID Connect”) – needed so we can get your person URN from the token. Without it you get “Scope openid is not authorized”.
   - **Share on LinkedIn** – needed for posting (`w_member_social`).
4. Wait for approval if required (both are usually instant for development).

---

## Step 3: Get Client ID and Client Secret

1. In the app, open the **Auth** tab.
2. Copy **Client ID** and **Client Secret**.
3. Add them to your **`.env`**:

```env
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
```

---

## Step 4: Get refresh token (one-time)

1. From the project root, run:

```bash
python scripts/linkedin_oauth.py
```

2. A browser window opens for LinkedIn login. Sign in and approve the app.
3. The script prints a line like:

```
LINKEDIN_REFRESH_TOKEN=...
```

4. Add that line to your **`.env`** (or append the value to an existing `LINKEDIN_REFRESH_TOKEN=` line).

---

## Step 5: Test the flow

1. Run the pipeline to get a new draft email:
   ```bash
   python scripts/run_pipeline.py
   ```
2. Reply to the email with **APPROVE-&lt;draft_id&gt;**.
3. Run the approval checker:
   ```bash
   python scripts/run_approval_check.py
   ```
4. You should see: `Approved draft ... → posted to LinkedIn: urn:li:share:...` and the post on your LinkedIn profile.

---

## Troubleshooting

- **"Scope openid is not authorized for your application"**  
  The app does not have **Sign In with LinkedIn** yet. In [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps) → your app → **Products** tab → **Add product** → add **Sign In with LinkedIn**. Then in `.env` set `LINKEDIN_SCOPE_OPENID=1` and run `python scripts/linkedin_oauth.py` again. The success page will show both `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_PERSON_URN`; add both to `.env`.

- **"Could not get person id"**  
  You need `LINKEDIN_PERSON_URN` in `.env`. Either add **Sign In with LinkedIn** (see above) and re-run OAuth with `LINKEDIN_SCOPE_OPENID=1` so the script can fill it from the token, or set it manually: `LINKEDIN_PERSON_URN=urn:li:person:YOUR_NUMERIC_ID` (you can find your numeric ID from browser dev tools on linkedin.com or from another tool that has profile access).

- **"LINKEDIN_REFRESH_TOKEN is not set"**  
  Run `python scripts/linkedin_oauth.py` and add the printed token line(s) to `.env`.

- **"Not enough permissions" or 403**  
  Ensure the app has **Share on LinkedIn** and that you re-authorized after adding it (run `linkedin_oauth.py` again).

- **Redirect URI mismatch**  
  The redirect URL in the app must be exactly `http://localhost:8080/callback` (or set `LINKEDIN_REDIRECT_URI` in `.env` to match what you added in the app).

- **Token expired**  
  Access tokens last ~60 days. Run `linkedin_oauth.py` again to get a new one and update `.env`.
