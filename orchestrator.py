from dataclasses import dataclass, field
import os

from azure_project.azure_handler import AzureHandler
from export.excel_handler import ExcelHandler

PROJECTS_LIST = [
        "HappyHome20",
        "HappyHome10",
        "Fenice",
        "ThermoICE2",
        "SmartRF",
        "JOINON EVO - RaaS and APP",
        "Energy_Metering",
        "LAB Framework",
        "Eracle"
    ]
class ReportOrchestrator:
    
    def __init__(self, logger, azure_handler=None, excel_handler=None):
        self.log = logger
        self.azure_handler = azure_handler if azure_handler else AzureHandler(logger=logger)
        self.excel_handler = excel_handler if excel_handler else ExcelHandler(logger=logger)

    def generate_report(self, parameters, stati):

        self.parameters = parameters
        self.stati = stati
        
        if self.stati["Testcase"]:
            self.log.info("Generazione foglio Testcase...")
            self.generate_testcase_sheet()

        if self.stati["Issue"]:
            self.log.info("Generazione foglio Issue...") 
            self.generate_issue_sheet()

        if self.stati["Changelog"]:
            self.log.info("Generazione foglio Changelog...")
            self.generate_changelog_sheet()

        self.save_report()

    def generate_testcase_sheet(self):

            testcase_titles = ["suiteId", "testSuite", "testCaseId", "testCase", "outcome", "configuration", "configurationValue", "note"]
            try:
                data = self.azure_handler.get_test_data(
                        project_id=self.parameters.project_name,
                        plan_id=self.parameters.tp,
                        suites_id=self.parameters.TestSuite_id
                    )
            except Exception as e:
                    self.log.info(f"Error occurred while fetching test data: {e}")
                    data = []
            self.excel_handler.make_new_sheet("Testcase")
            self.excel_handler.set_common_header()
            self.excel_handler.set_datasheet(
                section="ELENCO TEST CASE / TEST CASE LIST",
                table_titles=testcase_titles,
                data=data
            )
            self.excel_handler.color_state(column="F")  # per il tc column E is the state column

    def generate_issue_sheet(self):

        issue_titles = ["id", "workItemType", "title", "state", "tags", "priority", "notes"]
        query_issue = self.azure_handler.make_query(
            project_name=self.parameters.project_name,
            area_path=self.parameters.issue_path,
            found_in_build=self.parameters.found_in_build
        ).work_items
        self.azure_handler.print_work_item(query_issue)
        self.excel_handler.make_new_sheet("Issue")
        self.excel_handler.set_common_header()
        wi_list = []

        for wi_ref in query_issue:
            wi_list.append(self.azure_handler.work_item_tracking_client.get_work_item(wi_ref.id))
        self.excel_handler.set_datasheet(
            section="ELENCO ISSUE E BUG / ISSUE AND BUG LIST",
            table_titles=issue_titles,
            data=[(wi.id, wi.fields["System.WorkItemType"], wi.fields["System.Title"], wi.fields["System.State"], wi.fields.get("System.Tags", ""), wi.fields.get("Microsoft.VSTS.Common.Priority", ""), wi.fields.get("System.Notes", "")) for wi in wi_list]
        )
        self.excel_handler.color_state(column="E")  # per il tc column E is the state column

    def generate_changelog_sheet(self):
        table_titles = ["id", "workItemType", "title", "state", "tags", "priority", "notes"]
        query_changelog = self.azure_handler.make_query(
            project_name=self.parameters.project_name,
            area_path=self.parameters.changelog_path,
            product_version=self.parameters.fw_version
        ).work_items
        self.azure_handler.print_work_item(query_changelog)
        self.excel_handler.make_new_sheet("Changelog")
        self.excel_handler.set_common_header()
        wi_list = []

        for wi_ref in query_changelog:
            wi_list.append(self.azure_handler.work_item_tracking_client.get_work_item(wi_ref.id))
        self.excel_handler.set_datasheet(
            section="ELENCO CHANGELOG / CHANGELOG LIST",
            table_titles=table_titles,
            data=[(wi.id, wi.fields["System.WorkItemType"], wi.fields["System.Title"], wi.fields["System.State"], wi.fields.get("System.Tags", ""), wi.fields.get("Microsoft.VSTS.Common.Priority", ""), wi.fields.get("System.Notes", "")) for wi in wi_list]
        )
        self.excel_handler.color_state(column="E")  # per il tc column E is the state column

    def save_report(self):
        """Save the Excel report to the specified path with a filename based on the changelog path and firmware version, then open it in Excel."""
        if self.parameters.changelog_path:
            save_path = self.parameters.changelog_path.split('\\')[-1]
        elif self.parameters.tp:
            save_path = f"TP_{self.parameters.tp}"
        elif self.parameters.issue_path:
            save_path = self.parameters.issue_path.split('\\')[-1]

        else:
            self.log.info("[Errore generico] Non hai selezionato nulla... ")
            return #perchè se uno fa avvia senza niente esco e bona


        name = f"{save_path}_{self.parameters.fw_version}" if self.stati["Changelog"] or self.stati["Issue"] else f"{save_path}_Testcase"

        file_path = self.excel_handler.save(filename=f"{name}", parent_path=self.parameters.path)
        
        os.startfile(file_path)

    def get_available_projects(self):
        """Fetch and return a list of available Azure DevOps projects."""
        return  PROJECTS_LIST
        
@dataclass
class ReportParameters:
    project_name: str = ""
    path: str = ""
    tp: int = 0
    TestSuite_id: list = field(default_factory=list)
    fw_version: str = ""
    changelog_path: str = ""
    found_in_build: str = ""
    issue_path: str = ""
