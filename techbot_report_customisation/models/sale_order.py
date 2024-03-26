# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from num2words import num2words

from odoo.tools import html_keep_url, is_html_empty


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    subject = fields.Text(string='Subject')
    custom_sale_note = fields.Html(
        string="Sale Terms and conditions",
        compute='_compute_custom_sale_note',
        store=True, readonly=False, precompute=True)

    @api.depends('partner_id')
    def _compute_custom_sale_note(self):
        for order in self:
            order = order.with_company(order.company_id)
            if not is_html_empty(self.env.company.custom_sale_terms):
                order.custom_sale_note = order.with_context(lang=order.partner_id.lang).env.company.custom_sale_terms

    def amount_in_words(self, amount):
        return num2words(amount)

    def get_product_lot(self, line_id):
        for rec in self:
            product_id = line_id.product_id
            lot_ids = line_id.move_ids.lot_ids
            for lot in lot_ids:
                return lot.model_year

    def get_country_origin(self, line_id):
        for rec in self:
            product_id = line_id.product_id
            lot_ids = line_id.move_ids.lot_ids
            for lot in lot_ids:
                return lot.make