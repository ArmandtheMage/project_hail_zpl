

from ast import main
from py_compile import main
import sys

#-------------GUI----------------
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import filedialog

LABEL_WIDTH = 15

print("stiamo aprendo la GUI!")
def apri_gui():
    BG = "#242424"
    TEXT = "#cecece"
    ORANGE = "#e84e0f"
    INPUT_BG = "#ffffff"

    risultati = {}

    
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
        else:
            frame.grid_remove()

            #per eliminare i valori dei campi quando si disattiva la sezione
            if sezione == "Testcase":
                entry_tp.delete(0, tk.END)
                entry_suite.delete(0, tk.END)

    
    def seleziona_cartella():
        cartella = filedialog.askdirectory(
            initialdir=entry_path.get() if entry_path.get() else "/",
            title="Seleziona cartella"
        )

        if cartella:
            entry_path.delete(0, tk.END)
            entry_path.insert(0, cartella)

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
    entry_path.insert(0, "C:\\Users\\silvala\\OneDrive - Gewiss S.p.A\\Documenti\\ZPL\\eracle\\")
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
        "Joinon",
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

    tk.Label(frame_ch, text="FW Version", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=0, column=0,sticky="w")
    entry_fw_version = tk.Entry(frame_ch, bg=INPUT_BG, fg=BG, width=20)
    entry_fw_version.grid(row=0, column=1)

    tk.Label(frame_ch, text="Path file", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=1, column=0,sticky="w")
    entry_changelog_path = tk.Entry(frame_ch, bg=INPUT_BG, fg=BG, width=20)
    entry_changelog_path.grid(row=1, column=1)

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


    tk.Label(frame_is, text="Path file", bg=BG, fg=TEXT, width=LABEL_WIDTH).grid(row=1, column=0, sticky="w")
    entry_issue_path = tk.Entry(frame_is, bg=INPUT_BG, fg=BG, width=20)
    entry_issue_path.grid(row=1, column=1)

    canvas_is.bind("<Button-1>", lambda e: toggle("Issue", canvas_is, frame_is))

    # =====================================================
    # BUTTON
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

parametri = apri_gui()