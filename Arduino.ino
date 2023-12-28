#include <Servo.h>
#include <SoftwareSerial.h>
#define RX 2 //Connect to the TX pin of the HC-12
#define TX 3 //Connect to the RX pin of the HC-12

SoftwareSerial HC12(RX, TX); // HC-12 TX Pin, HC-12 RX Pin

byte thrusterLPin = 9, thrusterRPin = 11; // signal pins for each ESCs
Servo thrusterL, thrusterR; // create left and right thruster object

int data = 1500;
byte currentByte;
String readValue;

void setup() 
{
  Serial.begin(9600);
  HC12.begin(9600);

  thrusterL.attach(thrusterLPin);
  thrusterR.attach(thrusterRPin);
  thrusterL.writeMicroseconds(1500); // send "stop" signal to the Left ESC. Also necessary to arm the ESC
  thrusterR.writeMicroseconds(1500); // send "stop" signal to the Right ESC. Also necessary to arm the ESC
  
  delay(7000); // delay to allow the ESCs to recognize the stopped signal
}

void loop() 
{
  readValue = "";
  bool read = false;
  
  while(HC12.available()) 
  { 
    currentByte = HC12.read(); // Store each icoming byte from HC-12
    delay(5);
    // Reads the data between the start "+" and end marker ";"
    if (read == true) 
    {
      if (currentByte != ';') 
      {
        readValue += char(currentByte); // Add each byte to ReadBuffer string variable
      }
      else 
      {
        read = false;
      }
    }
    // Checks whether the received message statrs with the start marker "+"
    else if (currentByte == '+')
    {
      read = true; // If true start reading the message
    }
  }

  data = readValue.toInt();
  
  Serial.write(data);
  
  if(data > 10000 && data < 20000) 
  {
    data -= 10000;
    thrusterL.writeMicroseconds(data); // write to left thruster
  }
  else if(data > 20000 && data < 30000)
  {
    data -= 20000;
    thrusterR.writeMicroseconds(data); // write to right thruster
  }
  else if(data > 30000 && data < 40000)
  {
    data -= 30000;
    thrusterL.writeMicroseconds(data); // write to left thruster
    thrusterR.writeMicroseconds(data); // write to right thruster
  }
  else if(data > 40000 && data < 50000)
  {
    data -= 40000;
    int math = 1500 - data;
    thrusterL.writeMicroseconds(data); // write to left thruster
    thrusterR.writeMicroseconds(1500 + math); // write to right thruster
  }
  else if(data > 50000 && data < 60000)
  {
    data -= 50000;
    int math = 1500 - data;
    thrusterL.writeMicroseconds(1500 + math); // write to left thruster
    thrusterR.writeMicroseconds(data); // write to right thruster
  }
  
}
