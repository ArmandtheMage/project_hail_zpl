
#-------------GUI----------------
from asyncio import log
from py_compile import main
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from dataclasses import dataclass, field

import sys
import os

# Supporto PyInstaller: usa _MEIPASS se eseguibile, altrimenti la cartella dello script
BASE_PATH = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(os.path.join(__file__, ".."))))

sys.path.append(os.path.join(BASE_PATH, "azure_project"))
sys.path.append(os.path.join(BASE_PATH, "export"))
#sys.path.append(os.path.join(BASE_PATH))

from azure_handler import AzureHandler
from excel_handler import ExcelHandler
from utils.ZPL_log import ZPLLogger

BG = "#242424"
TEXT = "#cecece"
ORANGE = "#e84e0f"
INPUT_BG = "#ffffff"

LABEL_WIDTH = 20

print("stiamo aprendo la GUI!")
class GUI():
    """Launch the main Tkinter GUI for report generation.

    Presents input fields for project selection, test plan/suite IDs,
    changelog and issue parameters. On submit, queries Azure DevOps,
    builds an Excel report, saves it, and opens it in Excel.

    Returns:
        dict: A dictionary of all user-entered parameters.
    """
    
    def __init__(self, logger: ZPLLogger = None, azure_handler: AzureHandler = None, excel_handler: ExcelHandler = None):
        self.parameters = GUIparameters()

        log_widget = None
        self.log = ZPLLogger("ZPLLogger")

        self.az = azure_handler if azure_handler else AzureHandler(logger=self.log)
        self.ex = excel_handler if excel_handler else ExcelHandler(logger=self.log)

        self.stati = {
            "Testcase": True,
            "Changelog": False,
            "Issue": False
        }

        self.root = tk.Tk()
        self.root.title("Parametri Report")
        self.root.configure(bg=BG)

        self.main = tk.Frame(self.root, bg=BG)
        self.main.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.create_widgets()


    def conferma(self):
        """Callback for the 'Avvia' button. Collects form values, runs Azure
        queries for enabled sections (Testcase, Issue, Changelog), populates
        the Excel workbook, saves and opens the resulting file."""

        self.read_parameters()
        
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

    def read_parameters(self):
        """Read values from the GUI input fields and store them in self.parameters."""

        #valori comuni
        self.parameters.project_name = self.combo_project.get()
        self.parameters.path = self.entry_path.get()

        #issue
        self.parameters.tp = int(self.entry_tp.get()) if self.entry_tp.get() else 0
        
        # lista test suite (separate da virgola)
        suite_input = self.entry_suite.get()
        if suite_input.strip():
            self.parameters.TestSuite_id = [int(x.strip()) for x in suite_input.split(",")]
        else:
            self.parameters.TestSuite_id = []

        # changelog
        self.parameters.fw_version = self.entry_fw_version.get()
        self.parameters.changelog_path = self.entry_changelog_path.get()

        # issue
        self.parameters.found_in_build = self.entry_found_in_build.get()
        self.parameters.issue_path = self.entry_issue_path.get()

        # id, title, workitemtype, state, tags
        table_titles = ["id", "workItemType", "title", "state", "tags", "notes"]
        
    def generate_testcase_sheet(self):

            testcase_titles = ["suiteId", "testSuite", "testCaseId", "testCase", "outcome", "configuration", "configurationValue", "note"]
            try:
                data = self.az.get_test_data(
                        project_id=self.parameters.project_name,
                        plan_id=self.parameters.tp,
                        suites_id=self.parameters.TestSuite_id
                    )
            except Exception as e:
                    self.log.info(f"Error occurred while fetching test data: {e}")
                    data = []
            self.ex.make_new_sheet("Testcase")
            self.ex.set_common_header()
            self.ex.set_datasheet(
                section="ELENCO TEST CASE / TEST CASE LIST",
                table_titles=testcase_titles,
                data=data
            )
            self.ex.color_state(column="F")  # per il tc column E is the state column

    def generate_issue_sheet(self):

        issue_titles = ["id", "workItemType", "title", "state", "tags", "notes"]
        query_issue = self.az.make_query(
            project_name=self.parameters.project_name,
            area_path=self.parameters.issue_path,
            found_in_build=self.parameters.found_in_build
        ).work_items
        self.az.print_work_item(query_issue)
        self.ex.make_new_sheet("Issue")
        self.ex.set_common_header()
        wi_list = []

        for wi_ref in query_issue:
            wi_list.append(self.az.work_item_tracking_client.get_work_item(wi_ref.id))
        self.ex.set_datasheet(
            section="ELENCO ISSUE E BUG / ISSUE AND BUG LIST",
            table_titles=issue_titles,
            data=[(wi.id, wi.fields["System.WorkItemType"], wi.fields["System.Title"], wi.fields["System.State"], wi.fields.get("System.Tags", "")) for wi in wi_list]
        )
        self.ex.color_state(column="E")  # per il tc column E is the state column

    def generate_changelog_sheet(self):
        table_titles = ["id", "workItemType", "title", "state", "tags", "notes"]
        query_changelog = self.az.make_query(
            project_name=self.parameters.project_name,
            area_path=self.parameters.changelog_path,
            product_version=self.parameters.fw_version
        ).work_items
        self.az.print_work_item(query_changelog)
        self.ex.make_new_sheet("Changelog")
        self.ex.set_common_header()
        wi_list = []

        for wi_ref in query_changelog:
            wi_list.append(self.az.work_item_tracking_client.get_work_item(wi_ref.id))
        self.ex.set_datasheet(
            section="ELENCO CHANGELOG / CHANGELOG LIST",
            table_titles=table_titles,
            data=[(wi.id, wi.fields["System.WorkItemType"], wi.fields["System.Title"], wi.fields["System.State"], wi.fields.get("System.Tags", "")) for wi in wi_list]
        )
        self.ex.color_state(column="E")  # per il tc column E is the state column

    def save_report(self):
        """Save the Excel report to the specified path with a filename based on the changelog path and firmware version, then open it in Excel."""

        save_path = self.parameters.changelog_path.split('\\')[-1]
        name = f"{save_path}_{self.parameters.fw_version}" if self.stati["Changelog"] or self.stati["Issue"] else f"{save_path}_Testcase"

        file_path = self.ex.save(filename=f"{name}", parent_path=self.parameters.path)
        
        os.startfile(file_path)

    ## --- TOGGLE ---

    def toggle(self,sezione, canvas, frame):
        """Toggle a section on/off. Updates the indicator color, shows/hides
        the section frame, and clears input fields when deactivating.

        Args:
            sezione: Section key ('Testcase', 'Changelog', or 'Issue').
            canvas: Canvas widget containing the toggle circle.
            frame: Frame widget containing the section's input fields.
        """
        self.stati[sezione] = not self.stati[sezione]

        # cambia colore cerchio
        colore = ORANGE if self.stati[sezione] else INPUT_BG
        canvas.itemconfig("circle", fill=colore)

        # mostra/nasconde frame
        if self.stati[sezione]:
            frame.grid()
            if sezione == "Issue":
                self.copia_changelog_in_issue()     
        else:
            frame.grid_remove()

            #per eliminare i valori dei campi quando si disattiva la sezione
            if sezione == "Testcase":
                self.entry_tp.delete(0, tk.END)
                self.entry_suite.delete(0, tk.END)
            if sezione == "Changelog":
                self.entry_fw_version.delete(0, tk.END)
                self.entry_changelog_path.delete(0, tk.END)
            if sezione == "Issue":
                self.entry_found_in_build.delete(0, tk.END)
                self.entry_issue_path.delete(0, tk.END)
    
    def seleziona_cartella(self):
        """Open a folder selection dialog and update the path entry field."""
        cartella = filedialog.askdirectory(
            initialdir=self.entry_path.get() if self.entry_path.get() else "/",
            title="Seleziona cartella"
        )

        if cartella:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, cartella)
        
    def copia_changelog_in_issue(self, event = None):
        """Sync changelog fields into the issue section fields.

        Copies FW Version into 'Found in build' and Area Path into
        the issue Area Path, so the user doesn't have to type them twice.
        """
        self.entry_found_in_build.delete(0, tk.END)
        self.entry_found_in_build.insert(0, self.entry_fw_version.get())

        self.entry_issue_path.delete(0, tk.END)
        self.entry_issue_path.insert(0, self.entry_changelog_path.get())


    def create_widgets(self):
        self.create_header()
        self.create_testcase_section()
        self.create_changelog_section()
        self.create_issue_section()
        self.create_log_section()
        self.create_buttons()

    def create_header(self):
        #---save path---
        default_path = os.path.join(os.path.expanduser("~"), "OneDrive - Gewiss S.p.A", "Documenti", "ZPL")
        tk.Label(self.main, text="Path file", bg=BG, fg=TEXT).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_path = tk.Entry(self.main, bg=INPUT_BG, fg=BG, width=43)
        self.entry_path.insert(0, default_path)
        self.entry_path.grid(row=0, column=1, sticky="ew", pady=5,padx=5)
        
        btn_browse = tk.Button(self.main,text="📁",command=self.seleziona_cartella, bg=BG,fg="white", width=3,relief="flat")
        btn_browse.grid(row=0, column=1, sticky="e", pady=5)

        #---project name---
        tk.Label(self.main, text="Project name", bg=BG, fg=TEXT).grid(row=1, column=0, sticky="w", pady=5)

        project_list = [
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

        self.combo_project = ttk.Combobox(self.main, values=project_list, foreground=BG, width=65)
        self.combo_project.set("LAB Framework")
        self.combo_project.grid(row=1, column=1, sticky="w", pady=5, padx=5)


    def create_testcase_section(self):
        # =====================================================
        # =============== TEST CASE ============================
        # =====================================================

        self.testcase_section = ToggleSection(parent=self.main, title="Test case", bg=BG, row=3, text_color=TEXT, active=True, toggle_callback=self.toggle)
        frame_tc = self.testcase_section.frame

        #self.entry_tp = tk.Entry(frame_tc, bg=INPUT_BG, fg=BG, width=20)
        #self.entry_suite = tk.Entry(frame_tc, bg=INPUT_BG, fg=BG, width=20)

        tk.Label(frame_tc, text="Test Plan ID", bg=BG, fg=TEXT, width=LABEL_WIDTH,).grid(row=0, column=0, sticky="w")
        self.entry_tp = tk.Entry(frame_tc, bg=INPUT_BG, fg=BG, width=LABEL_WIDTH)
        self.entry_tp.grid(row=0, column=1)

        tk.Label(frame_tc, text="Test suite ID \n(es. 123,456)", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=1, column=0, sticky="w")
        self.entry_suite = tk.Entry(frame_tc, bg=INPUT_BG, fg=BG, width=LABEL_WIDTH)
        self.entry_suite.grid(row=1, column=1)

        self.testcase_section.canvas.bind("<Button-1>", lambda e: self.toggle("Testcase", self.testcase_section.canvas, frame_tc))


    def create_changelog_section(self):
        # =====================================================
        # =============== CHANGELOG ============================
        # =====================================================

        self.chanlog_section = ToggleSection(parent=self.main, title="Changelog", bg=BG, row=5, text_color=TEXT, active=False, toggle_callback=self.toggle)
        frame_ch = self.chanlog_section.frame
        

        #valori
        tk.Label(frame_ch, text="FW Version", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=0, column=0,sticky="w")
        self.entry_fw_version = tk.Entry(frame_ch, bg=INPUT_BG, fg=BG, width=20)
        self.entry_fw_version.grid(row=0, column=1)

        tk.Label(frame_ch, text="Area Path", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=1, column=0,sticky="w")
        self.entry_changelog_path = tk.Entry(frame_ch, bg=INPUT_BG, fg=BG, width=20)
        self.entry_changelog_path.grid(row=1, column=1)

        self.entry_fw_version.bind("<KeyRelease>", self.copia_changelog_in_issue)
        self.entry_changelog_path.bind("<KeyRelease>", self.copia_changelog_in_issue)

        self.chanlog_section.canvas.bind("<Button-1>", lambda e: self.toggle("Changelog", self.chanlog_section.canvas, frame_ch))


    def create_issue_section(self):
        # =====================================================
        # =============== ISSUE ================================
        # =====================================================
        self.issue_section = ToggleSection(parent=self.main, title="Issue", bg=BG, row=7, text_color=TEXT, active=False, toggle_callback=self.toggle)
        frame_is = self.issue_section.frame

        #valori
        tk.Label(frame_is, text="Found in build", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=0, column=0, sticky="w")
        self.entry_found_in_build = tk.Entry(frame_is, bg=INPUT_BG, fg=BG, width=20)
        self.entry_found_in_build.grid(row=0, column=1)

        tk.Label(frame_is, text="Area Path", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=1, column=0, sticky="w")
        self.entry_issue_path = tk.Entry(frame_is, bg=INPUT_BG, fg=BG, width=20)
        self.entry_issue_path.grid(row=1, column=1)

    
        self.issue_section.canvas.bind("<Button-1>", lambda e: self.toggle("Issue", self.issue_section.canvas, frame_is))

    def create_buttons(self):
        # =====================================================
        # BUTTON AVVIA
        # =====================================================
        tk.Button(
            self.main,
            text="Avvia",
            bg=ORANGE,
            fg="white",
            command=self.conferma,
            relief="flat",
            padx=20,
            pady=5
        ).grid(row=9, column=1, pady=20)

    def create_log_section(self):
    # =====================================================
    # TERMINALE LOG
    # =====================================================

        tk.Label(
            self.main,
            text="Log",
            bg=BG,
            fg=TEXT,
            font=("Consolas", 10, "bold")
        ).grid(row=10, column=0, sticky="w", pady=(10,0))

        self.log_widget = ScrolledText(
            self.main,
            height=10,
            width=80,
            bg="black",
            fg=TEXT,
            insertbackground="white",
            font=("Consolas", 9)
        )

        self.log_widget.grid(
            row=11,
            column=0,
            columnspan=3,
            sticky="nsew",
            pady=(5,0)
        )

        self.log.set_frame(self.log_widget)  # Attach the log widget to the logger



class ToggleSection:
    """A toggleable section in the GUI, consisting of a canvas indicator and a frame of
    input fields. Clicking the indicator toggles the section on/off, 
    changing its color and showing/hiding the frame."""

    def __init__(self, parent, title, bg, row, text_color, active = False, toggle_callback = None):
        self.parent = parent
        self.title = title
        BG = bg
        self.row = row
        TEXT_color = text_color
        self.active = active
        self.toggle_callback = toggle_callback

        self.canvas = tk.Canvas(parent, width=20, height=20, bg=bg, highlightthickness=0)
        self.canvas.grid(row=row, column=0, sticky="e", pady=(20,5))
        colore = ORANGE if active else TEXT
        self.canvas.create_oval(2, 2, 18, 18, fill=colore, tags="circle")

        tk.Label(parent, text=title, bg=bg, fg=text_color, font=("Arial", 10, "bold")).grid(row=row, column=1, sticky="w", pady=(20,5))
        self.frame = tk.Frame(parent, bg=bg)
        self.frame.grid(row=row+1, column=1, sticky="w")

        if not active:
            self.frame.grid_remove()
        
        self.canvas.bind("<Button-1>", lambda e: self.toggle())

    def toggle(self, event=None):
        """Toggle the section on/off. Updates the indicator color, shows/hides
        the section frame, and calls the provided toggle callback."""
        self.active = not self.active
        # cambia colore cerchio
        colore = ORANGE if self.active else TEXT
        self.canvas.itemconfig("circle", fill=colore)
        # mostra/nasconde frame
        if self.active:
            self.frame.grid()
        else:
            self.frame.grid_remove()
        # Call the provided callback to handle any additional logic
        if self.toggle_callback:
            self.toggle_callback(self.title, self.canvas, self.frame)

@dataclass
class GUIparameters:
    project_name: str = ""
    path: str = ""
    tp: int = 0
    TestSuite_id: list = field(default_factory=list)
    fw_version: str = ""
    changelog_path: str = ""
    found_in_build: str = ""
    issue_path: str = ""


#-------------------------------------------------------------------
#------------------------------FINE GUI-----------------------------
#-------------------------------------------------------------------

if __name__ == "__main__":
    gui = GUI()
    gui.root.mainloop()
