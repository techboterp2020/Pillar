from odoo import api, fields, models
from odoo.tools import float_compare


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    engine_no = fields.Char(string="Engine No",compute='_compute_lot_values', store=True)
    chassis_no = fields.Char(string="Chassis No",compute='_compute_lot_values', store=True)
    key_no = fields.Char(string="Key No",compute='_compute_lot_values', store=True)
    model_year = fields.Char(string="Model Year",compute='_compute_lot_values', store=True)
    color_internal = fields.Char(string="Internal Color",compute='_compute_lot_values', store=True)
    color_external = fields.Char(string="External Color",compute='_compute_lot_values', store=True)
    make = fields.Char(string='Origin',compute='_compute_lot_values', store=True)
    bill_of_entry = fields.Char(string="BOE",compute='_compute_lot_values', store=True)
    bill_of_lading = fields.Char(string="BOL",compute='_compute_lot_values', store=True)

    @api.depends('lot_id')
    def _compute_lot_values(self):
        for rec in self:
            if rec.lot_id:
                rec.engine_no = rec.lot_id.engine_no
                rec.chassis_no = rec.lot_id.chassis_no
                rec.key_no = rec.lot_id.key_no 
                rec.model_year = rec.lot_id.model_year
                rec.color_internal = rec.lot_id.color_internal
                rec.color_external = rec.lot_id.color_external
                rec.make = rec.lot_id.make
                rec.bill_of_entry = rec.lot_id.bill_of_entry 
                rec.bill_of_lading = rec.lot_id.bill_of_lading

            else:

                rec.engine_no = None
                rec.chassis_no = None
                rec.key_no = None
                rec.model_year = None
                rec.color_internal = None
                rec.color_external = None
                rec.make = None
                rec.bill_of_entry = None
                rec.bill_of_lading = None

    @api.model
    def _get_inventory_fields_write(self):
        fields = super(StockQuant, self)._get_inventory_fields_write()
        return fields + ['engine_no', 'chassis_no', 'key_no', 'model_year', 'color_internal', 'color_external', 'make',
                         'bill_of_entry', 'bill_of_lading']

    def action_apply_inventory(self):
        res = super(StockQuant, self).action_apply_inventory()
        for rec in self:
            if rec.lot_id:
                rec.lot_id.sudo().write({
                    'engine_no': rec.engine_no,
                    'chassis_no': rec.chassis_no,
                    'key_no': rec.key_no,
                    'model_year': rec.model_year,
                    'color_internal': rec.color_internal,
                    'color_external': rec.color_external,
                    'make': rec.make,
                    'bill_of_entry': rec.bill_of_entry,
                    'bill_of_lading': rec.bill_of_lading,
                })
        return res


