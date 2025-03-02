import serial
import time

class GRBLController:
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = serial.Serial(port, baudrate)
        self.initialize_grbl()

    def initialize_grbl(self):
        """Inizializza la connessione con GRBL."""
        self.serial_connection.write(b"\r\n\r\n")
        time.sleep(2)
        self.serial_connection.flushInput()

    def send_gcode(self, gcode):
        """Invia comandi G-code a GRBL."""
        if isinstance(gcode, str):
            gcode = gcode.splitlines()
        for command in gcode:
            self.serial_connection.write(f"{command}\n".encode())
            grbl_out = self.serial_connection.readline().strip()
            print(f"GRBL: {grbl_out.decode()}")

    def close(self):
        """Chiude la connessione seriale."""
        self.serial_connection.close()

if __name__ == "__main__":
    port = "COM3"  # Cambia con la tua porta seriale
    grbl = GRBLController(port)
    gcode_commands = [
        "G21",  # Imposta unità in millimetri
        "G90",  # Imposta modalità assoluta
        "G1 X10 Y10 F1000",  # Movimento lineare verso (10,10) a velocità 1000 mm/min
        "G1 X20 Y0",  # Movimento lineare verso (20,0)
    ]
    grbl.send_gcode(gcode_commands)
    grbl.close()