# Implementation Plan — GitHub Readiness & Test Suite

This plan details the steps required to make the FinRelief AI project fully prepared for GitHub, automated testing, and secure cloud deployment.

---

## 1. Existing Tests Found

During inspection, we located the following tests in [backend/tests/](file:///C:/Users/pavan/Downloads/Fin-Relief-main/Fin-Relief-main/backend/tests):
* [test_calculations.py](file:///C:/Users/pavan/Downloads/Fin-Relief-main/Fin-Relief-main/backend/tests/test_calculations.py): Tests individual logic units for DTI, stress index, and settlement percentage calculations.
* [test_gemini_fallback.py](file:///C:/Users/pavan/Downloads/Fin-Relief-main/Fin-Relief-main/backend/tests/test_gemini_fallback.py): Tests the Gemini client's rate-limiting, authentication failures, and safety fallback overrides.
* [test_settlement_api.py](file:///C:/Users/pavan/Downloads/Fin-Relief-main/Fin-Relief-main/backend/tests/test_settlement_api.py): Tests the FastAPI router endpoints for calculating, retrieving, and saving snapshots.

All existing tests utilize an isolated SQLite database setup defined in `conftest.py`, meaning they do not write to or require a live Neon PostgreSQL database.

---

## 2. Missing Test Coverage

To ensure a robust, professional CI pipeline and secure production behaviors, we need to add focused test cases for:
1. **Health Endpoint**: Validate database check handles connected/disconnected states correctly.
2. **Authentication Constraints**: Re-registration of duplicate emails must reject with a 400; logins with incorrect passwords must fail with a 401; protected routes must reject requests missing token headers.
3. **Loan Constraints**: Validate invalid field shapes (negative amounts, null fields) are blocked; confirm isolated loan ownership checks (users cannot access another user's loan).
4. **Rupee-Level E2E Flow**: Implement a dedicated test case that runs a complete workflow (Register -> Login -> Create Loan [₹3,50,000 personal loan, ₹18,000 EMI, 74 days overdue, ₹30,000 income] -> Generate Settlement -> Verify Saved Snapshot [₹144,550 settlement amount] -> Generate Letter -> Download PDF) under full database/service isolation.

---

## 3. Proposed Changes

We will add/modify the following files:

| File path | Purpose | Category |
| :--- | :--- | :--- |
| `docs/IMPLEMENTATION_PLAN.md` | Audit phase plan (this file). | Documentation |
| `backend/tests/test_e2e_flow.py` | Full E2E logic and consistency validation. | Test Change |
| `.gitignore` | Strengthen rules to ignore all `.env` files, builds, and SQLite databases. | Config Change |
| `backend/.env.example` | Safe placeholder environment keys for the backend. | Config Change |
| `frontend/.env.example` | Safe API URL target template for the frontend client. | Config Change |
| `.github/workflows/ci.yml` | GitHub Actions workflow for linting, building, and running isolated tests. | Config Change |
| `docs/DEPLOYMENT_GUIDE.md` | Numbered checklists for Render and Vercel wire-up. | Documentation |
| `docs/SECRET_ROTATION_GUIDE.md`| Rotation procedures for Neon, Gemini, and JWT tokens. | Documentation |
| `DEPLOYMENT_READINESS_REPORT.md`| Execution logs and readiness status. | Documentation |

---

## 4. Why Each Change is Needed

* **E2E Flow Tests**: Essential to guarantee that any future change to front-end forms or back-end math keeps the settlement logic, database model, proposal letter, and PDF stream unified down to the rupee.
* **.env.example files**: Let contributors build the project from scratch without leaking keys, and guide settings layout on hosting providers.
* **CI/CD Configuration**: Ensures code compilation and unit tests block commits before they reach main, preventing production breakage.
* **Guides & Reports**: Empower the repository owner to configure hosting from scratch, rotate compromised credentials safely, and verify deployment status without exposing private credentials in chat transcripts.

---

## 5. Deployment Risks Found

1. **Neon PostgreSQL Connection Times**: Free-tier databases on Neon automatically sleep. FastAPI's connection pool could raise connection timeout errors on startup. A keepalive or `pool_pre_ping=True` setting is recommended (FastAPI already has `pool_pre_ping=True` in `database.py`, which helps mitigate this).
2. **Vercel/Render CORS Trailing Slashes**: In `main.py`, Render matches `FRONTEND_URL` exactly. If the user registers `https://example.vercel.app/` (with a slash) but Render expects it without a slash, Axios calls in the browser will trigger CORS preflight exceptions.
3. **Lockfile Synchronization**: There is no `package-lock.json` committed to the repository (only `package.json`). This increases the risk that dependencies installed during the build on Vercel could introduce breaking sub-package updates.
