# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from collections import defaultdict
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import ast
import json
import re
import warnings

#forbidden fields
INTEGRITY_HASH_MOVE_FIELDS = ('date', 'journal_id', 'company_id')
INTEGRITY_HASH_LINE_FIELDS = ('debit', 'credit', 'account_id', 'partner_id')


class InheritAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_reconciliation_partials(self, vals_list):
        mov = self.env["account.move"]
        vals = []
        if self._context.get("payment",False):
            movs = mov.browse(self._context['imp_ids'].get("inv_ids",[]))
            inv_val = self._context['imp_ids'].get("inv_val",[])
            remaing_amount = 0
            for mv in movs:
                lins = (self._context['imp_ids'].get("payment_lines",[]) + mv.line_ids)\
                        .filtered_domain(self._context['imp_ids'].get("pdomain",[]))
                lins = lins.sorted(key=lambda line: (line.date_maturity or line.date, line.currency_id))
                val = lins.get_new_prepare_reconciliation_partials()
                
                amt_to_pay = 0.0
                if inv_val[str(mv.id)]['amount_to_pay'] > mv.amount_residual:
                    amt_to_pay = mv.amount_residual
                    remaing_amount = inv_val[str(mv.id)]['amount_to_pay'] - mv.amount_residual
                elif inv_val[str(mv.id)]['amount_to_pay'] < mv.amount_residual \
                and remaing_amount >= (mv.amount_residual - inv_val[str(mv.id)]['amount_to_pay']):
                    amt_to_pay = mv.amount_residual
                    remaing_amount -= (mv.amount_residual - inv_val[str(mv.id)]['amount_to_pay'])
                else:
                    amt_to_pay = inv_val[str(mv.id)]['amount_to_pay']
                if amt_to_pay:
                    val[0]['amount'] = amt_to_pay
                    val[0]['debit_amount_currency'] = amt_to_pay
                    val[0]['credit_amount_currency'] = amt_to_pay
                vals.append(val[0])
            return vals
        res = super(InheritAccountMoveLine,self)._prepare_reconciliation_partials(vals_list)
        return res

    def get_new_prepare_reconciliation_partials(self):

        debit_lines = iter(self.filtered('debit'))
        credit_lines = iter(self.filtered('credit'))
        debit_line = None
        credit_line = None

        debit_amount_residual = 0.0
        debit_amount_residual_currency = 0.0
        credit_amount_residual = 0.0
        credit_amount_residual_currency = 0.0
        debit_line_currency = None
        credit_line_currency = None

        partials_vals_list = []

        while True:

            # Move to the next available debit line.
            if not debit_line:
                debit_line = next(debit_lines, None)
                if not debit_line:
                    break
                debit_amount_residual = debit_line.amount_residual

                if debit_line.currency_id:
                    debit_amount_residual_currency = debit_line.amount_residual_currency
                    debit_line_currency = debit_line.currency_id
                else:
                    debit_amount_residual_currency = debit_amount_residual
                    debit_line_currency = debit_line.company_currency_id

            # Move to the next available credit line.
            if not credit_line:
                credit_line = next(credit_lines, None)
                if not credit_line:
                    break
                credit_amount_residual = credit_line.amount_residual

                if credit_line.currency_id:
                    credit_amount_residual_currency = credit_line.amount_residual_currency
                    credit_line_currency = credit_line.currency_id
                else:
                    credit_amount_residual_currency = credit_amount_residual
                    credit_line_currency = credit_line.company_currency_id

            min_amount_residual = min(debit_amount_residual, -credit_amount_residual)

            if debit_line_currency == credit_line_currency:
                # Reconcile on the same currency.

                # The debit line is now fully reconciled.
                if debit_line_currency.is_zero(debit_amount_residual_currency) or debit_amount_residual_currency < 0.0:
                    debit_line = None
                    continue

                # The credit line is now fully reconciled.
                if credit_line_currency.is_zero(credit_amount_residual_currency) or credit_amount_residual_currency > 0.0:
                    credit_line = None
                    continue

                min_amount_residual_currency = min(debit_amount_residual_currency, -credit_amount_residual_currency)
                min_debit_amount_residual_currency = min_amount_residual_currency
                min_credit_amount_residual_currency = min_amount_residual_currency

            else:
                # Reconcile on the company's currency.

                # The debit line is now fully reconciled.
                if debit_line.company_currency_id.is_zero(debit_amount_residual) or debit_amount_residual < 0.0:
                    debit_line = None
                    continue

                # The credit line is now fully reconciled.
                if credit_line.company_currency_id.is_zero(credit_amount_residual) or credit_amount_residual > 0.0:
                    credit_line = None
                    continue

                min_debit_amount_residual_currency = credit_line.company_currency_id._convert(
                    min_amount_residual,
                    debit_line.currency_id,
                    credit_line.company_id,
                    credit_line.date,
                )
                min_credit_amount_residual_currency = debit_line.company_currency_id._convert(
                    min_amount_residual,
                    credit_line.currency_id,
                    debit_line.company_id,
                    debit_line.date,
                )

            debit_amount_residual -= min_amount_residual
            debit_amount_residual_currency -= min_debit_amount_residual_currency
            credit_amount_residual += min_amount_residual
            credit_amount_residual_currency += min_credit_amount_residual_currency

            partials_vals_list.append({
                'amount': min_amount_residual,
                'debit_amount_currency': min_debit_amount_residual_currency,
                'credit_amount_currency': min_credit_amount_residual_currency,
                'debit_move_id': debit_line.id,
                'credit_move_id': credit_line.id,
            })

        return partials_vals_list
