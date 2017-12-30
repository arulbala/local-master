# -*- coding: utf-8 -*-
import logging
import pytz
import time
import babel

from odoo import _, api, fields, models, tools, _
from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta
from odoo.tools import float_compare, float_is_zero

_logger = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage = fields.Monetary('Wage', digits=(16, 2), required=True, help="Employee's monthly gross wage.", track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Salary Journal', default=lambda self: self.env['account.journal'].search([('code', '=', 'MISC')], limit=1))

    def _get_default_date_to(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y') + '-' + date.strftime('%m') + '-' + date.strftime('%d')

    air_ticket_allowance = fields.Float(string='Air Ticket Allowance')
    date_start_air_ticket = fields.Date('Start Date')
    date_end_air_ticket = fields.Date('End Date')
    calculate_air_pro_rata = fields.Boolean('Calculate Pro Rata')
    prorata_amount_air_ticket = fields.Float('Rate', compute='compute_air_ticket_allowance')
    calculation_date_for_air_ticket = fields.Date(string='Calculation Date', default=_get_default_date_to)
    air_ticket_calculation_amount = fields.Float('Amount', compute='compute_air_ticket_allowance')


    bonus = fields.Float(string='Bonus')
    date_start_bonus = fields.Date('Start Date')
    date_end_bonus = fields.Date('End Date')
    calculate_bonus_pro_rata = fields.Boolean('Calculate Pro Rata')
    prorata_amount_bonus = fields.Float('Rate', compute='compute_bonus')
    calculation_date_for_bonus = fields.Date(string='Calculation Date', default=_get_default_date_to)
    bonus_calculation_amount = fields.Float('Amount', compute='compute_bonus')


    schooling_allowance = fields.Float(string='Schooling Allowance')
    date_start_schooling = fields.Date('Start Date')
    date_end_schooling = fields.Date('End Date')
    calculate_schooling_pro_rata = fields.Boolean('Calculate Pro Rata')
    prorata_amount_schooling = fields.Float('Rate', compute='compute_schooling')
    calculation_date_for_schooling = fields.Date(string='Calculation Date', default=_get_default_date_to)
    schooling_calculation_amount = fields.Float('Amount', compute='compute_schooling')


    @api.onchange('air_ticket_allowance', 'date_start_air_ticket', 'date_end_air_ticket', 'calculation_date_for_air_ticket', 'calculate_air_pro_rata')
    def compute_air_ticket_allowance(self):
        d1 = 0
        d2 = 0
        d3 = 0
        length_of_service = 0
        amount = 0
        for line in self:
            if line.calculate_air_pro_rata:
                if line.date_start_air_ticket and line.date_end_air_ticket:
                    d1 = datetime.strptime(line.date_start_air_ticket, "%Y-%m-%d")
                    d2 = datetime.strptime(line.date_end_air_ticket, "%Y-%m-%d")
                    length_of_service  = abs((d2 - d1).days + 1)
                    amount = line.air_ticket_allowance / length_of_service
                    line.prorata_amount_air_ticket = amount
                    if line.calculation_date_for_air_ticket:
                        d3 = datetime.strptime(line.calculation_date_for_air_ticket, "%Y-%m-%d")
                        current_service  = abs((d3 - d1).days + 1)
                        line.air_ticket_calculation_amount= amount * current_service
            else:
                line.date_start_air_ticket = ''
                line.date_end_air_ticket = ''
                line.prorata_amount_air_ticket = ''
                line.calculation_date_for_air_ticket = ''
                line.air_ticket_calculation_amount = ''

    @api.onchange('bonus', 'date_start_bonus', 'date_end_bonus', 'calculate_bonus_pro_rata', 'calculation_date_for_bonus')
    def compute_bonus(self):
        d1 = 0
        d2 = 0
        d3 = 0
        length_of_service = 0
        amount = 0
        for line in self:
            if line.calculate_bonus_pro_rata:
                if line.date_start_bonus and line.date_end_bonus:
                    d1 = datetime.strptime(line.date_start_bonus, "%Y-%m-%d")
                    d2 = datetime.strptime(line.date_end_bonus, "%Y-%m-%d")
                    length_of_service  = abs((d2 - d1).days + 1)
                    amount = line.bonus / length_of_service
                    line.prorata_amount_bonus = amount
                    if line.calculation_date_for_bonus:
                        d3 = datetime.strptime(line.calculation_date_for_bonus, "%Y-%m-%d")
                        current_service  = abs((d3 - d1).days + 1)
                        line.bonus_calculation_amount= amount * current_service
            else:
                line.bonus_calculation_amount = ''
                line.date_start_bonus = ''
                line.date_end_bonus = ''
                line.calculation_date_for_bonus =''
                line.prorata_amount_bonus = ''

    @api.onchange('schooling_allowance', 'date_start_schooling', 'date_end_schooling', 'calculate_schooling_pro_rata', 'calculation_date_for_schooling')
    def compute_schooling(self):
        d1 = 0
        d2 = 0
        d3 = 0
        length_of_service = 0
        amount = 0
        for line in self:
            if line.calculate_schooling_pro_rata:
                if line.date_start_schooling and line.date_end_schooling:
                    d1 = datetime.strptime(line.date_start_schooling, "%Y-%m-%d")
                    d2 = datetime.strptime(line.date_end_schooling, "%Y-%m-%d")
                    length_of_service  = abs((d2 - d1).days + 1)
                    amount = line.schooling_allowance / length_of_service
                    line.prorata_amount_schooling = amount
                    if line.calculation_date_for_schooling:
                        d3 = datetime.strptime(line.calculation_date_for_schooling, "%Y-%m-%d")
                        current_service  = abs((d3 - d1).days + 1)
                        line.schooling_calculation_amount= amount * current_service
            else:
                line.schooling_calculation_amount = ''
                line.date_start_schooling = ''
                line.date_end_schooling = ''
                line.calculation_date_for_schooling = ''
                line.prorata_amount_schooling = ''

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_default_date_to(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y') + '-' + date.strftime('%m') + '-' + date.strftime('%d')

    mol_id = fields.Char(string='MOL ID')
    employee_bank_account_id = fields.One2many('hr.employee.bank.accounts', 'employee_id', string="Bank Account Number")
    date_of_join = fields.Date('Date Of joining')
    date_of_left = fields.Date('Date Of leaving')
    contract_type = fields.Selection([('limited','Limited'),('unlimited', 'Unlimited')], string="Contract Type")
    gratuity_amount = fields.Float(string='Gratuity amount', readonly=True)
    calculate_gratuity = fields.Boolean('Calculate Gratuity')
    length_of_service = fields.Integer('length Of Service', compute='compute_length_of_service')
    today_date = fields.Date(string='Date for Calculating Air Ticket', required=True, default=_get_default_date_to)

    @api.depends('loan_count','loan_ids')
    def compute_loan_count(self):
        count = 0
        for line in self:
            count = self.env['hr.loan'].search([('employee_id','=',line.id)])
            line.loan_count =len(count)

    @api.depends('date_of_join', 'date_of_left')
    def compute_length_of_service(self):
        d1 = 0
        d2 = 0
        for line in self:
            if line.date_of_join and line.date_of_left:
                d1 = datetime.strptime(line.date_of_join, "%Y-%m-%d")
                d2 = datetime.strptime(line.date_of_left, "%Y-%m-%d")
                line.length_of_service  = abs((d2 - d1).days + 1)

class HrEmployeeBankAccounts(models.Model):
    _name = 'hr.employee.bank.accounts'

    employee_id = fields.Many2one('hr.employee', 'Employee ID')
    account_number = fields.Char(string='Account Number', required=True)
    routing_code = fields.Char(string='Routing Code', required=True)
    iban = fields.Char('IBAN')
    bank_id = fields.Many2one('res.bank')
    default_bank_account = fields.Boolean('Default Bank Account')

class ResCompany(models.Model):
    _inherit = 'res.company'

    mol_id = fields.Char(string='MOL ID')
    company_bank_account_id = fields.One2many('hr.company.bank.accounts', 'company_id', string="Bank Account Number")

class HrCompanyBankAccounts(models.Model):
    _name = 'hr.company.bank.accounts'

    company_id = fields.Many2one('res.company', 'Company ID')
    name = fields.Char(string='Account Number', required=True)
    routing_code = fields.Char(string='Routing Code', required=True)
    iban = fields.Char('IBAN')
    bank_id = fields.Many2one('res.bank')

class HrSalaryRule(models.Model):
    _name = 'hr.salary.rule'
    _description = 'HR Salary Rule'
    _inherit=['hr.salary.rule','mail.thread']

class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread']

    image = fields.Binary(
        "Medium-sized photo", attachment=True,related='employee_id.image',
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft',
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""", track_visibility='onchange')
 #   loan_ids = fields.One2many('hr.payslip.loan.lines', 'payslip_id')

    total_amount = fields.Float(string='Total Amount', compute='compute_total_amount', store=True)
    total_allowance_amount = fields.Float(string='Total Allowance', compute='compute_allowance_amount')
    total_basic_amount = fields.Float(string='Total Allowance', compute='compute_basic_amount')
    total_detection_amount = fields.Float(string='Total Allowance', compute='compute_detection_amount')
    for_expense_payment = fields.Selection([('include','Include'),('exclude','Exclude')],string='Add Expenses', default='exclude')

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(fields.Date.from_string(date_from), datetime_time.min)
            day_to = datetime.combine(fields.Date.from_string(date_to), datetime_time.max)

            # compute leave days
            leaves = {}
            day_leave_intervals = contract.employee_id.iter_leaves(day_from, day_to, calendar=contract.resource_calendar_id)
            for day_intervals in day_leave_intervals:
                for interval in day_intervals:
                    holiday = interval[2]['leaves'].holiday_id
                    current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                        'name': holiday.holiday_status_id.name,
                        'sequence': 5,
                        'code': holiday.holiday_status_id.name,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'contract_id': contract.id,
                    })
                    leave_time = (interval[1] - interval[0]).seconds / 3600
                    current_leave_struct['number_of_hours'] += leave_time
                    work_hours = contract.employee_id.get_day_work_hours_count(interval[0].date(), calendar=contract.resource_calendar_id)
                    current_leave_struct['number_of_days'] += leave_time / work_hours

            # compute worked days
            work_data = contract.employee_id.get_work_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work_data['days'],
                'number_of_hours': work_data['hours'],
                'contract_id': contract.id,
            }

            overtime = {
                'name': _("OVERTIME Input"),
                'sequence': 1,
                'code': 'OVERTIME',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }

            res.append(attendances)
            res.append(overtime)
            res.extend(leaves.values())
        return res

    @api.depends('line_ids')
    @api.onchange('line_ids')
    def compute_total_amount(self):
        for slip in self:
            total_amount_new = 0.0
            for line in slip.line_ids:
                if line.salary_rule_id.code == 'NET':
                    total_amount_new+=line.total
            slip.total_amount = total_amount_new
            # total_loan_amount = 0.0
            # for loan_line in slip.loan_ids:
            #     total_expense_amount += loan_line.amount
            # slip.total_amount = total_amount_new + total_expense_amount + total_loan_amount

    @api.depends('line_ids')
    @api.onchange('line_ids')
    def compute_allowance_amount(self):
        for slip in self:
            total_amount_new = 0.0
            for line in slip.line_ids:
                if line.salary_rule_id.category_id.code == 'ALW':
                    total_amount_new+=line.total
            slip.total_allowance_amount = total_amount_new

    @api.depends('line_ids')
    @api.onchange('line_ids')
    def compute_basic_amount(self):
        for slip in self:
            total_amount_new = 0.0
            for line in slip.line_ids:
                if line.salary_rule_id.category_id.code == 'BASIC':
                    total_amount_new+=line.total
            slip.total_basic_amount = total_amount_new

    @api.depends('line_ids')
    @api.onchange('line_ids')
    def compute_detection_amount(self):
        for slip in self:
            total_amount_new = 0.0
            for line in slip.line_ids:
                if line.salary_rule_id.category_id.code == 'DED':
                    total_amount_new+=line.total
            slip.total_detection_amount = total_amount_new


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('close', 'Close'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    total_amount = fields.Float(string='Total Amount', compute='compute_total_amount')
    payslip_count = fields.Integer('Payslip Count', compute='compute_payslip_count')
    paid_payslips = fields.Float(string='Total Paid', compute='compute_paid_amount')
    paid_payslips_count = fields.Integer(string='Paid Payslip Count', compute='compute_paid_count')
    total_allowance = fields.Integer(string='Total Allowances', compute='compute_allowance_count')
    total_basic = fields.Integer(string='Total Basics', compute='compute_basic_count')
    total_detection = fields.Integer(string='Total Detections', compute='compute_detection_count')
    paid_total_allowance_amount = fields.Float(string='Paid Allowances', compute='compute_allowance_amount_paid')
    paid_total_basic_amount = fields.Float(string='Paid Basics', compute='compute_basic_amount_paid')
    paid_total_detection_amount = fields.Float(string='Effective Detections', compute='compute_detection_amount_paid')

    @api.multi
    def compute_sheet(self):
        for slips in self:
            if slips:
                for payslip in slips.slip_ids:
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
                return True

    @api.depends('slip_ids')
    @api.onchange('slip_ids')
    def compute_paid_count(self):
        for line in self:
            if line:
                count = self.env['hr.payslip'].search([('payslip_run_id','=', line.id),('state','=','paid')])
                line.paid_payslips_count = len(count)

    @api.depends('slip_ids')
    @api.onchange('slip_ids')
    def compute_paid_amount(self):
        for line in self:
            if line:
                paid_payslip_new = 0.0
                for slip in line.slip_ids:
                    if slip:
                        if slip.state == 'paid':
                            paid_payslip_new+=slip.total_amount
                line.paid_payslips = paid_payslip_new

    @api.depends('slip_ids')
    @api.onchange('slip_ids')
    def compute_payslip_count(self):
        if self.slip_ids:
            self.payslip_count=len(self.slip_ids)

    @api.depends('slip_ids')
    @api.onchange('slip_ids')
    def compute_total_amount(self):
        for line in self:
            total_amount_new = 0.0
            for slip in line.slip_ids:
                _logger.info(total_amount_new)
                total_amount_new+=slip.total_amount
            line.total_amount = total_amount_new

    @api.depends('slip_ids')
    @api.onchange('slip_ids')
    def compute_allowance_count(self):
        for line in self:
            total_amount_new = 0.0
            for slip in line.slip_ids:
                _logger.info(total_amount_new)
                total_amount_new+=slip.total_allowance_amount
            line.total_allowance = total_amount_new

    @api.depends('slip_ids')
    @api.onchange('slip_ids')
    def compute_basic_count(self):
        for line in self:
            total_amount_new = 0.0
            for slip in line.slip_ids:
                _logger.info(total_amount_new)
                total_amount_new+=slip.total_basic_amount
            line.total_basic = total_amount_new

    @api.depends('slip_ids')
    @api.onchange('slip_ids')
    def compute_detection_count(self):
        for line in self:
            total_amount_new = 0.0
            for slip in line.slip_ids:
                _logger.info(total_amount_new)
                total_amount_new+=slip.total_detection_amount
            line.total_detection = total_amount_new

    @api.depends('slip_ids')
    @api.onchange('slip_ids')
    def compute_allowance_amount_paid(self):
        for line in self:
                paid_payslip_new = 0.0
                for slip in line.slip_ids:
                        if slip.state == 'paid':
                            paid_payslip_new+=slip.total_allowance_amount
                line.paid_total_allowance_amount = paid_payslip_new

    @api.depends('slip_ids')
    @api.onchange('slip_ids')
    def compute_basic_amount_paid(self):
        for line in self:
            if line:
                paid_payslip_new = 0.0
                for slip in line.slip_ids:
                    if slip:
                        if slip.state == 'paid':
                            paid_payslip_new+=slip.total_basic_amount
                line.paid_total_basic_amount = paid_payslip_new


    @api.depends('slip_ids')
    @api.onchange('slip_ids')
    def compute_detection_amount_paid(self):
        for line in self:
            if line:
                paid_payslip_new = 0.0
                for slip in line.slip_ids:
                    if slip:
                        if slip.state == 'paid':
                            paid_payslip_new+=slip.total_detection_amount
                line.paid_total_detection_amount = paid_payslip_new

    @api.multi
    def batch_wise_payslip_confirm(self):
        for record in self.slip_ids:
            if record.state == 'draft':
                record.action_payslip_done()
        self.state='done'

# class HrPayslipLoanLines(models.Model):
#     _name = 'hr.payslip.loan.lines'
#
#     payslip_id = fields.Many2one('hr.payslip', 'Loan Lines')
#     loan_id = fields.Many2one('hr.loan', string='Loan')
#     employee_id = fields.Many2one('hr.employee',related='payslip_id.employee_id', string="Name")
#     amount = fields.Float(string='Amount', related='loan_id.loan_amount')
#     state = fields.Selection([('new', 'New'),
#                                 ('posted', 'Posted'),
#                                 ('paid_to_employee', 'Paid To Employee'),
#                                 ('paid_to_company', 'Paid To Company')
#                               ],related='loan_id.state', string='Status')
#     _sql_constraints = [
#         ('loan_id_uniq', 'unique(loan_id)',
#          ("This Loan was already added to this payslip or another, please remove the duplicate.!"))
#     ]
#
#     @api.onchange('loan_id')
#     def onchange_loan_id(self):
#         for payslip_loan in self:
#             return {'domain': {'loan_id': [('employee_id', '=', payslip_loan.payslip_id.employee_id.id), ('state', '=', 'posted')]}}