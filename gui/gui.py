
#-------------GUI----------------
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import filedialog

LABEL_WIDTH = 15
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "azure_project"))
sys.path.append(os.path.join(os.getcwd(), "export"))


from azure_handler import AzureHandler
from excel_handler import ExcelHandler

print("stiamo aprendo la GUI!")
def apri_gui():
    BG = "#242424"
    TEXT = "#cecece"
    ORANGE = "#e84e0f"
    INPUT_BG = "#ffffff"

    risultati = {}

    az = AzureHandler()
    ex = ExcelHandler()
    
    def conferma():
        #valori comuni
        risultati["project_name"] = combo_project.get()
        risultati["path"] = entry_path.get()

        #issue
        risultati["tp"] = int(entry_tp.get()) if entry_tp.get() else 0
        
        # lista test suite (separate da virgola)
        suite_input = entry_suite.get()
        if suite_input.strip():
            risultati["TestSuite_id"] = [int(x.strip()) for x in suite_input.split(",")]
        else:
            risultati["TestSuite_id"] = []

        # changelog
        risultati["fw_version"] = entry_fw_version.get()
        risultati["changelog_path"] = entry_changelog_path.get()

        # issue
        risultati["found_in_build"] = entry_found_in_build.get()
        risultati["issue_path"] = entry_issue_path.get()

        # id, title, workitemtype, state, tags
        table_titles = ["id", "workItemType", "title", "state", "tags", "notes"]
        
        if stati["Testcase"]:
            testcase_titles = ["suiteId", "testSuite", "testCaseId", "testCase", "outcome", "configuration", "configurationValue", "note"]
            data = az.get_test_data(
                project_id=risultati["project_name"],
                plan_id=risultati["tp"],
                suites_id=risultati["TestSuite_id"]
            )
            id_trest_suite  = ex.make_new_sheet("Testcase")
            ex.set_common_header()
            ex.set_datasheet(
                section="ELENCO TEST CASE / TEST CASE LIST",
                table_titles=testcase_titles,
                data=data
            )
            ex.color_state(column="F")  # per il tc column E is the state column

        if stati["Issue"]:
            query_issue = az.make_query(
                project_name=risultati["project_name"],
                area_path=risultati["issue_path"],
                found_in_build=risultati["found_in_build"]
            ).work_items
            az.print_work_item(query_issue)

            ex.make_new_sheet("Issue")
            ex.set_common_header()
            wi_list = []
            for wi_ref in query_issue:
                wi_list.append(az.work_item_tracking_client.get_work_item(wi_ref.id))
            ex.set_datasheet(
                section="ELENCO ISSUE E BUG / ISSUE AND BUG LIST",
                table_titles=table_titles,
                data=[(wi.id, wi.fields["System.WorkItemType"], wi.fields["System.Title"], wi.fields["System.State"], wi.fields.get("System.Tags", "")) for wi in wi_list]
            )
            ex.color_state(column="E")  # per il tc column E is the state column

        if stati["Changelog"]:
            query_changelog = az.make_query(
                project_name=risultati["project_name"],
                area_path=risultati["changelog_path"],
                product_version=risultati["fw_version"]
            ).work_items
            az.print_work_item(query_changelog)

            ex.make_new_sheet("Changelog")
            ex.set_common_header()
            wi_list = []
            for wi_ref in query_changelog:
                wi_list.append(az.work_item_tracking_client.get_work_item(wi_ref.id))
            ex.set_datasheet(
                section="ELENCO CHANGELOG / CHANGELOG LIST",
                table_titles=table_titles,
                data=[(wi.id, wi.fields["System.WorkItemType"], wi.fields["System.Title"], wi.fields["System.State"], wi.fields.get("System.Tags", "")) for wi in wi_list]
            )
            ex.color_state(column="E")  # per il tc column E is the state column
        save_path = risultati['changelog_path'].split('\\')[-1]
        ex.save(filename=f"{save_path}_{risultati['fw_version']}", parent_path=risultati["path"])
        root.destroy()

    # --- TOGGLE ---
    stati = {
        "Testcase": True,
        "Changelog": False,
        "Issue": False
    }

    def toggle(sezione, canvas, frame):
        stati[sezione] = not stati[sezione]

        # cambia colore cerchio
        colore = ORANGE if stati[sezione] else INPUT_BG
        canvas.itemconfig("circle", fill=colore)

        # mostra/nasconde frame
        if stati[sezione]:
            frame.grid()
            if sezione == "Issue":
                copia_changelog_in_issue
        else:
            frame.grid_remove()

            #per eliminare i valori dei campi quando si disattiva la sezione
            if sezione == "Testcase":
                entry_tp.delete(0, tk.END)
                entry_suite.delete(0, tk.END)
            
            if sezione == "Changelog":
                entry_fw_version.delete(0, tk.END)
                entry_changelog_path.delete(0, tk.END)

            if sezione == "Issue":
                entry_found_in_build.delete(0, tk.END)
                entry_issue_path.delete(0, tk.END)

    
    def seleziona_cartella():
        cartella = filedialog.askdirectory(
            initialdir=entry_path.get() if entry_path.get() else "/",
            title="Seleziona cartella"
        )

        if cartella:
            entry_path.delete(0, tk.END)
            entry_path.insert(0, cartella)
        
    def copia_changelog_in_issue(event:None):
        entry_found_in_build.delete(0, tk.END)
        entry_found_in_build.insert(0, entry_fw_version.get())

        entry_issue_path.delete(0, tk.END)
        entry_issue_path.insert(0, entry_changelog_path.get())


    # --- GUI ---
    root = tk.Tk()
    root.title("Parametri Report")
    root.geometry("500x500")
    root.configure(bg=BG)
    


    main = tk.Frame(root, bg=BG)
    main.pack(padx=20, pady=20, fill="both", expand=True)

    # -------- TOP FIELDS --------

    # ---------Path--------- 
    tk.Label(main, text="Path file", bg=BG, fg=TEXT).grid(row=0, column=0, sticky="w", pady=5)
    entry_path = tk.Entry(main, bg=INPUT_BG, fg=BG, width=43)
    entry_path.insert(0, "C:\\Users\\silvala\\OneDrive - Gewiss S.p.A\\Documenti\\ZPL\\")
    entry_path.grid(row=0, column=1, sticky="w", pady=5,padx=5)
    
    btn_browse = tk.Button(main,text="📁",command=seleziona_cartella, bg=BG,fg="white", width=3,relief="flat")
    btn_browse.grid(row=0, column=2, sticky="w")


    # ---------Project name---------
    tk.Label(main, text="Project name", bg=BG, fg=TEXT).grid(row=1, column=0, sticky="w", pady=5)

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

    combo_project = ttk.Combobox(main, values=project_list, foreground=BG, width=40)
    combo_project.set("LAB Framework")
    combo_project.grid(row=1, column=1, sticky="w", pady=5, padx=5)


    # =====================================================
    # =============== TEST CASE ============================
    # =====================================================

    canvas_tc = tk.Canvas(main, width=20, height=20, bg=BG, highlightthickness=0)
    canvas_tc.grid(row=3, column=0, sticky="e",pady=(20,5))

    circle_tc = canvas_tc.create_oval(2, 2, 18, 18, fill=ORANGE, tags="circle")

    tk.Label(main, text="Test case", bg=BG, fg=TEXT, font=("Arial", 10, "bold")).grid(row=3, column=1, sticky="w",pady=(20,5))
    frame_tc = tk.Frame(main, bg=BG)
    frame_tc.grid(row=4, column=1, sticky="w")

    tk.Label(frame_tc, text="Test Plan ID", bg=BG, fg=TEXT, width=LABEL_WIDTH,).grid(row=0, column=0, sticky="w")
    entry_tp = tk.Entry(frame_tc, bg=INPUT_BG, fg=BG, width=20)
    entry_tp.grid(row=0, column=1)

    tk.Label(frame_tc, text="Test suite ID \n(es. 123,456)", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=1, column=0, sticky="w")
    entry_suite = tk.Entry(frame_tc, bg=INPUT_BG, fg=BG, width=20)#
    entry_suite.grid(row=1, column=1)

    canvas_tc.bind("<Button-1>", lambda e: toggle("Testcase", canvas_tc, frame_tc))

    # =====================================================
    # =============== CHANGELOG ============================
    # =====================================================
    canvas_ch = tk.Canvas(main, width=20, height=20, bg=BG, highlightthickness=0)
    canvas_ch.grid(row=5, column=0, sticky="e",pady=(20,5))

    canvas_ch.create_oval(2, 2, 18, 18, fill=TEXT, tags="circle")

    tk.Label(main, text="Changelog", bg=BG, fg=TEXT, font=("Arial", 10, "bold")).grid(row=5, column=1, sticky="w", pady=(20,5))

    frame_ch = tk.Frame(main, bg=BG)
    frame_ch.grid(row=6, column=1, sticky="w")
    frame_ch.grid_remove()

    #valori
    tk.Label(frame_ch, text="FW Version", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=0, column=0,sticky="w")
    entry_fw_version = tk.Entry(frame_ch, bg=INPUT_BG, fg=BG, width=20)
    entry_fw_version.grid(row=0, column=1)

    tk.Label(frame_ch, text="Area Path", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=1, column=0,sticky="w")
    entry_changelog_path = tk.Entry(frame_ch, bg=INPUT_BG, fg=BG, width=20)
    entry_changelog_path.grid(row=1, column=1)

    entry_fw_version.bind("<KeyRelease>", copia_changelog_in_issue)
    entry_changelog_path.bind("<KeyRelease>", copia_changelog_in_issue)

    canvas_ch.bind("<Button-1>", lambda e: toggle("Changelog", canvas_ch, frame_ch))

    # =====================================================
    # =============== ISSUE ================================
    # =====================================================
    canvas_is = tk.Canvas(main, width=20, height=20, bg=BG, highlightthickness=0)
    canvas_is.grid(row=7, column=0, sticky="e",pady=(20,5))

    canvas_is.create_oval(2, 2, 18, 18, fill=TEXT, tags="circle")

    tk.Label(main, text="Issue", bg=BG, fg=TEXT, font=("Arial", 10, "bold")).grid(row=7, column=1, sticky="w", pady=(20,5))

    frame_is = tk.Frame(main, bg=BG)
    frame_is.grid(row=8, column=1, sticky="w")
    frame_is.grid_remove()

    tk.Label(frame_is, text="Found in build", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=0, column=0, sticky="w")
    entry_found_in_build = tk.Entry(frame_is, bg=INPUT_BG, fg=BG, width=20)
    entry_found_in_build.grid(row=0, column=1)

    tk.Label(frame_is, text="Area Path", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=1, column=0, sticky="w")
    entry_issue_path = tk.Entry(frame_is, bg=INPUT_BG, fg=BG, width=20)
    entry_issue_path.grid(row=1, column=1)

    canvas_is.bind("<Button-1>", lambda e: toggle("Issue", canvas_is, frame_is))

    # =====================================================
    # BUTTON AVVIA
    # =====================================================
    tk.Button(
        main,
        text="Avvia",
        bg=ORANGE,
        fg="white",
        command=conferma,
        relief="flat",
        padx=20,
        pady=5
    ).grid(row=9, column=1, pady=20)

    root.mainloop()
    return risultati


#-------------------------------------------------------------------
#------------------------------FINE GUI-----------------------------
#-------------------------------------------------------------------

if __name__ == "__main__":
    parametri = apri_gui()
