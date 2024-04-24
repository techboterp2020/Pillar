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
    vehicle_related = fields.Boolean(string='Vehicle Related')
    consignee_id = fields.Many2one('res.partner', string='Consignee')
    bl_no = fields.Char(string='BL/AWB/TWB No.')
    method_of_dispatch = fields.Char(string='Method of Dispatch')
    type_of_shipment = fields.Char(string='Type of Shipment')
    delivery_term = fields.Char('Delivery Term')
    country_final_destination = fields.Char(string='Country of Final Destination')
    transport_type = fields.Char(string='Vessel/Aircraft/Truck')
    voyage_no = fields.Char(string='Voyage No.')
    terms_method_payment = fields.Char('Terms/Method of payment')
    port_of_loading = fields.Char('Port of Loading')
    departure_date = fields.Date(string='Date of Departure')
    port_of_discharge = fields.Char(string='Port of Discharge')
    final_destination = fields.Char(string='Final Destination')
    marine_cover = fields.Char(string='Marine Cover Policy No.')
    letter_of_credit = fields.Char(string='Letter of Credit No.')

    @api.depends('partner_id')
    def _compute_custom_invoice_note(self):
        for order in self:
            order = order.with_company(order.company_id)
            if not is_html_empty(self.env.company.custom_invoice_terms):
                order.custom_invoice_note = order.with_context(lang=order.partner_id.lang).env.company.custom_invoice_terms

    def amount_in_words(self, amount):
        return num2words(amount)

    def get_product_lot(self, line_id):
        for rec in self:
            product_id = line_id.product_id
            sale_line_id = line_id.sale_line_ids
            if sale_line_id:
                lot_ids = sale_line_id.move_ids.lot_ids
                for lot in lot_ids:
                    return lot.model_year    

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