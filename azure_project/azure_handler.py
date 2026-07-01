import os
from dotenv import load_dotenv

from azure.devops.connection import Connection
from azure.devops.v7_0.core import CoreClient
from azure.devops.v7_0.work_item_tracking.models import Wiql
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.test.test_client import TestClient
from azure.devops.v7_0.test_plan.test_plan_client import TestPlanClient
from azure.devops.v7_0.test_plan.models import *

from  query_handler import QueryMaker, QueryConstraints


load_dotenv()

personal_access_token = os.getenv('PAT') if  os.getenv('PAT') else ''
organization_url = os.getenv('organization_url')

class AzureHandler:
    def __init__(self):
        self.credentials = BasicAuthentication('', personal_access_token)
        self.connection = Connection(base_url=organization_url, creds=self.credentials)
        self.core_client = self.connection.clients.get_core_client()
        self.test_client = self.connection.clients.get_test_client()
        self.test_plan_client = self.connection.clients.get_test_plan_client()
        self.work_item_tracking_client = self.connection.clients_v7_0.get_work_item_tracking_client()
        self.query_maker = QueryMaker(self.connection)

    def get_projects(self):
        return self.core_client.get_projects()
    
    def get_project(self, project_name):
        projects = self.get_projects()
        for project in projects:
            if project.name == project_name:
                return project
        return None

    def get_test_plans(self, project_id):
        return self.test_plan_client.get_test_plans(project=project_id)

    def get_test_suites(self, project_id, plan_id, expand:bool = True):
        return self.test_plan_client.get_test_suites_from_plan(project=project_id, plan_id=plan_id, expand=expand)

    def get_test_cases(self, project_id, plan_id, suite_id):
        return self.test_plan_client.get_points_list(
                project=project_id,
                continuation_token='-2147483648;3000', # TODO remove from here
                plan_id=plan_id,
                suite_id=suite_id,
                return_identity_ref=True,
                include_point_details=True
        )
    
    def get_test_data(self, project_id, plan_id, suites_id):
        test_points = []
        for suite_id in suites_id:
            test_points.extend(self.get_test_cases(project_id, plan_id, suite_id))

        test_data = []
        for test_point in test_points:
            ts_id = test_point.test_suite.id
            ts_name = test_point.test_suite.name
            tc_id = test_point.test_case_reference.id
            tc_name = test_point.test_case_reference.name
            tp_result = test_point.results
            outcome = tp_result.outcome
            config_name = test_point.configuration.name
            config_value = test_config = self.test_plan_client.get_test_configuration_by_id(project_id, test_point.configuration.id)
            config_value = test_config.name if test_config else "Nessuna"
            
            test_run = self.test_plan_client.get_test_results(project=project_id, run_id= tp_result.last_test_run_id) if tp_result.last_test_run_id else None
            notes = test_run[0].comment if test_run and len(test_run) > 0 else ""
            test_data.append((ts_id, ts_name, tc_id, tc_name, outcome, config_name, config_value, notes))
            
        return test_data

    def make_query(self, project_name, area_path, product_version="", found_in_build=""):
        # query = "SELECT [System.Id], [System.WorkItemType], [System.Title], [System.AssignedTo], [System.State], [System.Tags] FROM workitems WHERE "
        # query += f"[System.TeamProject] = '{project_name}' AND [System.WorkItemType] <> '' AND [Custom.ProductVersion] CONTAINS '{product_version}' AND [System.AreaPath] = '{area_path}'"
        constraints = [
            QueryConstraints("WorkItemType", "<>", ""),
            QueryConstraints("AreaPath", "=", area_path)
        ]
        if product_version:
            constraints.append(QueryConstraints("ProductVersion", "CONTAINS", product_version, isCustomField=True))
        if found_in_build:
            constraints.append(QueryConstraints("FoundInBuild", "CONTAINS", found_in_build, isCustomField=True))

        self.query_maker.constraints.extend(constraints)
        query = self.query_maker.build_query(project_name)
        return self.run_query(query)

    def run_query(self, query:str):
        print("*" * 40)
        print(f"Running query: {query}")
        print("*" * 40)
        wiql = Wiql(query=query)
        self.query_maker.constraints.clear()  # Clear constraints after running the query
        print(f"Query executed successfully. Number of work items found: {len(self.work_item_tracking_client.query_by_wiql(wiql=wiql).work_items)}")
        return self.work_item_tracking_client.query_by_wiql(wiql=wiql)
    

if __name__ == "__main__":
    handler = AzureHandler()
    projects = handler.get_projects()

    project_name = "JOINON EVO - RaaS and APP"
    area_path = "JOINON EVO - RaaS and APP\\MRE\\APP Team"
    product_version = "6.11"

    query_result = handler.make_query(project_name, area_path, product_version)

    print(f"Query Result for Project: {project_name}, Area Path: {area_path}, Product Version: {product_version}")
    print(f"Total Work Items Found: {len(query_result.work_items)}")
    print("-" * 50)
    for work_item in query_result.work_items: # As WorkItemReference
        work_item = handler.work_item_tracking_client.get_work_item(work_item.id)
        print(f"Work Item ID: {work_item.id}, title: {work_item.fields['System.Title']}, State: {work_item.fields['System.State']}, ProductVersion: {work_item.fields.get('Custom.ProductVersion', 'N/A')}, AreaPath: {work_item.fields['System.AreaPath']}")
        print("-" * 50)
