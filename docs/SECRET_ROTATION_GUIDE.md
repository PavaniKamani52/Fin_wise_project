# Secret Rotation Guide

If you suspect your production secrets have been exposed or if you are transitioning from development placeholders to production credentials, follow this step-by-step secret rotation guide.

---

## 1. Neon Database Secret Rotation
To revoke database access and secure your database:
1. Log in to the [Neon Console](https://console.neon.tech).
2. Go to your project page and select your active branch/database.
3. Under the **Roles** tab or connection details, click **Reset Password** for the owner user. This immediately invalidates the old database URL and stops active sessions.
4. Copy the newly generated **connection URL**. Be sure to select the **pooled** connection detail if using serverless connection limits.
5. Update your secrets:
   * **Locally**: Open your local `backend/.env` file and replace the `DATABASE_URL` value.
   * **In Production**: Go to the **Render Dashboard**, select your backend service, click the **Environment** tab, update the value of `DATABASE_URL`, and save.
   * ⚠️ *Warning: Do not commit the updated database connection URL to your Git repository.*

---

## 2. Google Gemini API Key Rotation
If your Gemini API key has been exposed in public logs:
1. Log in to [Google AI Studio](https://aistudio.google.com).
2. Navigate to your API keys list.
3. Find the compromised key and click **Delete / Revoke**. This stops the key from working immediately.
4. Click **Create API Key** to generate a new credentials string.
5. Update your secrets:
   * **Locally**: Open your local `backend/.env` file and replace the `GEMINI_API_KEY` value.
   * **In Production**: Update the value of `GEMINI_API_KEY` in the **Render** Environment dashboard and save.
   * *Note: The backend automatically handles empty/failed keys by falling back gracefully to professional offline templates.*

---

## 3. JWT signing key (`FINRELIEF_SECRET_KEY`)
To invalidate active sessions and secure JWT signatures:
1. Generate a new secure, random hex string in your local terminal:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Copy the resulting 64-character string.
3. Update your secrets:
   * **Locally**: Update the `FINRELIEF_SECRET_KEY` variable in `backend/.env`.
   * **In Production**: Update the value of `FINRELIEF_SECRET_KEY` in the **Render** Environment dashboard and save.
   * ⚠️ *Warning: Rotating this secret immediately invalidates all active user sessions, requiring current users to log back in.*

---

## 4. Final Security Check
Run these checks before committing changes:
* **Verify .gitignore**: Run `git status` in the root folder and confirm that your local `.env` files are not listed as untracked or staged.
* **Scan History**: If you have already committed files, run a history scan for secret fragments.
* **Verify Templates**: Ensure that only `backend/.env.example` and `frontend/.env.example` (containing safe placeholder values) are tracked by Git.
