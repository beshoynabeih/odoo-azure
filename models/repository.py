import base64
import requests
from odoo import api, fields, models, _


class Repository(models.Model):
    _name = "repository.project"
    _description = "Repository Project"
    _rec_name = "name"

    name = fields.Char()
    url = fields.Char()
    repo_id = fields.Char()
    project_id = fields.Many2one("project.project")

    @api.model
    def get_repository(self, organization, token, api_v):
        authorization = str(base64.b64encode(bytes(':' + token, 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization}
        url = f"https://dev.azure.com/{organization}/_apis/git/repositories?api-version={api_v}"
        response = requests.get(url, headers=header_json)
        return response

    def create_repository(self, organization, token, api_v):
        response = self.get_repository(organization, token, api_v)
        if response.status_code == 200:
            response = response.json()
            lst = []
            project_azure_model = self.env['project.project']

            for repo in response['value']:
                project_id = project_azure_model.search([('name', '=', repo['project']['name'])], limit=1).id
                lst.append({
                    'name': repo['name'],
                    'url': repo['url'],
                    'project_id': project_id,
                    'repo_id': repo['project']['id']
                })
            return self.create(lst)
        return "failed"
