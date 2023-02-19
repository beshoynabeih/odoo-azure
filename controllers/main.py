from odoo import http
from odoo.http import request
from collections import OrderedDict
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class Portal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        attendance_count = request.env['hr.attendance'].sudo().search_count([])
        values['attendance_count'] = attendance_count
        return values


class Azure(http.Controller):
    @http.route('/Azure/Devops/', type='http', auth="public", website=True)
    def ret_website_azure_dev_ops(self):
        repos = request.env['repository.project'].sudo().search([])
        return request.render("itq_azure_devops.azure_devops_page", {
            'repos': repos
        })

    @http.route('/Create/Request/', type='http', auth="public", website=True)
    def create_website_Request(self, **kwargs):
        print(kwargs)
        return request.render("itq_azure_devops.create_azure_devops", {})

    @http.route('/Create/Azure/', type='http', auth="public", website=True)
    def create_rq(self, **kwargs):
        print(kwargs)
        if request.env['config.devops'].sudo().create(kwargs) != "failed":
            return request.render("itq_azure_devops.thanks_message_id", {})
        else:
            return request.render('itq_azure_devops.fail_message_id')

    @http.route(['/my/attendance'], type='http', auth="user", website=True)
    def portal_my_attendance(self, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        domain = []
        all_attendance_count = request.env['hr.attendance'].sudo().search_count(
            [('employee_id', '=', request.env.user.id)])
        searchbar_sortings = {
            'date': {'label': 'Date', 'order': 'check_in desc'},
            'duedate': {'label': 'Due Date', 'order': 'check_out desc'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': 'All', 'domain': []},
            'Department of Management': {'label': 'Department of Management',
                                         'domain': [('department_id.name', '=', 'Management')]},
            'Department of Research & Development': {'label': 'Department of Research & Development',
                                                     'domain': [
                                                         ('department_id.name', '=', 'Research & Development')]}, }
        # default filter by value
        if not filterby:
            filterby = 'all'

        domain += searchbar_filters[filterby]['domain']
        pager = portal_pager(
            url="/my/attendance",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=all_attendance_count
        )
        all_attendance = request.env['hr.attendance'].sudo().search(domain, order=order)
        request.session['hr.attendance'] = all_attendance.ids[:100]
        values = {}
        values.update({
            'date': date_begin,
            'page_name': 'attendance',
            'pager': pager,
            'default_url': '/my/attendance',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'all_attendance': all_attendance,
        })

        return request.render("itq_azure_devops.portal_my_attendance",
                              values)
