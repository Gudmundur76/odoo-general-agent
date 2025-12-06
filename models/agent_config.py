# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AgentConfig(models.Model):
    _name = 'general.agent.config'
    _description = 'Agent Configuration'
    _rec_name = 'name'
    
    name = fields.Char('Configuration Name', required=True, default='Default Configuration')
    active = fields.Boolean('Active', default=True)
    
    # LLM API Keys
    openai_api_key = fields.Char('OpenAI API Key', help="API key for GPT-4 and other OpenAI models")
    anthropic_api_key = fields.Char('Anthropic API Key', help="API key for Claude models")
    google_api_key = fields.Char('Google API Key', help="API key for Gemini models")
    
    # Local LLM Configuration
    local_llm_url = fields.Char('Local LLM URL', default='http://localhost:11434', help="URL for Ollama or other local LLM server")
    local_llm_model = fields.Char('Local LLM Model', default='llama3.1:70b', help="Model name for local LLM")
    
    # External API Configuration
    notus_api_url = fields.Char('Notus API URL', help="URL for Notus pharmaceutical intelligence API")
    notus_api_key = fields.Char('Notus API Key', help="API key for Notus")
    
    discovery_api_url = fields.Char('Discovery API URL', help="URL for Discovery drug discovery API")
    discovery_api_key = fields.Char('Discovery API Key', help="API key for Discovery")
    
    # n8n Webhook Configuration
    n8n_webhook_base_url = fields.Char('n8n Webhook Base URL', help="Base URL for n8n webhooks")
    
    # General Settings
    enable_web_search = fields.Boolean('Enable Web Search', default=True, help="Allow agent to search the web")
    enable_code_execution = fields.Boolean('Enable Code Execution', default=False, help="Allow agent to execute Python code (use with caution)")
    
    # Rate Limiting
    max_tasks_per_hour = fields.Integer('Max Tasks Per Hour', default=100, help="Maximum tasks the agent can process per hour")
    max_tokens_per_day = fields.Integer('Max Tokens Per Day', default=1000000, help="Maximum LLM tokens per day")
    
    # Logging and Monitoring
    log_level = fields.Selection([
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error')
    ], default='INFO', string='Log Level')
    
    enable_sentry = fields.Boolean('Enable Sentry', default=False, help="Enable Sentry error tracking")
    sentry_dsn = fields.Char('Sentry DSN', help="Sentry Data Source Name")
    
    # Security
    allowed_domains = fields.Text('Allowed Domains', help="Comma-separated list of domains the agent can access")
    blocked_domains = fields.Text('Blocked Domains', help="Comma-separated list of domains the agent cannot access")
    
    @api.model
    def get_config(self):
        """Get the active configuration"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            # Create default configuration
            config = self.create({
                'name': 'Default Configuration',
                'active': True
            })
        return config
    
    @api.constrains('openai_api_key', 'anthropic_api_key', 'google_api_key')
    def _check_api_keys(self):
        """Ensure at least one API key is configured"""
        for record in self:
            if not any([record.openai_api_key, record.anthropic_api_key, record.google_api_key, record.local_llm_url]):
                raise ValidationError(_("At least one LLM API key or local LLM URL must be configured"))
    
    def action_test_openai(self):
        """Test OpenAI API connection"""
        self.ensure_one()
        if not self.openai_api_key:
            raise ValidationError(_("OpenAI API key is not configured"))
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'Connection successful'"}],
                max_tokens=10
            )
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('OpenAI Connection Successful'),
                    'message': response.choices[0].message.content,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('OpenAI Connection Failed'),
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_test_anthropic(self):
        """Test Anthropic API connection"""
        self.ensure_one()
        if not self.anthropic_api_key:
            raise ValidationError(_("Anthropic API key is not configured"))
        
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.anthropic_api_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say 'Connection successful'"}]
            )
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Anthropic Connection Successful'),
                    'message': response.content[0].text,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Anthropic Connection Failed'),
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_test_google(self):
        """Test Google API connection"""
        self.ensure_one()
        if not self.google_api_key:
            raise ValidationError(_("Google API key is not configured"))
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.google_api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content("Say 'Connection successful'")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Google Connection Successful'),
                    'message': response.text,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Google Connection Failed'),
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }
