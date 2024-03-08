from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    engine_no = fields.Char(string="Engine No")
    chassis_no = fields.Char(string="Chassis No")
    key_no = fields.Char(string="Key No")
    model_year = fields.Char(string="Model Year")
    color_internal = fields.Char(string="Internal Color")
    color_external = fields.Char(string="External Color")
    make = fields.Char(string='Origin')
    bill_of_entry = fields.Char(string="BOE")
    bill_of_lading = fields.Char(string="BOL")

    engine_no_related = fields.Char(string="Engine No", related='lot_id.engine_no')
    chassis_no_related = fields.Char(string="Chassis No", related='lot_id.chassis_no')
    key_no_related = fields.Char(string="Key No", related='lot_id.key_no')
    model_year_related = fields.Char(string="Model Year", related='lot_id.model_year')
    color_internal_related = fields.Char(string="Internal Color", related='lot_id.color_internal')
    color_external_related = fields.Char(string="External Color", related='lot_id.color_external')
    make_related = fields.Char(string='Origin', related='lot_id.make')
    bill_of_entry_related = fields.Char(string="BOE", related='lot_id.bill_of_entry')
    bill_of_lading_related = fields.Char(string="BOL", related='lot_id.bill_of_lading')

    @api.model
    def _get_value_production_lot(self):
        res = super(StockMoveLine, self)._get_value_production_lot()
        res.update({
            'engine_no': self.engine_no,
            'chassis_no': self.chassis_no,
            'key_no': self.key_no,
            'model_year': self.model_year,
            'color_internal': self.color_internal,
            'make': self.make,
            'color_external': self.color_external,
            'bill_of_entry': self.bill_of_entry,
            'bill_of_lading': self.bill_of_lading,
        })
        return res

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        for line in self:
            line.lot_id.update({
                'engine_no': line.engine_no,
                'chassis_no': line.chassis_no,
                'key_no': line.key_no,
                'model_year': line.model_year,
                'color_internal': line.color_internal,
                'make': line.make,
                'color_external': line.color_external,
                'bill_of_entry': line.bill_of_entry,
                'bill_of_lading': line.bill_of_lading,
            })
            quants = line.lot_id.quant_ids.filtered(
                lambda q: q.quantity != 0 and q.location_id.usage in ['customer', 'internal', 'transit'])
            if quants:
                quants.update({
                    'engine_no': line.engine_no,
                    'chassis_no': line.chassis_no,
                    'key_no': line.key_no,
                    'model_year': line.model_year,
                    'color_internal': line.color_internal,
                    'make': line.make,
                    'color_external': line.color_external,
                    'bill_of_entry': line.bill_of_entry,
                    'bill_of_lading': line.bill_of_lading
                })
        return res


