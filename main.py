import os
import tkinter as tk
from ui_setup import setup_ui, initialize_left_frame, initialize_graph, plot_initial_graph, clear_left_frame, show_graph
from gcode_file_operations import (
    load_existing_programs, create_new_program, edit_selected_program, save_new_program, cancel_new_program, save_edited_program
)
from arduino_operations import translate_gcode, upload_to_arduino
from simulation_operations import prepare_simulation, simulate_program, step_simulation

class CNCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CNC Tornio")

        self.setup_ui()
        self.load_existing_programs()

    def setup_ui(self):
        setup_ui(self)

    def initialize_left_frame(self):
        initialize_left_frame(self)

    def initialize_graph(self):
        initialize_graph(self)

    def plot_initial_graph(self):
        plot_initial_graph(self)

    def clear_left_frame(self):
        clear_left_frame(self)

    def show_graph(self):
        show_graph(self)

    def hide_graph(self):
        """Nasconde il grafico."""
        self.canvas.get_tk_widget().pack_forget()

    def load_existing_programs(self):
        load_existing_programs(self)

    def create_new_program(self):
        create_new_program(self)

    def edit_selected_program(self):
        edit_selected_program(self)

    def prepare_simulation(self):
        prepare_simulation(self)

    def upload_to_arduino(self):
        upload_to_arduino(self)

    def translate_gcode(self):
        translate_gcode(self)

    def save_new_program(self):
        save_new_program(self)

    def cancel_new_program(self):
        cancel_new_program(self)

    def save_edited_program(self, program_path):
        save_edited_program(self, program_path)

    def show_message(self, message, message_type="info"):
        """Mostra un messaggio nell'etichetta dei messaggi."""
        self.message_label.config(text=message, fg="green" if message_type == "info" else "red")

    def translate_gcode_to_arduino(self, program_path):
        """Traduci un programma G-code in comandi Arduino e scrivilo in un file .ino."""
        try:
            with open(program_path, 'r') as file:
                gcode_data = file.readlines()

            arduino_commands = self.convert_gcode_to_arduino(gcode_data)

            arduino_file_base = os.path.splitext(os.path.basename(program_path))[0]
            arduino_dir = os.path.join(os.path.dirname(program_path), arduino_file_base)
            os.makedirs(arduino_dir, exist_ok=True)

            arduino_file_path = os.path.join(arduino_dir, f"{arduino_file_base}.ino")
            with open(arduino_file_path, 'w') as arduino_file:
                arduino_file.write(arduino_commands)

            self.show_message(f"Programma tradotto e salvato in {arduino_file_path}", "info")
            return arduino_file_path
        except Exception as e:
            self.show_message(f"Errore: Impossibile tradurre il programma G-code: {e}", "error")
            return None

    def convert_gcode_to_arduino(self, gcode_data):
        """Converti le istruzioni G-code in comandi Arduino."""
        arduino_code = """
// Dichiarazione delle funzioni
void blink(int x, int y, int z);
void turnOnPin(int pin, int duration);
void turnOnAnalogPin(int pin, int duration);

// Configurazione iniziale
void setup() {
  pinMode(13, OUTPUT);  // Pin per il controllo
  Serial.begin(115200);  // Inizializza la comunicazione seriale
}

// Funzioni di utilità
void blink(int x, int y, int z) {
  int onTime = y * 1000;  // Converti in millisecondi
  int offTime = z * 1000; // Converti in millisecondi

  for (int i = 0; i < x; i++) {
    digitalWrite(13, HIGH); // Accendi il pin
    delay(onTime);          // Aspetta il tempo di accensione
    digitalWrite(13, LOW);  // Spegni il pin
    delay(offTime);         // Aspetta il tempo di spegnimento
  }
}

void turnOnPin(int pin, int duration) {
  pinMode(pin, OUTPUT);
  digitalWrite(pin, HIGH);
  delay(duration * 1000); // Converti in millisecondi
  digitalWrite(pin, LOW);
}

void turnOnAnalogPin(int pin, int duration) {
  pinMode(pin, OUTPUT);
  analogWrite(pin, 255); // Imposta il valore analogico massimo
  delay(duration * 1000); // Converti in millisecondi
  analogWrite(pin, 0); // Spegni il pin analogico
}

void loop() {
"""
        for line in gcode_data:
            line = line.strip()
            if line.startswith('G1'):
                parts = line.split()
                x = y = z = None
                for part in parts:
                    if part.startswith('X'):
                        x = part[1:]
                    elif part.startswith('Y'):
                        y = part[1:]
                    elif part.startswith('Z'):
                        z = part[1:]
                if x and y and z:
                    arduino_code += f'  blink({x}, {y}, {z});\n'
            elif line.startswith('G2'):
                parts = line.split()
                pin = duration = None
                for part in parts:
                    if part.startswith('X'):
                        pin = part[1:]
                    elif part.startswith('Y'):
                        duration = part[1:]
                if pin and duration:
                    arduino_code += f'  turnOnPin({pin}, {duration});\n'
            elif line.startswith('G3'):
                parts = line.split()
                pin = duration = None
                for part in parts:
                    if part.startswith('X'):
                        pin = part[1:]
                    elif part.startswith('Y'):
                        duration = part[1:]
                if pin and duration:
                    arduino_code += f'  turnOnAnalogPin({pin}, {duration});\n'
        arduino_code += """
}
"""
        return arduino_code

if __name__ == "__main__":
    root = tk.Tk()
    app = CNCApp(root)
    root.mainloop()