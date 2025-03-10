import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import math
from ui_setup import initialize_left_frame

def prepare_simulation(app):
    """Prepara la simulazione delle istruzioni G-code."""
    selected_program_index = app.program_listbox.curselection()
    if not selected_program_index:
        app.show_message("Errore: Nessun programma selezionato", "error")
        return

    program_path = app.program_listbox.get(selected_program_index)
    if not program_path.endswith('.gcode'):
        app.show_message("Errore: Seleziona un file G-code", "error")
        return

    app.clear_left_frame()
    with open(program_path, 'r') as file:
        gcode_instructions = file.readlines()

    app.gcode_listbox = tk.Listbox(app.left_frame)
    app.gcode_listbox.pack(padx=10, pady=10, fill="both", expand=True)
    for instruction in gcode_instructions:
        app.gcode_listbox.insert(tk.END, instruction.strip())

    create_position_frame(app)
    create_control_buttons(app, gcode_instructions)

    reset_simulation(app)
    app.show_graph()
    initialize_graph(app)

def create_position_frame(app):
    """Crea il frame dedicato alla posizione attuale."""
    app.position_frame = ttk.LabelFrame(app.left_frame, text="Posizione Attuale")
    app.position_frame.pack(padx=10, pady=10, fill="x", expand=True)
    app.position_x_label = tk.Label(app.position_frame, text="Posizione X: 0.00")
    app.position_x_label.pack(pady=5)
    app.position_y_label = tk.Label(app.position_frame, text="Posizione Y: 0.00")
    app.position_y_label.pack(pady=5)

def create_control_buttons(app, gcode_instructions):
    """Crea i pulsanti di controllo per la simulazione."""
    app.start_simulation_button = ttk.Button(app.left_frame, text="Avvia Simulazione", command=lambda: simulate_program(app, gcode_instructions))
    app.start_simulation_button.pack(pady=10)
    app.step_simulation_button = ttk.Button(app.left_frame, text="Esegui Istruzione", command=lambda: step_simulation(app))
    app.step_simulation_button.pack(pady=10)
    app.show_piece_button = ttk.Button(app.left_frame, text="Mostra Pezzo", command=lambda: show_piece(app))
    app.show_piece_button.pack(pady=10)
    app.back_button = ttk.Button(app.left_frame, text="Indietro", command=lambda: cancel_simulation(app))
    app.back_button.pack(pady=10)
    app.show_message("Premi 'Avvia Simulazione' per iniziare o 'Esegui Istruzione' per eseguire un'istruzione alla volta.")

def update_position(app, x, y):
    """Aggiorna la posizione nel grafico senza ridisegnare tutto."""
    current_x_data, current_y_data = list(app.line.get_xdata()), list(app.line.get_ydata())
    current_x_data.append(x)
    current_y_data.append(y)
    app.line.set_data(current_x_data, current_y_data)
    app.triangle.set_xy([[x, y], [x-1, y-1], [x+1, y-1]])
    app.canvas.draw()
    app.current_position = [x, y]
    app.position_x_label.config(text=f"Posizione X: {x:.2f}")
    app.position_y_label.config(text=f"Posizione Y: {y:.2f}")

def reset_simulation(app):
    """Resetta la simulazione alle impostazioni iniziali."""
    app.current_instruction_index = 0
    app.current_position = [30, -10]
    app.flipped_position = None  # Variabile di stato per tracciare la posizione ribaltata
    app.piece_shown = False  # Variabile di stato per tracciare se il pezzo è stato visualizzato
    initialize_graph(app, reset=True)
    deselect_all_instructions(app)

def initialize_graph(app, reset=False):
    """Inizializza il grafico."""
    if reset or not hasattr(app, 'line'):
        app.ax.clear()
        app.ax.set_xlabel("X")
        app.ax.set_ylabel("Y")
        app.ax.set_xlim([0, 35])
        app.ax.set_ylim([-10, 10])
        app.triangle = plt.Polygon([[30, -10], [29, -11], [31, -11]], closed=True, color='green')
        app.ax.add_patch(app.triangle)
        app.line, = app.ax.plot([], [], 'bo-')
    else:
        app.line.set_data([], [])
    app.canvas.draw()

def simulate_program(app, gcode_instructions):
    """Simula tutte le istruzioni G-code sul grafico."""
    reset_simulation(app)
    app.gcode_instructions = gcode_instructions
    execute_all_instructions(app)

def execute_all_instructions(app):
    """Esegue tutte le istruzioni G-code in sequenza."""
    while app.current_instruction_index < len(app.gcode_instructions):
        step_simulation(app)
    app.show_message("Simulazione completata")
    deselect_all_instructions(app)

def step_simulation(app):
    """Esegue un'istruzione G-code alla volta sul grafico."""
    if app.current_instruction_index >= app.gcode_listbox.size():
        app.show_message("Tutte le istruzioni sono state eseguite")
        reset_simulation(app)
        return
    if app.current_instruction_index > 0:
        app.gcode_listbox.itemconfig(app.current_instruction_index - 1, {'bg': 'white'})
    instruction = app.gcode_listbox.get(app.current_instruction_index).strip()
    app.gcode_listbox.itemconfig(app.current_instruction_index, {'bg': 'yellow'})
    app.canvas.draw()
    app.root.update()
    
    # Salva la posizione normale di partenza
    normal_start_position = app.current_position[:]
    x, y = normal_start_position

    # Esegui l'istruzione normale
    x, y, duration, feed_rate = execute_gcode_instruction(app, instruction, x, y)
    draw_line(app, normal_start_position, [x, y], 'bo-')
    normal_end_position = [x, y]
    
    # Aggiorna alla posizione di arrivo normale
    update_position(app, x, y)

    if app.piece_shown:
        # Calcola la posizione ribaltata di partenza e di arrivo
        flipped_start_y = -normal_start_position[1]
        flipped_end_y = -normal_end_position[1]
        flipped_start_position = [normal_start_position[0], flipped_start_y]
        flipped_end_position = [normal_end_position[0], flipped_end_y]
        
        # Esegui l'istruzione ribaltata partendo dalla posizione ribaltata
        draw_line(app, flipped_start_position, flipped_end_position, 'go-')
        
        # Torna alla posizione di arrivo normale
        update_position(app, normal_end_position[0], normal_end_position[1])
    app.current_instruction_index += 1
    if app.current_instruction_index >= app.gcode_listbox.size():
        app.show_message("Tutte le istruzioni sono state eseguite")
        app.gcode_listbox.itemconfig(app.current_instruction_index - 1, {'bg': 'white'})
        deselect_all_instructions(app)

def execute_gcode_instruction(app, instruction, current_x, current_y):
    """Esegue una singola istruzione G-code e aggiorna la posizione."""
    x, y, feed_rate = current_x, current_y, None
    duration = 0
    if instruction.startswith('G1') or instruction.startswith('G0'):
        parts = instruction.split()
        for part in parts:
            if part.startswith('X'):
                x = float(part[1:])
            elif part.startswith('Y'):
                y = float(part[1:])
            elif part.startswith('F'):
                feed_rate = float(part[1:])
        if feed_rate:
            distance = math.sqrt((x - current_x)**2 + (y - current_y)**2)
            duration = distance / feed_rate
    return x, y, duration, feed_rate

def draw_line(app, start, end, style):
    """Disegna una linea sul grafico."""
    app.ax.plot([start[0], end[0]], [start[1], end[1]], style)
    app.canvas.draw()

def deselect_all_instructions(app):
    """Deseleziona tutte le istruzioni nella Listbox."""
    app.gcode_listbox.selection_clear(0, tk.END)

def cancel_simulation(app):
    """Interrompe la simulazione e torna alla schermata principale."""
    clear_graph(app)
    app.clear_left_frame()
    initialize_left_frame(app)

def clear_graph(app):
    """Pulisce il grafico e lo reimposta alle dimensioni di default."""
    initialize_graph(app, reset=True)

def show_piece(app):
    """Mostra la lavorazione fatta fino ad ora sul pezzo ribaltando le coordinate Y."""
    current_x_data, current_y_data = list(app.line.get_xdata()), list(app.line.get_ydata())
    if not current_x_data or not current_y_data:
        app.show_message("Nessuna lavorazione da mostrare")
        return
    for i in range(len(current_x_data) - 1):
        draw_line(app, [current_x_data[i], -current_y_data[i]], [current_x_data[i+1], -current_y_data[i+1]], 'go-')
    app.piece_shown = True  # Imposta la variabile di stato su True
    app.flipped_position = [current_x_data[-1], -current_y_data[-1]]  # Salva la posizione ribaltata finale
    app.canvas.draw()
