#!/bin/bash
# Script to push MongoDB CVE repository to GitHub

echo "=========================================="
echo "MongoDB CVE-2025-14847 GitHub Push Script"
echo "=========================================="
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "Error: GitHub username is required"
    exit 1
fi

REPO_NAME="mongodb-cve-d3v"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo ""
echo "Repository URL: ${REPO_URL}"
echo ""

# Check if remote already exists
if git remote get-url origin &>/dev/null; then
    echo "Remote 'origin' already exists. Updating..."
    git remote set-url origin ${REPO_URL}
else
    echo "Adding remote 'origin'..."
    git remote add origin ${REPO_URL}
fi

echo ""
echo "Current branch: $(git branch --show-current)"
echo ""

# Push CVE branch
echo "Pushing CVE-2025-14847-MongoBleed branch..."
git push -u origin CVE-2025-14847-MongoBleed

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Successfully pushed CVE-2025-14847-MongoBleed branch!"
    echo ""
    echo "Repository URL: ${REPO_URL}"
    echo "Branch: CVE-2025-14847-MongoBleed"
    echo ""
    echo "Note: Make sure you've created the repository on GitHub first:"
    echo "https://github.com/new"
    echo "Repository name: ${REPO_NAME}"
else
    echo ""
    echo "Error: Failed to push. Make sure:"
    echo "1. The repository exists on GitHub: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    echo "2. You have push access"
    echo "3. You're authenticated with GitHub"
fi

