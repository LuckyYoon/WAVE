#include <Servo.h>
#include <SoftwareSerial.h>
#define RX 2 //Connect to the TX pin of the HC-12
#define TX 3 //Connect to the RX pin of the HC-12

SoftwareSerial mySerial(RX, TX);

byte thrusterLPin = 9, thrusterRPin = 11; // signal pins for each ESCs
Servo thrusterL, thrusterR; // create left and right thruster object

int data;

void setup() 
{
  Serial.begin(9600);
  mySerial.begin(9600);

  thrusterL.attach(thrusterLPin);
  thrusterR.attach(thrusterRPin);
  thrusterL.writeMicroseconds(1500); // send "stop" signal to the Left ESC. Also necessary to arm the ESC
  thrusterR.writeMicroseconds(1500); // send "stop" signal to the Right ESC. Also necessary to arm the ESC
  
  delay(7000); // delay to allow the ESCs to recognize the stopped signal
}

void loop() 
{
  if (mySerial.available()) 
  {
    data = mySerial.read();
    Serial.write(data);

    if (data > 10000 && data < 20000) 
    {
      data -= 10000;
      thrusterL.writeMicroseconds(data); // write to left thruster
    }
    else if(data > 20000 && data < 30000)
    {
      data -= 20000;
      thrusterR.writeMicroseconds(data); //write to right thruster
    }
    else if(data > 30000 && data < 40000)
    {
      data -= 30000;
      thrusterL.writeMicroseconds(data); // write to left thruster
      thrusterR.writeMicroseconds(data); //write to right thruster
    }
    else if(data > 40000 && data < 50000)
    {
      data -= 40000;
      thrusterL.writeMicroseconds(data); // write to left thruster
      thrusterR.writeMicroseconds(1500-(1500-data)); //write to right thruster
    }
    else if(data > 50000 && data < 60000)
    {
      data -= 50000;
      thrusterL.writeMicroseconds(1500-(1500-data)); // write to left thruster
      thrusterR.writeMicroseconds(data); //write to right thruster
    }
  }
  
}
