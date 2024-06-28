# -*- coding: utf-8 -*-
from odoo import api, fields, tools, models, _
from odoo.exceptions import UserError, ValidationError


class AccountApprovalConfig(models.Model):
    _name = 'sh.account.approval.config'
    _description = 'Account Approval Configuration'

    name = fields.Char()
    min_amount = fields.Float(string="Minimum Amount", required=True)
    company_ids = fields.Many2many(
        'res.company', string="Allowed Companies", default=lambda self: self.env.company)
    is_boolean = fields.Boolean(string="User Always in CC")
    account_approval_line = fields.One2many(
        'sh.account.approval.line', 'account_approval_config_id')

    @api.constrains('account_approval_line')
    def approval_line_level(self):
        if self.account_approval_line:
            levels = self.account_approval_line.mapped('level')
            if len(levels) != len(set(levels)):
                raise ValidationError('Levels must be different!!!')
