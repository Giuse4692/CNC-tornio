# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog
import serial
import time

# Flag per modalità simulazione
simulation_mode = True

# Variabili per feedback visivo
current_speed = 0
current_direction = "Stop"
spindle_position = {"X": 0, "Y": 0, "Z": 0}
programs = []

# Funzione per inviare comandi
def send_command(command):
    global current_speed, current_direction
    if simulation_mode:
        print(f"Simulazione: Comando inviato -> {command}")
    else:
        arduino.write(command.encode())

    # Aggiornare feedback visivo
    if command == 'u':
        current_speed += 10
    elif command == 'd':
        current_speed -= 10
    elif command == 'f':
        current_direction = "Avanti"
    elif command == 'b':
        current_direction = "Indietro"

    current_speed = max(0, min(current_speed, 255))  # Limita la velocità tra 0 e 255
    update_labels()

def increase_speed():
    send_command('u')

def decrease_speed():
    send_command('d')

def move_forward():
    send_command('f')

def move_backward():
    send_command('b')

def update_labels():
    speed_label.config(text=f"Velocità: {current_speed}")
    direction_label.config(text=f"Direzione: {current_direction}")

def update_position(x, y, z):
    spindle_position["X"] = x
    spindle_position["Y"] = y
    spindle_position["Z"] = z
    position_label.config(text=f"Posizione Spindle: X={x}, Y={y}, Z={z}")

def import_program():
    file_path = filedialog.askopenfilename(filetypes=[("G-code files", "*.nc;*.gcode;*.tap;*.cnc"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'r') as file:
            program_name = file_path.split('/')[-1]
            programs.append(program_name)
            program_listbox.insert(tk.END, program_name)

# Tentativo di connessione all'Arduino
if not simulation_mode:
    try:
        # Sostituisci 'COM3' con la porta del tuo Arduino
        arduino = serial.Serial('COM3', 9600, timeout=1)
        time.sleep(2)
    except serial.SerialException:
        print("Errore: Impossibile connettersi all'Arduino. Assicurati che sia collegato.")
        simulation_mode = True

# Creazione della finestra principale
root = tk.Tk()
root.title("Interfaccia di Controllo Motore")

# Creazione e posizionamento dei pulsanti
increase_button = tk.Button(root, text="Aumenta Velocità", command=increase_speed)
increase_button.grid(row=0, column=0, padx=10, pady=10)

decrease_button = tk.Button(root, text="Diminuisci Velocità", command=decrease_speed)
decrease_button.grid(row=1, column=0, padx=10, pady=10)

forward_button = tk.Button(root, text="Avanti", command=move_forward)
forward_button.grid(row=2, column=0, padx=10, pady=10)

backward_button = tk.Button(root, text="Indietro", command=move_backward)
backward_button.grid(row=3, column=0, padx=10, pady=10)

# Etichette per il feedback visivo
speed_label = tk.Label(root, text=f"Velocità: {current_speed}")
speed_label.grid(row=0, column=1, padx=10, pady=10)

direction_label = tk.Label(root, text=f"Direzione: {current_direction}")
direction_label.grid(row=1, column=1, padx=10, pady=10)

# Etichetta per la posizione dello spindle
position_label = tk.Label(root, text=f"Posizione Spindle: X=0, Y=0, Z=0")
position_label.grid(row=2, column=1, padx=10, pady=10)

# Lista programmi eseguiti
program_label = tk.Label(root, text="Programmi Eseguiti:")
program_label.grid(row=3, column=1, padx=10, pady=10)

program_listbox = tk.Listbox(root)
program_listbox.grid(row=4, column=1, padx=10, pady=10)

# Aggiungi programmi di esempio
for program in programs:
    program_listbox.insert(tk.END, program)

# Pulsante per importare programmi
import_button = tk.Button(root, text="Importa Programma", command=import_program)
import_button.grid(row=5, column=1, padx=10, pady=10)

# Avvio del ciclo di eventi della GUI
root.mainloop()