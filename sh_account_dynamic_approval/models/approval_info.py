from odoo import api, fields, tools, models, _


class ApprovalInfo(models.Model):
    _inherit = 'sh.approval.info'
    _description = "Approval Information"
    
    move_id = fields.Many2one('account.move')
