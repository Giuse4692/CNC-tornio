import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import re
import subprocess

class CNCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CNC Tornio")

        self.setup_ui()
        self.load_existing_programs()

    def setup_ui(self):
        """Configura l'interfaccia utente."""
        self.left_frame = ttk.Frame(self.root, width=200)
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.message_label = tk.Label(self.right_frame, text="", fg="red")
        self.message_label.pack(pady=5)

        self.initialize_left_frame()
        self.initialize_graph()
        self.plot_initial_graph()

    def initialize_left_frame(self):
        """Inizializza il frame sinistro con i pulsanti e la lista dei programmi."""
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.left_frame, text="Vecchi Programmi").pack(pady=10)

        self.program_listbox = tk.Listbox(self.left_frame)
        self.program_listbox.pack(padx=10, pady=10)

        button_width = 25

        buttons = [
            ("Crea Nuovo Programma", self.create_new_program),
            ("Modifica Programma", self.edit_selected_program),
            ("Carica su Arduino", self.upload_to_arduino),
            ("Traduci G-code", self.translate_gcode)
        ]

        for text, command in buttons:
            ttk.Button(self.left_frame, text=text, command=command, width=button_width).pack(pady=10)

    def initialize_graph(self):
        """Inizializza il grafico nel frame destro."""
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")

        self.canvas = FigureCanvasTkAgg(self.figure, self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_message(self, message, message_type="info"):
        """Mostra un messaggio nell'etichetta dei messaggi."""
        self.message_label.config(text=message, fg="green" if message_type == "info" else "red")

    def create_new_program(self):
        """Mostra i campi per la creazione di un nuovo programma."""
        self.clear_left_frame()
        self.show_new_program_form()
        self.hide_graph()

    def show_new_program_form(self):
        """Mostra il form per creare un nuovo programma."""
        ttk.Label(self.left_frame, text="Nome del Programma:").pack(pady=10)
        self.program_name_entry = ttk.Entry(self.left_frame)
        self.program_name_entry.pack(pady=10)

        ttk.Label(self.left_frame, text="Istruzioni G-code:").pack(pady=10)
        self.gcode_text = tk.Text(self.left_frame, width=40, height=10)
        self.gcode_text.pack(pady=10)

        self.save_button = ttk.Button(self.left_frame, text="Salva Programma", command=self.save_new_program)
        self.save_button.pack(pady=10)

        self.cancel_button = ttk.Button(self.left_frame, text="Annulla", command=self.cancel_new_program)
        self.cancel_button.pack(pady=10)

        self.show_message("Inserisci le istruzioni G-code e premi 'Salva Programma'.")

    def edit_selected_program(self):
        """Mostra i campi per modificare un programma selezionato."""
        selected_program_index = self.program_listbox.curselection()
        if not selected_program_index:
            self.show_message("Errore: Nessun programma selezionato", "error")
            return

        program_path = self.program_listbox.get(selected_program_index)
        if program_path.endswith('.gcode'):
            self.edit_program(program_path)
        else:
            self.show_message("Errore: Seleziona un file G-code", "error")

    def edit_program(self, program_path):
        """Mostra il form per modificare un programma esistente."""
        self.clear_left_frame()
        self.show_edit_program_form(program_path)
        self.hide_graph()

    def show_edit_program_form(self, program_path):
        """Mostra il form per modificare un programma esistente."""
        ttk.Label(self.left_frame, text=f"Modifica Programma: {os.path.basename(program_path)}").pack(pady=10)

        with open(program_path, 'r') as file:
            gcode_instructions = file.read()

        self.gcode_text = tk.Text(self.left_frame, width=40, height=10)
        self.gcode_text.insert(tk.END, gcode_instructions)
        self.gcode_text.pack(pady=10)

        self.save_button = ttk.Button(self.left_frame, text="Salva Modifiche", command=lambda: self.save_edited_program(program_path))
        self.save_button.pack(pady=10)

        self.cancel_button = ttk.Button(self.left_frame, text="Annulla", command=self.cancel_new_program)
        self.cancel_button.pack(pady=10)

        self.show_message("Modifica le istruzioni G-code e premi 'Salva Modifiche'.")

    def save_new_program(self):
        """Salva un nuovo programma G-code."""
        program_name = self.program_name_entry.get()
        gcode_instructions = self.gcode_text.get("1.0", tk.END).strip()

        if not program_name or not gcode_instructions:
            self.show_message("Errore: Nome del programma e istruzioni G-code non possono essere vuoti.", "error")
            return

        valid, error_message = self.validate_gcode(gcode_instructions)
        if not valid:
            self.show_message(f"Errore: {error_message}", "error")
            return

        gcode_file_path = os.path.join(os.path.dirname(__file__), f"{program_name}.gcode")
        with open(gcode_file_path, 'w') as gcode_file:
            gcode_file.write(gcode_instructions)

        self.initialize_left_frame()
        self.load_existing_programs()
        self.program_listbox.insert(tk.END, gcode_file_path)
        self.show_message(f"Nuovo programma creato in {gcode_file_path}", "info")
        self.show_graph()

    def save_edited_program(self, program_path):
        """Salva le modifiche a un programma G-code esistente."""
        gcode_instructions = self.gcode_text.get("1.0", tk.END).strip()

        if not gcode_instructions:
            self.show_message("Errore: Le istruzioni G-code non possono essere vuote.", "error")
            return

        valid, error_message = self.validate_gcode(gcode_instructions)
        if not valid:
            self.show_message(f"Errore: {error_message}", "error")
            return

        with open(program_path, 'w') as gcode_file:
            gcode_file.write(gcode_instructions)

        self.initialize_left_frame()
        self.load_existing_programs()
        self.show_message(f"Modifiche salvate in {program_path}", "info")
        self.show_graph()

    def validate_gcode(self, gcode):
        """Valida le istruzioni G-code."""
        valid_commands = {"G0", "G1", "G2", "G3", "G4", "G17", "G18", "G19", "G20", "G21", "G28", "G30", "G90", "G91", "G92"}
        for line_num, line in enumerate(gcode.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            match = re.match(r'^(G\d+)', line)
            if match and match.group(1) in valid_commands:
                continue
            return False, f"L'istruzione '{line}' alla linea {line_num} non è valida."
        return True, ""

    def cancel_new_program(self):
        """Annulla la creazione o modifica di un programma."""
        self.initialize_left_frame()
        self.load_existing_programs()
        self.show_graph()

    def translate_gcode(self):
        """Traduci un programma G-code in un programma Arduino."""
        selected_program_index = self.program_listbox.curselection()
        if not selected_program_index:
            self.show_message("Errore: Nessun programma selezionato", "error")
            return

        program_path = self.program_listbox.get(selected_program_index)
        if program_path.endswith('.gcode'):
            self.translate_gcode_to_arduino(program_path)
        else:
            self.show_message("Errore: Seleziona un file G-code", "error")

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

    def upload_to_arduino(self):
        """Carica il programma selezionato su Arduino."""
        selected_program_index = self.program_listbox.curselection()
        if not selected_program_index:
            self.show_message("Errore: Nessun programma selezionato", "error")
            return

        program_path = self.program_listbox.get(selected_program_index)

        if program_path.endswith('.gcode'):
            program_path = self.translate_gcode_to_arduino(program_path)
            if not program_path:
                return

        if program_path.endswith('.ino'):
            try:
                if not os.path.isfile(program_path):
                    self.show_message(f"Errore: Il file {program_path} non esiste.", "error")
                    return

                arduino_cli_path = os.path.join(os.path.dirname(__file__), 'arduino-cli', 'arduino-cli.exe')
                sketch_dir = os.path.dirname(program_path)

                compile_result = subprocess.run([arduino_cli_path, "compile", "--fqbn", "arduino:avr:uno", sketch_dir], capture_output=True, text=True)
                if compile_result.returncode != 0:
                    self.show_message(f"Errore durante la compilazione: {compile_result.stderr}", "error")
                    print(f"Errore durante la compilazione: {compile_result.stderr}")
                    return

                upload_result = subprocess.run([arduino_cli_path, "upload", "-p", "COM3", "--fqbn", "arduino:avr:uno", sketch_dir], capture_output=True, text=True)
                if upload_result.returncode == 0:
                    self.show_message("Programma caricato su Arduino con successo", "info")
                else:
                    self.show_message(f"Errore durante il caricamento: {upload_result.stderr}", "error")
                    print(f"Errore durante il caricamento: {upload_result.stderr}")
            except Exception as e:
                self.show_message(f"Errore: Impossibile caricare il programma su Arduino: {e}", "error")
                print(f"Impossibile caricare il programma su Arduino: {e}")
        else:
            self.show_message("Errore: Seleziona un file .ino per caricare su Arduino", "error")

    def plot_initial_graph(self):
        """Traccia il grafico iniziale."""
        self.ax.plot([], [])
        self.canvas.draw()

    def load_existing_programs(self):
        """Carica i programmi G-code dalla cartella corrente."""
        current_dir = os.path.dirname(__file__)
        for file_name in os.listdir(current_dir):
            if file_name.endswith('.gcode'):
                file_path = os.path.join(current_dir, file_name)
                self.program_listbox.insert(tk.END, file_path)

    def clear_left_frame(self):
        """Pulisce il frame sinistro."""
        for widget in self.left_frame.winfo_children():
            widget.destroy()

    def hide_graph(self):
        """Nasconde il grafico."""
        self.canvas.get_tk_widget().pack_forget()

    def show_graph(self):
        """Mostra il grafico."""
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.plot_initial_graph()

if __name__ == "__main__":
    root = tk.Tk()
    app = CNCApp(root)
    root.mainloop()
