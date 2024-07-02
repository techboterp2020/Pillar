from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

class MultiInvoicePayment(models.TransientModel):
    _inherit = "customer.multi.payments"
    
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
            idss.sh_to_reconcile = to_reconcile[0].filtered(lambda line:line.partner_id == idss.partner_id)
            payment_model[idss.id] = data[payment]
            payment_ids += idss
        
        payment_ids.action_post()
        
