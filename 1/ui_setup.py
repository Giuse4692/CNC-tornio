import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def setup_ui(app):
    """Configura l'interfaccia utente."""
    app.left_frame = ttk.Frame(app.root, width=200)
    app.left_frame.pack(side="left", fill="y")

    app.right_frame = ttk.Frame(app.root)
    app.right_frame.pack(side="right", fill="both", expand=True)

    # La label per il messaggio di errore o istruzioni verrà posizionata solo nel menu simulazione.
    app.message_label = tk.Label(app.right_frame, text="", fg="red")
    app.message_label.pack(pady=5)

    initialize_left_frame(app)
    initialize_graph(app)
    plot_initial_graph(app)

def initialize_left_frame(app):
    """Inizializza il frame sinistro con i pulsanti e la lista dei programmi."""
    for widget in app.left_frame.winfo_children():
        widget.destroy()

    ttk.Label(app.left_frame, text="Vecchi Programmi").pack(pady=10)

    app.program_listbox = tk.Listbox(app.left_frame)
    app.program_listbox.pack(padx=10, pady=10)

    button_width = 25
    buttons = [
        ("Crea Nuovo Programma", app.create_new_program),
        ("Modifica Programma", app.edit_selected_program),
        ("Simulazione", app.prepare_simulation),
        ("Carica su Arduino", app.upload_to_arduino),
        ("Traduci G-code", app.translate_gcode)
    ]

    for text, command in buttons:
        ttk.Button(app.left_frame, text=text, command=command, width=button_width).pack(pady=10)

    # Non includiamo qui le etichette per la posizione, ma solo per la simulazione
    # Etichette per la posizione X e Y, che verranno aggiunte solo nel menu simulazione
    app.position_x_label = tk.Label(app.left_frame, text="Posizione X: 0.00")
    app.position_y_label = tk.Label(app.left_frame, text="Posizione Y: 0.00")

def initialize_graph(app):
    """Inizializza il grafico nel frame destro."""
    clear_graph(app)  # Cancella il grafico esistente
    app.figure = Figure(figsize=(5, 5), dpi=100)
    app.ax = app.figure.add_subplot(111)
    app.ax.set_xlabel("X (mm)")
    app.ax.set_ylabel("Y (mm)")

    # Imposta i limiti degli assi
    app.ax.set_xlim([0, 35])
    app.ax.set_ylim([-10, 10])

    app.canvas = FigureCanvasTkAgg(app.figure, app.right_frame)
    app.canvas.get_tk_widget().pack(fill="both", expand=True)

def plot_initial_graph(app):
    """Traccia il grafico iniziale."""
    app.ax.plot([], [])
    app.canvas.draw()
    clear_graph(app)  # Cancella il grafico e lo rende bianco

def clear_left_frame(app):
    """Pulisce il frame sinistro."""
    for widget in app.left_frame.winfo_children():
        widget.destroy()

def clear_graph(app):
    """Pulisce il grafico e lo rende bianco."""
    if hasattr(app, 'ax'):
        app.ax.clear()
        app.ax.set_xlabel("X (mm)")
        app.ax.set_ylabel("Y (mm)")
        app.ax.set_xlim([0, 35])
        app.ax.set_ylim([-10, 10])
        app.ax.plot([], [])  # Traccia un grafico bianco
        app.canvas.draw()

def show_graph(app):
    """Mostra il grafico."""
    app.canvas.get_tk_widget().pack(fill="both", expand=True)
    plot_initial_graph(app)

def update_position(app, x, y):
    """Aggiorna la posizione X e Y nelle etichette."""
    app.position_x_label.config(text=f"Posizione X: {x:.2f}")
    app.position_y_label.config(text=f"Posizione Y: {y:.2f}")

def show_instruction_box(app):
    """Mostra il box delle istruzioni nel menu simulazione."""
    app.message_label.config(text="Simulazione in corso...")
    app.message_label.pack(side="bottom", pady=10, fill="x")

def hide_instruction_box(app):
    """Nasconde il box delle istruzioni."""
    app.message_label.pack_forget()

def prepare_simulation(self):
    """Prepara la simulazione."""
    # Mostra il box di istruzioni quando inizia la simulazione
    show_instruction_box(self)

    # Chiamata per iniziare la simulazione (ad esempio, inizializzare il grafico, ecc.)
    initialize_graph(self)
    
    # Mostra le etichette per la posizione solo nel menu simulazione
    self.position_x_label.pack(pady=5)
    self.position_y_label.pack(pady=5)

def stop_simulation(self):
    """Ferma la simulazione."""
    hide_instruction_box(self)
    
    # Nascondi le etichette per la posizione quando la simulazione finisce
    self.position_x_label.pack_forget()
    self.position_y_label.pack_forget()

