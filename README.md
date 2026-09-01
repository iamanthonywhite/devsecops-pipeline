A security-focused CI/CD pipeline that automatically scans code for vulnerabilities every time a developer pushes changes.
If the code is insecure, the pipeline blocks the deployment and alerts the developer — preventing vulnerable code from ever
reaching production.

> **Note:** The vulnerabilities in this project are intentional. `app/main.py` contains a deliberate SQL
> injection flaw, and `requirements.txt` pins a Pillow version with a known CVE — both included specifically
> to demonstrate that Semgrep and Trivy catch and block them automatically in Stages 1 and 2.

## Purpose

The core idea is **shifting security left** — instead of finding vulnerabilities after code is deployed, we catch them automatically
the moment a developer pushes code. Think of it like a security checkpoint at an airport.
Every piece of code passes through three gates before it reaches production:

## How It Works

**Gate 1 — Semgrep (SAST)**
*SAST (Static Application Security Testing) analyzes source code without running it, catching flaws early in development.*
Reads your source code line by line looking for dangerous patterns — SQL injection, hardcoded passwords, weak logic.
It flags the vulnerable endpoint in `app/main.py` before the app ever runs.

**Gate 2 — Trivy (SCA)**
*SCA (Software Composition Analysis) scans third-party dependencies and container images for known vulnerabilities, rather than your own code.*
Checks every package and dependency against a database of known CVEs. It catches outdated or vulnerable
libraries in `requirements.txt` and scans the Docker image for OS-level flaws.

**Gate 3 — HashiCorp Vault (Secrets Management)**
*Vault is a secrets management tool that stores and injects credentials at runtime, so nothing sensitive is ever hardcoded or stored in source control.*
Ensures no passwords or API keys are hardcoded in the code. In a production deployment, secrets would be
injected at runtime via a live Vault server — so even if someone stole the source code, they would get
nothing useful. For this project, the Vault integration is scaffolded and documented in the workflow file,
with the injection step simulated (via GitHub Actions secrets) rather than connecting to a live Vault instance.

If any gate catches a critical vulnerability, the build breaks and the developer is notified immediately — before bad
code touches a real server or real users.

Visit the "Actions" tab in this repository to see the preventions live.

## Tech Stack

- Python / FastAPI
- Docker
- GitHub Actions
- Semgrep
- Trivy
- HashiCorp Vault
