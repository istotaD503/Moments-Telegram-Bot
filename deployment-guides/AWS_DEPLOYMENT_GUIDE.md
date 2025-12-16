# Complete AWS Deployment Guide for Moments Bot

**Last Updated**: December 15, 2025

This guide will walk you through deploying your Telegram bot on AWS from scratch, assuming no prior AWS experience.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [AWS CLI Installation & Configuration](#aws-cli-installation--configuration)
4. [Architecture Overview](#architecture-overview)
5. [Code Preparation](#code-preparation)
6. [AWS Infrastructure Setup](#aws-infrastructure-setup)
7. [Docker Setup](#docker-setup)
8. [GitHub Actions CI/CD](#github-actions-cicd)
9. [Telegram Webhook Configuration](#telegram-webhook-configuration)
10. [Testing & Monitoring](#testing--monitoring)
11. [Cost Estimates](#cost-estimates)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You Need
- ✅ A Telegram bot token (from @BotFather)
- ✅ A GitHub account (for code hosting and CI/CD)
- ✅ A credit/debit card (for AWS account verification - they charge $1 temporarily)
- ✅ Basic command line knowledge
- ✅ This bot's code repository

### What You'll Learn
- Creating and securing an AWS account
- Using AWS Lambda, DynamoDB, and API Gateway
- Setting up Docker for serverless deployment
- Configuring CI/CD pipelines with GitHub Actions

---

## AWS Account Setup

### Step 1: Create Your AWS Account

1. **Go to AWS Signup**
   - Visit: https://aws.amazon.com
   - Click **"Create an AWS Account"** (top-right corner)

2. **Enter Account Details**
   - **Email address**: Use a valid email (you'll receive verification codes)
   - **Password**: Choose a strong password (min 8 characters)
   - **AWS account name**: Something like "MyPersonalAWS" (can be changed later)
   - Click **Continue**

3. **Contact Information**
   - Select **Personal** account type (unless you have a business)
   - Enter your full name, phone number, and address
   - Accept the AWS Customer Agreement
   - Click **Continue**

4. **Payment Information**
   - Enter credit/debit card details
   - AWS will charge $1 to verify the card (refunded within 3-5 days)
   - **Don't worry**: We'll use the Free Tier, so no charges for this bot
   - Click **Verify and Continue**

5. **Identity Verification**
   - Choose verification method: **Text message (SMS)** or **Voice call**
   - Enter your phone number
   - Enter the 4-digit code you receive
   - Click **Continue**

6. **Select Support Plan**
   - Choose **Basic support - Free**
   - Click **Complete sign up**

7. **Wait for Confirmation**
   - You'll see "Congratulations!" message
   - You'll receive an email confirmation (may take up to 24 hours, usually instant)
   - Click **Go to the AWS Management Console**

### Step 2: Secure Your Root Account

⚠️ **Important**: Your root account has unlimited access. Secure it immediately!

1. **Enable Multi-Factor Authentication (MFA)**
   - In the AWS Console, click your account name (top-right)
   - Select **Security credentials**
   - Under **Multi-factor authentication (MFA)**, click **Assign MFA device**
   - Choose **Authenticator app** (use Google Authenticator, Authy, or 1Password)
   - Scan the QR code with your phone
   - Enter two consecutive MFA codes
   - Click **Assign MFA**

2. **Create an IAM Admin User** (Don't use root for daily tasks)
   - Search for **IAM** in the top search bar
   - Click **Users** (left sidebar) → **Create user**
   - Username: `admin-user` (or your name)
   - Check ✅ **Provide user access to the AWS Management Console**
   - Select **I want to create an IAM user**
   - Set a custom password (save this!)
   - Uncheck "Users must create a new password at next sign-in"
   - Click **Next**
   - Click **Attach policies directly**
   - Search for `AdministratorAccess` and check it
   - Click **Next** → **Create user**
   - **Download the .csv file** with credentials (you need this!)

3. **Sign Out and Sign Back In as IAM User**
   - Click your account name → **Sign out**
   - Go to the sign-in URL from the CSV file (looks like: `https://123456789.signin.aws.amazon.com/console`)
   - Enter IAM username and password
   - **From now on, always use this IAM user, not root**

---

## AWS CLI Installation & Configuration

The AWS CLI (Command Line Interface) lets you control AWS from your terminal.

### Step 3: Install AWS CLI

**For macOS** (your system):
```bash
# Download and install
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify installation
aws --version
# Should output: aws-cli/2.x.x ...
```

**For Windows**:
- Download: https://awscli.amazonaws.com/AWSCLIV2.msi
- Run the installer
- Open Command Prompt and run: `aws --version`

**For Linux**:
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version
```

### Step 4: Configure AWS CLI Authentication

You have **two options** for authenticating the AWS CLI:

#### Option A: AWS SSO (Recommended - Uses Console Credentials)

This method lets you use your existing AWS Console login without creating access keys.

1. **Configure SSO Profile**:
   ```bash
   aws configure sso
   ```

2. **Answer the prompts**:
   - **SSO session name**: `my-aws` (or any name you like)
   - **SSO start URL**: `https://123456789.signin.aws.amazon.com/console` (your IAM sign-in URL from Step 2)
   - **SSO region**: `us-east-1`
   - **SSO registration scopes**: `sso:account:access` (press Enter for default)

3. **Browser will open automatically**:
   - Sign in with your IAM user credentials (`admin-user`)
   - Click **Allow** to authorize AWS CLI

4. **Continue in terminal**:
   - **Select the account** (should only show one)
   - **Select the role**: Choose `AdministratorAccess` or similar
   - **CLI default region**: `us-east-1`
   - **CLI default output format**: `json`
   - **CLI profile name**: `default` (or `admin`)

5. **Login when needed**:
   ```bash
   # Login (expires after 8 hours by default)
   aws sso login
   
   # Or if you used a custom profile name:
   aws sso login --profile admin
   ```

**Pros**: More secure (no long-lived credentials), easy to use  
**Cons**: Need to run `aws sso login` when session expires

#### Option B: Access Keys (Traditional Method)

This creates permanent credentials (less secure but doesn't expire).

1. **In AWS Console (as IAM user)**:
   - Search for **IAM** → Click **Users**
   - Click your username (`admin-user`)
   - Select **Security credentials** tab
   - Scroll to **Access keys** section
   - Click **Create access key**
   - Select **Command Line Interface (CLI)**
   - Check the confirmation box
   - Click **Next** → **Create access key**
   - **IMPORTANT**: Click **Download .csv file** (you can't see the secret key again!)

2. **Configure the CLI**:
   ```bash
   aws configure
   
   # You'll be prompted for 4 values:
   # AWS Access Key ID: [paste from CSV file]
   # AWS Secret Access Key: [paste from CSV file]
   # Default region name: us-east-1
   # Default output format: json
   ```

**Pros**: Doesn't expire, simpler for automation  
**Cons**: Less secure (credentials can be compromised)

### Step 5: Verify AWS CLI Access

**Test your authentication** (works with either option):
```bash
aws sts get-caller-identity
# Should show your account ID and user ARN
```

**Expected output**:
```json
{
    "UserId": "AIDAEXAMPLEID",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/admin-user"
}
```

**Note for GitHub Actions**: If you chose Option A (SSO), you'll still need to create access keys (Option B) for GitHub Actions to use in Step 24. Your local CLI can use SSO, but GitHub Actions requires access keys.

---

### Troubleshooting Step 5

#### Error: "Could not connect to the endpoint URL"

If you see an error like:
```
Could not connect to the endpoint URL: "https://sts.use-east-1.amazonaws.com/"
```

**Cause**: Typo in region name or incorrect AWS configuration.

**Fix**:
```bash
# Check your current configuration
aws configure list

# Look for the region - it should be "us-east-1" not "use-east-1"
# If it's wrong, reconfigure:
aws configure set region us-east-1

# Or if using SSO, check your ~/.aws/config file
cat ~/.aws/config
# Look for region = us-east-1 (not use-east-1 or other typos)

# Test again
aws sts get-caller-identity
```

**Common typos**:
- ❌ `use-east-1` → ✅ `us-east-1`
- ❌ `us-esat-1` → ✅ `us-east-1`
- ❌ `east-1` → ✅ `us-east-1`

#### Error: "The security token included in the request is invalid"

**For SSO users**: Your session expired.
```bash
aws sso login
# Then try again
aws sts get-caller-identity
```

**For Access Key users**: Invalid credentials.
```bash
# Reconfigure with correct keys from CSV file
aws configure
```

---

## Architecture Overview

### What We're Building

```
Telegram User
    ↓
Telegram API (sends updates via webhook)
    ↓
AWS API Gateway (HTTPS endpoint)
    ↓
AWS Lambda (runs your bot code in a container)
    ↓
AWS DynamoDB (stores user stories)
```

### Why This Architecture?

**Current Setup (Render.com)**:
- ❌ Uses polling (bot repeatedly asks Telegram "any updates?")
- ❌ Requires a server running 24/7
- ❌ Uses SQLite (file-based database, not scalable)
- ❌ Limited free tier

**New Setup (AWS Serverless)**:
- ✅ Webhook-based (Telegram pushes updates to you)
- ✅ No server to manage (Lambda runs only when needed)
- ✅ DynamoDB (cloud database, auto-scales)
- ✅ Pay only for what you use (~$0-1/month for low traffic)
- ✅ Auto-scales from 1 to 10,000 users

### Key AWS Services Explained

1. **Lambda**: Runs your code without managing servers
   - Think: "Serverless function that wakes up when Telegram sends a message"
   - Pricing: First 1 million requests/month FREE

2. **DynamoDB**: NoSQL database
   - Think: "Google Sheets but for code, infinitely fast"
   - Pricing: First 25 GB storage FREE

3. **API Gateway**: HTTPS endpoint
   - Think: "A public URL that triggers your Lambda"
   - Pricing: First 1 million requests/month FREE

4. **ECR (Elastic Container Registry)**: Docker image storage
   - Think: "GitHub for Docker images"
   - Pricing: 500 MB storage FREE

---

## Code Preparation

### Step 6: Create Webhook Handler

We need to change from polling (constantly checking for messages) to webhooks (Telegram tells us when there's a message).

**Create the file** `handlers/webhook.py`:

```python
import json
import logging
from telegram import Update
from telegram.ext import Application

logger = logging.getLogger(__name__)

# Global application instance (reused across Lambda invocations)
# This takes advantage of Lambda's execution context reuse ("warm starts")
application = None

async def get_application():
    """
    Get or create the Telegram application instance.
    
    Lambda Container Lifecycle:
    - Lambda reuses containers between invocations ("warm starts")
    - Global variables persist in memory between invocations in the same container
    - When Lambda scales up, new containers start with application = None
    - When a container is recycled (~15 min idle), a new one starts fresh
    
    Performance impact:
    - Creating Application() + initialize() takes ~500-1000ms
    - Reusing saves this overhead on every subsequent request
    - Trade-off: slightly more complex code for significant performance gain
    
    Thread safety:
    - Lambda invocations are single-threaded within a container
    - No concurrent requests in the same container = no race conditions
    - Each container has its own isolated application instance
    """
    global application
    
    if application is None:
        from bot import create_application
        application = create_application()
        await application.initialize()
        logger.info("✅ Created new application instance (cold start)")
    else:
        logger.info("♻️ Reusing existing application instance (warm start)")
    
    return application

async def lambda_handler(event, context):
    """
    AWS Lambda entry point for Telegram webhook.
    
    Execution flow:
    1. API Gateway receives POST from Telegram
    2. Lambda invokes this function (may reuse existing container)
    3. get_application() returns cached or new instance
    4. Process the update
    5. Return 200 OK to Telegram
    6. Lambda keeps container warm for ~15 minutes
    
    Performance characteristics:
    - Cold start (first request in new container): ~2-3 seconds
    - Warm start (subsequent requests): ~200-500ms
    - Memory persists between requests in same container
    
    Considerations:
    - Application state (like HTTP connections) is preserved between requests
    - This is intentional and beneficial for connection pooling
    - If you need fresh state per request, don't use this pattern
    
    Args:
        event: API Gateway HTTP API event (contains Telegram update JSON)
        context: Lambda context object (metadata about execution)
    
    Returns:
        dict: API Gateway response format
    """
    try:
        # Parse Telegram update from API Gateway body
        body = json.loads(event.get('body', '{}'))
        logger.info(f"Received update: {body}")
        
        # Get the application instance (creates on first call, reuses after)
        app = await get_application()
        
        # Process the update
        update = Update.de_json(body, app.bot)
        await app.process_update(update)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'ok': True})
        }
    
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

**Architectural Analysis:**

**✅ Why this IS best practice:**
1. **AWS Lambda documentation recommends it**: "Take advantage of execution environment reuse to improve performance"
2. **Cost optimization**: Faster execution = lower Lambda costs (charged per 100ms)
3. **Connection pooling**: HTTP clients, DB connections benefit from reuse
4. **Official pattern**: Used in AWS Lambda Powertools, AWS SDKs, etc.

**⚠️ When to be cautious:**
1. **Stateful objects**: Don't cache user-specific data (we're not - Application is stateless per-request)
2. **Memory leaks**: Long-running containers could accumulate memory (monitor with CloudWatch)
3. **Stale connections**: If Telegram changes tokens, restart Lambda (force new containers)
4. **Cold starts still happen**: When scaling up or after ~15min idle

**Alternative approaches:**

**Option 1: Create on every request (simpler but slower)**
```python
async def lambda_handler(event, context):
    # Recreate everything each time
    from bot import create_application
    app = create_application()
    await app.initialize()
    
    # ... process update ...
    
    await app.shutdown()  # Clean shutdown
    return response
```
- **Pros**: No global state, easier to reason about
- **Cons**: ~500ms slower per request, higher costs
- **Use when**: Simplicity > performance, very low traffic

**Option 2: Lazy initialization with singleton pattern (production-grade)**
```python
class ApplicationManager:
    _instance = None
    _app = None
    
    @classmethod
    async def get_application(cls):
        if cls._app is None:
            from bot import create_application
            cls._app = create_application()
            await cls._app.initialize()
        return cls._app

async def lambda_handler(event, context):
    app = await ApplicationManager.get_application()
    # ... use app ...
```
- **Pros**: More explicit, testable, thread-safe pattern
- **Cons**: More code, overkill for Lambda (single-threaded)

**Recommendation**: Use the global variable approach (as shown) because:
- Lambda guarantees single-threaded execution per container
- It's the simplest correct implementation
- AWS documentation explicitly recommends this pattern
- python-telegram-bot's Application is designed for reuse

**Monitoring warm/cold starts:**
Add to CloudWatch Insights query:
```
fields @timestamp, @message
| filter @message like /Created new application/
| stats count() as cold_starts by bin(5m)
```

### Step 7: Refactor bot.py for Dual Mode

We want to support both:
- **Local development**: Polling mode (for testing)
- **AWS production**: Webhook mode

**Replace your entire `bot.py` with this**:

```python
import os
import sys
import logging
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters

from config.settings import settings
from handlers.commands import CommandHandlers, WAITING_FOR_STORY

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def create_application():
    """
    Factory function to create telegram Application.
    
    Why a factory?
    - Lambda needs to create fresh instances for each invocation
    - Allows reuse in both polling (local) and webhook (AWS) modes
    """
    application = (
        Application.builder()
        .token(settings.bot_token)
        .build()
    )
    
    # Register error handler (group=-1 means it runs first)
    application.add_error_handler(CommandHandlers.error_handler, block=False)
    
    # Register conversation handler for /story command
    story_conversation = ConversationHandler(
        entry_points=[CommandHandler("story", CommandHandlers.story_command)],
        states={
            WAITING_FOR_STORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, CommandHandlers.receive_story)
            ]
        },
        fallbacks=[CommandHandler("cancel", CommandHandlers.cancel_story)]
    )
    
    application.add_handler(story_conversation)
    
    # Register simple command handlers
    application.add_handler(CommandHandler("start", CommandHandlers.start_command))
    application.add_handler(CommandHandler("help", CommandHandlers.help_command))
    application.add_handler(CommandHandler("mystories", CommandHandlers.my_stories_command))
    
    return application

async def main():
    """
    Local development mode with polling.
    
    Run this with: python bot.py
    Used for testing before deploying to AWS.
    """
    application = create_application()
    
    logger.info("🚀 Bot running in POLLING mode (local development)")
    logger.info("Press Ctrl+C to stop")
    
    # Initialize and start polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    # Keep running until Ctrl+C
    try:
        await application.updater.idle()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    # Only run polling mode when executed directly (not imported by Lambda)
    import asyncio
    asyncio.run(main())
```

### Step 8: Create DynamoDB Database Adapter

DynamoDB is very different from SQLite. Here's how we'll structure the data:

**Data Model**:
- **Partition Key (PK)**: `USER#{user_id}` - Groups all data for a user
- **Sort Key (SK)**: `STORY#{timestamp}` - Sorts stories chronologically
- This allows fast queries: "Get all stories for user X"

**Create the file** `models/dynamodb_story.py`:

```python
import boto3
import logging
from datetime import datetime
from typing import List, Dict
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class DynamoDBStoryDatabase:
    """
    DynamoDB implementation of story storage.
    
    Replaces SQLite for AWS Lambda (Lambda has ephemeral storage).
    
    Table Design:
    - PK (Partition Key): USER#{user_id}
    - SK (Sort Key): STORY#{ISO timestamp}
    - Attributes: username, story_text, created_at
    
    Why this design?
    - All user's stories are co-located (fast queries)
    - Sort key enables chronological ordering
    - No secondary indexes needed (cost-effective)
    """
    
    def __init__(self, table_name: str = None):
        """
        Initialize DynamoDB client.
        
        Args:
            table_name: DynamoDB table name (defaults to env var or 'MomentsBot-Stories')
        """
        self.table_name = table_name or os.getenv('DYNAMODB_TABLE', 'MomentsBot-Stories')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)
        logger.info(f"Connected to DynamoDB table: {self.table_name}")
    
    def save_story(self, user_id: int, username: str, story_text: str) -> bool:
        """
        Save a story to DynamoDB.
        
        Args:
            user_id: Telegram user ID (numeric)
            username: Telegram username (@handle)
            story_text: The moment/story content
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use ISO format for timestamps (sortable strings)
            timestamp = datetime.now().isoformat()
            
            self.table.put_item(
                Item={
                    'PK': f'USER#{user_id}',
                    'SK': f'STORY#{timestamp}',
                    'user_id': user_id,
                    'username': username or 'unknown',
                    'story_text': story_text,
                    'created_at': timestamp
                }
            )
            logger.info(f"✅ Saved story for user {user_id}")
            return True
        
        except ClientError as e:
            logger.error(f"❌ DynamoDB error: {e.response['Error']['Message']}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            return False
    
    def get_user_stories(self, user_id: int, limit: int = 50) -> List[Dict]:
        """
        Retrieve user's stories sorted by date (newest first).
        
        Args:
            user_id: Telegram user ID
            limit: Max stories to return (default 50)
        
        Returns:
            List of dicts with keys: story_text, created_at
        """
        try:
            response = self.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
                ExpressionAttributeValues={
                    ':pk': f'USER#{user_id}',
                    ':sk': 'STORY#'
                },
                ScanIndexForward=False,  # False = descending order (newest first)
                Limit=limit
            )
            
            stories = [
                {
                    'story_text': item['story_text'],
                    'created_at': item['created_at']
                }
                for item in response.get('Items', [])
            ]
            
            logger.info(f"📖 Retrieved {len(stories)} stories for user {user_id}")
            return stories
        
        except ClientError as e:
            logger.error(f"❌ DynamoDB query error: {e.response['Error']['Message']}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            return []
```

### Step 9: Update Command Handlers to Use Both Databases

We want the code to:
- Use **DynamoDB** when running in AWS Lambda
- Use **SQLite** when running locally

**Update `handlers/commands.py`** - Add this at the top (after imports):

```python
import os

# Choose database backend based on environment
if os.getenv('AWS_EXECUTION_ENV'):
    # Running in AWS Lambda
    from models.dynamodb_story import DynamoDBStoryDatabase
    story_db = DynamoDBStoryDatabase()
    logger.info("Using DynamoDB backend")
else:
    # Running locally
    from models.story import StoryDatabase
    story_db = StoryDatabase()
    logger.info("Using SQLite backend")

class CommandHandlers:
    # Remove the class-level story_db = StoryDatabase() line if it exists
    # We'll use the module-level story_db instead
    
    # ... rest of your existing code ...
```

**Update all methods** to use `story_db` instead of `CommandHandlers.story_db`:
- Change `CommandHandlers.story_db.save_story(...)` → `story_db.save_story(...)`
- Change `CommandHandlers.story_db.get_user_stories(...)` → `story_db.get_user_stories(...)`

### Step 10: Update Requirements

**Update `requirements.txt`**:

```txt
python-telegram-bot==20.7
python-dotenv==1.0.0
boto3==1.34.34
botocore==1.34.34
```

---

## AWS Infrastructure Setup

Now we'll create the AWS resources needed for the bot.

### Step 11: Create DynamoDB Table

**What it does**: Creates a database to store user stories.

```bash
aws dynamodb create-table \
    --table-name MomentsBot-Stories \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

**What each parameter means**:
- `--table-name`: Name of your table
- `--attribute-definitions`: Defines PK and SK as strings (S = String type)
- `--key-schema`: PK is partition key (HASH), SK is sort key (RANGE)
- `--billing-mode PAY_PER_REQUEST`: On-demand pricing (no provisioned capacity needed)
- `--region`: Where to create the table (us-east-1 is N. Virginia)

**Expected output**:
```json
{
    "TableDescription": {
        "TableName": "MomentsBot-Stories",
        "TableStatus": "CREATING",
        ...
    }
}
```

**Verify table creation** (wait ~30 seconds):
```bash
aws dynamodb describe-table --table-name MomentsBot-Stories --region us-east-1
# Look for "TableStatus": "ACTIVE"
```

### Step 12: Create ECR Repository

**What it does**: Creates a private Docker registry for your Lambda container images.

```bash
aws ecr create-repository \
    --repository-name moments-bot \
    --region us-east-1
```

**Expected output** (save the `repositoryUri`!):
```json
{
    "repository": {
        "repositoryUri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/moments-bot",
        ...
    }
}
```

**Copy the `repositoryUri`** - you'll need it later!

### Step 13: Create IAM Role for Lambda

Lambda needs permissions to:
1. Write logs to CloudWatch
2. Read/write to DynamoDB

**Create directory for AWS files**:
```bash
mkdir -p aws
```

**Create `aws/lambda-trust-policy.json`**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**What this means**: "Allow AWS Lambda service to assume this role" (like giving Lambda an ID badge).

**Create `aws/lambda-policy.json`** (replace `123456789012` with your AWS account ID):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:GetItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/MomentsBot-Stories"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

**What this means**: 
- First statement: "Allow reading/writing to MomentsBot-Stories table"
- Second statement: "Allow creating and writing to CloudWatch Logs"

**Get your AWS account ID**:
```bash
aws sts get-caller-identity --query Account --output text
# Example output: 123456789012
```

**Update the JSON file** with your account ID, then run:

```bash
# Create the IAM role
aws iam create-role \
    --role-name MomentsBotLambdaRole \
    --assume-role-policy-document file://aws/lambda-trust-policy.json

# Attach the permissions policy
aws iam put-role-policy \
    --role-name MomentsBotLambdaRole \
    --policy-name MomentsBotPolicy \
    --policy-document file://aws/lambda-policy.json
```

**Expected output**:
```json
{
    "Role": {
        "RoleName": "MomentsBotLambdaRole",
        "Arn": "arn:aws:iam::123456789012:role/MomentsBotLambdaRole",
        ...
    }
}
```

**Copy the `Arn`** - you'll need it for Lambda creation!

---

## Docker Setup

### Step 14: Create Lambda-Compatible Dockerfile

AWS Lambda requires a specific base image and structure.

**Create/replace your `Dockerfile`**:

```dockerfile
# AWS's official Python 3.11 runtime for Lambda
FROM public.ecr.aws/lambda/python:3.11

# Copy requirements and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bot.py ${LAMBDA_TASK_ROOT}/
COPY config/ ${LAMBDA_TASK_ROOT}/config/
COPY handlers/ ${LAMBDA_TASK_ROOT}/handlers/
COPY models/ ${LAMBDA_TASK_ROOT}/models/
COPY utils/ ${LAMBDA_TASK_ROOT}/utils/
COPY assets/ ${LAMBDA_TASK_ROOT}/assets/

# Set the Lambda handler
# Format: filename.function_name
CMD ["handlers.webhook.lambda_handler"]
```

**What each line means**:
- `FROM`: Base image with Python 3.11 and Lambda runtime
- `LAMBDA_TASK_ROOT`: Pre-defined path where Lambda loads code (`/var/task`)
- `RUN pip install`: Installs your dependencies
- `COPY`: Copies your code into the container
- `CMD`: Tells Lambda which function to run (our webhook handler)

### Step 15: Build and Push Docker Image

**Authenticate with ECR** (replace `123456789012` with your account ID):
```bash
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

**Build the image**:
```bash
# Replace with your ECR repository URI from Step 12
docker build --platform linux/amd64 -t 123456789012.dkr.ecr.us-east-1.amazonaws.com/moments-bot:latest .
```

**Why `--platform linux/amd64`?** 
- Lambda runs on Linux x86_64 architecture
- If you're on Mac M1/M2 (ARM), this ensures compatibility

**Push to ECR**:
```bash
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/moments-bot:latest
```

**Expected output**:
```
latest: digest: sha256:abc123... size: 1234
```

---

## Step 16: Create Lambda Function

**What it does**: Creates a serverless function that runs your bot code.

```bash
# Replace these values:
# - 123456789012: Your AWS account ID
# - arn:aws:iam::...: Role ARN from Step 13
# - YOUR_BOT_TOKEN: From @BotFather

aws lambda create-function \
    --function-name MomentsBot \
    --package-type Image \
    --code ImageUri=123456789012.dkr.ecr.us-east-1.amazonaws.com/moments-bot:latest \
    --role arn:aws:iam::123456789012:role/MomentsBotLambdaRole \
    --timeout 30 \
    --memory-size 512 \
    --environment "Variables={BOT_TOKEN=YOUR_BOT_TOKEN,DYNAMODB_TABLE=MomentsBot-Stories}" \
    --region us-east-1
```

**What each parameter means**:
- `--function-name`: Name of your Lambda function
- `--package-type Image`: We're using a Docker container (not a zip file)
- `--code ImageUri`: The Docker image we just pushed
- `--role`: IAM role that gives permissions
- `--timeout 30`: Max execution time (30 seconds)
- `--memory-size 512`: RAM allocation (512 MB)
- `--environment`: Environment variables (bot token, table name)

**Expected output**:
```json
{
    "FunctionName": "MomentsBot",
    "FunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:MomentsBot",
    "State": "Pending",
    ...
}
```

**Wait for function to be ready** (~30-60 seconds):
```bash
aws lambda wait function-active --function-name MomentsBot --region us-east-1
```

### Step 17: Create API Gateway

**What it does**: Creates a public HTTPS URL that triggers your Lambda when Telegram sends updates.

```bash
aws apigatewayv2 create-api \
    --name MomentsBotAPI \
    --protocol-type HTTP \
    --target arn:aws:lambda:us-east-1:123456789012:function:MomentsBot \
    --region us-east-1
```

**Replace `123456789012`** with your account ID.

**Expected output** (save the `ApiEndpoint`!):
```json
{
    "ApiId": "abc123xyz",
    "ApiEndpoint": "https://abc123xyz.execute-api.us-east-1.amazonaws.com",
    ...
}
```

**Copy the `ApiEndpoint`** - this is your webhook URL!

### Step 18: Grant API Gateway Permission to Invoke Lambda

**What it does**: Allows API Gateway to trigger your Lambda function.

```bash
# Replace 123456789012 with your account ID
# Replace abc123xyz with your API ID (from ApiEndpoint above)

aws lambda add-permission \
    --function-name MomentsBot \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:123456789012:abc123xyz/*/*/*" \
    --region us-east-1
```

**What this means**: "Allow API Gateway to call the MomentsBot Lambda function."

---

## Telegram Webhook Configuration

### Step 19: Set Telegram Webhook

**What it does**: Tells Telegram to send updates to your API Gateway instead of requiring polling.

```bash
# Replace YOUR_BOT_TOKEN with your actual token
# Replace the URL with your ApiEndpoint from Step 17

curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://abc123xyz.execute-api.us-east-1.amazonaws.com"}'
```

**Expected response**:
```json
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```

### Step 20: Verify Webhook

```bash
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
```

**Expected response**:
```json
{
  "ok": true,
  "result": {
    "url": "https://abc123xyz.execute-api.us-east-1.amazonaws.com",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "max_connections": 40
  }
}
```

**Check for**:
- ✅ `url` matches your API Gateway
- ✅ `pending_update_count: 0` (no errors)
- ❌ If you see errors, check Lambda logs (next section)

---

## Testing & Monitoring

### Step 21: Test Your Bot

1. **Open Telegram** and find your bot
2. **Send `/start`** - should receive welcome message
3. **Send `/story`** - should prompt for a moment
4. **Type a moment** - should save to DynamoDB
5. **Send `/mystories`** - should show your saved moments

### Step 22: Monitor Lambda Logs

**Stream live logs**:
```bash
aws logs tail /aws/lambda/MomentsBot --follow --region us-east-1
```

**View recent errors**:
```bash
aws logs filter-log-events \
    --log-group-name /aws/lambda/MomentsBot \
    --filter-pattern "ERROR" \
    --region us-east-1
```

### Step 23: Check DynamoDB Data

**Scan table** (view all items):
```bash
aws dynamodb scan \
    --table-name MomentsBot-Stories \
    --limit 10 \
    --region us-east-1
```

**Query specific user** (replace `123456789` with a real user ID):
```bash
aws dynamodb query \
    --table-name MomentsBot-Stories \
    --key-condition-expression "PK = :pk" \
    --expression-attribute-values '{":pk":{"S":"USER#123456789"}}' \
    --region us-east-1
```

---

## GitHub Actions CI/CD

### Step 24: Create GitHub Secrets

**What it does**: Stores sensitive credentials for automated deployments.

1. **Go to your GitHub repository**
2. **Click Settings** (top-right)
3. **Click Secrets and variables** → **Actions** (left sidebar)
4. **Click "New repository secret"** and add these:

| Secret Name | Value | Where to Find |
|-------------|-------|---------------|
| `AWS_ACCESS_KEY_ID` | Your access key | From Step 4 (CSV file) |
| `AWS_SECRET_ACCESS_KEY` | Your secret key | From Step 4 (CSV file) |
| `BOT_TOKEN` | Your bot token | From @BotFather |
| `AWS_ACCOUNT_ID` | Your 12-digit account ID | Run: `aws sts get-caller-identity --query Account --output text` |
| `LAMBDA_FUNCTION_NAME` | `MomentsBot` | The name you used in Step 16 |
| `ECR_REPOSITORY` | `moments-bot` | The name you used in Step 12 |

### Step 25: Create GitHub Actions Workflow

**Create directory**:
```bash
mkdir -p .github/workflows
```

**Create `.github/workflows/deploy.yml`**:

```yaml
name: Deploy to AWS Lambda

on:
  push:
    branches: [main]
  workflow_dispatch:  # Allows manual triggering

env:
  AWS_REGION: us-east-1

jobs:
  deploy:
    name: Build and Deploy
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: ${{ secrets.ECR_REPOSITORY }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          # Build with git commit SHA as tag
          docker build --platform linux/amd64 -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          
          # Also tag as 'latest'
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
      
      - name: Update Lambda function
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: ${{ secrets.ECR_REPOSITORY }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          aws lambda update-function-code \
            --function-name ${{ secrets.LAMBDA_FUNCTION_NAME }} \
            --image-uri $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      
      - name: Wait for Lambda update to complete
        run: |
          aws lambda wait function-updated \
            --function-name ${{ secrets.LAMBDA_FUNCTION_NAME }}
      
      - name: Update environment variables
        run: |
          aws lambda update-function-configuration \
            --function-name ${{ secrets.LAMBDA_FUNCTION_NAME }} \
            --environment "Variables={BOT_TOKEN=${{ secrets.BOT_TOKEN }},DYNAMODB_TABLE=MomentsBot-Stories}"
      
      - name: Deployment successful
        run: echo "🚀 Deployment complete!"
```

**What this workflow does**:
1. Triggers on every push to `main` branch
2. Builds Docker image with your latest code
3. Pushes to ECR with unique tag (git commit SHA)
4. Updates Lambda to use the new image
5. Updates bot token environment variable

### Step 26: Test CI/CD

**Commit and push**:
```bash
git add .
git commit -m "Add AWS deployment configuration"
git push origin main
```

**Watch the deployment**:
1. Go to your GitHub repo → **Actions** tab
2. Click the latest workflow run
3. Watch it build and deploy (~3-5 minutes)
4. ✅ Look for "Deployment complete!" message

**If it fails**:
- Check the error message in GitHub Actions logs
- Common issues:
  - Wrong AWS credentials → Re-check secrets
  - Permission denied → Verify IAM role has correct policies
  - Image push failed → Check ECR repository exists

---

## Cost Estimates

### Free Tier (First 12 Months)

| Service | Free Tier | Typical Bot Usage | Cost |
|---------|-----------|-------------------|------|
| **Lambda** | 1M requests/month | ~10K requests/month | $0.00 |
| **DynamoDB** | 25 GB storage, 25 RCU/WCU | ~1 MB storage, <1 RCU/WCU | $0.00 |
| **API Gateway** | 1M requests/month | ~10K requests/month | $0.00 |
| **ECR** | 500 MB storage | ~200 MB | $0.00 |
| **CloudWatch Logs** | 5 GB ingestion | ~100 MB | $0.00 |
| **Total** | | | **$0.00/month** |

### After Free Tier (Month 13+)

For a bot with **100 active users, ~1000 messages/day**:

| Service | Usage | Cost |
|---------|-------|------|
| **Lambda** | 30K requests/month @ 1s avg | $0.01 |
| **DynamoDB** | 10 MB storage, 30K writes, 30K reads | $0.30 |
| **API Gateway** | 30K requests/month | $0.03 |
| **ECR** | 500 MB storage | $0.05 |
| **CloudWatch Logs** | 1 GB/month | $0.50 |
| **Total** | | **~$0.89/month** |

**Scaling**: At **10,000 users** → ~$15-20/month (still much cheaper than a $7/month VPS).

---

## Troubleshooting

### Problem: Webhook not receiving updates

**Symptoms**: Bot doesn't respond in Telegram

**Debug steps**:
```bash
# 1. Check webhook status
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"

# 2. Check Lambda logs
aws logs tail /aws/lambda/MomentsBot --follow

# 3. Test Lambda directly
aws lambda invoke \
    --function-name MomentsBot \
    --payload '{"body": "{\"message\":{\"text\":\"/start\"}}"}' \
    response.json

# 4. Check API Gateway
curl -X POST https://YOUR_API_ENDPOINT.execute-api.us-east-1.amazonaws.com \
    -H "Content-Type: application/json" \
    -d '{"message":{"text":"test"}}'
```

**Common fixes**:
- ❌ Wrong webhook URL → Re-run Step 19 with correct URL
- ❌ Lambda timeout → Increase timeout: `aws lambda update-function-configuration --function-name MomentsBot --timeout 60`
- ❌ Permission denied → Verify Step 18 was completed

### Problem: "Internal server error" in Telegram

**Symptoms**: Bot responds with "Internal server error"

**Debug**:
```bash
# Check recent errors
aws logs filter-log-events \
    --log-group-name /aws/lambda/MomentsBot \
    --filter-pattern "ERROR" \
    --start-time $(date -u -d '10 minutes ago' +%s)000 \
    --region us-east-1
```

**Common causes**:
- ❌ Missing `BOT_TOKEN` env var → Re-run Step 16 configuration update
- ❌ DynamoDB permission denied → Check IAM policy in Step 13
- ❌ Python import error → Rebuild Docker image with correct dependencies

### Problem: DynamoDB write failed

**Symptoms**: Stories not saving, error in logs

**Debug**:
```bash
# Test DynamoDB access
aws dynamodb put-item \
    --table-name MomentsBot-Stories \
    --item '{"PK":{"S":"TEST#123"},"SK":{"S":"TEST#123"},"data":{"S":"test"}}' \
    --region us-east-1
```

**Common fixes**:
- ❌ Wrong table name → Check `DYNAMODB_TABLE` env var
- ❌ Permission denied → Verify Lambda role has `dynamodb:PutItem` permission
- ❌ Table doesn't exist → Re-run Step 11

### Problem: GitHub Actions deployment fails

**Symptoms**: Workflow shows red X

**Debug**:
1. Click the failed workflow in GitHub Actions
2. Expand the failed step
3. Look for error message

**Common errors**:
- `AccessDenied` → Check AWS credentials in secrets
- `RepositoryNotFoundException` → ECR repository name mismatch
- `ResourceNotFoundException` → Lambda function name mismatch

### Getting Help

**Check logs in order**:
1. GitHub Actions (for deployment issues)
2. CloudWatch Logs (for runtime errors)
3. Telegram webhook info (for webhook issues)

**Useful AWS Console URLs**:
- Lambda: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/MomentsBot
- DynamoDB: https://console.aws.amazon.com/dynamodbv2/home?region=us-east-1#table?name=MomentsBot-Stories
- CloudWatch: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252FMomentsBot

---

## Next Steps

### Recommended Improvements

1. **Set up CloudWatch Alarms**
   ```bash
   # Get notified if Lambda errors spike
   aws cloudwatch put-metric-alarm \
       --alarm-name MomentsBot-Errors \
       --metric-name Errors \
       --namespace AWS/Lambda \
       --statistic Sum \
       --period 300 \
       --evaluation-periods 1 \
       --threshold 10 \
       --comparison-operator GreaterThanThreshold \
       --dimensions Name=FunctionName,Value=MomentsBot
   ```

2. **Enable AWS Cost Explorer**
   - Go to AWS Console → Billing → Cost Explorer
   - Enable it (free)
   - Set up budget alerts ($1/month threshold)

3. **Infrastructure as Code** (Advanced)
   - Use **Terraform** or **CloudFormation** to manage all resources
   - Makes it easy to replicate or destroy the entire stack
   - Version control your infrastructure

4. **Add More Features**
   - Weekly email summaries (using AWS SES)
   - Story search (using DynamoDB GSI)
   - Export to PDF (using Lambda Layers for wkhtmltopdf)

### Cleanup (If You Want to Delete Everything)

**To avoid any charges**, delete resources in this order:

```bash
# 1. Delete Lambda function
aws lambda delete-function --function-name MomentsBot --region us-east-1

# 2. Delete API Gateway
API_ID=$(aws apigatewayv2 get-apis --query "Items[?Name=='MomentsBotAPI'].ApiId" --output text)
aws apigatewayv2 delete-api --api-id $API_ID --region us-east-1

# 3. Delete DynamoDB table
aws dynamodb delete-table --table-name MomentsBot-Stories --region us-east-1

# 4. Delete ECR images and repository
aws ecr batch-delete-image \
    --repository-name moments-bot \
    --image-ids imageTag=latest \
    --region us-east-1
aws ecr delete-repository --repository-name moments-bot --region us-east-1

# 5. Delete IAM role
aws iam delete-role-policy --role-name MomentsBotLambdaRole --policy-name MomentsBotPolicy
aws iam delete-role --role-name MomentsBotLambdaRole

# 6. Delete CloudWatch log groups
aws logs delete-log-group --log-group-name /aws/lambda/MomentsBot --region us-east-1
```

---

## Conclusion

Congratulations! 🎉 You've deployed a production-grade serverless Telegram bot on AWS.

**What you've accomplished**:
- ✅ Created and secured an AWS account
- ✅ Set up serverless architecture (Lambda + API Gateway + DynamoDB)
- ✅ Containerized your bot with Docker
- ✅ Configured automated CI/CD with GitHub Actions
- ✅ Learned AWS CLI, IAM, and infrastructure basics

**Your bot now**:
- Scales automatically from 1 to 10,000+ users
- Costs $0-1/month for typical usage
- Deploys automatically on every git push
- Stores data reliably in DynamoDB

**Resources for Learning More**:
- AWS Free Tier: https://aws.amazon.com/free/
- AWS Lambda Docs: https://docs.aws.amazon.com/lambda/
- DynamoDB Best Practices: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html
- Telegram Bot API: https://core.telegram.org/bots/api

---

**Need help?** Check the Troubleshooting section or open an issue in the GitHub repository.

**Happy coding!** 🚀
