import matplotlib.pyplot as plt
import numpy as np

def simulate_g00(commands):
    # Creazione della figura e degli assi
    fig, ax = plt.subplots()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel('Asse X')
    ax.set_ylabel('Asse Y')
    ax.set_title('Simulazione movimento G00')

    # Creazione del puntino iniziale
    point, = ax.plot([], [], 'bo')

    # Funzione di aggiornamento per il puntino
    def update_point(x, y):
        point.set_data(x, y)
        plt.draw()

    # Esecuzione dei comandi G00
    for command in commands:
        if command.startswith('G00'):
            parts = command.split()
            x = None
            y = None
            for part in parts:
                if part.startswith('X'):
                    x = float(part[1:])
                elif part.startswith('Y'):
                    y = float(part[1:])
            if x is not None and y is not None:
                update_point(x, y)
                plt.pause(1)

    plt.show()

# Lista di comandi G00 da simulare
commands = [
    'G00 X20 Y30',
    'G00 X40 Y50',
    'G00 X60 Y70',
    'G00 X80 Y90'
]

simulate_g00(commands)