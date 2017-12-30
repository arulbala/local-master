# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import math

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
from werkzeug import url_encode
from odoo.tools import float_compare
from odoo.tools.translate import _
from datetime import datetime


_logger = logging.getLogger(__name__)


class HrEmployeeGratuityWizard(models.TransientModel):

    _name = "hr.employee.gratuity.wizard"
    _description = "Hr Employee Gratuity Wizard"

    @api.model
    def _default_partner_id(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        payslip = self.env['hr.payslip'].browse(active_ids)
        return payslip.employee_id.id

    @api.model
    def _compute_one_day_salary_method(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        payslip = self.env['hr.payslip'].browse(active_ids)
        one_day_salary = 0.0
        for line in payslip:
            one_day_salary = float(line.contract_id.wage) *12 / 365
            return float(one_day_salary)

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=_default_partner_id)
    employee_join_date = fields.Date(related='employee_id.date_of_join', string='Date of Joining', readonly=True, required=True)
    employee_left_date = fields.Date(related='employee_id.date_of_left', string='Date of Leaving', readonly=True, required=True)
    length_of_service = fields.Integer(string='Length Of Services', required=True, compute='compute_length_of_service')
    amount = fields.Float(string='Payment Amount', compute='compute_payment_value')
    one_day_salary = fields.Float('One Day Salary', default=_compute_one_day_salary_method)
    contract_type = fields.Selection([('limited','Limited'),('unlimited', 'Unlimited')],related='employee_id.contract_type', string="Contract Type")
    manual_amount = fields.Float('Manual Amount')
    manual_amount_boolean = fields.Boolean('Manual Payment')

    @api.onchange('manual_amount_boolean')
    def onchange_manual_payment(self):
        if self.manual_amount_boolean:
            self.manual_amount = self.amount
        else:
            self.manual_amount = 0.0

    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if not self.amount > 0.0:
            raise ValidationError(_('The payment amount must be strictly positive.'))

    @api.depends('employee_join_date', 'employee_left_date')
    def compute_length_of_service(self):
        joining_date = self.employee_join_date
        leaving_date = self.employee_left_date
        d1 = 0
        d2 = 0
        if joining_date and leaving_date:
            d1 = datetime.strptime(joining_date, "%Y-%m-%d")
            d2 = datetime.strptime(leaving_date, "%Y-%m-%d")
            self.length_of_service  = abs((d2 - d1).days + 1)

    @api.depends('contract_type', 'length_of_service','one_day_salary')
    def compute_payment_value(self):
        gratuity_amount = 0
        accummulated_gratuity_days = 0
        if self.length_of_service >= 365:

            if self.contract_type == "limited":
                if self.length_of_service <= 1824:
                    gratuity_amount = 21 * self.one_day_salary * (self.length_of_service / 365)
                    accummulated_gratuity_days = 21
                if self.length_of_service > 1824:
                    gratuity_amount=30 * self.one_day_salary * (self.length_of_service / 365)
                    accummulated_gratuity_days=30

            if self.contract_type == "unlimited":
                if self.length_of_service <= 1094:
                    gratuity_amount=(21 * self.one_day_salary * (self.length_of_service / 365)) * 1 / 3
                    accummulated_gratuity_days=7
                if self.length_of_service > 1094  and self.length_of_service < 1825:
                    gratuity_amount=(21 * self.one_day_salary * (self.length_of_service / 365)) * 2 / 3
                    accummulated_gratuity_days=14;
                if self.length_of_service > 1824:
                    gratuity_amount=21 * self.one_day_salary * (self.length_of_service / 365);
                    accummulated_gratuity_days=21;

        self.amount = gratuity_amount

    @api.multi
    def button_confirm_gratuity(self):
        if self.length_of_service < 365:
            raise ValidationError(_('Service length Is not eligible to calculate the gratuity'))

        if self.manual_amount_boolean:
            self.employee_id.gratuity_amount = self.manual_amount
            self.employee_id.calculate_gratuity = True
        else:
            self.employee_id.gratuity_amount = self.amount
            self.employee_id.calculate_gratuity = True

        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        payslip = self.env['hr.payslip'].browse(active_ids)
        number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
        # delete old payslip lines
        payslip.line_ids.unlink()
        # set the list of contract for which the rules have to be applied
        # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
        contract_ids = payslip.contract_id.ids or \
            payslip.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
        lines = [(0, 0, line) for line in payslip._get_payslip_lines(contract_ids, payslip.id)]
        # expense_lines = []
        # for expense in payslip.expense_ids:
        #     expense_lines.append[(0, 0, expense)]
        # payslip.write({'expense_ids': expense_lines})
        payslip.write({'line_ids': lines, 'number': number})