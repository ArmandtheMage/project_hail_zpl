
#-------------GUI----------------
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from orchestrator import ReportOrchestrator, ReportParameters


import sys
import os

# Supporto PyInstaller: usa _MEIPASS se eseguibile, altrimenti la cartella dello script
BASE_PATH = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(os.path.join(__file__, ".."))))

sys.path.append(os.path.join(BASE_PATH, "azure_project"))
sys.path.append(os.path.join(BASE_PATH, "export"))
#sys.path.append(os.path.join(BASE_PATH))

#from azure_handler import AzureHandler
#from excel_handler import ExcelHandler
import orchestrator
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
    
    def __init__(self, logger: ZPLLogger = None, azure_handler=None, excel_handler=None):
        self.parameters = ReportParameters()

        self.log = logger if logger else ZPLLogger("ZPL_Logger")

        #self.az = azure_handler if azure_handler else AzureHandler(logger=self.log)
        #self.ex = excel_handler if excel_handler else ExcelHandler(logger=self.log)
        self.orchestrator = ReportOrchestrator(logger=self.log)

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
        self.send_parameters_to_orchestrator()

    def send_parameters_to_orchestrator(self):
        """Send the collected parameters and section states to the orchestrator
        for report generation."""
        self.orchestrator.generate_report(self.parameters, self.stati)
        #fagli generare l'evento che triggera l'orchetrator - vedi riga 460


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
        #table_titles = ["id", "workItemType", "title", "state", "tags", "priority", "notes"]
        
    
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

        project_list = self.orchestrator.get_available_projects()

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


#-------------------------------------------------------------------
#------------------------------FINE GUI-----------------------------
#-------------------------------------------------------------------

if __name__ == "__main__":
    gui = GUI()
    gui.root.mainloop()
