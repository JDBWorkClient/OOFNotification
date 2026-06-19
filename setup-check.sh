#!/bin/bash
# Engineer OOF Notification Agent - Quick Deployment Script

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Engineer OOF Notification Agent - Setup Checklist       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git not initialized"
    echo "Run: git init"
    exit 1
else
    echo "✅ Git repository initialized"
fi

# Check if files exist
echo ""
echo "Checking required files..."

files=("oof_notifier.py" ".github/workflows/oof-notification.yml" "DEPLOYMENT_GUIDE.md" "SETUP_READY.md")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
    fi
done

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  NEXT STEPS                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "1️⃣  Push code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Add Engineer OOF Notification Agent'"
echo "   git remote add origin https://github.com/YOUR_ORG/YOUR_REPO.git"
echo "   git push -u origin main"
echo ""

echo "2️⃣  Add GitHub Secrets (Settings → Secrets and variables → Actions):"
echo "   TEAMS_WEBHOOK_URL = <your_webhook_url>"
echo "   SHAREPOINT_SITE = https://microsoft.sharepoint.com/teams/WindowsAzureBuildout"
echo "   ROSTER_FILE = Roster-2026.xlsx"
echo ""

echo "3️⃣  Test the workflow:"
echo "   Actions → Engineer OOF Notification Check → Run workflow"
echo ""

echo "4️⃣  Verify:"
echo "   - Workflow runs successfully"
echo "   - Notification appears in Teams chat"
echo "   - Logs saved as artifacts"
echo ""

echo "✅ All set! Your notification agent is ready to deploy."
echo ""
