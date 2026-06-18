# CI/CD Configuration for Digital Wardrobe

This directory contains GitHub Actions workflows for automated testing, code quality checks, and deployment.

## Workflows

### 1. **backend-ci.yml** - Continuous Integration
**Triggers:** Push/PR to `main` or `develop` branches (backend files only)

**Jobs:**
- **lint-and-test**: Code linting and formatting checks
  - Flake8 for Python linting
  - Black for code formatting
  - Syntax validation
  - Security checks for hardcoded secrets

- **build-check**: Application build verification
  - PostgreSQL database setup
  - Application import test
  - Database model creation test

- **security-scan**: Dependency vulnerability scanning
  - Safety check for known vulnerabilities in dependencies

### 2. **code-quality.yml** - Code Quality Gate
**Triggers:** Pull requests to `main` or `develop`

**Checks:**
- Black formatting
- isort import sorting
- Flake8 linting
- Bandit security linting
- Auto-comments on PR with results

### 3. **deploy.yml** - Continuous Deployment
**Triggers:** 
- Push to `main` branch (backend files)
- Manual trigger via GitHub UI

**Actions:**
- SSH into production server
- Pull latest code
- Install dependencies
- Restart service
- Health check
- Deployment notification

## Setup Instructions

### 1. Enable GitHub Actions
GitHub Actions are automatically enabled for your repository. The workflows will run on next push.

### 2. Configure Secrets (for deployment)
Go to: **Repository Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:
```
SERVER_HOST          # Your server IP or domain (e.g., 192.168.1.100)
SERVER_USERNAME      # SSH username (e.g., ubuntu)
SERVER_SSH_KEY       # Private SSH key for server access
SERVER_PORT          # SSH port (default: 22)
APP_URL              # Your app URL for health check (e.g., https://api.yourapp.com)
```

### 3. Setup Production Environment
Go to: **Repository Settings → Environments → New environment**

Create environment: `production`
- Add protection rules (optional):
  - Required reviewers
  - Wait timer
  - Deployment branches (only main)

### 4. Local Development Setup
```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 5. Run Checks Locally (before pushing)
```bash
cd backend

# Format code
black app

# Sort imports
isort app

# Lint code
flake8 app --max-line-length=127

# Security scan
bandit -r app

# Run tests (when you add them)
pytest
```

## Workflow Status Badges

Add these to your README.md:

```markdown
![Backend CI](https://github.com/YOUR_USERNAME/digital-wardrobe/workflows/Backend%20CI/badge.svg)
![Code Quality](https://github.com/YOUR_USERNAME/digital-wardrobe/workflows/Code%20Quality%20Check/badge.svg)
```

## Modifying Workflows

### To change Python version:
Edit the `python-version` in workflow files (currently set to `3.12`)

### To add tests:
1. Create `backend/tests/` directory
2. Add test files (e.g., `test_api.py`)
3. Tests will run automatically in CI

### To change deployment target:
Edit `deploy.yml` script section with your server path and commands

## Troubleshooting

### Workflow fails on first run?
- Check that all dependencies in `requirements.txt` are correct
- Ensure `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM` are properly handled

### Deployment fails?
- Verify all secrets are configured correctly
- Check server SSH access manually
- Review deployment logs in GitHub Actions tab

### Code quality fails?
- Run formatting locally: `black app && isort app`
- Fix linting issues: `flake8 app`

## Next Steps

1. **Add Tests**: Create unit and integration tests in `backend/tests/`
2. **Add Health Endpoint**: Create `/health` endpoint for deployment verification
3. **Setup Monitoring**: Add error tracking (Sentry, etc.)
4. **Database Migrations**: Integrate Alembic migrations in deployment
