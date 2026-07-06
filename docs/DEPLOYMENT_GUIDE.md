# Production Deployment Guide

This guide walks you through the step-by-step procedure to push the **FinWise** codebase to a private GitHub repository and deploy it to production using **Render** (backend) and **Vercel** (frontend).

---

## 1. Create a Private GitHub Repository
1. Log in to your [GitHub account](https://github.com).
2. Click **New** (or go to `https://github.com/new`).
3. Set the repository name to `FinWise` (or a name of your choice).
4. Set visibility to **Private** (⚠️ *Critical to protect configuration settings and logic*).
5. Leave "Add a README", "Add .gitignore", and "Choose a license" **unchecked** (we already have these files on disk).
6. Click **Create repository**.

---

## 2. Initialize Git and Push Safely
Open PowerShell or your command prompt in your local project root (`Fin-Relief-main\Fin-Relief-main`) and run:

```bash
# 1. Add your files to stage
git add .

# 2. Commit your code
git commit -m "Initial commit of FinWise production-ready release"

# 3. Rename branch to main
git branch -M main

# 4. Link your local repo to GitHub
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git

# 5. Push to main branch
git push -u origin main
```

---

## 3. Confirm `.env` is Not Committed
Before proceeding, open your GitHub repository in your web browser and verify:
* **No `.env` or `.env.local` files** exist in your file listing.
* Only `.env.example` should be visible in the `/backend` and `/frontend` folders.
* *Note:* If you ever accidentally commit a `.env` file, refer to the [Secret Rotation Guide](SECRET_ROTATION_GUIDE.md) immediately.

---

## 4. Deploy Backend on Render
1. Create or log in to your account at [Render](https://render.com).
2. On your dashboard, click **New +** and select **Web Service**.
3. Connect your GitHub account and choose the private repository you created in Step 1.
4. Fill in the service configuration:
   * **Name**: `finwise-backend`
   * **Language**: `Python`
   * **Branch**: `main`
   * **Region**: Select your preferred server region (e.g., `Singapore` or `Oregon`)
   * **Root Directory**: `backend` (⚠️ *Required — tells Render where the FastAPI code is*)
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   * **Instance Type**: `Free` (or higher if you require faster wake times)
   * **Health Check Path**: `/health`

---

## 5. Add Backend Environment Variables in Render
1. On the web service configuration page, click the **Environment** tab.
2. Add the following environment variables (do not use quotes around values):

| Key | Value Description | Example / Template |
| :--- | :--- | :--- |
| `DATABASE_URL` | Your pooled Neon connection string | `postgresql://neondb_owner:...@ep-...neon.tech/neondb?sslmode=require` |
| `FINRELIEF_SECRET_KEY` | Hex string for JWT token generation | `[A 64-character random hex string]` |
| `GEMINI_API_KEY` | Your Google AI Studio Gemini API key | `[Your API Key]` |
| `FRONTEND_URL` | Temporary placeholder (we will update this in Pass 2) | `http://localhost:5173` |

3. Click **Save Changes** and wait for Render to build and deploy. Once finished, note down your backend's public URL at the top-left of the Render dashboard (e.g., `https://finwise-backend.onrender.com`).

---

## 6. Deploy Frontend on Vercel
1. Log in to [Vercel](https://vercel.com).
2. Click **Add New** > **Project** and import your private GitHub repository.
3. Configure the project:
   * **Framework Preset**: `Vite` (automatically detected)
   * **Root Directory**: `frontend` (⚠️ *Required — tells Vercel where the React code is*)
4. Expand **Environment Variables** and add:
   * Key: `VITE_API_URL`
   * Value: `[YOUR_LIVE_RENDER_BACKEND_URL_FROM_STEP_5]` (e.g., `https://finwise-backend.onrender.com` — *do not add a trailing slash*)
5. Click **Deploy**. Once completed, Vercel will provide your frontend's public URL (e.g., `https://finwise.vercel.app`).

---

## 7. Wire-Up: Update CORS Allowed Origin in Render
1. Return to your Render dashboard for `finwise-backend`.
2. Go to the **Environment** settings tab.
3. Edit the value of `FRONTEND_URL` and replace the local placeholder with your live Vercel frontend URL (e.g., `https://finwise.vercel.app` — *do not add a trailing slash*).
4. Save the changes. Render will automatically initiate a rolling redeploy to update CORS configurations.

---

## 8. Post-Deployment Verification

### Verify Health Endpoint
Open `https://[YOUR_RENDER_BACKEND_URL]/health` in your browser. Verify the response JSON reads:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Run E2E Production Smoke Test
1. Visit your live Vercel URL (e.g., `https://finwise.vercel.app`).
2. **Register**: Create a new test account.
3. **Demo Account Seed**: Alternatively, click **Try Demo** on the login page. This triggers a POST `/demo/seed` request to populate HDFC, SBI, and KreditBee loans.
4. **Loan CRUD**: Create a new personal loan with ₹3,50,000 outstanding, ₹18,000 EMI, and 74 overdue days.
5. **Settlement**: Navigate to the Settlement calculator page, click **Run Analysis**, and verify the recommendation displays:
   * Recommended Settlement %: **41.3%**
   * Expected Settlement Amount: **₹1,44,550**
6. **Save Snapshot**: Save the calculation and verify it is logged in the Trend Snapshot list.
7. **Letter Generation**: Go to the **Letters** tab, select the loan, and generate a draft. Confirm the text displays the exact amount (₹1,44,550).
8. **PDF Download**: Click **Download PDF** and confirm a formatted PDF streams successfully to your local downloads folder.
