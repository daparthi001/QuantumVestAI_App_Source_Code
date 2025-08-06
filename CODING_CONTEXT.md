# QuantumVestAI – Full Project Context

## 📌 Overview
QuantumVestAI is an AI-driven stock analysis and trading automation platform.  
It runs on AWS EKS with Kubernetes, uses FastAPI for the backend, React for the frontend, and PostgreSQL (RDS) for persistent storage.

### Key Responsibilities for Codex
- Fix database connectivity issues in Kubernetes pods
- Resolve Alembic migration import errors
- Improve WebSocket connections for real-time market data
- Fix UI startup, import paths, and dependency mismatches
- Automate DB initialization and seeding
- Optimize Helm/K8s workflows for startup scripts
- Resolve FastAPI template environment issues
- Debug registration form and WebSocket fixes in UI

---

## 🏗 Infrastructure
- **Kubernetes Namespace:** `dev`
- **Components:**
  - **db-init:** Runs `wait-for-db.sh` and SQL migrations
  - **db-seed:** Seeds initial data (`seed_db.py`)
  - **db-connection-status:** Monitors RDS connectivity
  - **quantumvestai-config:** App ENV (DEBUG, ENVIRONMENT, LOG_LEVEL)
  - **ui-config:** Starts FastAPI UI with uvicorn
  - **ui-scripts:** Fixes imports, installs dependencies, patches UI scripts

- **AWS RDS PostgreSQL:**
  - Monitored using `pg_isready` and `psql`
  - Configured with SSL (TLSv1.2)
  - Scripts validate DB connection and retry on failure

---

## 🗄 Database
- **Schemas:**
  - `model_data`: stock_prices, predictions, model_metrics, sentiment_analysis
  - `user_data`: user_preferences, saved_forecasts
- **Roles:**
  - `quantumvestai`: full access to both schemas
- **Functions:**
  - `update_modified_column()`
  - `get_latest_prediction()`
  - `get_prediction_accuracy()`
- **Seeding:**
  - `seed_db.py` creates users, portfolios, investments
  - Adds necessary indexes and logs successful seeding

---

## 🖥 UI & API Startup
- `ui-config`:
  - Installs `markupsafe`
  - Starts FastAPI with uvicorn
- `ui-scripts`:
  - **fix-imports.sh:** Fixes incorrect Python imports in utils and main.py
  - **install-dependencies.sh:** Installs missing Python & Node packages
  - **startup-wrapper.sh:** Runs all fixes, installs dependencies, starts UI
  - **market-data-fix.js:** Fixes WebSocket by adding `premium=true`
  - **registration-fix.js:** Fixes registration form submission with ALB ingress

---

## 🐛 Known Issues to Fix
1. **Database**: Internal service fails (`Connection Refused`), but RDS is accessible.
2. **Alembic**: PYTHONPATH import errors prevent migrations from running.
3. **WebSockets**: Real-time price updates disconnect intermittently.
4. **FastAPI Templates**: Jinja2 templates not bound properly to `app.state`.
5. **UI Dependencies**: Missing or mismatched Python/Node packages.
6. **Kubernetes Order**: db-init, db-seed, and app startup not synchronized.
7. **Registration Form**: UI registration fails behind AWS ALB ingress.

---

## 🧠 Codex Tasks
- Debug and modify `wait-for-db.sh` to handle internal Kubernetes service resolution.
- Patch `alembic.ini` to load dynamically from environment.
- Enhance `startup-wrapper.sh` to install all required dependencies before FastAPI starts.
- Modify `market-data-fix.js` to auto-reconnect WebSocket.
- Update `main.py` to store templates in `app.state` for Jinja2.
- Validate that `seed_db.py` runs after DB schema creation.
- Recommend Helm pre/post hooks for db-init and db-seed scripts.

---

## ✅ Example Codex Prompts
```python
# Fix Alembic import errors in QuantumVestAI
# Ensure PYTHONPATH is properly configured for migrations
