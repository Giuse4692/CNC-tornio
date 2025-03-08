import os  # 🔹 Forziamo l'import all'inizio

print(f"✅ [DEBUG] Modulo os caricato in arduino_operations: {os}")  # Test immediato

import subprocess


def translate_gcode(self):
    """Traduci un programma G-code in un programma Arduino e salva il file .ino."""
    selected_program_index = self.program_listbox.curselection()
    if not selected_program_index:
        self.show_message("Errore: Nessun programma selezionato", "error")
        return

    program_path = self.program_listbox.get(selected_program_index[0])  # Prendi il percorso corretto

    # Leggi il contenuto del file G-code
    try:
        with open(program_path, 'r') as file:
            gcode_data = file.readlines()  # Leggi tutte le righe del file
    except Exception as e:
        self.show_message(f"Errore durante la lettura del file: {e}", "error")
        return

    # Creiamo una cartella con il nome del file senza estensione
    base_name = os.path.splitext(os.path.basename(program_path))[0]  # Nome del file senza estensione
    sketch_folder = os.path.join(os.path.dirname(program_path), base_name)

    if not os.path.exists(sketch_folder):
        os.makedirs(sketch_folder)  # Crea la cartella se non esiste

    # Percorso completo per il file .ino
    arduino_file_path = os.path.join(sketch_folder, f"{base_name}.ino")

    # Converti il G-code in codice Arduino
    arduino_code = self.convert_gcode_to_arduino(gcode_data)  # Passa i dati G-code alla conversione

    # Scrivi il codice tradotto nel file .ino
    try:
        with open(arduino_file_path, 'w') as arduino_file:
            arduino_file.write(arduino_code)
    except Exception as e:
        self.show_message(f"Errore durante il salvataggio del file: {e}", "error")
        return

    self.show_message(f"Programma tradotto e salvato in {arduino_file_path}", "info")




def translate_gcode_to_arduino(app, program_path):
    """Traduci un programma G-code in comandi Arduino e salva in un file .ino."""

    print(f"🟢 [DEBUG] Funzione translate_gcode_to_arduino() chiamata con {program_path}")

    try:
        if not os.path.isfile(program_path):
            print(f"❌ [ERRORE] Il file {program_path} non esiste!")
            app.show_message(f"Errore: Il file {program_path} non esiste.", "error")
            return None

        # Leggi il contenuto del file G-code
        with open(program_path, 'r') as file:
            gcode_data = file.readlines()

        # Converti il G-code in codice Arduino
        arduino_code = convert_gcode_to_arduino(gcode_data)

        # Creiamo una cartella con il nome del file senza estensione
        base_name = os.path.splitext(os.path.basename(program_path))[0]  # Nome del file senza estensione
        sketch_folder = os.path.join(os.path.dirname(program_path), base_name)

        if not os.path.exists(sketch_folder):
            os.makedirs(sketch_folder)  # Crea la cartella se non esiste

        # Nome completo del file .ino
        arduino_file_path = os.path.join(sketch_folder, f"{base_name}.ino")

        # Salviamo il codice Arduino nel file
        with open(arduino_file_path, 'w') as arduino_file:
            arduino_file.write(arduino_code)

        print(f"✅ [DEBUG] File Arduino salvato in: {arduino_file_path}")
        app.show_message(f"Programma tradotto e salvato in {arduino_file_path}", "info")

        return arduino_file_path  # Ritorniamo il percorso del file .ino

    except Exception as e:
        print(f"❌ [ERRORE GENERALE] {e}")
        app.show_message(f"Errore: {e}", "error")
        return None

def convert_gcode_to_arduino(gcode_data):
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
        parts = line.strip().split()
        if line.startswith('G1'):
            x = y = z = None
            for part in parts:
                if part.startswith('X'): x = part[1:]
                elif part.startswith('Y'): y = part[1:]
                elif part.startswith('Z'): z = part[1:]
            if x and y and z: 
                arduino_code += f'  blink({x}, {y}, {z});\n'
        elif line.startswith('G2'):
            pin = duration = None
            for part in parts:
                if part.startswith('X'): pin = part[1:]
                elif part.startswith('Y'): duration = part[1:]
            if pin and duration: 
                arduino_code += f'  turnOnPin({pin}, {duration});\n'
        elif line.startswith('G3'):
            pin = duration = None
            for part in parts:
                if part.startswith('X'): pin = part[1:]
                elif part.startswith('Y'): duration = part[1:]
            if pin and duration: 
                arduino_code += f'  turnOnAnalogPin({pin}, {duration});\n'
    arduino_code += """
}
"""
    return arduino_code



def upload_to_arduino(app):
    """Carica il programma selezionato su Arduino."""
    selected_program_index = app.program_listbox.curselection()
    if not selected_program_index:
        app.show_message("Errore: Nessun programma selezionato", "error")
        return

    program_path = app.program_listbox.get(selected_program_index)
    arduino_file_path = translate_gcode_to_arduino(app, program_path)  # Ottieni il percorso del file Arduino

    if not arduino_file_path:
        return

    try:
        if not os.path.isfile(arduino_file_path):
            app.show_message(f"Errore: Il file {arduino_file_path} non esiste.", "error")
            return

        arduino_cli_path = os.path.join(os.path.dirname(__file__), 'arduino-cli', 'arduino-cli.exe')
        sketch_dir = os.path.dirname(arduino_file_path)

        compile_result = subprocess.run([arduino_cli_path, "compile", "--fqbn", "arduino:avr:uno", sketch_dir], capture_output=True, text=True)
        if compile_result.returncode != 0:
            app.show_message(f"Errore durante la compilazione: {compile_result.stderr}", "error")
            return

        upload_result = subprocess.run([arduino_cli_path, "upload", "-p", "COM3", "--fqbn", "arduino:avr:uno", sketch_dir], capture_output=True, text=True)
        if upload_result.returncode == 0:
            app.show_message("Programma caricato su Arduino con successo", "info")
        else:
            app.show_message(f"Errore durante il caricamento: {upload_result.stderr}", "error")
    except Exception as e:
        app.show_message(f"Errore: Impossibile caricare il programma su Arduino: {e}", "error")