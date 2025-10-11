from odoo import api, fields, models
from odoo.tools import float_compare


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    engine_no = fields.Char(string="Engine No")
    chassis_no = fields.Char(string="Chassis No")
    key_no = fields.Char(string="Key No")
    model_year = fields.Char(string="Model Year")
    color_internal = fields.Char(string="Internal Color")
    color_external = fields.Char(string="External Color")
    make = fields.Char(string='Origin')
    bill_of_entry = fields.Char(string="BOE")
    bill_of_lading = fields.Char(string="BOL")

    @api.model
    def create(self, vals):
        """When a quant is created, copy values from lot (if any)."""
        quant = super().create(vals)
        if quant.lot_id:
            lot = quant.lot_id
            quant.write({
                'engine_no': lot.engine_no,
                'chassis_no': lot.chassis_no,
                'key_no': lot.key_no,
                'model_year': lot.model_year,
                'color_internal': lot.color_internal,
                'color_external': lot.color_external,
                'make': lot.make,
                'bill_of_entry': lot.bill_of_entry,
                'bill_of_lading': lot.bill_of_lading,
            })
        return quant

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


