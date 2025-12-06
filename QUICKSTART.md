# Quick Start Guide: Deploy in 10 Minutes

Get your General AI Agent running on Odoo in less than 10 minutes.

## What You'll Need

- [ ] Odoo.sh or Odoo.com account (free trial available)
- [ ] At least one LLM API key:
  - **Google Gemini** (recommended): https://aistudio.google.com/app/apikey (Free tier: 15 requests/minute)
  - **OpenAI GPT-4**: https://platform.openai.com/api-keys ($5 minimum)
  - **Anthropic Claude**: https://console.anthropic.com/ ($5 minimum)

## Step 1: Get Odoo (2 minutes)

### Option A: Odoo.sh (Best for testing)

1. Go to https://www.odoo.sh
2. Click "Start Free Trial"
3. Sign up with GitHub account
4. Create project: `ai-agent-test`
5. Select Odoo 17.0

### Option B: Odoo.com (Best for production)

1. Go to https://www.odoo.com/trial
2. Fill in company details
3. Select "Custom" apps
4. Click "Start now"
5. Check email for credentials

## Step 2: Install Module (3 minutes)

### If using Odoo.sh:

```bash
# In your Odoo.sh project settings:
1. Go to "Settings" > "Repository"
2. Add GitHub repository: https://github.com/Gudmundur76/odoo-general-agent
3. Set branch: master
4. Click "Deploy"
5. Wait 5 minutes for build
```

### If using Odoo.com:

```bash
# Contact Odoo support to install custom module
# OR use Odoo.sh and connect to Odoo.com database
```

### Alternative: Local Installation

```bash
# Clone repository
git clone https://github.com/Gudmundur76/odoo-general-agent.git

# Install dependencies
pip3 install -r odoo-general-agent/requirements.txt

# Copy to Odoo addons
sudo cp -r odoo-general-agent /usr/lib/python3/dist-packages/odoo/addons/

# Restart Odoo
sudo systemctl restart odoo
```

## Step 3: Activate Module (2 minutes)

1. Log in to your Odoo instance
2. Go to **Apps** menu
3. Click "Update Apps List"
4. Search for "General AI Agent"
5. Click "Install"
6. Wait for installation (~1 minute)

## Step 4: Configure API Key (1 minute)

1. Go to **AI Agent** menu (top bar)
2. Click **Configuration > Settings**
3. Enter your API key:
   - **Google Gemini**: Paste your key from https://aistudio.google.com/app/apikey
   - OR **OpenAI**: Paste your key from https://platform.openai.com/api-keys
   - OR **Anthropic**: Paste your key from https://console.anthropic.com/
4. Click "Test Connection" button
5. If successful, click "Save"

## Step 5: Create Your First Agent (2 minutes)

1. Go to **AI Agent > Agents**
2. Click "Create" button
3. Fill in:
   - **Name**: `Customer Service Agent`
   - **Default LLM**: Select `Gemini 2.0 Flash` (cheapest, fastest)
   - **System Prompt**: Leave default or customize
4. Click "Save"
5. Click "Test Agent" button
6. Wait for response (~5 seconds)

**Success!** Your agent is now active.

## Step 6: Try It Out (2 minutes)

### Via UI:

1. Go to **AI Agent > Tasks**
2. Click "Create"
3. Select your agent
4. Enter task: `Find all customers with email containing "example.com"`
5. Set priority: `Normal`
6. Click "Save"
7. Click "Execute Now"
8. View result in "Result" field

### Via API:

```bash
# Get your session ID from browser cookies
# Then run:

curl -X POST https://your-instance.odoo.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "agent_id": 1,
      "message": "Hello! What can you help me with?",
      "session_id": "test_123"
    }
  }' \
  --cookie "session_id=YOUR_SESSION_ID"
```

## What's Next?

### Customize Your Agent

1. Go to **AI Agent > Agents > Your Agent**
2. Edit "System Prompt" to define behavior:

```
You are a customer service agent for [Your Company].

Your responsibilities:
- Answer customer inquiries
- Create support tickets
- Escalate urgent issues

Guidelines:
- Be friendly and professional
- Ask clarifying questions
- Provide step-by-step solutions
```

### Add More Agents

Create specialized agents for different tasks:

- **Sales Agent**: Qualify leads, create quotations
- **Support Agent**: Handle tickets, provide solutions
- **Project Agent**: Manage tasks, track progress
- **Analytics Agent**: Generate reports, analyze data

### Enable Autonomous Operation

1. Go to **Settings > Technical > Automation > Scheduled Actions**
2. Find "General Agent: Process Task Queue"
3. Ensure "Active" is checked
4. Set interval: `5 minutes`

Now your agent will automatically process queued tasks every 5 minutes!

### Add Custom Tools

1. Go to **AI Agent > Configuration** (requires System access)
2. Click "Tools" (if available) or contact admin
3. Create custom tools for your specific needs

## Troubleshooting

### "Module not found"
- Update apps list: **Apps > Update Apps List**
- Check module is in addons path
- Restart Odoo

### "API key invalid"
- Verify key at provider website
- Check for typos
- Ensure key has credits

### "Agent not responding"
- Check API key is configured
- Verify internet connectivity
- Check Odoo logs: `/var/log/odoo/odoo-server.log`

### "Task not executing"
- Ensure agent state is "Idle"
- Check cron job is active
- Try "Execute Now" button

## Cost Estimate

### Free Tier (Testing)

- **Odoo.sh**: Free trial (30 days)
- **Google Gemini**: Free (15 requests/min)
- **Total**: $0/month

### Production (Low Volume)

- **Odoo.com Starter**: $100/month
- **Google Gemini** (1,000 tasks/month): $5/month
- **Total**: $105/month

### Production (Medium Volume)

- **Odoo.com Standard**: $200/month
- **Google Gemini** (10,000 tasks/month): $50/month
- **Total**: $250/month

## Support

- **Documentation**: https://github.com/Gudmundur76/odoo-general-agent/blob/master/README.md
- **Deployment Guide**: https://github.com/Gudmundur76/odoo-general-agent/blob/master/DEPLOYMENT.md
- **Issues**: https://github.com/Gudmundur76/odoo-general-agent/issues
- **Discussions**: https://github.com/Gudmundur76/odoo-general-agent/discussions

## Next Steps

1. **Read full documentation**: [README.md](README.md)
2. **Explore use cases**: Customer service, sales, support, analytics
3. **Customize system prompt**: Define agent behavior
4. **Add custom tools**: Extend functionality
5. **Integrate external APIs**: Notus, Discovery, n8n, etc.
6. **Scale up**: Add more agents, increase capacity

**Congratulations! You now have a fully autonomous AI agent managing your Odoo operations.**

---

**Time to deploy**: 10 minutes  
**Cost to start**: $0 (free trial)  
**Time to value**: Immediate

*Built with ❤️ for the Odoo community*
