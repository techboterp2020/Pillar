# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import is_html_empty


class ResCompany(models.Model):
    _inherit = 'res.company'

    bank_details = fields.Char(string='Bank Details')
    bank_address = fields.Char(string='Bank Address')
    swift_code = fields.Char(string='UAE Swift Code')
    account_no = fields.Char(string='Account No.')
    iban_no = fields.Char(string='IBAN No.')
    # po_box_no = fields.Char(string='Po Box')
    custom_sale_terms = fields.Html(string='Default Sale Terms and Conditions', translate=True)
    custom_invoice_terms = fields.Html(string='Default Invoice Terms and Conditions', translate=True)
    enable_logo = fields.Boolean(string='Enable Logo')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    custom_sale_terms = fields.Html(related='company_id.custom_sale_terms', string="Sale Terms & Conditions", readonly=False)
    custom_invoice_terms = fields.Html(related='company_id.custom_invoice_terms', string="Invoice Terms & Conditions", readonly=False)


