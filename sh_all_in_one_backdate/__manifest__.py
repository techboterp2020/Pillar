# -*- coding: utf-8 -*-
# Part of Softhealer Technologies

{
    "name": "All In One Backdate - Basic | Sale Backdate | Purchase Backdate | Accounting Backdate | Invoice Backdate | Inventory Backdate",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Extra Tools",
    "summary": "Mass Backdate Sale order backdate Purchase order backdate Bill backdate Credit Note backdate Payment backdate Picking order backdate stock backdate inventory adjustment backdate stock operation backdate all stock back-date backdate Odoo",
    "description": """Our module is useful for confirm sales, purchase, accounting, MRP & inventory orders with selected confirmation backdate. You can put a custom backdate and remarks. You can mass assign backdate in one click. This selected date and remarks are also reflects in the stock moves, product moves & journal entries.""",
    "version": "16.0.1",
    "depends": ["stock_account", "purchase","sale_management" ],
    "data": [

        'sh_purchase_backdate/security/ir.model.access.csv',
        'sh_purchase_backdate/security/sh_purchase_backdate_groups.xml',
        'sh_purchase_backdate/data/purchase_order_data.xml',
        'sh_purchase_backdate/wizard/sh_mass_assign_backdate_wizard_views.xml',
        'sh_purchase_backdate/views/res_config_settings_views.xml',
        'sh_purchase_backdate/views/purchase_order_views.xml',
        'sh_purchase_backdate/views/account_move_views.xml',
        'sh_purchase_backdate/views/stock_picking_views.xml',
        'sh_purchase_backdate/views/stock_move_views.xml',
        'sh_purchase_backdate/views/stock_move_line_views.xml',


        'sh_sale_backdate/security/ir.model.access.csv',
        'sh_sale_backdate/security/sh_sale_backdate_groups.xml',
        'sh_sale_backdate/data/sale_order_data.xml',
        'sh_sale_backdate/wizard/sh_mass_assign_backdate_wizard_views.xml',
        'sh_sale_backdate/views/res_config_settings_views.xml',
        'sh_sale_backdate/views/sale_order_views.xml',
        'sh_sale_backdate/views/account_move_views.xml',
        'sh_sale_backdate/views/stock_picking_views.xml',
        'sh_sale_backdate/views/stock_move_views.xml',
        'sh_sale_backdate/views/stock_move_line_views.xml',

        'sh_stock_backdate/security/ir.model.access.csv',
        'sh_stock_backdate/security/sh_stock_backdate_groups.xml',
        'sh_stock_backdate/data/stock_picking_data.xml',
        'sh_stock_backdate/data/stock_scrap_data.xml',
        'sh_stock_backdate/wizard/sh_picking_backdate_wizard_views.xml',
        'sh_stock_backdate/wizard/sh_scrap_backdate_wizard_views.xml',
        'sh_stock_backdate/views/res_config_settings_views.xml',
        'sh_stock_backdate/views/stock_picking_views.xml',
        'sh_stock_backdate/views/stock_move_views.xml',
        'sh_stock_backdate/views/stock_scrap_views.xml',
        'sh_stock_backdate/views/stock_move_line_views.xml',

        'sh_account_backdate/security/ir.model.access.csv',
        'sh_account_backdate/security/sh_account_backdate_groups.xml',
        'sh_account_backdate/data/account_move_data.xml',
        'sh_account_backdate/data/account_payment_data.xml',
        'sh_account_backdate/wizard/sh_invoice_backdate_wizard_views.xml',
        'sh_account_backdate/wizard/sh_payment_backdate_wizard_views.xml',
        'sh_account_backdate/views/res_config_settings_views.xml',
        'sh_account_backdate/views/account_move_views.xml',
        'sh_account_backdate/views/account_payment_views.xml',
    ],

    "auto_install": False,
    "installable": True,
    "application": True,
    "images": ["static/description/background.png",],
    "license": "OPL-1",
    "price": 90,
    "currency": "EUR"
}
