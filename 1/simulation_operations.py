import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import math
from ui_setup import initialize_left_frame  # Importa la funzione dal file ui_setup.py

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

    # Mostra le istruzioni G-code
    with open(program_path, 'r') as file:
        gcode_instructions = file.readlines()

    app.gcode_listbox = tk.Listbox(app.left_frame)
    app.gcode_listbox.pack(padx=10, pady=10, fill="both", expand=True)
    for instruction in gcode_instructions:
        app.gcode_listbox.insert(tk.END, instruction.strip())

    # Creazione del box dedicato alla posizione
    app.position_frame = ttk.LabelFrame(app.left_frame, text="Posizione Attuale")
    app.position_frame.pack(padx=10, pady=10, fill="x", expand=True)
    
    app.position_x_label = tk.Label(app.position_frame, text="Posizione X: 0.00")
    app.position_x_label.pack(pady=5)

    app.position_y_label = tk.Label(app.position_frame, text="Posizione Y: 0.00")
    app.position_y_label.pack(pady=5)

    app.start_simulation_button = ttk.Button(app.left_frame, text="Avvia Simulazione", command=lambda: simulate_program(app, gcode_instructions))
    app.start_simulation_button.pack(pady=10)

    app.step_simulation_button = ttk.Button(app.left_frame, text="Esegui Istruzione", command=lambda: step_simulation(app))
    app.step_simulation_button.pack(pady=10)

    app.show_piece_button = ttk.Button(app.left_frame, text="Mostra Pezzo", command=lambda: show_piece(app))
    app.show_piece_button.pack(pady=10)

    app.back_button = ttk.Button(app.left_frame, text="Indietro", command=lambda: cancel_simulation(app))
    app.back_button.pack(pady=10)

    app.show_message("Premi 'Avvia Simulazione' per iniziare o 'Esegui Istruzione' per eseguire un'istruzione alla volta.")

    # Inizializza l'indice dell'istruzione corrente e la posizione
    reset_simulation(app)

    # Mostra immediatamente il triangolino alla posizione iniziale
    app.show_graph()
    initialize_graph(app)

def update_position(app, x, y):
    """Aggiorna la posizione nel grafico senza ridisegnare tutto."""
    current_x_data, current_y_data = app.line.get_xdata(), app.line.get_ydata()
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
    app.simulation_paused = False
    initialize_graph(app)
    deselect_all_instructions(app)

def initialize_graph(app):
    """Inizializza il grafico."""
    app.ax.clear()
    app.ax.set_xlabel("X")
    app.ax.set_ylabel("Y")
    app.ax.set_xlim([0, 35])
    app.ax.set_ylim([-20, 20])
    triangle = [[30, -10], [30-1, -10-1], [30+1, -10-1]]
    app.ax.add_patch(plt.Polygon(triangle, closed=True, color='green'))
    app.canvas.draw()

def simulate_program(app, gcode_instructions):
    """Simula tutte le istruzioni G-code sul grafico."""
    reset_simulation(app)
    app.gcode_instructions = gcode_instructions
    execute_next_instruction(app)

def execute_next_instruction(app):
    """Esegue la prossima istruzione G-code."""
    if app.simulation_paused or app.current_instruction_index >= len(app.gcode_instructions):
        app.show_message("Simulazione completata")
        return

    if app.current_instruction_index > 0:
        app.gcode_listbox.itemconfig(app.current_instruction_index - 1, {'bg': 'white'})

    instruction = app.gcode_instructions[app.current_instruction_index].strip()
    app.gcode_listbox.itemconfig(app.current_instruction_index, {'bg': 'yellow'})
    app.canvas.draw()
    app.root.update()

    x, y = app.current_position
    x, y, duration, feed_rate = execute_gcode_instruction(app, instruction, x, y)

    if instruction.startswith('G00') or instruction.startswith('G01'):
        if instruction.startswith('G00'):
            draw_line(app, app.current_position, [x, y], 'ro-')
            app.current_position = [x, y]
            app.canvas.draw()
            app.show_message(f"Eseguendo: {instruction}")
            app.current_instruction_index += 1
            execute_next_instruction(app)
        else:
            draw_line_with_speed(app, app.current_position, [x, y], 'bo-', feed_rate, lambda: on_line_draw_complete(app, [x, y]))
    else:
        app.current_instruction_index += 1
        execute_next_instruction(app)

def on_line_draw_complete(app, new_position):
    """Callback per quando il disegno della linea è completo."""
    app.current_position = new_position
    app.current_instruction_index += 1
    execute_next_instruction(app)

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

    x, y = app.current_position
    x, y, duration, feed_rate = execute_gcode_instruction(app, instruction, x, y)

    if instruction.startswith('G00') or instruction.startswith('G01'):
        if instruction.startswith('G00'):
            draw_line(app, app.current_position, [x, y], 'ro-')
            app.current_position = [x, y]
            app.canvas.draw()
            app.show_message(f"Eseguendo: {instruction}")
            app.current_instruction_index += 1
        else:
            draw_line_with_speed(app, app.current_position, [x, y], 'bo-', feed_rate, lambda: on_step_complete(app, [x, y]))
    else:
        app.current_instruction_index += 1

def on_step_complete(app, new_position):
    """Callback per quando il disegno della linea è completo in modalità step."""
    app.current_position = new_position
    app.show_message(f"Istruzione completata: {app.gcode_listbox.get(app.current_instruction_index - 1)}")

def execute_gcode_instruction(app, instruction, current_x, current_y):
    """Esegue una singola istruzione G-code e aggiorna la posizione."""
    x, y = current_x, current_y
    feed_rate = None
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

def draw_line_with_speed(app, start, end, style, feed_rate, callback):
    """Disegna una linea sul grafico in modo incrementale rispettando la velocità di avanzamento."""
    x0, y0 = start
    x1, y1 = end
    distance = math.sqrt((x1 - x0)**2 + (y1 - y0)**2)
    steps = int(distance * 10)
    dx = (x1 - x0) / steps
    dy = (y1 - y0) / steps
    delay = int((distance / feed_rate) / steps * 1000)

    def draw_step(step):
        if step > steps:
            callback()
            return
        app.ax.plot([x0 + dx * (step - 1), x0 + dx * step], [y0 + dy * (step - 1), y0 + dy * step], style)
        app.canvas.draw()
        app.root.after(delay, lambda: draw_step(step + 1))
    
    draw_step(1)

def draw_line(app, start, end, style):
    """Disegna una linea sul grafico."""
    app.ax.plot([start[0], end[0]], [start[1], end[1]], style)
    app.canvas.draw()

def deselect_all_instructions(app):
    """Deseleziona tutte le istruzioni nella Listbox."""
    app.gcode_listbox.selection_clear(0, tk.END)

def cancel_simulation(app):
    """Interrompe la simulazione e torna alla schermata principale."""
    app.simulation_stopped = True
    app.clear_left_frame()
    initialize_left_frame(app)

def show_piece(app):
    """Mostra il pezzo attuale."""
    app.show_message("Funzionalità 'Mostra Pezzo' non ancora implementata.")
