import tkinter as tk
from tkinter import ttk

def setup_ui(app):
    """Configura l'interfaccia utente."""
    app.left_frame = ttk.Frame(app.root, width=200)
    app.left_frame.pack(side="left", fill="y")

    app.right_frame = ttk.Frame(app.root)
    app.right_frame.pack(side="right", fill="both", expand=True)

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

def initialize_graph(app):
    """Inizializza il grafico nel frame destro."""
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    app.figure = Figure(figsize=(5, 5), dpi=100)
    app.ax = app.figure.add_subplot(111)
    app.ax.set_xlabel("X (mm)")
    app.ax.set_ylabel("Y (mm)")

    # Imposta i limiti degli assi
    app.ax.set_xlim([0, 35])
    app.ax.set_ylim([-20, 20])

    app.canvas = FigureCanvasTkAgg(app.figure, app.right_frame)
    app.canvas.get_tk_widget().pack(fill="both", expand=True)

def plot_initial_graph(app):
    """Traccia il grafico iniziale."""
    app.ax.plot([], [])
    app.canvas.draw()

def clear_left_frame(app):
    """Pulisce il frame sinistro."""
    for widget in app.left_frame.winfo_children():
        widget.destroy()

def show_graph(app):
    """Mostra il grafico."""
    app.canvas.get_tk_widget().pack(fill="both", expand=True)
    plot_initial_graph(app)