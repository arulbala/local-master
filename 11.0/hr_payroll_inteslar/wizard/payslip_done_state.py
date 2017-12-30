# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class HrPayslipConfirm(models.TransientModel):
    """
    This wizard will confirm the all the selected draft payslips
    """

    _name = "hr.payslip.confirm"
    _description = "Confirm the selected Payslips"

    @api.multi
    def payslip_confirm(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['hr.payslip'].browse(active_ids):
            if record.state not in ('draft'):
                raise UserError(_("Selected Payslips(s) cannot be confirmed as they are not in 'Draft' state."))
            record.action_payslip_done()
        return {'type': 'ir.actions.act_window_close'}