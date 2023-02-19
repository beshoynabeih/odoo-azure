# -*- coding: utf-8 -*-
{
    'name': 'Azure Devops',
    'summary': '',
    'depends': ['base', 'web', 'timesheet_grid'],
    'author': 'Beshoy Nabeih',
    'data': [
        'security/ir.model.access.csv',
        'views/azure_devops_view.xml',
        'views/config_view.xml',
        # 'views/project_view.xml',
        'views/repository_view.xml',
        'views/template.xml',
        'views/template_js.xml',
        # 'views/website_form.xml',
        'views/attendance_template.xml',
        'views/hr_timesheet.xml',
        # 'report/project.xml',
        # 'report/repository.xml',
        # 'report/azure_devops.xml',
        # 'report/config.xml',
        # 'report/report_xlsx.xml',
    ],
    'demo': [
    ],
    'application': True,
    'assets': {
        'web.assets_backend': [
            # ('replace', 'web/static/src/webclient/actions/action_service.js',
            'itq_azure_devops/static/src/js/url_action.js',
        ]
    }
}
