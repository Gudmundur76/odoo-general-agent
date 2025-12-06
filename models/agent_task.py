# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AgentTask(models.Model):
    _name = 'general.agent.task'
    _description = 'Agent Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date asc'
    
    name = fields.Char('Task Name', compute='_compute_name', store=True)
    agent_id = fields.Many2one('general.agent', 'Agent', required=True, ondelete='cascade', tracking=True)
    session_id = fields.Char('Session ID', default='default', help="Session identifier for conversation context")
    
    task = fields.Text('Task Description', required=True, tracking=True)
    result = fields.Text('Result', readonly=True)
    
    state = fields.Selection([
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], default='queued', string='State', required=True, tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('5', 'Normal'),
        ('8', 'High'),
        ('10', 'Urgent')
    ], default='5', string='Priority', required=True, tracking=True)
    
    # Timestamps
    create_date = fields.Datetime('Created', readonly=True)
    start_date = fields.Datetime('Started', readonly=True)
    complete_date = fields.Datetime('Completed', readonly=True)
    
    # Execution info
    execution_time = fields.Float('Execution Time (seconds)', compute='_compute_execution_time', store=True)
    retry_count = fields.Integer('Retry Count', default=0, readonly=True)
    max_retries = fields.Integer('Max Retries', default=3)
    
    # User who created the task
    user_id = fields.Many2one('res.users', 'Created By', default=lambda self: self.env.user, readonly=True)
    
    @api.depends('task')
    def _compute_name(self):
        for record in self:
            if record.task:
                # Take first 50 characters of task as name
                record.name = record.task[:50] + '...' if len(record.task) > 50 else record.task
            else:
                record.name = 'New Task'
    
    @api.depends('start_date', 'complete_date')
    def _compute_execution_time(self):
        for record in self:
            if record.start_date and record.complete_date:
                delta = record.complete_date - record.start_date
                record.execution_time = delta.total_seconds()
            else:
                record.execution_time = 0.0
    
    @api.model
    def queue_task(self, agent_id, task, priority='5', session_id='default'):
        """Queue a task for the agent"""
        return self.create({
            'agent_id': agent_id,
            'task': task,
            'priority': priority,
            'session_id': session_id
        })
    
    def action_execute_now(self):
        """Execute this task immediately"""
        self.ensure_one()
        
        if self.state != 'queued':
            raise ValidationError(_("Only queued tasks can be executed"))
        
        try:
            self.write({
                'state': 'processing',
                'start_date': fields.Datetime.now()
            })
            
            result = self.agent_id.execute_task(self.task, self.session_id)
            
            self.write({
                'state': 'completed',
                'result': result,
                'complete_date': fields.Datetime.now()
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Task Completed'),
                    'message': _('Task executed successfully'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            self.write({
                'state': 'failed',
                'result': str(e),
                'complete_date': fields.Datetime.now()
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Task Failed'),
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_retry(self):
        """Retry a failed task"""
        self.ensure_one()
        
        if self.state != 'failed':
            raise ValidationError(_("Only failed tasks can be retried"))
        
        if self.retry_count >= self.max_retries:
            raise ValidationError(_("Maximum retry attempts reached"))
        
        self.write({
            'state': 'queued',
            'retry_count': self.retry_count + 1,
            'result': False
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Task Requeued'),
                'message': _('Task has been added back to the queue'),
                'type': 'info',
                'sticky': False,
            }
        }
    
    def action_cancel(self):
        """Cancel a queued task"""
        self.ensure_one()
        
        if self.state not in ['queued', 'processing']:
            raise ValidationError(_("Only queued or processing tasks can be cancelled"))
        
        self.write({
            'state': 'cancelled',
            'complete_date': fields.Datetime.now()
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Task Cancelled'),
                'message': _('Task has been cancelled'),
                'type': 'warning',
                'sticky': False,
            }
        }
