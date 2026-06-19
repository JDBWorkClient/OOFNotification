# Engineer OOF Notification Agent - Final Setup

## ✅ What's Ready

### Files Created:
1. **`oof_notifier.py`** - Python agent that:
   - Checks **TOMORROW'S** leave status
   - Runs once daily at **12:00 PM UTC**
   - Sends Teams notifications in advance
   - Tracks changes in state file
   - Logs all activity

2. **`.github/workflows/oof-notification.yml`** - GitHub Actions workflow:
   - Scheduled for **12:00 PM UTC daily** (Cron: `0 12 * * *`)
   - Installs Python + dependencies
   - Sends notifications to Teams
   - Saves logs as artifacts

3. **`DEPLOYMENT_GUIDE.md`** - Complete setup instructions

---

## 🚀 Deployment Steps

### Step 1: Push to GitHub

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Engineer OOF Notification Agent - Daily advance notifications"

# Add remote and push
git remote add origin https://github.com/YOUR_ORG/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Configure GitHub Secrets

1. Go to your repo on GitHub.com
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these THREE secrets:

| Secret | Value | Example |
|--------|-------|---------|
| `TEAMS_WEBHOOK_URL` | Your Teams incoming webhook URL | `https://outlook.webhook.office.com/webhookb2/YOUR_ID/IncomingWebhook/YOUR_KEY` |
| `SHAREPOINT_SITE` | SharePoint site URL | `https://microsoft.sharepoint.com/teams/WindowsAzureBuildout` |
| `ROSTER_FILE` | Excel roster filename | `Roster-2026` or `Roster-2026.xlsx` |

### Step 3: Test Workflow

1. Go to **Actions** tab in GitHub
2. Select **Engineer OOF Notification Check**
3. Click **Run workflow** → **Run workflow**
4. Wait ~30 seconds, refresh the page
5. Click the workflow run to see logs

### Step 4: Verify

Expected output in logs:
```
[2026-06-18 12:00:00] [INFO] Engineer OOF Notification Agent Started
[2026-06-18 12:00:01] [INFO] Fetching roster from SharePoint...
[2026-06-18 12:00:02] [INFO] Status change: Chandan: UNKNOWN → OUT_OF_OFFICE
[2026-06-18 12:00:03] [INFO] ✓ Teams notification sent for Chandan
[2026-06-18 12:00:04] [INFO] Engineer OOF Notification Agent Stopped
```

---

## 📅 Schedule Details

**Timing:**
- ✅ Runs **once per day** at **12:00 PM UTC**
- ✅ Checks **TOMORROW'S** roster
- ✅ Sends notifications **today** (advance warning)

**Time Zone Conversion:**
| Your Timezone | Run Time |
|---------------|----------|
| PST/PDT (Pacific) | 5:00 AM |
| MST/MDT (Mountain) | 6:00 AM |
| CST/CDT (Central) | 7:00 AM |
| EST/EDT (Eastern) | 8:00 AM |
| UTC | 12:00 PM |

**To Change Time:**
Edit `.github/workflows/oof-notification.yml` line 5:
```yaml
- cron: '0 12 * * *'  # Change '12' to your preferred UTC hour
```

---

## 📊 How It Works

```
Daily at 12:00 PM UTC
    ↓
GitHub Actions triggered
    ↓
Checkout code + Setup Python
    ↓
Run: python oof_notifier.py
    ↓
├─ Load previous state (oof-state.json)
├─ Fetch tomorrow's roster from SharePoint
├─ Compare with previous state
├─ Detect who's on leave TOMORROW
├─ Send Teams notification TODAY
└─ Save new state
    ↓
Logs saved as artifact (30 days)
    ↓
Notification in Engineer OOF Bot chat
```

---

## 🔔 Example Notification

When Chandan is on leave tomorrow, you get this notification TODAY at 12:00 PM:

```
🔴 Chandan is now OUT OF OFFICE

---

Engineer: Chandan
Track: RTEG
Status: OUT OF OFFICE
Email: chandan@microsoft.com
Notified: 2026-06-18 12:00:00 UTC
```

---

## ✅ Verification Checklist

Before going live:

- [ ] Code pushed to GitHub
- [ ] 3 secrets added in Settings → Secrets
- [ ] Workflow runs successfully (test manually)
- [ ] Teams notification appears in Engineer OOF Bot chat
- [ ] Logs visible in workflow artifacts
- [ ] Schedule time is correct for your timezone

---

## 📝 Monitoring

### View Recent Runs
**Repo → Actions → Engineer OOF Notification Check**

### Download Logs
1. Click workflow run
2. Click **Artifacts** → **oof-logs-***.zip
3. Extract and check `logs/oof-notifications.log`

### Manual Test
**Actions → Engineer OOF Notification Check → Run workflow**

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflow not running | Check cron syntax at crontab.guru; verify Actions enabled |
| Notifications not sent | Verify TEAMS_WEBHOOK_URL secret is set correctly |
| Excel file not found | Check ROSTER_FILE name matches SharePoint exactly |
| Wrong timezone | Edit cron expression in workflow file |
| State not saving | Check logs for permission errors |

---

## 📞 Next Steps

1. **Push code** to GitHub
2. **Add secrets** in repository settings
3. **Test manually** by running workflow
4. **Verify notification** appears in Teams
5. **Done!** It will run automatically daily at 12:00 PM UTC

---

## 💡 Optional Enhancements

After initial setup, you can add:

- Slack notifications for failures
- Email notifications to team lead
- Webhook for custom integrations
- Multiple team support
- Database for historical tracking

---

**Ready to deploy?** Follow the steps above and your notifications will start tomorrow! 🚀
