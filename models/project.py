import base64
import requests
from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = "project.project"

    url = fields.Char()
    repository_ids = fields.One2many("repository.project", "project_id")

    @api.model
    def get_projects(self, organization, token, api_v):
        authorization = str(base64.b64encode(bytes(':' + token, 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization}
        url = f"https://dev.azure.com/{organization}/_apis/projects?api-version={api_v}"
        response = requests.get(url, headers=header_json)
        return response

    def create_projects(self, organization, token, api_v):
        response = self.get_projects(organization, token, api_v)
        if response.status_code == 200:
            response = response.json()
            lst = []
            for project in response['value']:
                lst.append({'name': project['name'], 'url': project['url']})

            return self.create(lst)
        return "failed"
