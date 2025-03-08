import os
import re
import tkinter as tk
from tkinter import ttk

def load_existing_programs(app):
    """Carica i programmi G-code dalla cartella corrente."""
    current_dir = os.path.dirname(__file__)
    for file_name in os.listdir(current_dir):
        if file_name.endswith('.gcode'):
            file_path = os.path.join(current_dir, file_name)
            app.program_listbox.insert(tk.END, file_path)

def create_new_program(app):
    """Mostra i campi per la creazione di un nuovo programma."""
    app.clear_left_frame()
    show_new_program_form(app)
    app.hide_graph()

def show_new_program_form(app):
    """Mostra il form per creare un nuovo programma."""
    ttk.Label(app.left_frame, text="Nome del Programma:").pack(pady=10)
    app.program_name_entry = ttk.Entry(app.left_frame)
    app.program_name_entry.pack(pady=10)

    ttk.Label(app.left_frame, text="Istruzioni G-code:").pack(pady=10)
    app.gcode_text = tk.Text(app.left_frame, width=40, height=10)
    app.gcode_text.pack(pady=10)

    app.save_button = ttk.Button(app.left_frame, text="Salva Programma", command=app.save_new_program)
    app.save_button.pack(pady=10)

    app.cancel_button = ttk.Button(app.left_frame, text="Annulla", command=app.cancel_new_program)
    app.cancel_button.pack(pady=10)

    app.show_message("Inserisci le istruzioni G-code e premi 'Salva Programma'.")

def edit_selected_program(app):
    """Mostra i campi per modificare un programma selezionato."""
    selected_program_index = app.program_listbox.curselection()
    if not selected_program_index:
        app.show_message("Errore: Nessun programma selezionato", "error")
        return

    program_path = app.program_listbox.get(selected_program_index)
    if program_path.endswith('.gcode'):
        edit_program(app, program_path)
    else:
        app.show_message("Errore: Seleziona un file G-code", "error")

def edit_program(app, program_path):
    """Mostra il form per modificare un programma esistente."""
    app.clear_left_frame()
    show_edit_program_form(app, program_path)
    app.hide_graph()

def show_edit_program_form(app, program_path):
    """Mostra il form per modificare un programma esistente."""
    ttk.Label(app.left_frame, text=f"Modifica Programma: {os.path.basename(program_path)}").pack(pady=10)

    with open(program_path, 'r') as file:
        gcode_instructions = file.read()

    app.gcode_text = tk.Text(app.left_frame, width=40, height=10)
    app.gcode_text.insert(tk.END, gcode_instructions)
    app.gcode_text.pack(pady=10)

    app.save_button = ttk.Button(app.left_frame, text="Salva Modifiche", command=lambda: save_edited_program(app, program_path))
    app.save_button.pack(pady=10)

    app.cancel_button = ttk.Button(app.left_frame, text="Annulla", command=app.cancel_new_program)
    app.cancel_button.pack(pady=10)

    app.show_message("Modifica le istruzioni G-code e premi 'Salva Modifiche'.")

def save_new_program(app):
    """Salva un nuovo programma G-code."""
    program_name = app.program_name_entry.get()
    gcode_instructions = app.gcode_text.get("1.0", tk.END).strip()

    if not program_name or not gcode_instructions:
        app.show_message("Errore: Nome del programma e istruzioni G-code non possono essere vuoti.", "error")
        return

    valid, error_message = validate_gcode(gcode_instructions)
    if not valid:
        app.show_message(f"Errore: {error_message}", "error")
        return

    gcode_file_path = os.path.join(os.path.dirname(__file__), f"{program_name}.gcode")
    with open(gcode_file_path, 'w') as gcode_file:
        gcode_file.write(gcode_instructions)

    app.initialize_left_frame()
    app.load_existing_programs()
    app.program_listbox.insert(tk.END, gcode_file_path)
    app.show_message(f"Nuovo programma creato in {gcode_file_path}", "info")
    app.show_graph()

def save_edited_program(app, program_path):
    """Salva le modifiche a un programma G-code esistente."""
    gcode_instructions = app.gcode_text.get("1.0", tk.END).strip()

    if not gcode_instructions:
        app.show_message("Errore: Le istruzioni G-code non possono essere vuote.", "error")
        return

    valid, error_message = validate_gcode(gcode_instructions)
    if not valid:
        app.show_message(f"Errore: {error_message}", "error")
        return

    with open(program_path, 'w') as gcode_file:
        gcode_file.write(gcode_instructions)

    app.initialize_left_frame()
    app.load_existing_programs()
    app.show_message(f"Modifiche salvate in {program_path}", "info")
    app.show_graph()

def validate_gcode(gcode):
    """Valida le istruzioni G-code."""
    valid_commands = {"G0", "G1", "G2", "G3", "G4", "G17", "G18", "G19", "G20", "G21", "G28", "G30", "G90", "G91", "G92", "G00", "G01", "M30"}
    for line_num, line in enumerate(gcode.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        match = re.match(r'^(G\d+|M\d+)', line)
        if match and match.group(1) in valid_commands:
            continue
        return False, f"L'istruzione '{line}' alla linea {line_num} non è valida."
    return True, ""

def cancel_new_program(app):
    """Annulla la creazione o modifica di un programma."""
    app.initialize_left_frame()
    app.load_existing_programs()
    app.show_graph()