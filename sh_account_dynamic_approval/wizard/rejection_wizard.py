from odoo import api, fields, tools, models, _
from datetime import datetime


class RejectionReasonWizard(models.TransientModel):
    _inherit = 'sh.reject.reason.wizard'
    _description = "Reject Reason Wizard"

    # name = fields.Char(string="Reason", required=True)

    def action_reject_order(self):

        active_obj = self.env[self.env.context.get('active_model')].browse(
            self.env.context.get('active_id'))
        
        if self.env.context.get('active_model') == 'account.move':

            active_obj.write({
            'reject_reason': self.name,
            'reject_by': active_obj.env.user,
            'rejection_date': datetime.now(),
            'state': 'reject',
            })

            invoice_template_id = active_obj.env.ref(
                "sh_account_dynamic_approval.email_template_reject_invoice")

            bill_template_id = active_obj.env.ref(
                "sh_account_dynamic_approval.email_template_reject_bill")


            if invoice_template_id and active_obj.move_type == 'out_invoice':
                invoice_template_id.sudo().send_mail(active_obj.id, force_send=True, email_values={
                    'email_from': active_obj.env.user.email, 'email_to': active_obj.user_id.email})

            if bill_template_id and active_obj.move_type == 'in_invoice':
                bill_template_id.sudo().send_mail(active_obj.id, force_send=True, email_values={
                    'email_from': active_obj.env.user.email, 'email_to': active_obj.user_id.email})

            if active_obj.user_id:

                active_obj.env['bus.bus']._sendone(active_obj.user_id.partner_id, 'sh_notification_info', 
                    {'title': _('Notitification'),
                    'message': 'Dear User!! Your invoice is Rejected' if active_obj.move_type == 'out_invoice' else 'Dear User!! Your Bill is Rejected'
                    })

        return super(RejectionReasonWizard,self).action_reject_order()
