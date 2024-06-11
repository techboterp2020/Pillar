# -*- coding: utf-8 -*-

{
    "name": "Account Dynamic Approval | Invoice Dynamic Approval | Bill Dynamic Approval | Invoice Approval Process | Bill Approval Process",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Accounting",
    "summary": "Dynamic Invoice Approval Dynamic Accounting Approval Invoice Multi Approval Bill Multiple Approval Invoice Double Approval User Wise Approval Group Wise Approval Invoice Workflow Approval Multi level Approval Invoice Multi level Validation Odoo",
    "description": """This module allows you to set dynamic and multi-level approvals in the invoice/bill so each invoice/bill can be approved by many levels. invoice/bill can be approved based on untaxed/ total amount and approved by particular users or groups they get emails notification about invoice/bill that waiting for approval. When an invoice/bill approves or rejects user gets a notification about it.""",
    "version": "16.0.1",
    "depends": ["sale_management","account", "bus","sh_base_dynamic_approval"],
    "data": [
        'security/ir.model.access.csv',
        'data/mail_data.xml',
        'wizard/rejection_wizard_views.xml',
        'views/account_approval_line_views.xml',
        'views/account_approval_config_views.xml',
        'views/res_config_setting_views.xml',
        'views/inherit_account_move_views.xml',
        'views/approval_info_views.xml'

    ],


    "auto_install": False,
    "installable": True,
    "application": True,
    "license": "OPL-1",
    "images": ["static/description/background.png", ],
    "price": 30,
    "currency": "EUR"
}
