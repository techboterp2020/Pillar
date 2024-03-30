# -*- coding: utf-8 -*-

from odoo import models, fields, api
from num2words import num2words

from odoo.tools import is_html_empty


class AccountMove(models.Model):
    _inherit = 'account.move'

    mode_of_transport = fields.Char(string='Mode of Transport')
    mode_of_dispatch = fields.Char(string='Mode of Dispatch')
    total_product_weight = fields.Float(string='Total Product Weight', compute='get_total_product_weight')
    custom_invoice_note = fields.Html(
        string="Invoice Terms and conditions",
        compute='_compute_custom_invoice_note',
        store=True, readonly=False, precompute=True)

    @api.depends('partner_id')
    def _compute_custom_invoice_note(self):
        for order in self:
            order = order.with_company(order.company_id)
            if not is_html_empty(self.env.company.custom_invoice_terms):
                order.custom_invoice_note = order.with_context(lang=order.partner_id.lang).env.company.custom_invoice_terms

    def amount_in_words(self, amount):
        return num2words(amount)

    def get_country_origin(self, line_id):
        for rec in self:
            product_id = line_id.product_id
            sale_line_id = line_id.sale_line_ids
            if sale_line_id:
                lot_ids = sale_line_id.move_ids.lot_ids
                for lot in lot_ids:
                    return lot.make

    def get_lot_ids(self):
        for rec in self:
            line_ids = rec.invoice_line_ids
            for line in line_ids:
                sale_line_id = line.sale_line_ids
                if sale_line_id:
                    # lot_ids = sale_line_id.move_ids.lot_ids
                    move_ids = sale_line_id.move_ids
                    for move in move_ids:
                        picking_id = move.picking_id
                        if picking_id.picking_type_code == 'outgoing':
                            move_line_ids = picking_id.move_line_ids_without_package
                            if move_line_ids:
                                return move_line_ids

    def get_total_product_weight(self):
        for rec in self:
            total_weight = 0
            line_ids = rec.invoice_line_ids
            for line in line_ids:
                total_weight += line.product_id.weight * line.quantity
            rec.total_product_weight = total_weight