# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import datetime
from dateutil.relativedelta import relativedelta
import json
import os
import logging
import requests
import werkzeug.utils
import werkzeug.wrappers

from itertools import islice
from xml.etree import ElementTree as ET

import odoo

from odoo import http, models, fields, _
from odoo.http import request
from odoo.tools import pycompat, OrderedSet
from odoo.addons.http_routing.models.ir_http import slug, _guess_mimetype
from odoo.addons.web.controllers.main import WebClient, Binary, Home
from odoo.addons.portal.controllers.portal import pager as portal_pager

_logger = logging.getLogger(__name__)


class HRDashboard(Home):

    @http.route('/hr_payroll_uae/payrollbatchwise', type="http", auth="public", website=True)
    def get_payroll_breakdowns(self,**post):
        batch_id = post['batch_id']
        payslip_run_id = int(batch_id)
        salary_rules = request.env['hr.salary.rule'].sudo().search([('active','=','True')])
        rules_chart = []
        name=''
        amount = 0.0
        for rules in salary_rules:
            payslips = request.env['hr.payslip'].sudo().search([('payslip_run_id', '=', payslip_run_id)])
            amount = 0.0
            for slip_ids in payslips:
                for lines in slip_ids.line_ids:
                    if lines.code not in ('GROSS','NET'):
                        if lines.name == rules.name:
                            amount += abs(lines.total)

            if amount:
                rules_chart.append({'name': rules.name.replace("'","\'"), 'y': amount})

        return json.dumps(rules_chart)

    @http.route('/hr_payroll_uae/payroll_summary', type="http", auth="public", website=True)
    def get_payroll_summary(self, **post):
        company_id = request.env.user.company_id.id
        departments = request.env['hr.department'].sudo().search([('company_id', '=', company_id)])
        departments_list = []
        for department in departments:
            departments_list.append(department.name)

        salary_rules = request.env['hr.salary.rule'].sudo().search([('active', '=', 'True'),
                                                                    ('code', '!=', 'GROSS'),
                                                                    ('code', '!=', 'NET'),
                                                                    ('category_id.code','!=','DED')])
        rules_chart = []
        state = post['state']
        flag = 0
        for rules in salary_rules:
            amount_array = []
            for department in departments:
                domain = [('employee_id.department_id.id', '=', department.id),
                          ('date_from', '<=', (datetime.date.today() + relativedelta(day=31)).strftime('%Y-%m-%d')),
                          ('date_from', '>=', (datetime.date.today() - relativedelta(day=1)).strftime('%Y-%m-%d')),
                          ('state', '=', state)]

                if post['date_from'] and post['date_to']:
                    domain = [('employee_id.department_id.id', '=', department.id),
                              ('date_from', '>=', datetime.datetime.strptime(post['date_from'], '%Y-%m-%d')),
                              ('date_to', '<=', datetime.datetime.strptime(post['date_to'], '%Y-%m-%d')),
                              ('state', '=',state)]
                payslips = request.env['hr.payslip'].sudo().search(domain)
                amount = 0.0
                for slip in payslips:
                    for lines in slip.line_ids:
                        if lines.code not in ('GROSS', 'NET'):
                            if lines.name == rules.name:
                                amount += lines.total
                if amount>0:
                    amount_array.append(amount)
                    flag = 1
            rules_chart.append({'name': rules.name.replace("'", "\'"), 'data': amount_array})

        final_data = []
        if flag:
            final_data.append(departments_list)
            final_data.append(rules_chart)

        return json.dumps(final_data)

    @http.route('/hr_payroll_uae/payroll_breakdown', type="http", auth="public", website=True)
    def get_payroll_breakdown(self, **post):
        company_id = request.env.user.company_id.id
        salary_rules = request.env['hr.salary.rule'].sudo().search([('active', '=', 'True'),
                                                                    ('code', '!=', 'GROSS'),
                                                                    ('code', '!=', 'NET'),
                                                                    ('category_id.code','!=','DED')])
        rules_chart = []
        state = post['state']
        for rules in salary_rules:
            domain = [('date_from', '>=', datetime.datetime.strptime(post['date_from'], '%Y-%m-%d')),
                      ('date_to', '<=', datetime.datetime.strptime(post['date_to'], '%Y-%m-%d')),
                      ('state', '=', state),
                      ('company_id','=',company_id)]
            payslips = request.env['hr.payslip'].sudo().search(domain)
            amount = 0.0
            for slip in payslips:
                for lines in slip.line_ids:
                    if lines.code not in ('GROSS', 'NET'):
                        if lines.name == rules.name:
                            amount += abs(lines.total)
            if amount>0:
                rules_chart.append({'name': rules.name.replace("'", "\'"), 'y': amount})
        return json.dumps(rules_chart)

    '''    
    @http.route('/hr_payroll_uae/payroll_breakdown_paid', type="http", auth="public", website=True)
    def get_payroll_breakdown_paid(self, **post):
        salary_rules = request.env['hr.salary.rule'].sudo().search([('active', '=', 'True'),('code', '!=', 'GROSS'),('code', '!=', 'NET'),('category_id.code','!=','DED')])
        rules_chart = []
        for rules in salary_rules:
            domain = [('date_from', '<=', (datetime.date.today() + relativedelta(day=31)).strftime('%Y-%m-%d')),
                      ('date_from', '>=', (datetime.date.today() - relativedelta(day=1)).strftime('%Y-%m-%d')),
                      ('state', '=', 'paid')]

            if post['date_from'] and post['date_to']:
                domain = [('date_from', '>=', datetime.datetime.strptime(post['date_from'], '%Y-%m-%d')),
                          ('date_to', '<=', datetime.datetime.strptime(post['date_to'], '%Y-%m-%d')),
                          ('state', '=', 'paid')]
            payslips = request.env['hr.payslip'].sudo().search(domain)
            amount = 0.0
            for slip in payslips:
                for lines in slip.line_ids:
                    if lines.code not in ('GROSS', 'NET'):
                        if lines.name == rules.name:
                            amount += abs(lines.total)

            if amount>0:
                rules_chart.append({'name': rules.name.replace("'", "\'"), 'y': amount})
        return json.dumps(rules_chart)
    '''
    @http.route('/hr_payroll_uae/payroll_breakdown_deductions', type="http", auth="public", website=True)
    def get_payroll_breakdown_deductions(self, **post):
        company_id = request.env.user.company_id.id
        salary_rules = request.env['hr.salary.rule'].sudo().search(
            [('active', '=', 'True'),('category_id.code','=','DED')])
        rules_chart = []
        state = post['state']
        for rules in salary_rules:
            #_logger.info(rules.name)
            #domain = [('date_from', '<=', (datetime.date.today() + relativedelta(day=31)).strftime('%Y-%m-%d')),
            #          ('date_from', '>=', (datetime.date.today() - relativedelta(day=1)).strftime('%Y-%m-%d')),
            #          ('state', '=', 'paid')]

            #if post['date_from'] and post['date_to']:
            domain = [('date_from', '>=', datetime.datetime.strptime(post['date_from'], '%Y-%m-%d')),
                      ('date_to', '<=', datetime.datetime.strptime(post['date_to'], '%Y-%m-%d')),
                      ('state', '=', state),
                      ('company_id', '=', company_id)]

            payslips = request.env['hr.payslip'].sudo().search(domain)
            amount = 0.0
            for slip in payslips:
                for lines in slip.line_ids:
                    if lines.code not in ('GROSS', 'NET'):
                        if lines.name == rules.name:
                            amount += abs(lines.total)

            if amount > 0:
                rules_chart.append({'name': rules.name.replace("'", "\'"), 'y': amount})
        return json.dumps(rules_chart)

    @http.route('/hr_payroll_uae/payroll_employees_salary', type="http", auth="public", website=True)
    def get_payroll_employees_summary(self, **post):
        labels = ['AED 3000', 'AED 3001 - 5000', 'AED 5001 - 6000', 'AED 6001 - 7000', '> AED 7000']
        final_data = []
        flag = 0
        company_id = request.env.user.company_id.id
        first_total = request.env['hr.contract'].sudo().search_count([('wage','<=',3000),('state','=','open'),('employee_id.company_id.id','=',company_id)])
        if first_total>0:
            flag = 1
        final_data.append(first_total)

        second_total = request.env['hr.contract'].sudo().search_count([('wage', '>', 3000),('wage','<=',5000), ('state', '=', 'open'),('employee_id.company_id.id','=',company_id)])
        if second_total>0:
            flag = 1
        final_data.append(second_total)

        third_total = request.env['hr.contract'].sudo().search_count(
            [('wage', '>', 5000), ('wage', '<=', 6000), ('state', '=', 'open'),('employee_id.company_id.id','=',company_id)])
        if third_total>0:
            flag = 1
        final_data.append(third_total)

        fourth_total = request.env['hr.contract'].sudo().search_count(
            [('wage', '>', 6000), ('wage', '<=', 7000), ('state', '=', 'open'),('employee_id.company_id.id','=',company_id)])
        if fourth_total>0:
            flag = 1
        final_data.append(fourth_total)

        fifth_total = request.env['hr.contract'].sudo().search_count(
            [('wage', '>', 7000), ('state', '=', 'open'),('employee_id.company_id.id','=',company_id)])
        if fifth_total>0:
            flag = 1
        final_data.append(fifth_total)

        if flag > 0:
            return json.dumps([labels,final_data])
        else:
            return json.dumps([])

    @http.route('/hr_payroll_uae/update_total_tabs', type="http", auth="public", website=True)
    def get_payroll_tabs_data(self, **post):
        company_id = request.env.user.company_id.id
        drafted_domain = [('date_from', '>=', datetime.datetime.strptime(post['date_from'], '%Y-%m-%d')),
                          ('date_to', '<=', datetime.datetime.strptime(post['date_to'], '%Y-%m-%d')),
                          ('state', '=', 'draft'),
                          ('company_id', '=', company_id)
                          ]
        posted_domain = [('date_from', '>=', datetime.datetime.strptime(post['date_from'], '%Y-%m-%d')),
                          ('date_to', '<=', datetime.datetime.strptime(post['date_to'], '%Y-%m-%d')),
                          ('state', '=', 'done'),
                          ('company_id', '=', company_id)
                          ]
        paid_domain = [('date_from', '>=', datetime.datetime.strptime(post['date_from'], '%Y-%m-%d')),
                          ('date_to', '<=', datetime.datetime.strptime(post['date_to'], '%Y-%m-%d')),
                          ('state', '=', 'paid'),
                          ('company_id', '=', company_id)
                          ]


        drafted_total = request.env['hr.payslip'].sudo().search_count(drafted_domain)
        posted_total = request.env['hr.payslip'].sudo().search_count(posted_domain)
        paid_total = request.env['hr.payslip'].sudo().search_count(paid_domain)

        data = {'drafted_total':drafted_total,'posted_total':posted_total,'paid_total':paid_total}
        return json.dumps(data)
