# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    bl_no = fields.Char(string='BL/AWB/TWB No.')
    consignee_id = fields.Many2one('res.partner', string='Consignee')
    method_of_dispatch = fields.Char(string='Method of Dispatch')
    type_of_shipment = fields.Char(string='Type of Shipment')
    country_origin_goods = fields.Char(string='Country of Origin of Goods')
    delivery_term = fields.Char('Delivery Term')
    country_final_destination = fields.Char(string='Country of Final Destination')
    transport_type = fields.Char(string='Vessel/Aircraft/Truck')
    voyage_no = fields.Char(string='Voyage No.')
    port_of_loading = fields.Char('Port of Loading')
    departure_date = fields.Date(string='Date of Departure')
    port_of_discharge = fields.Char(string='Port of Discharge')
    final_destination = fields.Char(string='Final Destination')
    packing_information = fields.Text(string='Packing Information')

    vehicle_related = fields.Boolean(string='Vehicle Related')
    ci_no = fields.Char(string="CI No.",compute='_compute_invoice_value')
    invoice_date = fields.Date(string="Date",compute='_compute_invoice_value')
    total_measurement = fields.Char('Total Measurement')
    
    @api.depends('sale_id')
    def _compute_invoice_value(self):
       for record in self:
        ci_no = False
        invoice_date = False
        if self.sale_id:
            if self.sale_id.invoice_ids:
                ci_no = self.sale_id.invoice_ids[0].name
                invoice_date = self.sale_id.invoice_ids[0].date
        self.ci_no = ci_no
        self.invoice_date = invoice_date       




class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    measurement = fields.Char(string='Measurement')
    net_weight = fields.Float(string='Net Weight')
    total_weight = fields.Float(string='Total Weight')
    remarks = fields.Char(string='Remarks')