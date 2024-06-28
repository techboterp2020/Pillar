# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    payment_method_line_id = fields.Many2one("account.payment.method",string="Método de Pago")
    sequence_id = fields.Many2one("ir.sequence",string="Secuencia Cheque")