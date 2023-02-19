import base64

import requests
from odoo import api, fields, models, _


class Config(models.Model):
    _name = "config.devops"
    _description = "Config Devops"
    _rec_name = "organization"

    organization = fields.Char(ondelete='cascade')
    token = fields.Char()
    project_ids = fields.Many2many("project.project", readonly=True)
    api_version = fields.Char(default='6.0', required=True)

    @api.model
    def create(self, vals):
        projects = self.env['project.project'].create_projects(vals.get('organization'),
                                                               vals.get('token'),
                                                               vals['api_version'])
        repos = self.env['repository.project'].create_repository(vals.get('organization'),
                                                                 vals.get('token'),
                                                                 vals['api_version'])
        if projects != "failed" and repos != "failed":
            vals['project_ids'] = [(4, project.id) for project in projects]
            return super(Config, self).create(vals)
        return "failed"

    def get_projetcs(self):
        token = self.token
        organization = self.organization
        authorization = str(
            base64.b64encode(bytes(':' + token, 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization}
        url = f"https://dev.azure.com/{organization}/_apis/projects?api-version={self.api_version}"
        response = requests.get(url, headers=header_json)
        response = response.json()
        projects = []
        for repo in response.get('value'):
            projects.append(repo.get('name'))
        return projects
