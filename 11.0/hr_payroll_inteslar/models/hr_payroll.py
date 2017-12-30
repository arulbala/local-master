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
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare, float_is_zero

_logger = logging.getLogger(__name__)

class HrPayrollDashboard(models.Model):
    _name = "hr.payroll.dashboard"

    @api.one
    def _get_count(self):
        draft_count = self.env['hr.payslip'].search(
            [('state', '=', 'draft')])
        posted_count = self.env['hr.payslip'].search(
            [('state', '=', 'done')])
        paid_count = self.env['hr.payslip'].search(
            [('sate', '=', 'paid')])

        self.orders_count = len(orders_count)
        self.quotations_count = len(quotations_count)
        self.orders_done_count = len(orders_done_count)

    color = fields.Integer(string='Color Index')
    name = fields.Char(string="Name")
    draft_count = fields.Integer(compute='_get_count')
    posted_count = fields.Integer(compute='_get_count')
    paid_count = fields.Integer(compute='_get_count')
