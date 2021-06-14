#include <SoftwareSerial.h>
#include <TinyGPS.h>


TinyGPS gps;
SoftwareSerial ss(4,3);

/*Uses serial digital ports 3 4 */

void setup() {
  Serial.begin(115200);
  ss.begin(9600);

  Serial.print("Simple TinyGPS example v."); Serial.println(TinyGPS::library_version());
  Serial.println("By Cansat Team");
  Serial.println();

}

void loop() {
  bool newData= false; 
  unsigned long chars;
  unsigned short sentences, failed; 

  for (unsigned long start= millis(); millis() - start < 1000;)
  {
    while (ss.available())
    {
      char c = ss.read();
      if (gps.encode(c))
        newData=true;
    }
    
  }
