# Deployment Guide: General AI Agent for Odoo

This guide walks you through deploying the General AI Agent module to Odoo.sh and Odoo.com.

## Prerequisites

- GitHub account (already connected)
- Odoo.sh account (create at https://www.odoo.sh)
- Odoo.com account (create at https://www.odoo.com)
- LLM API keys (OpenAI, Anthropic, or Google)

## Option 1: Deploy to Odoo.sh (Recommended for Development)

### Step 1: Create Odoo.sh Project

1. Go to https://www.odoo.sh
2. Click "Create a new project"
3. Fill in:
   - **Project name**: `ai-agent-platform`
   - **Odoo version**: 17.0
   - **Repository**: Connect to `https://github.com/Gudmundur76/odoo-general-agent`
4. Click "Create"

### Step 2: Configure Project

1. Go to **Settings > Branches**
2. Select `master` branch
3. Enable:
   - [x] Automatic deployment
   - [x] Install custom modules
   - [x] Run tests

### Step 3: Add Module to Build

Create `odoo.conf` in repository root:

```ini
[options]
addons_path = /home/odoo/src/user,/home/odoo/src/odoo/addons
```

Create `.odoo_sh/requirements.txt`:

```
langchain>=0.1.0
langchain-community>=0.0.20
langchain-openai>=0.0.5
langchain-anthropic>=0.1.0
langchain-google-genai>=0.0.6
openai>=1.10.0
anthropic>=0.18.0
google-generativeai>=0.3.0
requests>=2.31.0
pydantic>=2.0.0
duckduckgo-search>=4.0.0
```

Commit and push:

```bash
git add odoo.conf .odoo_sh/requirements.txt
git commit -m "Add Odoo.sh configuration"
git push origin master
```

### Step 4: Wait for Deployment

1. Go to **Builds** tab
2. Wait for build to complete (~5-10 minutes)
3. Click on build to see logs
4. Once complete, click "Connect" to access instance

### Step 5: Install Module

1. Log in to your Odoo.sh instance
2. Go to **Apps**
3. Click "Update Apps List"
4. Search for "General AI Agent"
5. Click "Install"

### Step 6: Configure API Keys

1. Go to **AI Agent > Configuration > Settings**
2. Enter your API keys:
   - OpenAI: `sk-...`
   - Anthropic: `sk-ant-...`
   - Google: `AIza...`
3. Click "Test Connection" for each
4. Save

### Step 7: Create First Agent

1. Go to **AI Agent > Agents**
2. Click "Create"
3. Fill in:
   - **Name**: "Customer Service Agent"
   - **Default LLM**: "Gemini 2.0 Flash"
   - **System Prompt**: (use default or customize)
4. Click "Save"
5. Click "Test Agent"

**Success!** Your agent is now running on Odoo.sh.

---

## Option 2: Deploy to Odoo.com (Recommended for Production)

### Step 1: Create Odoo.com Instance

1. Go to https://www.odoo.com/trial
2. Fill in:
   - **Company name**: Your company
   - **Apps**: Select "Custom"
3. Click "Start now"

### Step 2: Access Your Instance

1. Check your email for login credentials
2. Log in to your Odoo.com instance
3. Complete initial setup wizard

### Step 3: Install Module via Apps

**Note**: Odoo.com doesn't support custom modules directly. You have two options:

#### Option A: Request Custom Module Installation (Enterprise customers)

1. Contact Odoo support
2. Provide GitHub repository URL
3. Request module installation
4. Wait for approval (~1-2 business days)

#### Option B: Use Odoo.sh with Odoo.com Database

1. Deploy to Odoo.sh (see Option 1)
2. Use Odoo.sh instance as production
3. Configure custom domain
4. Set up SSL certificate

---

## Option 3: Self-Hosted Deployment

### Step 1: Install Odoo

**Ubuntu/Debian:**

```bash
# Add Odoo repository
wget -O - https://nightly.odoo.com/odoo.key | sudo apt-key add -
echo "deb http://nightly.odoo.com/17.0/nightly/deb/ ./" | sudo tee /etc/apt/sources.list.d/odoo.list

# Install Odoo
sudo apt-get update
sudo apt-get install odoo
```

### Step 2: Install Python Dependencies

```bash
sudo pip3 install -r requirements.txt
```

### Step 3: Install Module

```bash
# Clone repository
cd /tmp
git clone https://github.com/Gudmundur76/odoo-general-agent.git

# Copy to Odoo addons
sudo cp -r odoo-general-agent /usr/lib/python3/dist-packages/odoo/addons/

# Restart Odoo
sudo systemctl restart odoo
```

### Step 4: Configure Odoo

Edit `/etc/odoo/odoo.conf`:

```ini
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your_password
```

Restart Odoo:

```bash
sudo systemctl restart odoo
```

### Step 5: Install Module

1. Go to http://localhost:8069
2. Create database
3. Go to **Apps**
4. Click "Update Apps List"
5. Search for "General AI Agent"
6. Click "Install"

### Step 6: Configure Nginx (Optional)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## Post-Deployment Configuration

### 1. Set Up Cron Jobs

Ensure the cron job is active:

1. Go to **Settings > Technical > Automation > Scheduled Actions**
2. Find "General Agent: Process Task Queue"
3. Ensure "Active" is checked
4. Set interval to 5 minutes

### 2. Configure Security

1. Go to **Settings > Users & Companies > Groups**
2. Assign users to "General Agent / User" or "General Agent / Manager"

### 3. Set Up Monitoring (Optional)

If using Sentry:

1. Go to **AI Agent > Configuration > Settings**
2. Enable Sentry
3. Enter Sentry DSN
4. Save

### 4. Test API Endpoints

```bash
# Test chat endpoint
curl -X POST https://your-instance.odoo.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "agent_id": 1,
      "message": "Hello, can you help me?",
      "session_id": "test_123"
    }
  }' \
  --cookie "session_id=YOUR_SESSION_ID"
```

---

## Troubleshooting

### Module Not Appearing in Apps List

**Solution:**
1. Check module is in addons path
2. Update apps list: **Apps > Update Apps List**
3. Check Odoo logs: `/var/log/odoo/odoo-server.log`

### Python Dependencies Missing

**Solution:**
```bash
sudo pip3 install -r requirements.txt
sudo systemctl restart odoo
```

### API Keys Not Working

**Solution:**
1. Test keys directly at provider website
2. Check for typos in configuration
3. Verify API key has sufficient credits
4. Check Odoo logs for specific errors

### Cron Job Not Running

**Solution:**
1. Check cron is active: **Settings > Technical > Scheduled Actions**
2. Manually run: Click "Run Manually"
3. Check Odoo logs for errors
4. Verify agent state is "Idle"

### Performance Issues

**Solution:**
1. Use Gemini instead of GPT-4 (10x cheaper)
2. Reduce max_tokens setting
3. Implement caching (coming in v1.1)
4. Use local LLM for high-volume tasks

---

## Production Checklist

Before going live:

- [ ] All API keys configured and tested
- [ ] Cron job active and running
- [ ] Security groups assigned correctly
- [ ] Backup strategy implemented
- [ ] Monitoring configured (Sentry)
- [ ] SSL certificate installed
- [ ] Custom domain configured
- [ ] Rate limiting configured
- [ ] Test all critical workflows
- [ ] Documentation provided to team

---

## Support

- **GitHub Issues**: https://github.com/Gudmundur76/odoo-general-agent/issues
- **Documentation**: https://github.com/Gudmundur76/odoo-general-agent/wiki
- **Discussions**: https://github.com/Gudmundur76/odoo-general-agent/discussions

---

## Next Steps

1. **Create your first agent** - Follow the Quick Start guide
2. **Customize tools** - Add domain-specific tools
3. **Integrate with external APIs** - Connect Notus, Discovery, etc.
4. **Monitor performance** - Track success rates and execution times
5. **Scale up** - Add more agents for different departments

**Congratulations! Your General AI Agent is now deployed and ready to automate your business operations.**
