import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D
import math

class CNCApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Impostazioni della finestra principale
        self.title("Simulazione CNC")
        self.geometry("800x600")

        # Frame sinistro per la lista dei programmi e i pulsanti
        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        # Lista dei programmi (Listbox)
        self.program_listbox = tk.Listbox(self.left_frame)
        self.program_listbox.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")

        # Creazione dei label per la posizione
        self.position_x_label = tk.Label(self.left_frame, text="Posizione X: 0.00")
        self.position_x_label.grid(row=1, column=0, padx=10, pady=5)

        self.position_y_label = tk.Label(self.left_frame, text="Posizione Y: 0.00")
        self.position_y_label.grid(row=2, column=0, padx=10, pady=5)

        # Frame dei pulsanti (per evitare sovrapposizioni)
        button_frame = tk.Frame(self.left_frame)
        button_frame.grid(row=3, column=0, pady=10)

        self.start_simulation_button = ttk.Button(button_frame, text="Avvia Simulazione", command=lambda: prepare_simulation(self))
        self.start_simulation_button.grid(row=0, column=0, padx=5)

        self.step_simulation_button = ttk.Button(button_frame, text="Esegui Istruzione", command=lambda: step_simulation(self))
        self.step_simulation_button.grid(row=0, column=1, padx=5)

        self.pause_simulation_button = ttk.Button(button_frame, text="Pausa", command=lambda: pause_simulation(self))
        self.pause_simulation_button.grid(row=0, column=2, padx=5)

        self.resume_simulation_button = ttk.Button(button_frame, text="Riprendi", command=lambda: resume_simulation(self))
        self.resume_simulation_button.grid(row=0, column=3, padx=5)

        self.back_button = ttk.Button(button_frame, text="Indietro", command=self.cancel_new_program)
        self.back_button.grid(row=0, column=4, padx=5)

        self.show_message("Premi 'Avvia Simulazione' per iniziare o 'Esegui Istruzione' per eseguire un'istruzione alla volta.")

        # Posizione iniziale
        self.current_position = [30, -10]

        # Impostazioni per il grafico
        self.figure, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky="nswe")

        # Configura il layout (per far espandere le righe e le colonne)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

    def show_message(self, message, message_type="info"):
        """Funzione per mostrare messaggi."""
        print(f"[{message_type}] {message}")

    def cancel_new_program(self):
        """Funzione per annullare il programma."""
        print("Programma annullato.")

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
    app.gcode_listbox.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")
    for instruction in gcode_instructions:
        app.gcode_listbox.insert(tk.END, instruction.strip())

    # Inizializza la lista delle istruzioni G-code per la simulazione
    app.gcode_instructions = gcode_instructions
    app.current_instruction_index = 0
    app.simulation_paused = False

    # Inizializza il grafico
    initialize_graph(app)

    app.show_message("Premi 'Avvia Simulazione' per iniziare o 'Esegui Istruzione' per eseguire un'istruzione alla volta.")
    reset_simulation(app)

def update_position(app, x, y):
    """Aggiorna la posizione nel grafico senza ridisegnare tutto."""
    # Aggiungi nuovi dati alla linea esistente
    current_x_data, current_y_data = app.line.get_xdata(), app.line.get_ydata()
    
    # Aggiorna le liste con i nuovi dati
    current_x_data += [x]  # Aggiungi la nuova coordinata X
    current_y_data += [y]  # Aggiungi la nuova coordinata Y

    # Aggiorna la posizione del triangolo (simula il movimento del CNC)
    app.triangle.set_xy([[x, y], [x-1, y-1], [x+1, y-1]])

    # Ridisegna solo la linea e il triangolo
    app.canvas.draw()

    # Aggiorna la posizione corrente
    app.current_position = [x, y]

    # Aggiorna le label con la nuova posizione
    app.position_x_label.config(text=f"Posizione X: {x:.2f}")
    app.position_y_label.config(text=f"Posizione Y: {y:.2f}")

    """Aggiorna la posizione nel grafico senza ridisegnare tutto."""
    # Aggiungi nuovi dati alla linea esistente
    current_x_data, current_y_data = app.line.get_xdata(), app.line.get_ydata()
    
    # Aggiorna le liste con i nuovi dati
    current_x_data += [x]  # Aggiungi la nuova coordinata X
    current_y_data += [y]  # Aggiungi la nuova coordinata Y

    # Aggiorna la posizione del triangolo (simula il movimento del CNC)
    app.triangle.set_xy([[x, y], [x-1, y-1], [x+1, y-1]])

    # Ridisegna solo la linea e il triangolo
    app.canvas.draw()

    # Aggiorna la posizione corrente
    app.current_position = [x, y]

    # Aggiorna le label con la nuova posizione
    app.position_x_label.config(text=f"Posizione X: {x:.2f}")
    app.position_y_label.config(text=f"Posizione Y: {y:.2f}")

def reset_simulation(app):
    """Resetta la simulazione alle impostazioni iniziali."""
    app.current_instruction_index = 0
    app.current_position = [30, -10]  # Posizione iniziale
    app.simulation_paused = False
    
    # Resetta il grafico
    initialize_graph(app)
    
    # Resetta la linea di movimento
    if hasattr(app, 'line'):  # Controlla se la linea esiste
        app.line.set_xdata([])  # Resetta le coordinate X
        app.line.set_ydata([])  # Resetta le coordinate Y
        app.canvas.draw()  # Rende effettivo il reset

def initialize_graph(app):
    """Inizializza il grafico."""
    app.ax.set_xlabel("X")
    app.ax.set_ylabel("Y")
    app.ax.set_xlim([0, 35])
    app.ax.set_ylim([-20, 20])

    # Crea una linea vuota (inizialmente senza dati)
    app.line = Line2D([], [], color='blue', marker='o', markersize=5, linestyle='-', linewidth=2)
    app.ax.add_line(app.line)  # Aggiungi la linea al grafico

    # Crea il triangolo (posizione iniziale)
    app.triangle = plt.Polygon([[30, -10], [30-1, -10-1], [30+1, -10-1]], closed=True, color='green')
    app.ax.add_patch(app.triangle)

    # Disegna il grafico iniziale
    app.canvas.draw()

def step_simulation(app):
    """Esegue una singola istruzione G-code alla volta."""
    if app.simulation_paused or app.current_instruction_index >= len(app.gcode_instructions):
        return

    # Esegui la prossima istruzione G-code
    instruction = app.gcode_instructions[app.current_instruction_index].strip()
    x, y = app.current_position
    x, y, duration, feed_rate = execute_gcode_instruction(app, instruction, x, y)

    # Aggiorna la posizione nel grafico
    update_position(app, x, y)

    # Aumenta l'indice per la prossima istruzione
    app.current_instruction_index += 1

def execute_gcode_instruction(app, instruction, current_x, current_y):
    """Esegue una singola istruzione G-code e aggiorna la posizione."""
    x, y = current_x, current_y
    feed_rate = None
    duration = 0  # Inizializza la durata

    if instruction.startswith('G1') or instruction.startswith('G0'):
        parts = instruction.split()
        for part in parts:
            if part.startswith('X'):
                x = float(part[1:])  # Aggiorna la coordinata X
            elif part.startswith('Y'):
                y = float(part[1:])  # Aggiorna la coordinata Y
            elif part.startswith('F'):
                feed_rate = float(part[1:])
                
        # Calcola la durata basata sulla velocità di avanzamento (feed rate)
        if feed_rate:
            distance = math.sqrt((x - current_x)**2 + (y - current_y)**2)
            duration = distance / feed_rate
    return x, y, duration, feed_rate

def simulate_program(app, gcode_instructions):
    """Esegue tutte le istruzioni G-code della simulazione senza interruzioni."""
    app.simulation_paused = False
    app.current_instruction_index = 0  # Resetta l'indice all'inizio
    app.current_position = [30, -10]  # Resetta la posizione iniziale
    app.gcode_instructions = gcode_instructions  # Riassegna le istruzioni G-code
    execute_all_instructions(app)

def execute_all_instructions(app):
    """Esegue tutte le istruzioni G-code in sequenza utilizzando un ciclo."""
    if app.current_instruction_index >= len(app.gcode_instructions):
        app.show_message("Simulazione completata!", "info")
        reset_simulation(app)
        return

    for i in range(app.current_instruction_index, len(app.gcode_instructions)):
        step_simulation(app)

    app.show_message("Simulazione completata!", "info")
    reset_simulation(app)

def pause_simulation(app):
    """Pausa la simulazione."""
    app.simulation_paused = True

def resume_simulation(app):
    """Riprende la simulazione."""
    if app.simulation_paused:
        app.simulation_paused = False
        execute_next_instruction(app)

def deselect_all_instructions(app):
    """Deseleziona tutte le istruzioni nella Listbox."""
    app.gcode_listbox.selection_clear(0, tk.END)

# Avvia la GUI
if __name__ == "__main__":
    app = CNCApp()
    app.mainloop()
