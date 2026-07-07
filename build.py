"""
Script per creare l'eseguibile con PyInstaller.
Scansiona automaticamente le cartelle del progetto e le include nel build.
"""
import os
import subprocess
import sys

# Cartella root del progetto
ROOT = os.path.dirname(os.path.abspath(__file__))

# Cartelle da includere come dati (moduli + risorse)
CARTELLE_DA_INCLUDERE = ["azure_project", "export", "gui"]

# Cartelle/file da escludere dalla scansione
ESCLUDI = {"__pycache__", ".git", "build", "dist", "venv", ".venv", "env"}

# Nome dell'eseguibile finale
NOME_EXE = "HailZPL"

# Entry point
ENTRY_POINT = "run.py"


def trova_dati():
    """Trova tutte le cartelle da aggiungere come --add-data."""
    add_data = []
    for cartella in CARTELLE_DA_INCLUDERE:
        percorso = os.path.join(ROOT, cartella)
        if os.path.isdir(percorso):
            # Aggiunge la cartella intera con il suo path relativo
            add_data.append(f"{percorso}{os.pathsep}{cartella}")
    return add_data


def trova_hidden_imports():
    """Trova i moduli Python nelle cartelle del progetto per --hidden-import."""
    hidden = []
    for cartella in CARTELLE_DA_INCLUDERE:
        percorso = os.path.join(ROOT, cartella)
        if not os.path.isdir(percorso):
            continue
        for file in os.listdir(percorso):
            if file.endswith(".py") and file != "__init__.py":
                modulo = f"{cartella}.{file[:-3]}"
                hidden.append(modulo)
    return hidden


def build():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", NOME_EXE,
    ]

    # Aggiungi dati
    for dato in trova_dati():
        cmd.extend(["--add-data", dato])

    # Aggiungi hidden imports
    for modulo in trova_hidden_imports():
        cmd.extend(["--hidden-import", modulo])

    # Entry point
    cmd.append(os.path.join(ROOT, ENTRY_POINT))

    print("Comando PyInstaller:")
    print(" ".join(f'"{c}"' if " " in c else c for c in cmd))
    print()

    risultato = subprocess.run(cmd, cwd=ROOT)
    if risultato.returncode == 0:
        print(f"\nBuild completato! Eseguibile in: dist/{NOME_EXE}.exe")
    else:
        print(f"\nErrore durante il build (exit code: {risultato.returncode})")
    
    return risultato.returncode


if __name__ == "__main__":
    sys.exit(build())
