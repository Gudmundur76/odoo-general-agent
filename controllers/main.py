# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class GeneralAgentController(http.Controller):
    
    @http.route('/api/agent/chat', type='json', auth='user', methods=['POST'], csrf=False)
    def agent_chat(self, agent_id, message, session_id='default'):
        """
        Chat with the agent via API
        
        Args:
            agent_id: ID of the agent
            message: User message
            session_id: Session identifier for conversation context
            
        Returns:
            dict with 'response' and 'status'
        """
        try:
            agent = request.env['general.agent'].browse(agent_id)
            
            if not agent.exists():
                return {
                    'status': 'error',
                    'error': 'Agent not found'
                }
            
            # Execute task
            response = agent.execute_task(message, session_id)
            
            return {
                'status': 'success',
                'response': response,
                'agent_id': agent_id,
                'session_id': session_id
            }
            
        except Exception as e:
            _logger.error(f"Agent chat error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @http.route('/api/agent/queue', type='json', auth='user', methods=['POST'], csrf=False)
    def queue_task(self, agent_id, task, priority='5', session_id='default'):
        """
        Queue a task for the agent
        
        Args:
            agent_id: ID of the agent
            task: Task description
            priority: Task priority (0-10)
            session_id: Session identifier
            
        Returns:
            dict with task_id and status
        """
        try:
            agent_task = request.env['general.agent.task'].queue_task(
                agent_id=agent_id,
                task=task,
                priority=priority,
                session_id=session_id
            )
            
            return {
                'status': 'success',
                'task_id': agent_task.id,
                'message': 'Task queued successfully'
            }
            
        except Exception as e:
            _logger.error(f"Queue task error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @http.route('/api/agent/status', type='json', auth='user', methods=['GET'], csrf=False)
    def agent_status(self, agent_id):
        """
        Get agent status
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            dict with agent status and statistics
        """
        try:
            agent = request.env['general.agent'].browse(agent_id)
            
            if not agent.exists():
                return {
                    'status': 'error',
                    'error': 'Agent not found'
                }
            
            return {
                'status': 'success',
                'agent': {
                    'id': agent.id,
                    'name': agent.name,
                    'state': agent.state,
                    'current_task': agent.current_task,
                    'tasks_completed': agent.total_tasks_completed,
                    'tasks_failed': agent.total_tasks_failed,
                    'success_rate': agent.success_rate,
                    'average_execution_time': agent.average_execution_time
                }
            }
            
        except Exception as e:
            _logger.error(f"Agent status error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @http.route('/api/agent/list', type='json', auth='user', methods=['GET'], csrf=False)
    def list_agents(self):
        """
        List all active agents
        
        Returns:
            dict with list of agents
        """
        try:
            agents = request.env['general.agent'].search([('active', '=', True)])
            
            return {
                'status': 'success',
                'agents': [{
                    'id': agent.id,
                    'name': agent.name,
                    'state': agent.state,
                    'default_llm': agent.default_llm,
                    'tasks_completed': agent.total_tasks_completed,
                    'success_rate': agent.success_rate
                } for agent in agents]
            }
            
        except Exception as e:
            _logger.error(f"List agents error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @http.route('/api/agent/tools', type='json', auth='user', methods=['GET'], csrf=False)
    def list_tools(self):
        """
        List all available tools
        
        Returns:
            dict with list of tools
        """
        try:
            tools = request.env['general.agent.tool'].search([('active', '=', True)])
            
            return {
                'status': 'success',
                'tools': [{
                    'id': tool.id,
                    'name': tool.name,
                    'display_name': tool.display_name,
                    'description': tool.description,
                    'tool_type': tool.tool_type,
                    'usage_count': tool.usage_count
                } for tool in tools]
            }
            
        except Exception as e:
            _logger.error(f"List tools error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
