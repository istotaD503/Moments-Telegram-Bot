# Fly.io Deployment Guide for Moments Bot

**Last Updated**: December 15, 2025

This guide will walk you through deploying your Telegram bot on Fly.io - a simpler, more developer-friendly alternative to AWS and Render.com.

---

## Table of Contents

1. [Why Fly.io?](#why-flyio)
2. [Prerequisites](#prerequisites)
3. [Install Fly.io CLI](#install-flyio-cli)
4. [Prepare Your Application](#prepare-your-application)
5. [Deploy to Fly.io](#deploy-to-flyio)
6. [Database Options](#database-options)
7. [Monitoring & Logs](#monitoring--logs)
8. [Cost Estimates](#cost-estimates)
9. [Troubleshooting](#troubleshooting)

---

## Why Fly.io?

**Comparison:**

| Feature | Fly.io | AWS Lambda | Render.com |
|---------|--------|------------|------------|
| **Setup Complexity** | ⭐ Simple | ⭐⭐⭐⭐⭐ Complex | ⭐⭐ Medium |
| **Deployment** | `fly deploy` | Multi-step process | Git push |
| **Bot Mode** | ✅ Polling (native) | ❌ Webhook only | ✅ Polling |
| **Database** | ✅ SQLite works | ❌ Needs DynamoDB | ✅ SQLite works |
| **Free Tier** | $5/month credit | Pay-as-you-go | Limited hours |
| **Global Edge** | ✅ Yes | ✅ Yes | ❌ No |
| **Docker Support** | ✅ Native | ✅ Complex | ✅ Yes |
| **Learning Curve** | 📈 Low | 📈 High | 📈 Medium |

**TL;DR**: Fly.io is the sweet spot between simplicity and features.

---

## Prerequisites

### What You Need
- ✅ A Telegram bot token (from @BotFather)
- ✅ A GitHub account (optional, for deployment)
- ✅ A credit card (for Fly.io verification - no charges with free tier)
- ✅ Basic command line knowledge
- ✅ Your bot's code (already set up!)

### What You'll Learn
- Installing and using Fly.io CLI
- Deploying Docker containers to Fly.io
- Managing secrets and environment variables
- Setting up persistent storage for SQLite
- Monitoring logs and scaling

---

## Install Fly.io CLI

### Step 1: Install flyctl

**For macOS** (your system):
```bash
# Using Homebrew (recommended)
brew install flyctl

# Verify installation
flyctl version
# Should output: flyctl v0.x.x ...
```

### Step 2: Sign Up and Authenticate

```bash
# Sign up or log in
flyctl auth signup

# Or if you already have an account
flyctl auth login
```

**What happens**:
1. Browser opens to Fly.io signup/login page
2. Create account with email or GitHub
3. Verify email address
4. Add credit card (required, but won't be charged with free tier)
5. CLI is automatically authenticated

**Verify authentication**:
```bash
flyctl auth whoami
# Should show your email
```

---

## Prepare Your Application

### Step 3: Keep Your Existing Code

**Good news**: Your current bot code works perfectly for Fly.io! No need to change from polling to webhooks.

Your current structure:
```
Moments Bot/
├── bot.py              # ✅ Keep as-is (polling mode)
├── handlers/
│   └── commands.py     # ✅ Keep as-is
├── models/
│   └── story.py        # ✅ Keep as-is (SQLite works!)
├── config/
│   └── settings.py     # ✅ Keep as-is
├── utils/
│   └── assets.py       # ✅ Keep as-is
├── assets/
│   └── welcome_message.txt
├── requirements.txt    # ✅ Keep as-is
├── Dockerfile          # ⚠️ Update (see below)
└── .env                # ⚠️ Don't deploy (use secrets)
```

### Step 4: Update Dockerfile for Fly.io

**Replace your `Dockerfile` with this**:

```dockerfile
# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bot.py .
COPY config/ ./config/
COPY handlers/ ./handlers/
COPY models/ ./models/
COPY utils/ ./utils/
COPY assets/ ./assets/

# Create directory for SQLite database (persistent volume will mount here)
RUN mkdir -p /data

# Run the bot
CMD ["python", "bot.py"]
```

**Key differences from AWS version**:
- ✅ Uses standard Python image (not Lambda-specific)
- ✅ Runs `python bot.py` directly (polling mode works!)
- ✅ Creates `/data` directory for persistent SQLite storage
- ✅ No webhook handler needed

### Step 5: Update Database Path for Persistent Storage

**Update `models/story.py`** to use Fly.io's persistent volume:

Find the `__init__` method in your `StoryDatabase` class and update:

```python
import os

class StoryDatabase:
    def __init__(self):
        # Use /data for Fly.io persistent volume, fall back to local for development
        db_dir = os.getenv('DB_DIR', 'data')
        os.makedirs(db_dir, exist_ok=True)
        
        self.db_path = os.path.join(db_dir, 'stories.db')
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_table()
```

**Why this change?**
- Fly.io provides persistent volumes at `/data`
- Local development still uses `data/` directory
- Data survives container restarts

---

## Deploy to Fly.io

### Step 6: Initialize Fly.io App

```bash
# Navigate to your project directory
cd ~/Playground/Moments\ Bot

# Launch the app (interactive setup)
flyctl launch
```

**Answer the prompts**:

```
? Choose an app name (leave blank to generate one): moments-bot
? Choose a region for deployment: [Select closest to you, e.g., iad (Ashburn, Virginia)]
? Would you like to set up a Postgresql database now? No
? Would you like to set up an Upstash Redis database now? No
? Create .dockerignore from 3 .gitignore files? Yes
? Would you like to deploy now? No
```

**What this creates**:
- `fly.toml` - Fly.io configuration file
- `.dockerignore` - Files to exclude from Docker build

### Step 7: Configure fly.toml

**Update the generated `fly.toml`**:

```toml
# fly.toml app configuration file
app = "moments-bot"
primary_region = "iad"

[build]

[env]
  # Set DB_DIR to use persistent volume
  DB_DIR = "/data"

[mounts]
  # Persistent volume for SQLite database
  source = "moments_data"
  destination = "/data"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

**Configuration explained**:
- `app`: Your unique app name
- `primary_region`: Where your app runs (choose closest to users)
- `[mounts]`: Persistent storage for SQLite database
- `[[vm]]`: Resource allocation (256MB is enough for this bot)

### Step 8: Create Persistent Volume

```bash
# Create a 1GB volume for SQLite database
flyctl volumes create moments_data --size 1 --region iad

# Verify volume creation
flyctl volumes list
```

**Expected output**:
```
ID          NAME           SIZE  REGION  ZONE  ENCRYPTED  ATTACHED VM  CREATED AT
vol_xyz123  moments_data   1GB   iad     1a2b  true       -            1 min ago
```

### Step 9: Set Environment Variables (Secrets)

```bash
# Set your bot token (replace with your actual token)
flyctl secrets set BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Verify secrets are set
flyctl secrets list
```

**Important**:
- ❌ **Never** commit `.env` or secrets to Git
- ✅ Use `flyctl secrets` for sensitive data
- ✅ Secrets are encrypted and injected at runtime

### Step 10: Deploy Your Bot

```bash
# Deploy the application
flyctl deploy

# Watch the deployment progress
# This will:
# 1. Build Docker image
# 2. Push to Fly.io registry
# 3. Create VM and mount volume
# 4. Start your bot
```

**Expected output**:
```
==> Building image
==> Pushing image to fly
==> Deploying
 ✓ [1/1] Machine xyz created
 ✓ Machine xyz started

Visit your app at: https://moments-bot.fly.dev/
```

### Step 11: Verify Deployment

```bash
# Check app status
flyctl status

# View live logs
flyctl logs

# Test your bot in Telegram
# Send /start to your bot
```

**What to look for in logs**:
```
🚀 Bot running in POLLING mode (local development)
Using SQLite backend
Connected to database: /data/stories.db
✅ Successfully created table 'stories'
```

---

## Database Options

### Option 1: SQLite with Persistent Volume (Recommended for Small Bots)

**Current setup** - Already configured above!

**Pros**:
- ✅ Simple - no external database needed
- ✅ Free - included in your VM
- ✅ Fast - local file access
- ✅ Your current code works as-is

**Cons**:
- ❌ Single instance only (can't scale horizontally)
- ❌ Backups require manual setup

**Backup SQLite database**:
```bash
# Download database backup
flyctl ssh sftp get /data/stories.db ./stories-backup.db

# Restore database
flyctl ssh sftp shell
put ./stories-backup.db /data/stories.db
```

### Option 2: Fly.io Postgres (For Scaling)

If you expect heavy usage or need multiple instances:

```bash
# Create Postgres cluster
flyctl postgres create --name moments-bot-db --region iad

# Attach to your app
flyctl postgres attach moments-bot-db
```

**Update `requirements.txt`**:
```txt
python-telegram-bot==20.7
python-dotenv==1.0.0
psycopg2-binary==2.9.9
```

**Create `models/postgres_story.py`** (similar to DynamoDB version from AWS guide, but using PostgreSQL).

---

## Monitoring & Logs

### View Logs

```bash
# Stream live logs
flyctl logs

# Filter for errors
flyctl logs | grep ERROR

# Last 100 lines
flyctl logs --limit 100
```

### Access Your VM

```bash
# SSH into your VM
flyctl ssh console

# Check database file
ls -lh /data/
cat /data/stories.db  # View SQLite file

# Exit
exit
```

### Monitoring Dashboard

```bash
# Open Fly.io dashboard
flyctl dashboard
```

Visit: https://fly.io/dashboard/moments-bot

**Dashboard shows**:
- CPU and memory usage
- Request metrics
- VM status
- Volume usage
- Recent deployments

### Scaling

```bash
# Scale up memory (if needed)
flyctl scale memory 512

# Check current resources
flyctl scale show

# Scale down (save money)
flyctl scale memory 256
```

---

## Cost Estimates

### Free Tier (Hobby Plan)

Fly.io provides **$5/month credit** which covers:

| Resource | Free Allowance | Your Bot Usage | Cost |
|----------|----------------|----------------|------|
| **Shared CPU VM** | 3x 256MB VMs | 1x 256MB VM | $0.00 |
| **Persistent Volume** | 3GB total | 1GB | $0.00 |
| **Outbound Transfer** | 100GB/month | <1GB/month | $0.00 |
| **Total** | | | **$0.00/month** |

### If You Exceed Free Tier

For **100+ active users**:

| Resource | Usage | Cost |
|----------|-------|------|
| **VM (256MB)** | 730 hours/month | $1.94 |
| **Volume (1GB)** | 1GB | $0.15 |
| **Bandwidth** | 5GB/month | $0.00 (under limit) |
| **Total** | | **~$2.09/month** |

**Still cheaper than**:
- AWS Lambda + DynamoDB: ~$0.89/month (but complex setup)
- Render.com paid: $7/month
- DigitalOcean Droplet: $6/month

---

## Continuous Deployment (GitHub Actions)

### Step 12: Automate Deployment

Create `.github/workflows/fly-deploy.yml`:

```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    name: Deploy app
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: superfly/flyctl-actions/setup-flyctl@master
      
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

**Setup GitHub secret**:
```bash
# Generate Fly.io API token
flyctl tokens create deploy

# Copy the token
# Go to GitHub repo → Settings → Secrets → Actions
# Create secret: FLY_API_TOKEN = <paste token>
```

**Now**: Every push to `main` automatically deploys!

---

## Troubleshooting

### Problem: Bot not responding

**Check logs**:
```bash
flyctl logs
```

**Common issues**:
- ❌ Missing `BOT_TOKEN` secret → Run: `flyctl secrets set BOT_TOKEN=...`
- ❌ VM crashed → Run: `flyctl status` then `flyctl restart`
- ❌ Database permission error → Check `/data` mount in `fly.toml`

### Problem: "Out of memory" error

**Symptoms**: Logs show `Killed` or `OOMKilled`

**Fix**:
```bash
# Increase memory to 512MB
flyctl scale memory 512

# Verify
flyctl scale show
```

### Problem: Database file missing after restart

**Cause**: Volume not properly mounted

**Fix**:
```bash
# Check volume status
flyctl volumes list

# Verify fly.toml has [mounts] section
cat fly.toml | grep -A3 mounts

# Re-deploy
flyctl deploy
```

### Problem: Can't connect to Telegram

**Debug**:
```bash
# Test network from VM
flyctl ssh console

# Inside VM:
curl https://api.telegram.org/botYOUR_TOKEN/getMe
exit
```

**Fix**: Ensure Fly.io's IP isn't blocked by Telegram (rare, but check).

### Getting Help

**Check status**:
```bash
flyctl doctor  # Diagnose issues
flyctl status  # App status
flyctl logs    # Recent logs
```

**Fly.io Community**:
- Forum: https://community.fly.io
- Discord: https://fly.io/discord
- Docs: https://fly.io/docs

---

## Next Steps

### Recommended Improvements

1. **Set up automated backups**:
   ```bash
   # Create backup script
   cat > backup.sh << 'EOF'
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   flyctl ssh sftp get /data/stories.db ./backups/stories_${DATE}.db
   EOF
   
   chmod +x backup.sh
   
   # Run daily via cron
   crontab -e
   # Add: 0 2 * * * /path/to/backup.sh
   ```

2. **Add health checks**:
   ```toml
   # In fly.toml, add:
   [[services]]
     http_checks = []
     internal_port = 8080
     protocol = "tcp"
   ```

3. **Monitor with Sentry** (optional):
   ```bash
   pip install sentry-sdk
   
   # Add to bot.py:
   import sentry_sdk
   sentry_sdk.init(dsn="YOUR_SENTRY_DSN")
   ```

4. **Use Fly.io regions for low latency**:
   ```bash
   # Add more regions (for global users)
   flyctl regions add ams syd
   
   # List available regions
   flyctl platform regions
   ```

---

## Cleanup (If Needed)

**To delete everything**:

```bash
# Destroy the app
flyctl apps destroy moments-bot

# Delete volumes
flyctl volumes delete moments_data

# Verify removal
flyctl apps list
```

---

## Comparison: Fly.io vs AWS

**Summary table**:

| Aspect | Fly.io | AWS Lambda |
|--------|--------|------------|
| **Setup Time** | 10 minutes | 2-3 hours |
| **Commands** | 5 commands | 15+ commands |
| **Code Changes** | None | Major (webhooks, DynamoDB) |
| **Free Tier** | $5/month credit | Pay-as-you-go |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Learning Curve** | Low | High |

**When to choose Fly.io**:
- ✅ You want simple deployment
- ✅ Polling mode is fine
- ✅ SQLite is sufficient
- ✅ Low-to-medium traffic bot
- ✅ You value developer experience

**When to choose AWS**:
- ✅ You need extreme scalability (1M+ users)
- ✅ You're already using AWS ecosystem
- ✅ You need complex integrations (SES, S3, etc.)
- ✅ You have DevOps expertise

---

## Conclusion

Congratulations! 🎉 You've deployed your Telegram bot on Fly.io.

**What you've accomplished**:
- ✅ Deployed with a single command (`flyctl deploy`)
- ✅ Kept your existing code (no webhooks needed!)
- ✅ Used SQLite with persistent storage
- ✅ Set up automatic deployments via GitHub Actions
- ✅ Learned Fly.io CLI and monitoring

**Your bot now**:
- Runs 24/7 on Fly.io's global edge network
- Costs $0/month (under free tier)
- Deploys automatically on git push
- Uses familiar SQLite database
- Is production-ready!

**Resources for Learning More**:
- Fly.io Docs: https://fly.io/docs
- Fly.io Pricing: https://fly.io/docs/about/pricing/
- Fly.io Community: https://community.fly.io
- Telegram Bot API: https://core.telegram.org/bots/api

---

**Need help?** Check the Troubleshooting section or ask in the Fly.io community forum.

**Happy coding!** 🚀
