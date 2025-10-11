# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import api,models,fields
from odoo.exceptions import UserError
from odoo import fields, models, api, _ , Command
class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    payment_inv_ids = fields.One2many('payment.invoice.lines', 'payment_cus_id')
    has_invoice_lines = fields.Boolean(default=False)
    
    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        result = super(AccountPayment,self)._prepare_move_line_default_vals(write_off_line_vals)
        new_result = []
        if self.payment_inv_ids:
            for rec in result:
                if self.partner_type == 'customer':
                    if rec['debit']:
                        name = rec['name']
                        date_maturity = rec['date_maturity']
                        amount_currency = rec['amount_currency']
                        currency_id = rec['currency_id']
                        debit = True
                        credit = 0
                        partner_id = rec['partner_id']
                        account_id = rec['account_id']
                else:
                    if rec['credit']:
                        name = rec['name']
                        date_maturity = rec['date_maturity']
                        amount_currency = rec['amount_currency']
                        currency_id = rec['currency_id']
                        debit = 0
                        credit = True
                        partner_id = rec['partner_id']
                        account_id = rec['account_id'] 
                        
            my_result = {
            'name': name,
            'date_maturity': date_maturity,
            'amount_currency': amount_currency,
            'currency_id': currency_id,
            'debit': debit,
            'credit': credit,
            'partner_id': partner_id,
            'account_id': account_id,
            'exchange_rate': self.exchange_rate
            }

            [new_result.append({
                    'name': name,
                    'date_maturity': date_maturity,
                    'amount_currency': -pay.amount_to_pay if self.partner_type == 'customer' else pay.amount_to_pay,
                    'currency_id': currency_id,
                    'debit': 0 if self.partner_type == 'customer' else round(pay.amount_to_pay * self.exchange_rate,2) if self.currencies_are_different else pay.amount_to_pay,
                    'credit': 0 if self.partner_type == 'supplier' else round(pay.amount_to_pay * self.exchange_rate,2) if self.currencies_are_different else pay.amount_to_pay,
                    'partner_id': partner_id,
                    'account_id': self.destination_account_id.id,
                    'exchange_rate': self.exchange_rate,
                    'document_type_id': pay.invoice_id.l10n_latam_document_type_id.id,
                    'doc_number': pay.invoice_id.l10n_latam_document_number,
                    }) for pay in self.payment_inv_ids]
            
            total = round(sum([rec['debit'] if rec['debit'] else rec['credit'] for rec in new_result]),2)
            
            if my_result['debit']:
                my_result['debit'] = total
            else:
                my_result['credit'] = total
            
            new_result.append(my_result)
            
            return new_result
                
        else:
            return result
        
    
    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                if not self.payment_inv_ids:
                    if len(liquidity_lines) != 1:
                        raise UserError(_(
                            "Journal Entry %s is not valid. In order to proceed, the journal items must "
                            "include one and only one outstanding payments/receipts account.",
                            move.display_name,
                        ))

                    if len(counterpart_lines) != 1:
                        raise UserError(_(
                            "Journal Entry %s is not valid. In order to proceed, the journal items must "
                            "include one and only one receivable/payable account (with an exception of "
                            "internal transfers).",
                            move.display_name,
                        ))

                    if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                        raise UserError(_(
                            "Journal Entry %s is not valid. In order to proceed, the journal items must "
                            "share the same currency.",
                            move.display_name,
                        ))

                    if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                        raise UserError(_(
                            "Journal Entry %s is not valid. In order to proceed, the journal items must "
                            "share the same partner.",
                            move.display_name,
                        ))

                if counterpart_lines.account_id.account_type == 'asset_receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                if liquidity_amount > 0.0:
                    payment_vals_to_write.update({'payment_type': 'inbound'})
                elif liquidity_amount < 0.0:
                    payment_vals_to_write.update({'payment_type': 'outbound'})

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))
    
    def _synchronize_to_moves(self, changed_fields):
        ''' Update the account.move regarding the modified account.payment.
        :param changed_fields: A list containing all modified fields on account.payment.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        if not any(field_name in changed_fields for field_name in self._get_trigger_fields_to_synchronize()):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):
            liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

            # Make sure to preserve the write-off amount.
            # This allows to create a new payment with custom 'line_ids'.

            write_off_line_vals = []
            if liquidity_lines and counterpart_lines and writeoff_lines:
                write_off_line_vals.append({
                    'name': writeoff_lines[0].name,
                    'account_id': writeoff_lines[0].account_id.id,
                    'partner_id': writeoff_lines[0].partner_id.id,
                    'currency_id': writeoff_lines[0].currency_id.id,
                    'amount_currency': sum(writeoff_lines.mapped('amount_currency')),
                    'balance': sum(writeoff_lines.mapped('balance')),
                })

            line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)

            if self.payment_inv_ids:
                line_ids_commands = [
                    Command.update(liquidity_lines.id, line_vals_list[0]) if liquidity_lines else Command.create(line_vals_list[0])
                ]
                for i,rec in enumerate(counterpart_lines):
                    line_ids_commands.append(Command.update(rec.id, line_vals_list[i+1]))
            else:
                line_ids_commands = [
                    Command.update(liquidity_lines.id, line_vals_list[0]) if liquidity_lines else Command.create(line_vals_list[0]),
                    Command.update(counterpart_lines.id, line_vals_list[1]) if counterpart_lines else Command.create(line_vals_list[1])
                ]

                for line in writeoff_lines:
                    line_ids_commands.append((2, line.id))

                for extra_line_vals in line_vals_list[2:]:
                    line_ids_commands.append((0, 0, extra_line_vals))

            # Update the existing journal items.
            # If dealing with multiple write-off lines, they are dropped and a new one is generated.

            pay.move_id.write({
                'partner_id': pay.partner_id.id,
                'currency_id': pay.currency_id.id,
                'partner_bank_id': pay.partner_bank_id.id,
                'line_ids': line_ids_commands,
            })


class PaymentInvoiceLines(models.Model):
    _name = 'payment.invoice.lines'
    _description = 'Invoice Lines'
    
    payment_cus_id = fields.Many2one('account.payment')
    invoice_id = fields.Many2one('account.move',
        string="Invoice Numbers",readonly=True)
    partner_id = fields.Many2one('res.partner',string='Customer',
        related='invoice_id.partner_id', 
        store=True, readonly=True, related_sudo=False)
    currency_id = fields.Many2one("res.currency",string="Moneda",related="invoice_id.currency_id")
    amount_residual = fields.Monetary(related="invoice_id.amount_residual", string="Saldo")
    total_amount = fields.Float("Invoice Amount",readonly=True)
    amount_to_pay = fields.Float(string='Receive Amount',readonly=True)
    payment_diff = fields.Float(string='Residual Amount',readonly=True)
    