# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import json

_logger = logging.getLogger(__name__)

try:
    from langchain.tools import StructuredTool
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class AgentTool(models.Model):
    _name = 'general.agent.tool'
    _description = 'Agent Tool'
    _order = 'sequence, name'
    
    name = fields.Char('Tool Name', required=True, help="Internal name (snake_case)")
    display_name = fields.Char('Display Name', required=True)
    description = fields.Text('Description', required=True, help="What this tool does")
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)
    
    tool_type = fields.Selection([
        ('odoo_crm', 'Odoo CRM'),
        ('odoo_sales', 'Odoo Sales'),
        ('odoo_project', 'Odoo Project'),
        ('odoo_helpdesk', 'Odoo Helpdesk'),
        ('external_api', 'External API'),
        ('web_search', 'Web Search'),
        ('custom_python', 'Custom Python')
    ], string='Tool Type', required=True)
    
    # For Odoo tools
    model_name = fields.Char('Odoo Model', help="e.g., res.partner, crm.lead")
    method_name = fields.Char('Method Name', help="e.g., search, create, write")
    
    # For external API tools
    api_url = fields.Char('API URL')
    api_method = fields.Selection([
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE')
    ], string='HTTP Method')
    api_headers = fields.Text('API Headers (JSON)', help="JSON object with headers")
    
    # For custom Python tools
    python_code = fields.Text('Python Code', help="Python function that will be executed")
    
    # Input schema
    input_schema = fields.Text('Input Schema (JSON)', help="JSON schema for tool inputs")
    
    # Usage statistics
    usage_count = fields.Integer('Usage Count', default=0, readonly=True)
    last_used = fields.Datetime('Last Used', readonly=True)
    
    @api.constrains('name')
    def _check_name(self):
        """Ensure tool name is valid Python identifier"""
        for record in self:
            if not record.name.replace('_', '').isalnum():
                raise ValidationError(_("Tool name must be alphanumeric with underscores only"))
    
    def get_langchain_tool(self):
        """Convert this tool to a LangChain StructuredTool"""
        self.ensure_one()
        
        if not LANGCHAIN_AVAILABLE:
            raise ValidationError(_("LangChain is not installed"))
        
        # Parse input schema
        try:
            schema_dict = json.loads(self.input_schema) if self.input_schema else {}
        except json.JSONDecodeError:
            schema_dict = {}
        
        # Create Pydantic model for inputs
        class ToolInput(BaseModel):
            pass
        
        # Add fields from schema
        for field_name, field_info in schema_dict.items():
            field_type = field_info.get('type', 'string')
            field_desc = field_info.get('description', '')
            
            if field_type == 'string':
                setattr(ToolInput, field_name, Field(default='', description=field_desc))
            elif field_type == 'integer':
                setattr(ToolInput, field_name, Field(default=0, description=field_desc))
            elif field_type == 'boolean':
                setattr(ToolInput, field_name, Field(default=False, description=field_desc))
        
        # Create tool function
        def tool_func(**kwargs):
            return self._execute_tool(kwargs)
        
        # Create LangChain tool
        return StructuredTool(
            name=self.name,
            description=self.description,
            func=tool_func,
            args_schema=ToolInput
        )
    
    def _execute_tool(self, inputs):
        """Execute the tool with given inputs"""
        self.ensure_one()
        
        # Update usage statistics
        self.sudo().write({
            'usage_count': self.usage_count + 1,
            'last_used': fields.Datetime.now()
        })
        
        try:
            if self.tool_type.startswith('odoo_'):
                return self._execute_odoo_tool(inputs)
            elif self.tool_type == 'external_api':
                return self._execute_api_tool(inputs)
            elif self.tool_type == 'web_search':
                return self._execute_web_search(inputs)
            elif self.tool_type == 'custom_python':
                return self._execute_python_tool(inputs)
            else:
                raise ValidationError(_("Unknown tool type: %s") % self.tool_type)
        except Exception as e:
            _logger.error(f"Tool {self.name} execution failed: {str(e)}")
            return f"Error: {str(e)}"
    
    def _execute_odoo_tool(self, inputs):
        """Execute Odoo model method"""
        if not self.model_name or not self.method_name:
            raise ValidationError(_("Model name and method name are required for Odoo tools"))
        
        model = self.env[self.model_name]
        method = getattr(model, self.method_name)
        
        # Execute method
        result = method(**inputs)
        
        # Convert result to JSON-serializable format
        if isinstance(result, models.Model):
            return json.dumps([{
                'id': r.id,
                'name': r.display_name
            } for r in result])
        else:
            return json.dumps(result)
    
    def _execute_api_tool(self, inputs):
        """Execute external API call"""
        import requests
        
        if not self.api_url:
            raise ValidationError(_("API URL is required"))
        
        # Parse headers
        headers = json.loads(self.api_headers) if self.api_headers else {}
        
        # Make API call
        if self.api_method == 'GET':
            response = requests.get(self.api_url, params=inputs, headers=headers)
        elif self.api_method == 'POST':
            response = requests.post(self.api_url, json=inputs, headers=headers)
        elif self.api_method == 'PUT':
            response = requests.put(self.api_url, json=inputs, headers=headers)
        elif self.api_method == 'DELETE':
            response = requests.delete(self.api_url, params=inputs, headers=headers)
        
        response.raise_for_status()
        return json.dumps(response.json())
    
    def _execute_web_search(self, inputs):
        """Execute web search"""
        try:
            from duckduckgo_search import DDGS
            query = inputs.get('query', '')
            max_results = inputs.get('max_results', 5)
            
            results = DDGS().text(query, max_results=max_results)
            return json.dumps(results)
        except ImportError:
            return "Error: duckduckgo-search not installed. Install with: pip install duckduckgo-search"
    
    def _execute_python_tool(self, inputs):
        """Execute custom Python code"""
        if not self.python_code:
            raise ValidationError(_("Python code is required"))
        
        # Create execution context
        context = {
            'env': self.env,
            'inputs': inputs,
            'json': json,
            '_logger': _logger
        }
        
        # Execute code
        exec(self.python_code, context)
        
        # Return result
        return context.get('result', 'No result returned')


# Pre-defined tools that will be created on module installation
PREDEFINED_TOOLS = [
    {
        'name': 'search_customers',
        'display_name': 'Search Customers',
        'description': 'Search for customers in CRM by name or email',
        'tool_type': 'custom_python',
        'input_schema': json.dumps({
            'query': {'type': 'string', 'description': 'Search query (name or email)'}
        }),
        'python_code': '''
partners = env['res.partner'].search([
    '|', ('name', 'ilike', inputs['query']),
    ('email', 'ilike', inputs['query'])
], limit=10)

result = json.dumps([{
    'id': p.id,
    'name': p.name,
    'email': p.email,
    'phone': p.phone,
    'company': p.company_name
} for p in partners])
'''
    },
    {
        'name': 'create_lead',
        'display_name': 'Create Lead',
        'description': 'Create a new lead in CRM',
        'tool_type': 'custom_python',
        'input_schema': json.dumps({
            'name': {'type': 'string', 'description': 'Lead name'},
            'email': {'type': 'string', 'description': 'Contact email'},
            'description': {'type': 'string', 'description': 'Lead description'}
        }),
        'python_code': '''
lead = env['crm.lead'].create({
    'name': inputs['name'],
    'email_from': inputs.get('email'),
    'description': inputs.get('description'),
    'user_id': env.user.id
})

result = f"Lead created with ID: {lead.id}"
'''
    },
    {
        'name': 'search_tickets',
        'display_name': 'Search Helpdesk Tickets',
        'description': 'Search for helpdesk tickets',
        'tool_type': 'custom_python',
        'input_schema': json.dumps({
            'query': {'type': 'string', 'description': 'Search query'}
        }),
        'python_code': '''
tickets = env['helpdesk.ticket'].search([
    '|', ('name', 'ilike', inputs['query']),
    ('description', 'ilike', inputs['query'])
], limit=10)

result = json.dumps([{
    'id': t.id,
    'name': t.name,
    'partner': t.partner_id.name if t.partner_id else '',
    'stage': t.stage_id.name if t.stage_id else '',
    'description': t.description or ''
} for t in tickets])
'''
    },
    {
        'name': 'web_search',
        'display_name': 'Web Search',
        'description': 'Search the web for information',
        'tool_type': 'web_search',
        'input_schema': json.dumps({
            'query': {'type': 'string', 'description': 'Search query'},
            'max_results': {'type': 'integer', 'description': 'Maximum number of results (default: 5)'}
        }),
        'python_code': ''
    }
]
