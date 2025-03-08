import tkinter as tk
import os
from ui_setup import (setup_ui, initialize_left_frame, initialize_graph,
                      plot_initial_graph, clear_left_frame, show_graph)
from gcode_file_operations import (
    load_existing_programs, create_new_program, edit_selected_program,
    save_new_program, cancel_new_program, save_edited_program)
from arduino_operations import translate_gcode_to_arduino, upload_to_arduino
from simulation_operations import prepare_simulation, simulate_program, step_simulation

class CNCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CNC Tornio")
        self.setup_ui()
        self.load_existing_programs()

    def setup_ui(self): setup_ui(self)
    def initialize_left_frame(self): initialize_left_frame(self)
    def initialize_graph(self): initialize_graph(self)
    def plot_initial_graph(self): plot_initial_graph(self)
    def clear_left_frame(self): clear_left_frame(self)
    def show_graph(self): show_graph(self)
    def hide_graph(self): self.canvas.get_tk_widget().pack_forget()
    def load_existing_programs(self): load_existing_programs(self)
    def create_new_program(self): create_new_program(self)
    def edit_selected_program(self): edit_selected_program(self)
    def prepare_simulation(self): prepare_simulation(self)
    def upload_to_arduino(self): upload_to_arduino(self)
    def save_new_program(self): save_new_program(self)
    def cancel_new_program(self): cancel_new_program(self)
    def save_edited_program(self, program_path): save_edited_program(self, program_path)
    def show_message(self, message, message_type="info"):
        self.message_label.config(text=message, fg="green" if message_type == "info" else "red")

    def translate_gcode(self):
        """Funzione chiamata dal pulsante 'Traduci G-code'."""
        selected_program_index = self.program_listbox.curselection()
        if not selected_program_index:
            self.show_message("Errore: Nessun programma selezionato", "error")
            return

        # Ottieni il percorso del programma G-code selezionato
        program_path = self.program_listbox.get(selected_program_index[0])

        # Assicurati che il percorso del file esista
        if not os.path.isfile(program_path):
            self.show_message(f"Errore: Il file {program_path} non esiste.", "error")
            return

        # Chiama la funzione translate_gcode_to_arduino per fare la traduzione
        arduino_file_path = translate_gcode_to_arduino(self, program_path)  # Passa il percorso del programma
        if arduino_file_path:
            self.show_message(f"Programma tradotto con successo: {arduino_file_path}", "info")


if __name__ == "__main__":
    root = tk.Tk()
    app = CNCApp(root)
    root.mainloop()
