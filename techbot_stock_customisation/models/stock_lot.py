from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = 'stock.lot'

    engine_no = fields.Char(string="Engine No")
    chassis_no = fields.Char(string="Chassis No")
    key_no = fields.Char(string="Key No")
    model_year = fields.Char(string="Model Year")
    color_internal = fields.Char(string="Internal Color")
    color_external = fields.Char(string="External Color")
    make = fields.Char( string='Origin')
    bill_of_entry = fields.Char(string="BOE")
    bill_of_lading = fields.Char(string="BOL")
