# Engineer OOF Notification Agent - Deployment Guide

## GitHub Actions Setup

### Step 1: Push to GitHub

1. Initialize git in your repository:
```bash
git init
git add .
git commit -m "Add Engineer OOF Notification Agent"
git remote add origin https://github.com/YOUR_ORG/YOUR_REPO.git
git push -u origin main
```

### Step 2: Configure Secrets

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `TEAMS_WEBHOOK_URL` | Your Teams Webhook URL | `https://outlook.webhook.office.com/webhookb2/...` |
| `SHAREPOINT_SITE` | SharePoint site URL | `https://microsoft.sharepoint.com/teams/WindowsAzureBuildout` |
| `ROSTER_FILE` | Excel file name | `Roster-2026.xlsx` |

### Step 3: Verify Workflow

1. Go to **Actions** tab in GitHub
2. Click on **Engineer OOF Notification Check**
3. Click **Run workflow** to test

### Step 4: View Logs

- Logs appear in the workflow run details
- Artifacts are saved for 30 days
- Check **Artifacts** section for detailed logs

---

## How It Works

```
GitHub Actions Scheduler (every 5 minutes)
    ↓
Checkout code + Install Python deps
    ↓
Run oof_notifier.py
    ↓
Fetch SharePoint roster
    ↓
Check for status changes
    ↓
Send Teams notifications via webhook
    ↓
Save logs as artifact
```

---

## Schedule Options

Edit `.github/workflows/oof-notification.yml` to change frequency:

| Frequency | Cron |
|-----------|------|
| Every 5 minutes | `*/5 * * * *` |
| Every 15 minutes | `*/15 * * * *` |
| Every hour | `0 * * * *` |
| Daily at 8 AM | `0 8 * * *` |
| Business hours only | `0 8-18 * * 1-5` |

---

## Environment Variables

Configure in GitHub Secrets or `.github/workflows/oof-notification.yml`:

- `TEAMS_WEBHOOK_URL` - Teams incoming webhook
- `SHAREPOINT_SITE` - SharePoint site URL
- `ROSTER_FILE` - Excel roster file name
- `CHECK_INTERVAL` - Check interval in seconds (default: 300)

---

## Troubleshooting

### Workflow not running?
- Check Actions are enabled in Settings
- Verify cron syntax at crontab.guru
- Check workflow file is in `.github/workflows/` folder

### Notifications not sending?
- Verify `TEAMS_WEBHOOK_URL` secret is set
- Check workflow logs for errors
- Run workflow manually from Actions tab

### Excel file not found?
- Verify `ROSTER_FILE` secret matches actual filename
- File must be in SharePoint "Shift Rosters" folder
- Need openpyxl installed (included in workflow)

---

## Monitoring & Alerts

### View Recent Runs
```
GitHub Repo → Actions → Engineer OOF Notification Check
```

### Download Logs
1. Go to workflow run details
2. Click **Artifacts** section
3. Download `oof-logs-*` zip file

### Add Slack Notifications (Optional)
Modify workflow to also notify Slack on failures:

```yaml
- name: Notify Slack on Failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
    text: 'OOF Notification Agent failed!'
```

---

## Cost

✅ **Free on GitHub** - Public/private repos get 2000 free Actions minutes/month

---

## Support

For issues, check:
- Workflow run logs in Actions tab
- Artifact logs folder
- GitHub Actions documentation: https://docs.github.com/actions
