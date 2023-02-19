import base64
import requests
from odoo import api, fields, models, _
from datetime import date
from datetime import datetime


class PullRequestLinks(models.Model):
    _name = 'pull.request.url'

    url = fields.Char()
    azure_devops_id = fields.Many2one('azure.devops')
    pull_request = fields.Char('Pull Request ID')


class AzureDevops(models.Model):
    _name = "azure.devops"
    rec_name = "project_id"

    config_id = fields.Many2one("config.devops", "Organization")
    project_id = fields.Many2one("project.project")
    repository_id = fields.Many2one("repository.project", domain="[('project_id', '=', project_id)]")
    url_ids = fields.One2many('pull.request.url', 'azure_devops_id')

    def _get_pull_url(self, top, skip=False):
        project = self.project_id.name.replace(' ', '%20')
        authorization = str(base64.b64encode(bytes(':' + self.config_id.token, 'ascii')), 'ascii')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization}
        url = f"https://dev.azure.com/{self.config_id.organization}/{project}/_apis/git/pullrequests"
        params = {
            'searchCriteria.status': 'all',
            'searchCriteria.creatorId': '2ae6a92e-fa48-62a1-af7a-9f92298b119f',
            '$top': top,
            'api-version': '6.0',
        }
        if skip:
            params['$skip'] = skip
        return url, params, headers

    def _get_pull_requests(self, top, skip=False):
        url, params, headers = self._get_pull_url(top, skip)
        response = requests.get(url, params, headers=headers)
        return response.json()['value']

    def GetPullRequests(self, top=10, skip=False):
        values = self._get_pull_requests(top, skip)
        _pr_link = 'https://dev.azure.com/ahmadhaffez0867/Amer%20Project/_git/amer/pullrequest/'
        lst_links = []
        for pull in values:
            creation_date = datetime.strptime(pull.get('creationDate')[:25], '%Y-%m-%dT%H:%M:%S.%f')
            today = datetime.today().replace(hour=0, minute=0, second=0)
            if creation_date < today:
                break
            lst_links.append(pull.get('pullRequestId'))
        else:
            self.GetPullRequests(top, top)
        self.url_ids = [(5, 0, 0)]
        self.url_ids = [(0, 0, {
            'url': _pr_link + str(pr_id),
            'pull_request': pr_id
        }) for pr_id in lst_links]

    def ButtonListPullrequests(self):
        return self.GetPullRequests()

    def _get_workitem_url(self, pr_id):
        project = self.project_id.name.replace(' ', '%20')
        authorization = str(base64.b64encode(bytes(':' + self.config_id.token, 'ascii')), 'ascii')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + authorization
        }

        url = f"https://dev.azure.com/{self.config_id.organization}/{project}/_apis/git/repositories/amer/pullrequests/{pr_id}/workitems/"
        params = {
            'api-version': '6.0',
        }
        return url, params, headers

    def _get_pr_workitems(self):
        work_items = set()
        for pr in self.url_ids:
            url, params, headers = self._get_workitem_url(pr.pull_request)
            response = requests.get(url, params, headers=headers)
            for work_item in response.json()['value']:
                work_items.add(work_item.get('id'))
        return work_items

    def open_work_items(self):
        work_items = self._get_pr_workitems()
        if not work_items:
            return
        project = self.project_id.name.replace(' ', '%20')
        work_item_url = f'https://dev.azure.com/{self.config_id.organization}/{project}/_workitems/edit/'
        return {
            'type': 'ir.actions.act_url',
            'target': '_blank',
            'url': [work_item_url + str(wi) for wi in work_items],
        }

    def ListPullrequests(self):
        project = self.project_id.name
        project = project.replace(' ', '%20')
        token = self.config_id.token
        organization = self.config_id.organization
        authorization = str(
            base64.b64encode(bytes(':' + token, 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization}
        url = f"https://dev.azure.com/{organization}/{project}/_apis/git/pullrequests?searchCriteria.status=all&$top=3&api-version=6.0"
        response = requests.get(url, headers=header_json)
        response = response.json()
        lst_links = []
        for pull in response.get('value'):
            lst_links.append(pull.get('url'))
        return {'type': 'ir.actions.act_url',
                'url': lst_links,
                'target': 'new'}

    def ListRepositories(self):
        project = self.project_id.name
        project = project.replace(' ', '%20')
        token = self.config_id.token
        organization = self.config_id.organization
        authorization = str(
            base64.b64encode(bytes(':' + token, 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization}
        url = f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories?api-version=6.0"
        response = requests.get(url, headers=header_json)
        response = response.json()
        print(response)
        lst_repos = []
        for repo in response.get('value'):
            lst_repos.append(repo.get('name'))
        return lst_repos

    def ListPullrequestsOfSpecific(self):
        repositoryName = self.repository_id.name
        project = self.project_id.name
        project = project.replace(' ', '%20')
        token = self.config_id.token
        organization = self.config_id.organization
        authorization = str(
            base64.b64encode(bytes(':' + token, 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization}
        url = f"https://dev.azure.com/{organization}/{project}/_apis/git/pullrequests?api-version=6.0"
        response = requests.get(url, headers=header_json)
        response = response.json()
        pullRequests = []
        for pull in response.get('value'):
            if pull.get('repository').get('name') == repositoryName:
                dict = {'repository': pull.get('repository').get('name'), 'pullRequestId': pull.get('pullRequestId'),
                        'uniqueName': pull.get('createdBy').get('displayName'),
                        'repositoryId': pull.get('repository').get('id')}
                pullRequests.append(dict)
        return pullRequests

    def ListworkItems(self):
        workItems = []
        pullRequests = self.ListPullrequestsOfSpecific()
        project = self.project_id.name
        project = project.replace(' ', '%20')
        token = self.config_id.token
        organization = self.config_id.organization
        authorization = str(
            base64.b64encode(bytes(':' + token, 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization}
        for pull in pullRequests:
            url = f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{pull.get('repositoryId')}/pullRequests/{pull.get('pullRequestId')}/workitems?api-version=6.0"
            response = requests.get(url, headers=header_json)
            response = response.json()
            for work in response.get('value'):
                dict = {
                    'id': work.get('id'),
                    'url': work.get('url')
                }
                workItems.append(dict)
        return workItems

    def getPullrequest_ids(self):
        project = self.project_id.name
        project = project.replace(' ', '%20')
        token = self.config_id.token
        organization = self.config_id.organization
        authorization = str(
            base64.b64encode(bytes(':' + token, 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization}
        url = f"https://dev.azure.com/{organization}/{project}/_apis/git/pullrequests?api-version=6.0"
        response = requests.get(url, headers=header_json)
        response = response.json()
        lst = []
        for pull in response.get('value'):
            if pull.get('repository').get('name') == self.repository_id.name:
                dict = {
                    'pullRequestId': pull.get('pullRequestId'),
                    'repositoryId': pull.get('repository').get('id')
                }
                lst.append(dict)
        return lst

    def getWorkItems_ids(self):
        pullRequests = self.getPullrequest_ids()
        project = self.project_id.name
        project = project.replace(' ', '%20')
        token = self.config_id.token
        organization = self.config_id.organization
        authorization = str(
            base64.b64encode(bytes(':' + token, 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization}
        lst = []
        for pull in pullRequests:
            url = f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{pull.get('repositoryId')}/pullRequests/{pull.get('pullRequestId')}/workitems?api-version=6.0"
            response = requests.get(url, headers=header_json)
            response = response.json()
            workItems = response.get('value')
            for workItem in workItems:
                lst.append(workItem.get('id'))
        return lst

    def getInfoAboutWorkItems(self):
        workItems_ids = self.getWorkItems_ids()
        converted_list = [str(element) for element in workItems_ids]
        joined_string = ",".join(converted_list)
        token = self.config_id.token
        authorization = str(
            base64.b64encode(bytes(':' + 'xexjgh5lcrxxv7hevcofjzgwt4layyrbvg4zuuue5v22ti74wqmq', 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json-patch+json', 'Authorization': 'Basic ' + authorization}
        url = 'https://dev.azure.com/%s/_apis/wit/workitems?ids=%s&api-version=6.0' % (
            self.config_id.organization, joined_string)
        print(url)
        response = requests.get(url, headers=header_json)
        response = response.json()
        WorkItems = response.get('value')

        lst = []
        for workItem in WorkItems:
            dict = {
                'id': workItem.get('id'),
                'assignedTo': workItem.get('fields').get('System.AssignedTo').get('displayName'),
                'CreatedBy': workItem.get('fields').get('System.CreatedBy').get('displayName'),
                'Reason': workItem.get('fields').get('System.Reason'),
                'ChangedBy': workItem.get('fields').get('System.ChangedBy').get('displayName'),
                'type': workItem.get('fields').get('System.WorkItemType'),
                'url': workItem.get('url')
            }
            lst.append(dict)
        return lst

    def getLast10Pullrequest(self):
        project = self.project_id.name
        project = project.replace(' ', '%20')
        token = self.config_id.token
        organization = self.config_id.organization
        authorization = str(
            base64.b64encode(bytes(':' + token, 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization}
        today = date.today()
        url = f"https://dev.azure.com/{organization}/{project}/_apis/git/pullrequests?&$top=10&closedDate={today}&api-version=6.0"
        print(url)
        response = requests.get(url, headers=header_json)
        response = response.json()
        lst = []
        for pull in response.get('value'):
            if pull.get('repository').get('name') == self.repository_id.name:
                dict = {
                    'pullRequestId': pull.get('pullRequestId'),
                    'repositoryId': pull.get('repository').get('id'),
                    'codeReviewId': pull.get('codeReviewId'),
                    'createdBy': pull.get('createdBy').get('displayName'),
                    'status': pull.get('status'),
                }
                lst.append(dict)
        return lst

    def WorkItemsOFpULLRequest(self):
        pullRequests = self.getLast10Pullrequest()
        project = self.project_id.name
        project = project.replace(' ', '%20')
        token = self.config_id.token
        organization = self.config_id.organization
        authorization = str(
            base64.b64encode(bytes(':' + token, 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization}
        lst = []
        for pull in pullRequests:
            url = f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{pull.get('repositoryId')}/pullRequests/{pull.get('pullRequestId')}/workitems?api-version=6.0"
            response = requests.get(url, headers=header_json)
            print(response.content)
            response = response.json()
            workItems = response.get('value')
            for workItem in workItems:
                lst.append(workItem.get('id'))
        return lst

    def get10InfoAboutWorkItems(self):
        lst_org = self.search([])
        workItems_ids = self.WorkItemsOFpULLRequest()
        converted_list = [str(element) for element in workItems_ids]
        joined_string = ",".join(converted_list)
        authorization = str(
            base64.b64encode(bytes(':' + 'xexjgh5lcrxxv7hevcofjzgwt4layyrbvg4zuuue5v22ti74wqmq', 'ascii')), 'ascii')
        header_json = {'Content-Type': 'application/json-patch+json', 'Authorization': 'Basic ' + authorization}
        url = 'https://dev.azure.com/%s/_apis/wit/workitems?ids=%s&api-version=6.0' % (
            self.config_id.organization, joined_string)
        print(url)
        response = requests.get(url, headers=header_json)
        response = response.json()
        WorkItems = response.get('value')
        lst = []
        for workItem in WorkItems:
            dict = {
                'id': workItem.get('id'),
                'assignedTo': workItem.get('fields').get('System.AssignedTo').get('displayName'),
                'CreatedBy': workItem.get('fields').get('System.CreatedBy').get('displayName'),
                'Reason': workItem.get('fields').get('System.Reason'),
                'ChangedBy': workItem.get('fields').get('System.ChangedBy').get('displayName'),
                'type': workItem.get('fields').get('System.WorkItemType')
            }
            lst.append(dict)
        return lst

    def PrintReport(self):
        return self.env.ref('itq_azure_devops.action_report_azure_devops').report_action(self)
