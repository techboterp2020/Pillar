# -*- coding: utf-8 -*-

from odoo import models, fields, api
from num2words import num2words

class AccountMove(models.Model):
    _inherit = 'account.move'

    mode_of_transport = fields.Char(string='Mode of Transport')
    mode_of_dispatch = fields.Char(string='Mode of Dispatch')
    total_product_weight = fields.Float(string='Total Product Weight', compute='get_total_product_weight')

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
                    lot_ids = sale_line_id.move_ids.lot_ids
                    if lot_ids:
                        return lot_ids

    def get_total_product_weight(self):
        for rec in self:
            total_weight = 0
            line_ids = rec.invoice_line_ids
            for line in line_ids:
                total_weight += line.product_id.weight * line.quantity
            rec.total_product_weight = total_weight