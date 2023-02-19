import base64
import json

import requests

from odoo import api, fields, models, _


class AnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def get_azure_create(self):
        pass

    def create_azure_tasks(self):
        config = self.env['config.devops'].search([('project_ids', 'in', self.project_id.id)], limit=1)
        if not config:
            return
        project = self.project_id.name.replace(' ', '%20')
        authorization = str(base64.b64encode(bytes(':' + config.token, 'ascii')), 'ascii')
        headers = {'Content-Type': 'application/json-patch+json', 'Authorization': 'Basic ' + authorization}
        task = "$Task"
        url = f"https://dev.azure.com/{config.organization}/{project}/_apis/wit/workitems/{task}?api-version={config.api_version}"
        data = [
            {
                "op": "add",
                "path": "/fields/System.Title",
                "from": None,
                "value": "Sample task"
            },
            {
                "op": "add",
                "path": "/fields/System.Description",
                "from": None,
                "value": "asdasd"
            },
            {
                "op": "add",
                "path": "/fields/System.AssignedTo",
                "from": None,
                "value": "Beshoy Nabeih Aziz"
            },
            {
                "op": "add",
                "path": "/fields/System.State",
                "from": None,
                "value": "Closed"
            },
        ]
        res = requests.post(url, headers=headers, data=json.dumps(data))
        print(res)
        # for line in self:
        #     print(line)
