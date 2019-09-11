#include <Nextion.h>
#include <SoftwareSerial.h>

const int tempSensor = A0;
float airT = 0;
static char outtemp[6];

const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];

const int numReadings = 4;
char raceCaptureOutput[numReadings];
boolean newData = false;


// Declare Nextion object - (page id = 0, component id = 0, 
// component name = "b0")
NexText tTempC = NexText (1, 5, "tTempC");


void setup()
{
  Serial.begin(9600);
  Serial.println("Teensy Read");
  nexInit();
  Serial.println("Display Ready");
}


void loop()
{
  recvWithStartEndMarkers();
  if (newData == true){
    strcpy(tempChars, receivedChars);
    parseData();
    newData = false;
  }
  tempRead();
}


void tempRead(){
  float tempVal = analogRead(tempSensor);
  float tempVoltage = (tempVal/1024.0) * 5.0;
  float airT = (tempVoltage - .5) * 100;
  Serial.print("Air temp:");
  Serial.print(airT);
  dtostrf(airT, 6, 1, outtemp);
  tTempC.setText(outtemp);
}


void recvWithStartEndMarkers()
{
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false)
  {
    rc = Serial.read();

    if (recvInProgress = true) {
      if (rc != endMarker){
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars){
          ndx = numChars - 1;
        }
      }
    else {
        receivedChars[ndx] = '\0';
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }
    else if (rc == startMarker){
      recvInProgress = true;
    }
  }
}


void parseData()
{
  char * strtokIndx;
  strtokIndx = strtok(tempChars, ",");
  raceCaptureOutput[0] = atof(strtokIndx);
  Serial.println(raceCaptureOutput[0]);
  strtokIndx = strtok(NULL, ",");
  raceCaptureOutput[1] = atof(strtokIndx);
  Serial.println(raceCaptureOutput[1]);
  
}