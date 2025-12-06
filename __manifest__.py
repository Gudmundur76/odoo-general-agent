# -*- coding: utf-8 -*-
{
    'name': 'General AI Agent',
    'version': '17.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Open Source General AI Agent for Odoo - Autonomous Business Operations',
    'description': """
General AI Agent for Odoo
==========================

A powerful, open-source AI agent that autonomously manages your Odoo operations.

Features:
---------
* Multi-LLM Support (GPT-4, Claude, Gemini, Local LLMs)
* Deep Odoo Integration (CRM, Sales, Projects, Helpdesk)
* Autonomous Task Processing
* Natural Language Chat Interface
* Customizable Tool Registry
* PostgreSQL-backed Memory System
* Real-time Dashboard and Analytics
* Task Queue with Priority Management
* External API Integration Support
* Comprehensive Error Handling and Logging

Use Cases:
----------
* Automated Customer Service
* Intelligent Lead Qualification
* Sales Order Processing
* Project Task Management
* Helpdesk Ticket Resolution
* Business Intelligence and Reporting
* Market Research and Analysis
* Workflow Automation

Perfect for:
------------
* Biotech/Pharma Companies
* E-commerce Businesses
* Professional Services
* Manufacturing Companies
* Any Odoo User Seeking AI Automation

Open Source:
------------
Licensed under LGPL-3.0
GitHub: https://github.com/pippinlitli/odoo-general-agent
Documentation: https://github.com/pippinlitli/odoo-general-agent/wiki

Cost-Effective:
---------------
* Uses your own LLM API keys
* No per-user licensing fees
* Full control over data and privacy
* Self-hostable in Iceland or anywhere

    """,
    'author': 'Pippin Litli',
    'website': 'https://github.com/pippinlitli/odoo-general-agent',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'crm',
        'sale_management',
        'project',
        'helpdesk',
    ],
    'external_dependencies': {
        'python': [
            'langchain',
            'langchain-openai',
            'langchain-anthropic',
            'langchain-google-genai',
            'langchain-community',
            'openai',
            'anthropic',
            'google-generativeai',
            'requests',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/cron_data.xml',
        'views/agent_views.xml',
        'views/agent_task_views.xml',
        'views/agent_config_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
    'price': 0.00,
    'currency': 'EUR',
}
