# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    bl_no = fields.Char(string='BL/AWB/TWB No.')
    consignee_id = fields.Many2one('res.partner', string='Consignee')
    method_of_dispatch = fields.Char(string='Method of Dispatch')
    type_of_shipment = fields.Char(string='Type of Shipment')
    country_origin_goods = fields.Char(string='Country of Origin of Goods')
    country_final_destination = fields.Char(string='Country of Final Destination')
    transport_type = fields.Char(string='Vessel/Aircraft/Truck')
    voyage_no = fields.Char(string='Voyage No.')
    port_of_loading = fields.Char('Port of Loading')
    departure_date = fields.Date(string='Date of Departure')
    port_of_discharge = fields.Char(string='Port of Discharge')
    final_destination = fields.Char(string='Final Destination')
    packing_information = fields.Text(string='Packing Information')

    vehicle_related = fields.Boolean(string='Vehicle Related')

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    measurement = fields.Char(string='Measurement')
    net_weight = fields.Float(string='Net Weight')
    total_weight = fields.Float(string='Total Weight')
    remarks = fields.Char(string='Remarks')