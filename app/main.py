"""
DevSecOps Demo - FastAPI Microservice
======================================
This microservice intentionally contains a SQL Injection vulnerability
in the /user/{username} endpoint to demonstrate SAST detection via Semgrep.

The pipeline will:
  - DETECT this flaw with Semgrep (Stage 1 - SAST)
  - DETECT the vulnerable Pillow dependency with Trivy (Stage 2 - SCA)
  - BREAK THE BUILD before any insecure code reaches production
"""

import os
from fastapi import FastAPI, HTTPException
from database import init_db, get_connection

app = FastAPI(
    title="DevSecOps Demo API",
    description="A microservice with an intentional vulnerability for CI/CD security scanning.",
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    init_db()


# ──────────────────────────────────────────────────────────────
# SECURE endpoint - uses parameterized query (correct approach)
# ──────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "devsecops-demo"}


@app.get("/users")
def list_users():
    """List all users - uses a safe parameterized query."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "username": r[1], "email": r[2], "role": r[3]}
        for r in rows
    ]


# ──────────────────────────────────────────────────────────────
# ⚠️  VULNERABLE endpoint - SQL Injection via string formatting
#     Semgrep rule: python.lang.security.audit.formatted-sql-query
#     This endpoint will BREAK THE BUILD in Stage 1 (SAST)
# ──────────────────────────────────────────────────────────────
@app.get("/user/{username}")
def get_user(username: str):
    """
    INTENTIONALLY VULNERABLE: Fetches a user by username.

    The query below uses f-string formatting instead of parameterized
    queries, making it vulnerable to SQL injection.

    Example exploit:
        GET /user/alice' OR '1'='1
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ⚠️ VULNERABLE LINE — Semgrep will flag this
    query = f"SELECT id, username, email, role FROM users WHERE username = '{username}'"
    cursor.execute(query)

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": row[0], "username": row[1], "email": row[2], "role": row[3]}


# ──────────────────────────────────────────────────────────────
# SECRETS — injected at runtime via HashiCorp Vault (Stage 3)
# Note: no credentials are hardcoded here
# ──────────────────────────────────────────────────────────────
@app.get("/config")
def show_config():
    """Shows which secrets are available (not their values)."""
    db_password_set = bool(os.getenv("DB_PASSWORD"))
    api_key_set = bool(os.getenv("API_KEY"))
    return {
        "DB_PASSWORD_injected": db_password_set,
        "API_KEY_injected": api_key_set,
        "note": "Secrets injected at runtime via HashiCorp Vault — never hardcoded.",
    }
