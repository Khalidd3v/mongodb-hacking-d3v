# Push to GitHub Instructions

## Repository Setup

1. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Repository name: `mongodb-cve-d3v`
   - Description: `MongoDB CVE-2025-14847 (MongoBleed) Data Export Tool`
   - Set to **Public**
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

2. **Add remote and push:**
   ```bash
   # Add remote (replace YOUR_USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/mongodb-cve-d3v.git
   
   # Push the CVE branch
   git push -u origin CVE-2025-14847-MongoBleed
   
   # Also push main branch
   git checkout main
   git push -u origin main
   ```

## Quick Push Command

If you've already created the repo, run:
```bash
git remote add origin https://github.com/YOUR_USERNAME/mongodb-cve-d3v.git
git push -u origin CVE-2025-14847-MongoBleed
```

## Current Branch Structure

- **main**: Main branch
- **CVE-2025-14847-MongoBleed**: CVE-specific branch with the exploit tool

