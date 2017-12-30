# -*- coding: utf-8 -*-
{
    'name': 'UAE Payroll',
    'version': '1.0',
    'category': 'HR',
    'license': 'OPL-1',
    'author':'inteslar',
    'summary': 'By Inteslar',
    'description': """
Key Features
------------
* Employee Contracts limited or unlimited based on field in employee master
* Employee Gratuity Calculation
* Batchwise Payslips SIF File Generation
* Batchwise Payslips Register Payment
* Pay the expenses through the payslips
* Configurable accounts for posting the entries
        """,
    'depends': ['base',
                'hr',
                'account',
                'hr_payroll_account',
                'hr_payroll',
                'highcharts',
                'board',
                'web',
                ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_payroll_data.xml',
        'wizard/hr_payslip_sif_generation_view.xml',
        'wizard/hr_payslip_batchwise_sif_generation_view.xml',
        'wizard/hr_payroll_register_payment.xml',
        'wizard/hr_payroll_batchwise_register_payment.xml',
        'wizard/hr_employee_gratuity_view.xml',
        'views/hr_payslip_views.xml',
        'views/hr_payslip_views.xml',
        'views/report_payslip_templates.xml',
        'views/report_payslipdetails_templates.xml',
        'wizard/payslip_confirm_state_view.xml',
        'views/payroll_dashboard.xml',
    ],
    'installable': True,
    'auto_install': False,
}