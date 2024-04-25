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
    partner_bank_id = fields.Many2one('res.partner.bank', string='Bank',domain="[('id', 'in', available_partner_bank_ids)]",)    

    available_partner_bank_ids = fields.Many2many(
        comodel_name='res.partner.bank',
        compute='_compute_available_partner_bank_ids',
    )
    partner_bank_id = fields.Many2one('res.partner.bank', string="Recipient Bank Account",
        readonly=False, store=True, tracking=True,
        domain="[('id', 'in', available_partner_bank_ids)]",
        check_company=True)

    
    @api.depends('partner_bank_id')
    def _compute_available_partner_bank_ids(self):
        for each in self:
            bank_ids = self.env['res.partner.bank'].search([('partner_id','=',each.company_id.partner_id.id)])
            if bank_ids:
                each.available_partner_bank_ids = bank_ids.ids
            else:
                each.available_partner_bank_ids = False    
  
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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'    

    year_of_production = fields.Char('Year of Production')            