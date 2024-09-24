# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}

class MultiInvoicePayment(models.TransientModel):
    _name="customer.multi.payments"
    _description="Customer Multi Payments"

    memo = fields.Char(string='Memo')
    payment_date = fields.Date(required=True, default=fields.Date.context_today)
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money'), ('transfer', 'Internal Transfer')], string='Payment Type', required=True, readonly=True, default="outbound")
    journal_id = fields.Many2one('account.journal',required=True, domain=[('type', 'in', ('bank', 'cash'))])
    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Payment Method Type',store=True,readonly=False,
                                        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"
                                        "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n"
                                        "Check: Pay bill by check and print it from Odoo.\n"
                                        "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit, module account_batch_payment must be installed.\n"
                                        "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
    final_amount = fields.Float(string='Total Amount', \
        compute='_final_amount',store=True)
    is_customer = fields.Boolean(string="Is Customer")
    customer_invoice_ids = fields.One2many('customer.invoice.lines','customer_wizard_id')
    supplier_invoice_ids = fields.One2many('supplier.invoice.lines','supplier_wizard_id')
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')])

    operation_number = fields.Char('Num. Cheq./Oper.')
    date_payment_create = fields.Date("Fecha Creación",default=fields.Date.today)
    date_payment_due = fields.Date("Fecha de Vencimiento")
    hide_date_payment_due = fields.Boolean(default=False)
    sequence_id = fields.Many2one("ir.sequence",string="Secuencia Cheque")
    
    rate_date = fields.Date('Rate Date', default=lambda self: fields.Date.context_today(self))
    user_rate = fields.Boolean('User Rate')
    exchange_rate = fields.Float('Exchange Rate', digits=(12,6))
    # Extra fields 
    line_ids = fields.Many2many('account.move.line', 'customer_payment_register_move_line_rel', 'customer_wizard_id', 'customer_line_id',
        string="Journal items", readonly=True, copy=False,)

    @api.onchange('journal_id','payment_method_line_id')
    def _onchange_journal_id(self):
        for record in self:
            if record.partner_type == 'supplier':
                if record.journal_id.payment_method_line_id and  record.payment_method_line_id.payment_method_id and record.journal_id.payment_method_line_id.id == record.payment_method_line_id.payment_method_id.id:
                    if record.journal_id.sequence_check_id:
                        record.sequence_id = record.journal_id.sequence_check_id
                        record.operation_number = record.sequence_id.next_by_id()
                        record.date_payment_due = fields.Date.today()
                        record.hide_date_payment_due = False
                    else:
                        record.operation_number = False
                        record.sequence_id = False
                        record.date_payment_due = False
                        record.hide_date_payment_due = True
                else:
                    record.sequence_id = False
                    record.operation_number = False
                    record.date_payment_due = False
                    record.hide_date_payment_due = True
            else:
                record.date_payment_due = False
                record.hide_date_payment_due = True
               
    @api.onchange('payment_type', 'journal_id')
    def _onchange_payment_method_line_id(self):
        for wizard in self:
            if wizard.journal_id:
                available_payment_method_lines = wizard.journal_id._get_available_payment_method_lines(wizard.payment_type)
            else:
                available_payment_method_lines = False
            if available_payment_method_lines:
                return {'domain':{'payment_method_line_id':[('id','in',available_payment_method_lines.ids)]}}
            else:
                return {'domain':{'payment_method_line_id':[]}}
    @api.model
    def _compute_payment_amount(self, invoices, currency, journal, date=None):
        '''Compute the total amount for the payment wizard.

        :param invoices:    Invoices on which compute the total as an account.invoice recordset.
        :param currency:    The payment's currency as a res.currency record.
        :param journal:     The payment's journal as an account.journal record.
        :param date:        The payment's date as a datetime.date object.
        :return:            The total amount to pay the invoices.
        '''
        company = journal.company_id
        currency = currency or journal.currency_id or company.currency_id

        date = date or fields.Date.context_today

        if not invoices:
            return 0.0

        self.env['account.move'].flush_model(['move_type', 'currency_id'])
        self.env['account.move.line'].flush_model(['amount_residual', 'amount_residual_currency', 'move_id', 'account_id'])
        # self.env['account.account'].flush(['user_type_id'])
        # self.env['account.account.type'].flush(['type'])
        self._cr.execute('''
            SELECT
                move.move_type AS type,
                move.currency_id AS currency_id,
                SUM(line.amount_residual) AS amount_residual,
                SUM(line.amount_residual_currency) AS residual_currency
            FROM account_move move
            LEFT JOIN account_move_line line ON line.move_id = move.id
            LEFT JOIN account_account account ON account.id = line.account_id
            WHERE move.id IN %s
            AND account.account_type IN ('asset_receivable', 'liability_payable')
            GROUP BY move.id, move.move_type
        ''', [tuple(invoices.ids)])
        query_res = self._cr.dictfetchall()

        total = 0.0
        for res in query_res:
            move_currency = self.env['res.currency'].browse(res['currency_id'])
            if move_currency == currency and move_currency != company.currency_id:
                total += res['residual_currency']
            else:
                total += company.currency_id._convert(res['amount_residual'], currency, company, date)
        return total

    @api.depends("customer_invoice_ids","supplier_invoice_ids")
    def _final_amount(self):
        for amount in self:
            total = 0
            if amount.customer_invoice_ids:
                for i in amount.customer_invoice_ids:
                    total += i.amount_to_pay
                amount.update({
                    'final_amount' : total
                })
            if amount.supplier_invoice_ids:
                for i in amount.supplier_invoice_ids:
                    total += i.amount_to_pay
                amount.update({
                    'final_amount' : total
                })
                
            
    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if self.payment_type:
            return {'domain': {'payment_method_line_id': [('payment_type', '=', self.payment_type)]}}

    def _get_invoices(self):
        return self.env['account.move'].browse(self._context.get('active_ids',[]))

    @api.model
    def default_get(self, fields):

        res = super().default_get(fields)

        if 'line_ids' in fields and 'line_ids' not in res:
            if self._context.get('active_model') == 'account.move':
                lines = self.env['account.move'].browse(self._context.get('active_ids', [])).line_ids
            elif self._context.get('active_model') == 'account.move.line':
                lines = self.env['account.move.line'].browse(self._context.get('active_ids', []))
            else:
                raise UserError(_(
                    "The register payment wizard should only be called on account.move or account.move.line records."
                ))
            available_lines = self.env['account.move.line']
            for line in lines:
                if line.move_id.state != 'posted':
                    raise UserError(_("You can only register payment for posted journal entries."))

                # if line.account_internal_type not in ('receivable', 'payable'):
                if line.account_type not in ('asset_receivable', 'liability_payable'):
                    continue
                if line.currency_id:
                    if line.currency_id.is_zero(line.amount_residual_currency):
                        continue
                else:
                    if line.company_currency_id.is_zero(line.amount_residual):
                        continue
                available_lines |= line

            # Check.
            if not available_lines:
                raise UserError(_("You can't register a payment because there is nothing left to pay on the selected journal items."))
            if len(lines.company_id) > 1:
                raise UserError(_("You can't create payments for entries belonging to different companies."))
            # if len(set(available_lines.mapped('account_internal_type'))) > 1:
            if len(set(available_lines.mapped('account_type'))) > 1:
                raise UserError(_("You can't register payments for journal items being either all inbound, either all outbound."))
            res['line_ids'] = [(6, 0, available_lines.ids)]

        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        invoices = self.env[active_model].browse(active_ids)

        if any((invoice.state != 'posted' or invoice.payment_state not in ['not_paid','in_payment','partial']) for invoice in invoices):
            raise UserError(_("You can only register payments for posted"
                              " invoices"))

        if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.move_type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].move_type]
               for inv in invoices):
            raise UserError(_("You cannot mix customer invoices and vendor"
                              " bills in a single payment."))
            
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("In order to pay multiple invoices at once, they"
                              " must use the same currency."))

        rec = {}
        inv_list = []
        if MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].move_type] == 'customer':
            for inv in invoices:
                inv_list.append((0,0,{
                    'invoice_id' : inv.id,  
                    'partner_id' : inv.partner_id.commercial_partner_id.id,
                    'total_amount' : inv.amount_total or 0.0,
                    'payment_diff' : inv.amount_residual or 0.0,
                    'amount_to_pay' : inv.amount_residual or 0.0,
                    }))
            rec.update({'customer_invoice_ids':inv_list,'is_customer':True})
        if MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].move_type] == 'supplier':
            for inv in invoices:
                inv_list.append((0,0,{
                    'invoice_id' : inv.id,  
                    'partner_id' : inv.partner_id.commercial_partner_id.id,
                    'total_amount' : inv.amount_total or 0.0,
                    'payment_diff' : inv.amount_residual or 0.0,
                    'amount_to_pay' : inv.amount_residual or 0.0,
                    }))
            rec.update({'supplier_invoice_ids':inv_list,'is_customer':False})
            
        total_amount = sum(inv.amount_residual * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.move_type] for inv in invoices)
        
        amount = self._compute_payment_amount(invoices, invoices[0].currency_id, invoices[0].journal_id)
        rec.update({
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].move_type],
            'payment_type' : 'inbound' if amount > 0 else 'outbound',
        })
        res.update(rec)
        if invoices:
            res.update({
              'exchange_rate' : invoices[0].currency_id._get_conversion_rate(invoices[0].currency_id, self.env.company.currency_id,
                                                                       self.env.company, datetime.today())  
            })
        return res


    @api.model
    def _get_line_batch_key(self, line):
        ''' Turn the line passed as parameter to a dictionary defining on which way the lines
        will be grouped together.
        :return: A python dictionary.
        '''
        return {
            'partner_id': line.partner_id.id,
            'account_id': line.account_id.id,
            'currency_id': (line.currency_id or line.company_currency_id).id,
            'partner_bank_id': line.move_id.partner_bank_id.id,
            # 'partner_type': 'customer' if line.account_internal_type == 'receivable' else 'supplier',
            'partner_type': 'customer' if line.account_type == 'asset_receivable' else 'supplier',
            'payment_type': 'inbound' if line.balance > 0.0 else 'outbound',
        }

    def _get_batches(self):
        ''' Group the account.move.line linked to the wizard together.
        :return: A list of batches, each one containing:
            * key_values:   The key as a dictionary used to group the journal items together.
            * moves:        An account.move recordset.
        '''
        self.ensure_one()

        lines = self.line_ids

        if len(lines.company_id) > 1:
            raise UserError(_("You can't create payments for entries belonging to different companies."))
        if not lines:
            raise UserError(_("You can't open the register payment wizard without at least one receivable/payable line."))

        batches = {}
        for line in lines:
            batch_key = self._get_line_batch_key(line)

            serialized_key = '-'.join(str(v) for v in batch_key.values())
            batches.setdefault(serialized_key, {
                'key_values': batch_key,
                'lines': self.env['account.move.line'],
            })
            batches[serialized_key]['lines'] += line
        return list(batches.values())    

    def get_new_payment_vals(self,payment):
        invoices = self.env['account.move'].browse(payment['invoice_list'])
        if not self.user_rate and self.rate_date and invoices[0].currency_id:
            self.exchange_rate = invoices[0].currency_id._get_conversion_rate(invoices[0].currency_id, self.env.company.currency_id,
                                                                       self.env.company, self.rate_date)
        values = {            
            'date': self.payment_date,
            'amount': abs(payment['final_total']),
            'payment_type': self.payment_type,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].move_type],
            'ref':  " ".join(i.payment_reference or i.ref or i.name for i in invoices)+" "+(self.memo or ""),
            'journal_id': self.journal_id.id,
            'currency_id': invoices[0].currency_id.id,
            'partner_id': invoices[0].commercial_partner_id.commercial_partner_id.id,
            'partner_bank_id': invoices[0].partner_bank_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'date_payment_create': self.date_payment_create,
            'date_payment_due': self.date_payment_due,
            'operation_number': self.operation_number,
            'rate_date' : self.rate_date,
            'exchange_rate' : self.exchange_rate,
            'operation_number': self.operation_number,
            'has_invoice_lines': True,
            'payment_inv_ids': [(0,0, {'invoice_id':v['invoice_id'],
                                       'amount_to_pay':v['amount_to_pay'],
                                       'total_amount':v['total_amount'],
                                       'payment_diff':v['payment_diff']}) for v in payment['inv_val']]
        }
        return values                                                          

    def register_multi_payment(self):
        if self.customer_invoice_ids:
            for amount in self.customer_invoice_ids:
                if not amount.amount_to_pay > 0.0:
                    raise UserError(_("Amount must be strictly positive \n"
                                    "Enter Receive amount"))
        elif self.supplier_invoice_ids:
            for amount in self.supplier_invoice_ids:
                if not amount.amount_to_pay > 0.0:
                    raise UserError(_("Amount must be strictly positive \n"
                                    "Enter Receive amount"))
        else:
            raise UserError(_("Something vent wrong.... \n"))


        data = []
        context = {}
        
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        invoices = self.env[active_model].browse(active_ids)
        to_reconcile = []

        data = {}
        context = {}
        
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        invoices = self.env[active_model].browse(active_ids)
        to_reconcile = []

        if self.is_customer:
            for inv in self.customer_invoice_ids:
                context.update({'is_customer':True})
                inv.payment_diff = inv.invoice_id.amount_residual - inv.amount_to_pay
                partner_id = str(inv.invoice_id.partner_id.commercial_partner_id.id)

                if partner_id in data:
                    old_payment = data[partner_id]['final_total']
                    final_total = old_payment + inv.amount_to_pay
                    data[partner_id].update({
                                'partner_id': partner_id,
                                'final_total' : final_total,
                                'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[inv.invoice_id.move_type],
                                'payment_method_line_id': inv.payment_method_line_id,
                                'invoice_list' : data[partner_id]['invoice_list'] + [inv.invoice_id.id]
                                })
                    data[partner_id]['inv_val'].append({
                        'invoice_id': inv.invoice_id.id,
                        'amount_to_pay' : inv.amount_to_pay,
                        'total_amount' : inv.total_amount,
                        'payment_diff' : inv.payment_diff,
                        })
                else:
                    data.update({ partner_id : {
                        'invoice_id' : inv.id,
                        'partner_id' : inv.partner_id.commercial_partner_id.id,
                        'total_amount' : inv.total_amount,
                        'final_total' : inv.amount_to_pay,
                        'invoice_list' : [inv.invoice_id.id],
                        'inv_val' : [{
                            'invoice_id': inv.invoice_id.id,
                            'amount_to_pay' : inv.amount_to_pay,
                            'total_amount' : inv.total_amount,
                            'payment_diff' : inv.payment_diff,
                            }]
                        }
                        })
        else:
            for inv in self.supplier_invoice_ids:
                context.update({'is_customer':False})
                partner_id = str(inv.invoice_id.partner_id.commercial_partner_id.id)              
                if partner_id in data:
                    old_payment = data[partner_id]['final_total']
                    final_total = old_payment + inv.amount_to_pay
                    data[partner_id].update({
                                'partner_id': partner_id,
                                'final_total' : final_total,
                                'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[inv.invoice_id.move_type],
                                'payment_method_line_id': inv.payment_method_line_id,
                                'invoice_list' : data[partner_id]['invoice_list'] + [inv.invoice_id.id]
                                })
                    data[partner_id]['inv_val'].append({
                                'invoice_id': inv.invoice_id.id,
                                'amount_to_pay' : inv.amount_to_pay,
                                'total_amount' : inv.total_amount,
                                'payment_diff' : inv.payment_diff,
                        })
                else:
                    data.update({ partner_id : {
                        'invoice_id' : inv.id,
                        'partner_id' : inv.partner_id.commercial_partner_id.id,
                        'total_amount' : inv.total_amount,
                        'final_total' : inv.amount_to_pay,
                        'invoice_list' : [inv.invoice_id.id],
                        'inv_val' : [{
                            'invoice_id': inv.invoice_id.id,
                            'amount_to_pay' : inv.amount_to_pay,
                            'total_amount' : inv.total_amount,
                            'payment_diff' : inv.payment_diff,
                            }]
                        }})

        context.update({'payment':data})
        
        # domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
        domain = [('parent_state', '=', 'posted'), ('account_type', 'in', ('asset_receivable', 'liability_payable')),
                  ('reconciled', '=', False)]

        batches = self._get_batches()

        for lin in batches:
            to_reconcile.append(lin['lines'])

        payment_vals_list = []

        payment_model = {}
        payment_ids = self.env['account.payment']

        for payment in list(data):
            idss = self.env['account.payment'].create(self.get_new_payment_vals(data[payment]))
            payment_model[idss.id] = data[payment]
            payment_ids += idss
        
        payment_ids.action_post()
        
        new_to_reconcile = self.env['account.move.line']
        for rec in to_reconcile:
            new_to_reconcile |= rec
        
        for payment in payment_ids:
            payment_lines = payment.line_ids.filtered_domain(domain)
            for account in payment_lines.account_id:

                for mov_line in payment_lines:
                    (mov_line + new_to_reconcile).filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False),('doc_number','=',mov_line.doc_number),('partner_id','=',mov_line.partner_id.id)]).reconcile()


    @api.onchange('payment_date','rate_date')
    def _onchange_payment_date(self):
        for record in self:
            record.rate_date = record.payment_date
            invoice = False
            if record.partner_type == 'customer':
                invoice = record.customer_invoice_ids[0]
            else:
                invoice = record.supplier_invoice_ids[0]
            record.exchange_rate = invoice.currency_id._get_conversion_rate(invoice.currency_id, record.env.company.currency_id,
                                                                        record.env.company, record.payment_date)  
              


class InvoiceLines(models.TransientModel):
    _name = 'customer.invoice.lines'
    _description = 'Customer Invoice Lines'

    customer_wizard_id = fields.Many2one('customer.multi.payments')
    invoice_id = fields.Many2one('account.move',required=True,
        string="Invoice Numbers")
    partner_id = fields.Many2one('res.partner',string='Customer',
        related='invoice_id.partner_id', 
        store=True, readonly=True, related_sudo=False)
    currency_id = fields.Many2one("res.currency",string="Moneda",related="invoice_id.currency_id")
    amount_residual = fields.Monetary(related="invoice_id.amount_residual", string="Saldo")
    payment_method_line_id = fields.Many2one('account.payment.method.line',string='Payment Type')
    total_amount = fields.Float("Invoice Amount", required=True)
    amount_to_pay = fields.Float(string='Receive Amount')
    payment_diff = fields.Float(string='Residual Amount',store=True)

class InvoiceLines(models.TransientModel):
    _name = 'supplier.invoice.lines'
    _description = 'Supplier Invoice Lines'

    supplier_wizard_id = fields.Many2one('customer.multi.payments')
    invoice_id = fields.Many2one('account.move',required=True,
        string="Bill Numbers")
    partner_id = fields.Many2one('res.partner',string='Vendor',
        related='invoice_id.partner_id', 
        store=True, readonly=True, related_sudo=False)
    currency_id = fields.Many2one("res.currency",string="Moneda",related="invoice_id.currency_id")
    amount_residual = fields.Monetary(related="invoice_id.amount_residual", string="Saldo")
    payment_method_line_id = fields.Many2one('account.payment.method.line',string='Payment Type')
    total_amount = fields.Float("Invoice Amount", required=True)
    payment_diff = fields.Float(string='Residual Amount',store=True,readonly=True)
    amount_to_pay = fields.Float(string='Receive Amount')


