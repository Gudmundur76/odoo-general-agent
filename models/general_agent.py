# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import json
from datetime import datetime

_logger = logging.getLogger(__name__)

try:
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.chat_models import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.tools import StructuredTool
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.memory import ConversationBufferMemory
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except ImportError:
    _logger.warning("LangChain not installed. Please install: pip install langchain langchain-openai langchain-anthropic langchain-google-genai")
    LANGCHAIN_AVAILABLE = False


class GeneralAgent(models.Model):
    _name = 'general.agent'
    _description = 'General AI Agent'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    name = fields.Char('Agent Name', required=True, tracking=True)
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([
        ('idle', 'Idle'),
        ('thinking', 'Thinking'),
        ('executing', 'Executing'),
        ('waiting', 'Waiting'),
        ('error', 'Error')
    ], default='idle', string='State', tracking=True)
    
    # Configuration
    default_llm = fields.Selection([
        ('gpt4', 'GPT-4 Turbo'),
        ('gpt4o', 'GPT-4o'),
        ('gpt4o_mini', 'GPT-4o Mini'),
        ('claude', 'Claude 3.5 Sonnet'),
        ('gemini', 'Gemini 2.0 Flash'),
        ('local', 'Local LLM (Ollama)')
    ], default='gemini', string='Default LLM', required=True)
    
    temperature = fields.Float('Temperature', default=0.7, help="Controls randomness (0-1)")
    max_iterations = fields.Integer('Max Iterations', default=10, help="Maximum agent iterations per task")
    max_tokens = fields.Integer('Max Tokens', default=4000, help="Maximum tokens per response")
    
    # System Prompt
    system_prompt = fields.Text('System Prompt', default=lambda self: self._default_system_prompt())
    
    # Statistics
    current_task = fields.Text('Current Task', readonly=True)
    last_result = fields.Text('Last Result', readonly=True)
    total_tasks_completed = fields.Integer('Tasks Completed', default=0, readonly=True)
    total_tasks_failed = fields.Integer('Tasks Failed', default=0, readonly=True)
    total_execution_time = fields.Float('Total Execution Time (seconds)', default=0.0, readonly=True)
    average_execution_time = fields.Float('Average Execution Time (seconds)', compute='_compute_average_time', store=True)
    success_rate = fields.Float('Success Rate (%)', compute='_compute_success_rate', store=True)
    
    # Relations
    task_ids = fields.One2many('general.agent.task', 'agent_id', string='Tasks')
    config_id = fields.Many2one('general.agent.config', string='Configuration', ondelete='restrict')
    
    # Timestamps
    last_execution_date = fields.Datetime('Last Execution', readonly=True)
    
    @api.depends('total_tasks_completed', 'total_execution_time')
    def _compute_average_time(self):
        for agent in self:
            if agent.total_tasks_completed > 0:
                agent.average_execution_time = agent.total_execution_time / agent.total_tasks_completed
            else:
                agent.average_execution_time = 0.0
    
    @api.depends('total_tasks_completed', 'total_tasks_failed')
    def _compute_success_rate(self):
        for agent in self:
            total = agent.total_tasks_completed + agent.total_tasks_failed
            if total > 0:
                agent.success_rate = (agent.total_tasks_completed / total) * 100
            else:
                agent.success_rate = 0.0
    
    def _default_system_prompt(self):
        return """You are a General AI Agent managing business operations in Odoo.

Your role is to:
1. Manage customer relationships (CRM)
2. Process sales orders
3. Handle support tickets
4. Coordinate projects and tasks
5. Generate business insights and reports
6. Automate workflows

You have access to:
- Odoo CRM (leads, opportunities, customers)
- Odoo Sales (orders, products, invoices)
- Odoo Projects (tasks, issues, timesheets)
- Odoo Helpdesk (tickets, knowledge base)
- Web search capabilities
- External APIs (when configured)

Guidelines:
- Be proactive and efficient
- Always act in the best interest of the business
- Provide clear explanations for your actions
- Ask for clarification when needed
- Log all important decisions
- Escalate to humans when appropriate

Remember: You are an assistant, not a replacement for human judgment."""
    
    def _get_llm(self, model_type=None):
        """Get LLM instance based on configuration"""
        if not LANGCHAIN_AVAILABLE:
            raise UserError(_("LangChain is not installed. Please install required dependencies."))
        
        self.ensure_one()
        model = model_type or self.default_llm
        config = self.config_id or self.env['general.agent.config'].get_config()
        
        try:
            if model == 'gpt4':
                return ChatOpenAI(
                    model_name="gpt-4-turbo-preview",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=config.openai_api_key
                )
            elif model == 'gpt4o':
                return ChatOpenAI(
                    model_name="gpt-4o",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=config.openai_api_key
                )
            elif model == 'gpt4o_mini':
                return ChatOpenAI(
                    model_name="gpt-4o-mini",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=config.openai_api_key
                )
            elif model == 'claude':
                return ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=config.anthropic_api_key
                )
            elif model == 'gemini':
                return ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    google_api_key=config.google_api_key
                )
            elif model == 'local':
                from langchain.llms import Ollama
                return Ollama(
                    model=config.local_llm_model or "llama3.1:70b",
                    base_url=config.local_llm_url or "http://localhost:11434"
                )
            else:
                raise ValidationError(_("Unknown LLM model: %s") % model)
        except Exception as e:
            _logger.error(f"Error initializing LLM {model}: {str(e)}")
            raise UserError(_("Failed to initialize LLM: %s") % str(e))
    
    def _get_tools(self):
        """Get all available tools for the agent"""
        self.ensure_one()
        tools = []
        
        # Get custom tools from agent_tool model
        custom_tools = self.env['general.agent.tool'].search([('active', '=', True)])
        for tool in custom_tools:
            tools.append(tool.get_langchain_tool())
        
        return tools
    
    def _create_agent_executor(self):
        """Create LangChain agent executor"""
        self.ensure_one()
        
        llm = self._get_llm()
        tools = self._get_tools()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(llm, tools, prompt)
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            max_iterations=self.max_iterations,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def execute_task(self, task, session_id='default'):
        """Execute a task using the agent"""
        self.ensure_one()
        
        if not LANGCHAIN_AVAILABLE:
            raise UserError(_("LangChain is not installed. Cannot execute tasks."))
        
        start_time = datetime.now()
        
        # Update state
        self.write({
            'state': 'thinking',
            'current_task': task
        })
        
        try:
            # Create agent executor
            self.write({'state': 'executing'})
            agent_executor = self._create_agent_executor()
            
            # Execute task
            result = agent_executor.invoke({"input": task})
            output = result.get('output', '')
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self.write({
                'state': 'idle',
                'last_result': output,
                'total_tasks_completed': self.total_tasks_completed + 1,
                'total_execution_time': self.total_execution_time + execution_time,
                'last_execution_date': fields.Datetime.now()
            })
            
            # Log success
            self.message_post(
                body=_("Task completed successfully in %.2f seconds") % execution_time,
                subject=_("Task Execution Success")
            )
            
            return output
            
        except Exception as e:
            error_msg = str(e)
            _logger.error(f"Agent task execution failed: {error_msg}")
            
            # Update statistics
            self.write({
                'state': 'error',
                'last_result': f"Error: {error_msg}",
                'total_tasks_failed': self.total_tasks_failed + 1
            })
            
            # Log error
            self.message_post(
                body=_("Task execution failed: %s") % error_msg,
                subject=_("Task Execution Error"),
                message_type='notification'
            )
            
            raise UserError(_("Task execution failed: %s") % error_msg)
    
    def action_test_agent(self):
        """Test the agent with a simple task"""
        self.ensure_one()
        
        test_task = "Hello! Please introduce yourself and list the tools you have access to."
        
        try:
            result = self.execute_task(test_task)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Agent Test Successful'),
                    'message': result[:200] + '...' if len(result) > 200 else result,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Agent Test Failed'),
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_reset_statistics(self):
        """Reset agent statistics"""
        self.ensure_one()
        self.write({
            'total_tasks_completed': 0,
            'total_tasks_failed': 0,
            'total_execution_time': 0.0,
            'last_result': False,
            'current_task': False
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Statistics Reset'),
                'message': _('Agent statistics have been reset'),
                'type': 'info',
                'sticky': False,
            }
        }
    
    @api.model
    def cron_process_queue(self):
        """Cron job to process queued tasks"""
        agents = self.search([('active', '=', True), ('state', '=', 'idle')])
        
        for agent in agents:
            # Get next task from queue
            task = self.env['general.agent.task'].search([
                ('state', '=', 'queued'),
                ('agent_id', '=', agent.id)
            ], limit=1, order='priority desc, create_date asc')
            
            if task:
                try:
                    task.write({'state': 'processing'})
                    result = agent.execute_task(task.task, task.session_id)
                    task.write({
                        'state': 'completed',
                        'result': result,
                        'complete_date': fields.Datetime.now()
                    })
                except Exception as e:
                    task.write({
                        'state': 'failed',
                        'result': str(e),
                        'complete_date': fields.Datetime.now()
                    })
                    _logger.error(f"Task {task.id} failed: {str(e)}")
