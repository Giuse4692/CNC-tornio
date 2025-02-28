const int motorPin = 9; // PWM pin for motor control
int motorSpeed = 0;

void setup() {
  pinMode(motorPin, OUTPUT);
  Serial.begin(9600); // Initialize serial communication at 9600 baud rate
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read(); // Read the incoming command

    if (command == 'u') {
      motorSpeed += 10;
    } else if (command == 'd') {
      motorSpeed -= 10;
    }
    motorSpeed = constrain(motorSpeed, 0, 255);
    analogWrite(motorPin, motorSpeed); // Set the motor speed
  }
}