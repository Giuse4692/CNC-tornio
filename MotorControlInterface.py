import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class CNCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CNC Tornio")
        
        # Frame sinistro per i vecchi programmi e il tasto per creare nuovi programmi
        self.left_frame = ttk.Frame(self.root, width=200)
        self.left_frame.pack(side="left", fill="y")
        
        self.program_list_label = ttk.Label(self.left_frame, text="Vecchi Programmi")
        self.program_list_label.pack(pady=10)
        
        self.program_listbox = tk.Listbox(self.left_frame)
        self.program_listbox.pack(padx=10, pady=10)
        
        self.new_program_button = ttk.Button(self.left_frame, text="Crea Nuovo Programma", command=self.create_new_program)
        self.new_program_button.pack(pady=10)
        
        self.load_program_button = ttk.Button(self.left_frame, text="Carica Programma", command=self.load_program)
        self.load_program_button.pack(pady=10)
        
        self.translate_program_button = ttk.Button(self.left_frame, text="Traduci G-code", command=self.translate_gcode)
        self.translate_program_button.pack(pady=10)
        
        # Frame destro per il piano cartesiano
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side="right", fill="both", expand=True)
        
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        
        self.canvas = FigureCanvasTkAgg(self.figure, self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.plot_initial_graph()
    
    def create_new_program(self):
        # Funzione per creare un nuovo programma
        pass
    
    def load_program(self):
        # Funzione per caricare un programma
        file_path = filedialog.askopenfilename(title="Seleziona il programma", filetypes=(("Python files", "*.py"), ("Arduino files", "*.ino"), ("G-code files", "*.gcode")))
        if file_path:
            self.program_listbox.insert(tk.END, file_path)
    
    def translate_gcode(self):
        # Funzione per tradurre un programma G-code in un programma Arduino
        selected_program_index = self.program_listbox.curselection()
        if not selected_program_index:
            messagebox.showerror("Errore", "Nessun programma selezionato")
            return
        
        program_path = self.program_listbox.get(selected_program_index)
        if program_path.endswith('.gcode'):
            self.translate_gcode_to_arduino(program_path)
        else:
            messagebox.showerror("Errore", "Seleziona un file G-code")
    
    def translate_gcode_to_arduino(self, program_path):
        # Funzione per tradurre G-code in comandi Arduino e scrivere in un file .ino
        try:
            with open(program_path, 'r') as file:
                gcode_data = file.readlines()
            
            arduino_commands = self.convert_gcode_to_arduino(gcode_data)
            
            arduino_file_path = os.path.splitext(program_path)[0] + ".ino"
            with open(arduino_file_path, 'w') as arduino_file:
                arduino_file.write(arduino_commands)
            
            messagebox.showinfo("Successo", f"Programma tradotto e salvato in {arduino_file_path}")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile tradurre il programma G-code: {e}")
    
    def convert_gcode_to_arduino(self, gcode_data):
        # Funzione per convertire G-code in comandi Arduino
        arduino_code = """
// Configurazione iniziale
void setup() {
  pinMode(9, OUTPUT);  // Pin per il PWM
  pinMode(10, OUTPUT); // Pin per il PWM
  pinMode(11, OUTPUT); // Pin per il PWM
  Serial.begin(115200);  // Inizializza la comunicazione seriale
}

// Funzioni di utilità
void wave(int x, int y, int z) {
  analogWrite(9, y);  // PWM sul pin 9
  analogWrite(10, y); // PWM sul pin 10
  analogWrite(11, y); // PWM sul pin 11
  
  int delayTime = 1000000 / z;  // Calcola il tempo di delay in microsecondi
  
  for (int i = 0; i < x; i++) {
    digitalWrite(9, HIGH);
    digitalWrite(10, HIGH);
    digitalWrite(11, HIGH);
    delayMicroseconds(delayTime);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    delayMicroseconds(delayTime);
  }
}

void loop() {
  // Loop principale vuoto
}

// Comandi tradotti dal file G-code
"""
        for line in gcode_data:
            line = line.strip()
            if line.startswith('G1'):  # Traduzione del comando G1
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
                    arduino_code += f'wave({x}, {y}, {z});\n'
        return arduino_code
    
    def plot_initial_graph(self):
        # Funzione per tracciare il grafico iniziale
        self.ax.plot([], [])
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = CNCApp(root)
    root.mainloop()
