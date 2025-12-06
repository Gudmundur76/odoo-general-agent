# General AI Agent for Odoo

![License](https://img.shields.io/badge/license-LGPL--3.0-blue.svg)
![Odoo](https://img.shields.io/badge/Odoo-17.0-purple.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

A powerful, open-source AI agent that autonomously manages your Odoo business operations using LangChain and multiple LLM providers.

## Features

### 🤖 Multi-LLM Support
- **OpenAI GPT-4** (GPT-4 Turbo, GPT-4o, GPT-4o Mini)
- **Anthropic Claude** (Claude 3.5 Sonnet)
- **Google Gemini** (Gemini 2.0 Flash)
- **Local LLMs** (via Ollama)

### 🔧 Deep Odoo Integration
- **CRM**: Lead management, customer search, opportunity tracking
- **Sales**: Order processing, product catalog, invoicing
- **Projects**: Task management, timesheet tracking
- **Helpdesk**: Ticket resolution, knowledge base
- **Custom Tools**: Extensible tool system for any Odoo model

### ⚡ Autonomous Operation
- **Task Queue**: Priority-based task processing
- **Cron Jobs**: Automatic task execution every 5 minutes
- **Error Handling**: Automatic retry with configurable limits
- **Session Management**: Conversation context tracking

### 🎨 User Interface
- **Dashboard**: Real-time agent status and statistics
- **Chat Interface**: Natural language interaction via API
- **Kanban Views**: Visual task management
- **Analytics**: Success rates, execution times, performance metrics

### 🔒 Security & Privacy
- **Self-Hosted**: Full control over data and infrastructure
- **Iceland Hosting**: GDPR-compliant, sovereign hosting
- **API Key Management**: Secure credential storage
- **Access Control**: Role-based permissions

### 💰 Cost-Effective
- **No Per-User Fees**: One-time setup, unlimited users
- **Your Own API Keys**: Direct LLM access, no markup
- **Open Source**: Free to use, modify, and distribute
- **Low Infrastructure Cost**: ~$100-600/month total

## Installation

### Prerequisites

- Odoo 17.0 or later
- Python 3.8+
- PostgreSQL database

### Step 1: Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 2: Install Odoo Module

1. Copy the `odoo_general_agent` directory to your Odoo addons path:
   ```bash
   cp -r odoo_general_agent /path/to/odoo/addons/
   ```

2. Update Odoo apps list:
   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "General AI Agent"
   - Click "Install"

### Step 3: Configure API Keys

1. Go to **AI Agent > Configuration > Settings**
2. Enter your API keys:
   - **OpenAI**: Get from https://platform.openai.com/api-keys
   - **Anthropic**: Get from https://console.anthropic.com/
   - **Google**: Get from https://aistudio.google.com/app/apikey
3. Test connections using the "Test Connection" buttons
4. Save configuration

### Step 4: Create Your First Agent

1. Go to **AI Agent > Agents**
2. Click "Create"
3. Fill in:
   - **Name**: e.g., "Customer Service Agent"
   - **Default LLM**: Choose your preferred model (Gemini recommended for cost)
   - **System Prompt**: Define the agent's behavior
4. Click "Save"
5. Click "Test Agent" to verify it's working

## Usage

### Via User Interface

#### Queue a Task
1. Go to **AI Agent > Tasks**
2. Click "Create"
3. Select agent
4. Enter task description
5. Set priority
6. Click "Save"

The task will be automatically processed within 5 minutes.

#### Execute Immediately
1. Open a task
2. Click "Execute Now"

### Via API

#### Chat with Agent
```python
import requests

url = "https://your-odoo-instance.com/api/agent/chat"
data = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "agent_id": 1,
        "message": "Find all customers with email containing 'example.com'",
        "session_id": "user_123"
    }
}

response = requests.post(url, json=data, cookies={"session_id": "your_session"})
print(response.json())
```

#### Queue a Task
```python
url = "https://your-odoo-instance.com/api/agent/queue"
data = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "agent_id": 1,
        "task": "Create a sales order for customer ABC Corp",
        "priority": "8",
        "session_id": "automation_bot"
    }
}

response = requests.post(url, json=data, cookies={"session_id": "your_session"})
```

#### Get Agent Status
```python
url = "https://your-odoo-instance.com/api/agent/status"
data = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "agent_id": 1
    }
}

response = requests.post(url, json=data, cookies={"session_id": "your_session"})
```

### Via Python (Internal)

```python
# Get agent
agent = env['general.agent'].browse(1)

# Execute task directly
result = agent.execute_task("Find all high-priority leads")

# Queue task
task = env['general.agent.task'].queue_task(
    agent_id=agent.id,
    task="Process pending orders",
    priority='8'
)
```

## Customization

### Adding Custom Tools

1. Go to **AI Agent > Configuration > Tools** (requires System access)
2. Click "Create"
3. Fill in:
   - **Name**: `my_custom_tool` (snake_case)
   - **Display Name**: "My Custom Tool"
   - **Description**: What the tool does
   - **Tool Type**: Choose type
   - **Input Schema**: Define inputs as JSON
   - **Python Code**: Write tool logic

Example custom tool:
```python
# Tool: send_email
# Input Schema: {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}

mail = env['mail.mail'].create({
    'email_to': inputs['to'],
    'subject': inputs['subject'],
    'body_html': inputs['body']
})
mail.send()

result = f"Email sent to {inputs['to']}"
```

### Modifying System Prompt

The system prompt defines the agent's behavior. Edit it in the agent form view.

Example prompts:

**Customer Service Agent:**
```
You are a customer service agent for [Company Name].

Your responsibilities:
- Answer customer inquiries promptly and professionally
- Create support tickets for complex issues
- Escalate urgent matters to human staff
- Maintain a friendly, helpful tone

Guidelines:
- Always greet customers warmly
- Ask clarifying questions when needed
- Provide step-by-step solutions
- Follow up on unresolved issues
```

**Sales Agent:**
```
You are a sales agent for [Company Name].

Your responsibilities:
- Qualify leads based on budget, authority, need, timeline
- Create sales opportunities
- Generate quotations
- Follow up on pending orders

Guidelines:
- Be consultative, not pushy
- Understand customer needs first
- Recommend appropriate products
- Close deals when ready
```

## Architecture

### Components

```
odoo_general_agent/
├── models/
│   ├── general_agent.py      # Core agent logic
│   ├── agent_task.py          # Task queue management
│   ├── agent_config.py        # Configuration
│   └── agent_tool.py          # Tool registry
├── controllers/
│   └── main.py                # API endpoints
├── views/
│   ├── agent_views.xml        # Agent UI
│   ├── agent_task_views.xml   # Task UI
│   ├── agent_config_views.xml # Config UI
│   └── menu_views.xml         # Menu structure
├── security/
│   ├── ir.model.access.csv    # Access rights
│   └── security.xml           # Security groups
├── data/
│   └── cron_data.xml          # Cron jobs
└── __manifest__.py            # Module metadata
```

### Data Flow

```
User/API → Task Queue → Cron Job → Agent → LLM → Tools → Odoo Models → Result
```

### LLM Selection Strategy

The agent uses a multi-LLM approach:

1. **Gemini 2.0 Flash** (Default): Best cost/performance ratio
   - Cost: ~$0.0005 per task
   - Speed: ~2 seconds
   - Quality: Excellent for most tasks

2. **GPT-4o Mini**: Balanced option
   - Cost: ~$0.002 per task
   - Speed: ~3 seconds
   - Quality: Very good

3. **Claude 3.5 Sonnet**: Best for complex reasoning
   - Cost: ~$0.01 per task
   - Speed: ~4 seconds
   - Quality: Exceptional

4. **Local LLM**: Privacy-focused
   - Cost: Infrastructure only
   - Speed: Varies
   - Quality: Depends on model

## Cost Analysis

### Monthly Infrastructure Costs

| Component | Cost |
|-----------|------|
| Odoo.com (Starter) | $100 |
| LLM API (Gemini, 10K tasks) | $50 |
| **Total** | **$150/month** |

### Cost Per Task

| LLM | Cost per 1K tasks | Cost per 10K tasks |
|-----|-------------------|-------------------|
| Gemini 2.0 Flash | $0.50 | $5.00 |
| GPT-4o Mini | $2.00 | $20.00 |
| GPT-4o | $10.00 | $100.00 |
| Claude 3.5 Sonnet | $10.00 | $100.00 |
| Local LLM | $0 | $0 |

### Break-Even Analysis

- **Monthly cost**: $150
- **Break-even**: 1 customer at $299/month
- **Profitable from first sale**

## Use Cases

### 1. Customer Service Automation
- Respond to customer inquiries 24/7
- Create support tickets automatically
- Route complex issues to human agents
- Maintain conversation history

### 2. Sales Order Processing
- Qualify leads automatically
- Generate quotations
- Process orders
- Send follow-up emails

### 3. Project Management
- Create and assign tasks
- Update project status
- Generate progress reports
- Coordinate team activities

### 4. Business Intelligence
- Analyze sales data
- Generate reports
- Identify trends
- Provide insights

### 5. Biotech/Pharma Operations
- Patent search and analysis
- FDA data queries
- Clinical trial tracking
- Competitive intelligence
- Drug discovery workflows

## Deployment

### Odoo.sh Deployment

1. **Create Odoo.sh Project**
   ```bash
   # Push to GitHub first
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/odoo-general-agent.git
   git push -u origin main
   ```

2. **Connect to Odoo.sh**
   - Go to https://www.odoo.sh
   - Create new project
   - Connect GitHub repository
   - Select branch
   - Deploy

3. **Configure Production**
   - Set environment variables for API keys
   - Enable cron jobs
   - Configure backup strategy

### Self-Hosted Deployment

1. **Install Odoo**
   ```bash
   # Ubuntu/Debian
   wget -O - https://nightly.odoo.com/odoo.key | apt-key add -
   echo "deb http://nightly.odoo.com/17.0/nightly/deb/ ./" >> /etc/apt/sources.list.d/odoo.list
   apt-get update && apt-get install odoo
   ```

2. **Install Module**
   ```bash
   cp -r odoo_general_agent /usr/lib/python3/dist-packages/odoo/addons/
   systemctl restart odoo
   ```

3. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8069;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Troubleshooting

### Agent Not Executing Tasks

**Check:**
1. Cron job is active: **Settings > Technical > Automation > Scheduled Actions**
2. Agent state is "Idle"
3. API keys are configured correctly
4. Python dependencies are installed

### LLM Connection Errors

**Solutions:**
1. Test API keys: **Configuration > Settings > Test Connection**
2. Check API key validity at provider website
3. Verify network connectivity
4. Check Odoo logs: `/var/log/odoo/odoo-server.log`

### Task Execution Failures

**Debug:**
1. Check task result field for error message
2. Review agent execution logs
3. Test tool individually
4. Verify Odoo model permissions

### Performance Issues

**Optimize:**
1. Use Gemini instead of GPT-4 (10x cheaper, similar quality)
2. Reduce max_tokens setting
3. Implement caching for repeated queries
4. Use local LLM for high-volume tasks

## Roadmap

### v1.1 (Q1 2025)
- [ ] Voice interface (speech-to-text, text-to-speech)
- [ ] Multi-agent collaboration
- [ ] Advanced analytics dashboard
- [ ] Mobile app

### v1.2 (Q2 2025)
- [ ] Integration with external services (Slack, Teams, email)
- [ ] Workflow builder (visual automation designer)
- [ ] A/B testing for prompts
- [ ] Fine-tuning support

### v2.0 (Q3 2025)
- [ ] Self-learning capabilities
- [ ] Autonomous goal setting
- [ ] Multi-language support
- [ ] Enterprise features (SSO, audit logs)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/pippinlitli/odoo-general-agent.git
cd odoo-general-agent

# Install dependencies
pip3 install -r requirements.txt

# Run tests
python3 -m pytest tests/
```

## Support

- **Documentation**: https://github.com/pippinlitli/odoo-general-agent/wiki
- **Issues**: https://github.com/pippinlitli/odoo-general-agent/issues
- **Discussions**: https://github.com/pippinlitli/odoo-general-agent/discussions

## License

This project is licensed under the LGPL-3.0 License - see [LICENSE](LICENSE) file for details.

## Credits

**Author**: Pippin Litli  
**Website**: https://github.com/pippinlitli  
**Built with**: LangChain, Odoo, Python

## Acknowledgments

- **LangChain** for the agent framework
- **Odoo** for the business platform
- **OpenAI**, **Anthropic**, **Google** for LLM APIs
- **Open Source Community** for inspiration and support

---

**Made with ❤️ for the Odoo community**

*Democratizing AI automation for businesses worldwide*
