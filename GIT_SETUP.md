# Git Setup and Deployment Commands

Complete guide to push your Customer Decay Analyzer project to GitHub.

## Prerequisites

- Git installed on your system
- GitHub account
- Repository created at: https://github.com/prakharrrshukla/Customer_decay

## Step-by-Step Instructions

### 1. Initialize Git Repository (if not already done)

```bash
cd customer-decay-backend

# Initialize git
git init

# Verify git initialization
git status
```

### 2. Configure Git (First Time Only)

```bash
# Set your name
git config --global user.name "Your Name"

# Set your email
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

### 3. Add Files to Git

```bash
# Check current status
git status

# Add all files (respects .gitignore)
git add .

# Or add specific files
git add README.md
git add models/
git add routes/
git add scripts/
git add tests/
git add utils/
git add app.py
git add requirements.txt
git add .gitignore
git add LICENSE
git add CONTRIBUTING.md
git add setup.sh

# Verify files staged
git status
```

### 4. Create Initial Commit

```bash
# Commit with descriptive message
git commit -m "Initial commit: Customer Decay Analyzer - Hackathon submission

- Complete backend API with Flask
- Gemini AI integration for behavioral analysis
- Qdrant vector database for similarity search
- Dual-AI approach (60/40 weighted scoring)
- Comprehensive test suite with 6 test cases
- Full documentation (README, API docs, testing guide)
- Sample data generation scripts
- Health monitoring endpoints
- Built for lablab.ai Hackathon

Team: Sameer Pahwa, Prakhar Shukla, Heer Shah, Kasak Kumari"

# Verify commit
git log --oneline
```

### 5. Connect to GitHub Remote

```bash
# Add remote repository
git remote add origin https://github.com/prakharrrshukla/Customer_decay.git

# Verify remote
git remote -v
```

### 6. Push to GitHub

```bash
# Push to main branch
git push -u origin main

# If using master branch instead:
# git push -u origin master

# If you need to rename branch:
# git branch -M main
# git push -u origin main
```

### 7. Verify on GitHub

Visit https://github.com/prakharrrshukla/Customer_decay and verify:
- ✅ All files uploaded
- ✅ README.md displays correctly
- ✅ .gitignore working (no .env or data files)
- ✅ LICENSE visible
- ✅ Repository description set

## Common Issues and Solutions

### Issue: Push rejected (non-fast-forward)

**Problem**: Remote has commits you don't have locally

**Solution**:
```bash
# Fetch and merge remote changes
git pull origin main --rebase

# Or force push (CAUTION: overwrites remote)
git push -u origin main --force
```

### Issue: Authentication failed

**Problem**: Need GitHub credentials

**Solution Option 1 - Personal Access Token**:
```bash
# 1. Generate token at: https://github.com/settings/tokens
# 2. Use token as password when prompted
# 3. Save credentials (optional)
git config --global credential.helper store
```

**Solution Option 2 - SSH Key**:
```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# 2. Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. Copy public key
cat ~/.ssh/id_ed25519.pub
# Add to GitHub: https://github.com/settings/keys

# 4. Change remote to SSH
git remote set-url origin git@github.com:prakharrrshukla/Customer_decay.git
```

### Issue: Large files rejected

**Problem**: Files > 100MB not allowed

**Solution**:
```bash
# Check large files
find . -size +50M -not -path "./venv/*"

# Remove from git
git rm --cached path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore

# Commit and push
git commit -m "Remove large files"
git push
```

### Issue: .env file accidentally committed

**Problem**: Sensitive data in repository

**Solution**:
```bash
# Remove from git but keep local file
git rm --cached .env

# Ensure it's in .gitignore
echo ".env" >> .gitignore

# Commit removal
git commit -m "Remove .env from repository"
git push

# IMPORTANT: Rotate all API keys immediately!
```

## Making Updates After Initial Push

### Standard Update Workflow

```bash
# 1. Make your changes
# Edit files as needed

# 2. Check what changed
git status
git diff

# 3. Stage changes
git add .

# 4. Commit with message
git commit -m "feat: add email notification system"

# 5. Push to GitHub
git push
```

### Commit Message Conventions

Use conventional commits format:

```bash
# New feature
git commit -m "feat(models): add sentiment analysis to analyzer"

# Bug fix
git commit -m "fix(api): handle empty behavior data gracefully"

# Documentation
git commit -m "docs(readme): add installation troubleshooting"

# Code style/formatting
git commit -m "style: format code with black"

# Refactoring
git commit -m "refactor(routes): simplify error handling logic"

# Tests
git commit -m "test: add unit tests for vector store"

# Build/dependencies
git commit -m "chore(deps): upgrade qdrant-client to 1.8.0"
```

## Creating a Release

### Tag a Release Version

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release v1.0.0 - Hackathon submission

Features:
- Complete backend API
- Gemini + Qdrant integration
- 85% prediction accuracy
- Full documentation"

# Push tag to GitHub
git push origin v1.0.0

# Or push all tags
git push --tags
```

### Create GitHub Release

1. Go to: https://github.com/prakharrrshukla/Customer_decay/releases
2. Click "Draft a new release"
3. Select tag: v1.0.0
4. Title: "v1.0.0 - Hackathon Submission"
5. Description: Copy from BUILD_COMPLETE.md
6. Attach files (optional): screenshots, demo video
7. Click "Publish release"

## Branch Management

### Create Feature Branch

```bash
# Create and switch to new branch
git checkout -b feature/email-notifications

# Make changes and commit
git add .
git commit -m "feat: add email notification system"

# Push branch to GitHub
git push -u origin feature/email-notifications
```

### Create Pull Request

1. Go to GitHub repository
2. Click "Pull requests" → "New pull request"
3. Select: base: main ← compare: feature/email-notifications
4. Fill in PR template
5. Click "Create pull request"
6. Wait for review and merge

### Merge Branch

```bash
# Switch to main
git checkout main

# Merge feature branch
git merge feature/email-notifications

# Push merged changes
git push

# Delete feature branch (optional)
git branch -d feature/email-notifications
git push origin --delete feature/email-notifications
```

## Collaboration Workflow

### Pull Latest Changes

```bash
# Before starting work
git pull origin main
```

### Handle Merge Conflicts

```bash
# If conflict occurs during pull/merge
# 1. Open conflicted files
# 2. Look for conflict markers:
#    <<<<<<< HEAD
#    Your changes
#    =======
#    Their changes
#    >>>>>>> branch-name

# 3. Resolve conflicts manually
# 4. Remove conflict markers
# 5. Stage resolved files
git add resolved-file.py

# 6. Complete merge
git commit -m "Merge: resolve conflicts"

# 7. Push
git push
```

## Repository Maintenance

### Update .gitignore

```bash
# After updating .gitignore
git rm -r --cached .
git add .
git commit -m "chore: update .gitignore"
git push
```

### Clean Up Repository

```bash
# Remove untracked files (dry run)
git clean -n

# Remove untracked files (for real)
git clean -f

# Remove ignored files too
git clean -fx
```

### View History

```bash
# View commit history
git log --oneline --graph --all

# View file history
git log --follow filename

# View changes in commit
git show commit-hash
```

## GitHub Repository Settings

### Set Repository Description

1. Go to: https://github.com/prakharrrshukla/Customer_decay
2. Click "⚙️ Settings"
3. Description: "Predict customer churn 90 days in advance using Gemini AI + Qdrant"
4. Website: Add demo URL
5. Topics: Add tags (ai, machine-learning, churn-prediction, gemini, qdrant, hackathon)

### Configure Branch Protection

1. Go to Settings → Branches
2. Add rule for "main"
3. Enable:
   - Require pull request reviews
   - Require status checks to pass
   - Include administrators

### Add README Badges

Already included in README.md:
- ![License](https://img.shields.io/badge/license-MIT-blue.svg)
- ![Python](https://img.shields.io/badge/python-3.9+-green.svg)
- ![Gemini](https://img.shields.io/badge/Gemini-API-orange.svg)
- ![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-red.svg)

## Quick Reference

```bash
# Status
git status

# Add files
git add .

# Commit
git commit -m "message"

# Push
git push

# Pull
git pull

# Create branch
git checkout -b branch-name

# Switch branch
git checkout branch-name

# Merge
git merge branch-name

# View log
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

## GitHub CLI (Optional)

Install: https://cli.github.com/

```bash
# Authenticate
gh auth login

# Create repo
gh repo create Customer_decay --public

# View repo
gh repo view

# Create PR
gh pr create --title "Add feature" --body "Description"

# View issues
gh issue list
```

## Success Checklist

After pushing to GitHub, verify:

- [ ] All files uploaded (check file count)
- [ ] README displays correctly with badges
- [ ] .gitignore working (no sensitive files)
- [ ] LICENSE file present
- [ ] Repository description set
- [ ] Topics/tags added
- [ ] Repository set to public
- [ ] Team members added as collaborators
- [ ] Branch protection enabled (optional)
- [ ] Issues enabled
- [ ] Discussions enabled (optional)

## Next Steps

1. **Add collaborators**: Settings → Collaborators → Add team members
2. **Create issues**: For bugs and feature requests
3. **Set up CI/CD**: GitHub Actions for automated testing
4. **Enable GitHub Pages**: For documentation website
5. **Star repository**: Help with visibility
6. **Share link**: Post on social media, hackathon platform

---

**Repository URL**: https://github.com/prakharrrshukla/Customer_decay

**Need help?** See [CONTRIBUTING.md](CONTRIBUTING.md) or contact team.churnbusters@example.com
