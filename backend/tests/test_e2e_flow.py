import pytest
from fastapi.testclient import TestClient
import re
from unittest.mock import patch

# ── 1. Health Endpoint Test ──────────────────────────────────────────
def test_health_endpoint(client: TestClient):
    """
    GIVEN the API is running
    WHEN the health endpoint is queried
    THEN it should return status healthy and database connected
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

# ── 2. Authentication Tests ──────────────────────────────────────────
def test_authentication_constraints(client: TestClient):
    """
    Verify registration constraints, duplicate prevention, credential checks,
    and route protection.
    """
    unique_email = "e2e_auth_user@example.com"
    
    # 2a. Register succeeds with valid data
    reg_resp = client.post("/auth/register", json={
        "name": "E2E User",
        "email": unique_email,
        "password": "ValidSecurePassword123!"
    })
    assert reg_resp.status_code == 201
    assert "access_token" in reg_resp.json()
    
    # 2b. Duplicate email is rejected
    duplicate_resp = client.post("/auth/register", json={
        "name": "E2E Duplicate",
        "email": unique_email,
        "password": "ValidSecurePassword123!"
    })
    assert duplicate_resp.status_code == 400
    assert "already exists" in duplicate_resp.json()["detail"].lower()
    
    # 2c. Login succeeds with correct credentials
    login_resp = client.post("/auth/login", json={
        "email": unique_email,
        "password": "ValidSecurePassword123!"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()
    
    # 2d. Login fails with wrong password
    bad_login_resp = client.post("/auth/login", json={
        "email": unique_email,
        "password": "IncorrectPassword"
    })
    assert bad_login_resp.status_code == 401
    assert "incorrect email or password" in bad_login_resp.json()["detail"].lower()
    
    # 2e. Protected routes reject missing/invalid tokens
    protected_resp = client.get("/loans")
    assert protected_resp.status_code == 401

# ── 3. Loan Constraints & Ownership Tests ────────────────────────────
def test_loan_constraints_and_isolation(client: TestClient):
    """
    Verify creating, reading, validating, and isolating user loans.
    """
    # Register and login two separate users
    user_a_email = "usera@example.com"
    user_b_email = "userb@example.com"
    
    # Register User A
    reg_a = client.post("/auth/register", json={
        "name": "User A",
        "email": user_a_email,
        "password": "Password123!"
    })
    token_a = reg_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # Register User B
    reg_b = client.post("/auth/register", json={
        "name": "User B",
        "email": user_b_email,
        "password": "Password123!"
    })
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # 3a. Create loan for User A
    loan_resp = client.post("/loans", headers=headers_a, json={
        "lender": "ICICI Bank",
        "loan_type": "Personal loan",
        "amount": 100000,
        "emi": 5000,
        "overdue_days": 30,
        "income": 25000
    })
    assert loan_resp.status_code == 201
    loan_id = loan_resp.json()["id"]
    
    # 3b. Read loans for User A (must return User A's loan)
    list_a = client.get("/loans", headers=headers_a)
    assert list_a.status_code == 200
    loans_a = list_a.json()
    assert len(loans_a) == 1
    assert loans_a[0]["id"] == loan_id
    
    # 3c. Reject invalid loan values (e.g. negative amount, zero EMI)
    bad_loan_resp = client.post("/loans", headers=headers_a, json={
        "lender": "Bad Bank",
        "loan_type": "Personal loan",
        "amount": -5000,
        "emi": 0,
        "overdue_days": 10,
        "income": 10000
    })
    assert bad_loan_resp.status_code == 400 # FastAPI/Pydantic or router validation error
    
    # 3d. Ensure User B cannot read User A's loan
    not_found_resp = client.get(f"/loans/{loan_id}", headers=headers_b)
    assert not_found_resp.status_code == 404
    
    # 3e. Ensure User B cannot update User A's loan
    bad_patch = client.patch(f"/loans/{loan_id}", headers=headers_b, json={"amount": 200000})
    assert bad_patch.status_code == 404

# ── 4 & 5. Settlement Calculation & Persistence Tests ────────────────
def test_settlement_calculation_and_persistence(client: TestClient):
    """
    Use deterministic ₹3,50,000 personal loan values to verify
    formula matching and database snapshot persistence.
    """
    # Register and login user
    reg = client.post("/auth/register", json={
        "name": "Settle User",
        "email": "settle_test@example.com",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add loan with specific values:
    # Outstanding amount = ₹3,50,000, EMI = ₹18,000, Overdue = 74 days, Income = ₹30,000
    loan_resp = client.post("/loans", headers=headers, json={
        "lender": "ICICI Bank",
        "loan_type": "Personal loan",
        "amount": 350000,
        "emi": 18000,
        "overdue_days": 74,
        "income": 30000
    })
    assert loan_resp.status_code == 201
    loan_id = loan_resp.json()["id"]
    
    # 4a. Run settlement calculations
    settle_resp = client.post(f"/settlement/{loan_id}", headers=headers)
    assert settle_resp.status_code == 200
    settle_data = settle_resp.json()
    
    # Formula matching validation
    assert settle_data["dti_ratio"] == 60.0
    assert settle_data["stress_score"] == 46.4
    assert settle_data["settlement_percentage"] == 41.3
    assert settle_data["settlement_amount"] == 144550.0
    
    # 4b. Verify missing or invalid loan parameters return 404
    fake_settle_resp = client.post("/settlement/9999", headers=headers)
    assert fake_settle_resp.status_code == 404
    
    # 5. Verify snapshot persistence in isolated database
    snapshots_resp = client.get("/snapshots", headers=headers)
    assert snapshots_resp.status_code == 200
    snapshots = snapshots_resp.json()
    assert len(snapshots) == 1
    assert snapshots[0]["loan_id"] == loan_id
    assert snapshots[0]["settlement_percentage"] == 41.3
    assert snapshots[0]["stress_score"] == 46.4

# ── 6. Letters and PDFs Tests ────────────────────────────────────────
def test_letters_and_pdf_generation(client: TestClient):
    """
    Verify proposal letter text generation containing correct figures,
    and check ReportLab PDF output formats.
    """
    reg = client.post("/auth/register", json={
        "name": "Letter User",
        "email": "letter_test@example.com",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add loan & run settlement (required for snapshots)
    loan_resp = client.post("/loans", headers=headers, json={
        "lender": "ICICI Bank",
        "loan_type": "Personal loan",
        "amount": 350000,
        "emi": 18000,
        "overdue_days": 74,
        "income": 30000
    })
    loan_id = loan_resp.json()["id"]
    client.post(f"/settlement/{loan_id}", headers=headers)
    
    # Mocking Gemini client to ensure fallback behavior is predictable for tests
    with patch("routers.letters.generate_letter_body") as mock_gemini:
        # We simulate the fallback template being returned
        fallback_text = (
            "Subject: One Time Settlement request.\n"
            "I propose an amount of Rs. 144,550 which is 41.3% of the outstanding balance."
        )
        mock_gemini.return_value = (fallback_text, "fallback")
        
        # 6a. Generate proposal letter
        letter_resp = client.post(f"/letters/{loan_id}", headers=headers)
        assert letter_resp.status_code == 201
        letter_data = letter_resp.json()
        assert letter_data["settlement_pct"] == 41.3
        assert "144,550" in letter_data["letter_text"]
        
        # 6b. Verify PDF response
        letter_id = letter_data["id"]
        pdf_resp = client.get(f"/letters/download/{letter_id}", headers=headers)
        assert pdf_resp.status_code == 200
        assert pdf_resp.headers["content-type"] == "application/pdf"
        # Verify content starts with PDF signature bytes
        assert pdf_resp.content.startswith(b"%PDF")

# ── 7. Safe Full E2E Integration Flow Test ───────────────────────────
def test_safe_e2e_integration_flow(client: TestClient):
    """
    Unified E2E verification without external network dependency.
    """
    user_email = "e2e_integration@example.com"
    
    # 7a. Register
    reg = client.post("/auth/register", json={
        "name": "Integration User",
        "email": user_email,
        "password": "SecurePassword123!"
    })
    assert reg.status_code == 201
    
    # 7b. Login
    login = client.post("/auth/login", json={
        "email": user_email,
        "password": "SecurePassword123!"
    })
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 7c. Create Loan
    loan = client.post("/loans", headers=headers, json={
        "lender": "ICICI Bank",
        "loan_type": "Personal loan",
        "amount": 350000,
        "emi": 18000,
        "overdue_days": 74,
        "income": 30000
    })
    assert loan.status_code == 201
    loan_id = loan.json()["id"]
    
    # 7d. Generate & Save Settlement snapshot
    settle = client.post(f"/settlement/{loan_id}", headers=headers)
    assert settle.status_code == 200
    assert settle.json()["settlement_amount"] == 144550.0
    
    # 7e. Verify Saved Snapshot
    snapshots = client.get("/snapshots", headers=headers)
    assert len(snapshots.json()) == 1
    assert snapshots.json()[0]["settlement_percentage"] == 41.3
    
    # 7f. Generate letter (uses natural key fallback when GEMINI_API_KEY is dummy)
    letter = client.post(f"/letters/{loan_id}", headers=headers)
    assert letter.status_code == 201
    assert "144,550" in letter.json()["letter_text"]
    
    # 7g. Download PDF stream
    letter_id = letter.json()["id"]
    pdf = client.get(f"/letters/download/{letter_id}", headers=headers)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF")
