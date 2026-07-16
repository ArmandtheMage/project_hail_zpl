import os
import sys
from dotenv import load_dotenv

from azure.devops.connection import Connection
from azure.devops.v7_0.core import CoreClient
from azure.devops.v7_0.work_item_tracking.models import Wiql
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.test.test_client import TestClient
from azure.devops.v7_0.test_plan.test_plan_client import TestPlanClient
from azure.devops.v7_0.test_plan.models import *
from azure.devops.v7_0.work_item_tracking.work_item_tracking_client import WorkItemTrackingClient

try:
    from .query_handler import QueryMaker, QueryConstraints
except ImportError:
    from query_handler import QueryMaker, QueryConstraints

from logging import Logger


# Cerca il .env nella cartella dell'exe (non in _MEIPASS)
if getattr(sys, 'frozen', False):
    _env_path = os.path.join(os.path.dirname(sys.executable), '.env')
else:
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(_env_path)

personal_access_token = os.getenv('PAT') if  os.getenv('PAT') else ''
organization_url = os.getenv('organization_url')

class AzureHandler:
    """Client wrapper for Azure DevOps REST API.

    Provides methods to interact with Azure DevOps projects, test plans,
    test suites, test cases, and work items. Handles authentication via
    Personal Access Token loaded from a .env file.
    """

    def __init__(self, logger: Logger=None ):
        self.logger = logger
        self.credentials = BasicAuthentication('', personal_access_token)
        self.connection = Connection(base_url=organization_url, creds=self.credentials)
        self.core_client :CoreClient = self.connection.clients.get_core_client()
        self.test_client :TestClient = self.connection.clients.get_test_client()
        self.test_plan_client :TestPlanClient = self.connection.clients.get_test_plan_client()
        self.work_item_tracking_client :WorkItemTrackingClient = self.connection.clients_v7_0.get_work_item_tracking_client()
        self.query_maker = QueryMaker(self.connection)

    #def logger.info(self, msg):
    #    if self.logger:
    #        self.logger.info(msg)

    def get_projects(self):
        """Retrieve all projects accessible from the configured organization."""
        return self.core_client.get_projects()
    
    def get_project(self, project_name):
        """Find a project by name.

        Args:
            project_name: Exact name of the Azure DevOps project.

        Returns:
            The matching project object, or None if not found.
        """
        projects = self.get_projects()
        for project in projects:
            if project.name == project_name:
                return project
        return None

    def get_test_plans(self, project_id):
        """Retrieve all test plans for a given project."""
        return self.test_plan_client.get_test_plans(project=project_id)

    def get_test_suites(self, project_id, plan_id, expand:bool = True):
        """Retrieve all test suites belonging to a specific test plan.

        Args:
            project_id: Project name or ID.
            plan_id: Test plan ID.
            expand: If True, includes child suite details.
        """
        return self.test_plan_client.get_test_suites_for_plan(project=project_id, plan_id=plan_id, expand=expand)

    def get_test_cases(self, project_id, plan_id, suite_id):
        """Retrieve all test points (test case instances) for a specific suite.

        Args:
            project_id: Project name or ID.
            plan_id: Test plan ID.
            suite_id: Test suite ID.

        Returns:
            List of test points including outcome and configuration details.
        """
        return self.test_plan_client.get_points_list(
                project=project_id,
                continuation_token='-2147483648;3000', # TODO remove from here
                plan_id=plan_id,
                suite_id=suite_id,
                return_identity_ref=True,
                include_point_details=True
        )

    def get_test_data(self, project_id, plan_id, suites_id:list = []):
        """Fetch test results for one or more suites and return structured data.

        Collects test points from the specified suites (or all suites in the plan
        if none are specified), then enriches each point with configuration and
        run comment details.

        Args:
            project_id: Project name or ID.
            plan_id: Test plan ID.
            suites_id: List of suite IDs to query. If empty, queries all suites in the plan.

        Returns:
            List of tuples: (suite_id, suite_name, tc_id, tc_name, outcome,
            config_name, config_value, notes).
        """
        test_points = []
        self.logger.info(f"Fetching test data for project_id: {project_id}, plan_id: {plan_id}, suites_id: {suites_id}")
        if not suites_id:
            self.logger.info(f"No suites_id provided. Fetching all test suites for project_id: {project_id} and plan_id: {plan_id}")
            test_suites = self.get_test_suites(project_id, plan_id)
            suites_id = [suite.id for suite in test_suites]

        for suite_id in suites_id:
            suite = self.test_plan_client.get_test_suite_by_id(project_id, plan_id,suite_id, False)
            test_points.extend(self.get_test_cases(project_id, plan_id, suite_id))
            self.logger.info(f"Fetched suites_id: {suite.id} {suite.name}")

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

            test_run = self.test_client.get_test_results(project=project_id, run_id= tp_result.last_test_run_id) if tp_result.last_test_run_id else None
            notes = test_run[0].comment if test_run and len(test_run) > 0 else ""
            test_data.append((ts_id, ts_name, tc_id, tc_name, outcome, config_name, config_value, notes))
            
        return test_data

    def make_query(self, project_name, area_path, product_version="", found_in_build=""):
        """Build and execute a WIQL query against work items.

        Constructs constraints based on area path and optional filters
        (product version, found-in-build), then runs the query.

        Args:
            project_name: Azure DevOps project name.
            area_path: Full area path to filter on.
            product_version: Optional product version string (CONTAINS match).
            found_in_build: Optional build identifier (CONTAINS match).

        Returns:
            Query result containing matching work item references.
        """
        if not (product_version or found_in_build):
            raise ValueError("Version must be provided for the query.")
        
        constraints = [QueryConstraints("WorkItemType", "<>", "")]
        
        if area_path:
            constraints.append(QueryConstraints("AreaPath", "=", area_path))

        if product_version:
            constraints.append(QueryConstraints("ProductVersion", "CONTAINS", product_version, isCustomField=True))
        if found_in_build:
            constraints.append(QueryConstraints("FoundInBuild", "CONTAINS", found_in_build, isCustomField=True))

        self.query_maker.constraints.extend(constraints)
        query = self.query_maker.build_query(project_name)
        return self.run_query(query)

    def run_query(self, query:str):
        """Execute a raw WIQL query string and return the result.

        Args:
            query: Complete WIQL query string.

        Returns:
            WorkItemQueryResult with work_items list and metadata.
        """
        self.logger.debug(f"Running query: {query}")
        wiql = Wiql(query=query)
        self.query_maker.constraints.clear()  # Clear constraints after running the query
        self.logger.info(f"Query executed successfully. Number of work items found: {len(self.work_item_tracking_client.query_by_wiql(wiql=wiql).work_items)}")
        return self.work_item_tracking_client.query_by_wiql(wiql=wiql)
    
    def print_work_item(self, work_items: list):
        """Print a summary (ID + Title) of each work item reference to stdout."""
        for work_item in work_items:
            wi = self.work_item_tracking_client.get_work_item(work_item.id)
            #self.logger.info(f"found work item: {wi.id}, {wi.fields['System.Title']}")
    

if __name__ == "__main__":
    handler = AzureHandler()
    projects = handler.get_projects()

    project_name = "JOINON EVO - RaaS and APP"
    area_path = "JOINON EVO - RaaS and APP\\MRE\\APP Team"
    product_version = "6.11"

    query_result = handler.make_query(project_name, area_path, product_version)

    handler.logger.info(f"Query Result for Project: {project_name}, Area Path: {area_path}, Product Version: {product_version}")
    handler.logger.info(f"Total Work Items Found: {len(query_result.work_items)}")
    print("-" * 50)
    for work_item in query_result.work_items: # As WorkItemReference
        work_item = handler.work_item_tracking_client.get_work_item(work_item.id)
        handler.logger.info(f"Work Item ID: {work_item.id}, title: {work_item.fields['System.Title']}, State: {work_item.fields['System.State']}, ProductVersion: {work_item.fields.get('Custom.ProductVersion', 'N/A')}, AreaPath: {work_item.fields['System.AreaPath']}")
        print("-" * 50)
