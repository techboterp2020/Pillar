from odoo import models, fields, api


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    beneficiary = fields.Char(
        string='Beneficiary',
    )
    swift_code = fields.Char(
        string='UAE Swift Code',
    )
    iban_no = fields.Char(
        string='IBAN No',
    )