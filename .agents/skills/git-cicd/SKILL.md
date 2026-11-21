---
name: git-cicd
description: >-
  Git workflow, version control, pre-commit quality enforcement, and GitHub Actions CI/CD automation skill.
  Use when creating branches, staging and committing changes, configuring git hooks, managing GitHub secrets
  for Netlify deployment, or configuring automated CI/CD test-and-deploy pipelines.
---

# Git Workflow & CI/CD Skill

This skill governs version control, pre-commit quality enforcement, and continuous integration/continuous deployment (CI/CD) pipelines for the project.

## Repository Architecture

```text
├── .agents/skills/           # Antigravity agent skills
│   ├── career-hub-testing/   # Automated testing & compliance skill
│   ├── netlify-deploy/       # Netlify packaging & deployment skill
│   └── git-cicd/             # Git & CI/CD workflow skill
├── .github/workflows/        # Automated GitHub Actions
│   └── ci-cd-netlify.yml     # Continuous test & deploy pipeline
├── .githooks/                # Git client-side hooks
│   └── pre-commit            # Automated test gate before any commit
├── tests/                    # Python unit test suite
│   ├── run_all_tests.py      # Master test runner
│   ├── test_site_integrity.py
│   └── test_compliance_and_dates.py
├── scripts/                  # Automated deployment scripts
│   ├── deploy_netlify.py
│   └── deploy_netlify.sh
├── netlify.toml              # Production Netlify configuration
└── index.html                # Root website entrypoint
```

## Local Git Setup & Pre-Commit Hook

To ensure that no broken navigation links, missing assets, or accidental date regressions are ever committed:

1. **Activate the local pre-commit hook:**
   ```bash
   git config core.hooksPath .githooks
   chmod +x .githooks/pre-commit
   ```

2. **How it works:**
   Every time you execute `git commit`, git triggers `.githooks/pre-commit`, which runs `python3 tests/run_all_tests.py`. If any test fails, the commit is aborted immediately with detailed failure diagnostics.

## GitHub Actions CI/CD Workflow (`.github/workflows/ci-cd-netlify.yml`)

The repository includes a 2-stage automated pipeline:

1. **Job 1: Test & Lint**
   - Triggered on every `push` and `pull_request` to `main` or `master`.
   - Spins up Python 3.11 environment on `ubuntu-latest`.
   - Runs `python3 tests/run_all_tests.py`.
   - Halts pipeline if integrity or GDPR tests fail.

2. **Job 2: Deploy to Netlify**
   - Depends on Job 1 passing.
   - Deploys automatically to `https://sailakshminl.netlify.app`.
   - Produces preview deployments on Pull Requests and live production deployments on pushes to `main`.

### Configuring GitHub Repository Secrets

To enable automated zero-touch deployment on GitHub:
1. Go to your GitHub repository: **Settings** → **Secrets and variables** → **Actions**.
2. Add the following repository secrets:
   * **`NETLIFY_AUTH_TOKEN`**: Personal Access Token generated at [https://app.netlify.com/user/applications](https://app.netlify.com/user/applications).
   * **`NETLIFY_SITE_ID`**: `787b918a-9066-43e5-815f-4710abbfd307`

## Standard Commit Workflow

```bash
# 1. Check working directory status
git status

# 2. Stage changes
git add .

# 3. Commit (triggers automated pre-commit test runner)
git commit -m "feat(hub): add women in tech directory, netlify cicd and testing suite"

# 4. Push to remote repository (triggers GitHub Actions CI/CD)
git push origin master
```
