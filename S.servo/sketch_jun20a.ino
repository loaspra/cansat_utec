#include "Simple_MPU6050.h"          // incluye libreria Simple_MPU6050
#define MPU6050_ADDRESS_AD0_LOW     0x68      // direccion I2C con AD0 en LOW o sin conexion
#define MPU6050_ADDRESS_AD0_HIGH    0x69      // direccion I2C con AD0 en HIGH
#define MPU6050_DEFAULT_ADDRESS     MPU6050_ADDRESS_AD0_LOW // por defecto AD0 en LOW
#include <Servo.h>

Simple_MPU6050 mpu;       // crea objeto con nombre mpu
ENABLE_MPU_OVERFLOW_PROTECTION();   // activa proteccion


// #define OFFSETS  -5114,     484,    1030,      46,     -14,       6  // Colocar valores personalizados
Servo ServoX;

#define spamtimer(t) for (static uint32_t SpamTimer; (uint32_t)(millis() - SpamTimer) >= (t); SpamTimer = millis())
// spamtimer funcion para generar demora al escribir en monitor serie sin usar delay()

#define printfloatx(Name,Variable,Spaces,Precision,EndTxt) print(Name); {char S[(Spaces + Precision + 3)];Serial.print(F(" ")); Serial.print(dtostrf((float)Variable,Spaces,Precision ,S));}Serial.print(EndTxt);
// printfloatx funcion para mostrar en monitor serie datos para evitar el uso se multiples print()

// mostrar_valores funcion que es llamada cada vez que hay datos disponibles desde el sensor
void mostrar_valores (int16_t *gyro, int16_t *accel, int32_t *quat, uint32_t *timestamp) {  
  uint8_t SpamDelay = 100;      // demora para escribir en monitor serie de 100 mseg
  Quaternion q;         // variable necesaria para calculos posteriores
  VectorFloat gravity;        // variable necesaria para calculos posteriores
  float ypr[3] = { 0, 0, 0 };     // array para almacenar valores de yaw, pitch, roll
  float xyz[3] = { 0, 0, 0 };     // array para almacenar valores convertidos a grados de yaw, pitch, roll
  spamtimer(SpamDelay) {      // si han transcurrido al menos 100 mseg entonces proceder
    mpu.GetQuaternion(&q, quat);    // funcion para obtener valor para calculo posterior
    mpu.GetGravity(&gravity, &q);   // funcion para obtener valor para calculo posterior
    mpu.GetYawPitchRoll(ypr, &q, &gravity); // funcion obtiene valores de yaw, ptich, roll
    mpu.ConvertToDegrees(ypr, xyz);   // funcion convierte a grados sexagesimales
    Serial.printfloatx(F("Yaw")  , xyz[0], 9, 4, F(",   "));  // muestra en monitor serie rotacion de eje Z, yaw
    Serial.printfloatx(F("Pitch"), xyz[1], 9, 4, F(",   "));  // muestra en monitor serie rotacion de eje Y, pitch
    Serial.printfloatx(F("Roll") , xyz[2], 9, 4, F(",   "));  // muestra en monitor serie rotacion de eje X, roll
    Serial.println();       // salto de linea
    if ( xyz[0] > abs(30.0) ){     // si el pitch es mayor a 10 grados
      ServoX.write(180);   // muestra texto
      delay(5000);
      ServoX.write(90);
    }
    if ( xyz[1] > abs(30.0)){    // si el pitch es menor a -10 grados
       ServoX.write(180);    // muestra texto
       delay(5000);
        ServoX.write(90);
      }
   else if(xyz[2]> abs(30.0)){
          ServoX.write(180); 
          delay(5000);
          ServoX.write(90);
    }
      }
  }
  int PrintAllValues(int16_t *gyro, int16_t *accel, int32_t *quat, uint8_t SpamDelay = 100) {
  Quaternion q;
  VectorFloat gravity;
  float ypr[3] = { 0, 0, 0 };
  float xyz[3] = { 0, 0, 0 };
  spamtimer(SpamDelay) {// non blocking delay before printing again. This skips the following code when delay time (ms) hasn't been met
    mpu.GetQuaternion(&q, quat);
    mpu.GetGravity(&gravity, &q);
    mpu.GetYawPitchRoll(ypr, &q, &gravity);
    mpu.ConvertToDegrees(ypr, xyz);
    
    Serial.printfloatx(F("Yaw")  , xyz[0], 9, 4, F(",   ")); //printfloatx is a Helper Macro that works with Serial.print that I created (See #define above)
    Serial.printfloatx(F("Pitch"), xyz[1], 9, 4, F(",   "));
    Serial.printfloatx(F("Roll") , xyz[2], 9, 4, F(",   "));
    
      Serial.printfloatx(F("ax")   , accel[0], 5, 0, F(",   "));
      Serial.printfloatx(F("ay")   , accel[1], 5, 0, F(",   "));
      Serial.printfloatx(F("az")   , accel[2], 5, 0, F(",   "));
      Serial.printfloatx(F("gx")   , gyro[0],  5, 0, F(",   "));
      Serial.printfloatx(F("gy")   , gyro[1],  5, 0, F(",   "));
      Serial.printfloatx(F("gz")   , gyro[2],  5, 0, F("\n"));
    
    Serial.println();
    
//    if ( accel[1] > abs(30.0) ){     // si el pitch es mayor a 10 grados
//      ServoX.write(180);   // muestra texto
//    }
//    if ( accel[2] > abs(30.0)){    // si el pitch es menor a -10 grados
//       ServoX.write(180);    // muestra texto
//      }
//   else if(accel[3]> abs(30.0)){
//          ServoX.write(180); 
//    }
    
  }}


void setup() {
  ServoX.attach(5,625,2400);
  ServoX.write(90);
  uint8_t val;
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE  // activacion de bus I2C a 400 Khz
  Wire.begin();
  Wire.setClock(400000);
#elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
  Fastwire::setup(400, true);
#endif
  
  Serial.begin(115200);     // inicializacion de monitor serie a 115200 bps
  while (!Serial);      // espera a enumeracion en caso de modelos con USB nativo
  Serial.println(F("Inicio:"));   // muestra texto estatico
#ifdef OFFSETS                // si existen OFFSETS
  Serial.println(F("Usando Offsets predefinidos"));     // texto estatico
  mpu.SetAddress(MPU6050_ADDRESS_AD0_LOW).load_DMP_Image(OFFSETS);  // inicializacion de sensor

#else                   // sin no existen OFFSETS
  Serial.println(F(" No se establecieron Offsets, haremos unos nuevos.\n" // muestra texto estatico
                   " Colocar el sensor en un superficie plana y esperar unos segundos\n"
                   " Colocar los nuevos Offsets en #define OFFSETS\n"
                   " para saltar la calibracion inicial \n"
                   " \t\tPresionar cualquier tecla y ENTER"));
  while (Serial.available() && Serial.read());    // lectura de monitor serie
  while (!Serial.available());        // si no hay espera              
  while (Serial.available() && Serial.read());    // lecyura de monitor serie
  mpu.SetAddress(MPU6050_ADDRESS_AD0_LOW).CalibrateMPU().load_DMP_Image();  // inicializacion de sensor
#endif
  mpu.on_FIFO(mostrar_valores);   // llamado a funcion mostrar_valores si memoria FIFO tiene valores
}


//int PrintAllValues(int16_t *gyro, int16_t *accel, int32_t *quat, uint16_t SpamDelay = 100) {
//  Quaternion q;
//  VectorFloat gravity;
//  float ypr[3] = { 0, 0, 0 };
//  float xyz[3] = { 0, 0, 0 };
//  spamtimer(SpamDelay) {// non blocking delay before printing again. This skips the following code when delay time (ms) hasn't been met
//    mpu.GetQuaternion(&q, quat);
//    mpu.GetGravity(&gravity, &q);
//    mpu.GetYawPitchRoll(ypr, &q, &gravity);
//    mpu.ConvertToDegrees(ypr, xyz);
//    
//    Serial.printfloatx(F("Yaw")  , xyz[0], 9, 4, F(",   ")); //printfloatx is a Helper Macro that works with Serial.print that I created (See #define above)
//    Serial.printfloatx(F("Pitch"), xyz[1], 9, 4, F(",   "));
//    Serial.printfloatx(F("Roll") , xyz[2], 9, 4, F(",   "));
//    
//      Serial.printfloatx(F("ax")   , accel[0], 5, 0, F(",   "));
//      Serial.printfloatx(F("ay")   , accel[1], 5, 0, F(",   "));
//      Serial.printfloatx(F("az")   , accel[2], 5, 0, F(",   "));
//      Serial.printfloatx(F("gx")   , gyro[0],  5, 0, F(",   "));
//      Serial.printfloatx(F("gy")   , gyro[1],  5, 0, F(",   "));
//      Serial.printfloatx(F("gz")   , gyro[2],  5, 0, F("\n"));
//    
//    Serial.println();
//    */
////    if ( accel[1] > abs(30.0) ){     // si el pitch es mayor a 10 grados
////      ServoX.write(180);   // muestra texto
////    }
////    if ( accel[2] > abs(30.0)){    // si el pitch es menor a -10 grados
////       ServoX.write(180);    // muestra texto
////      }
////   else if(accel[3]> abs(30.0)){
////          ServoX.write(180); 
////    }
//    
//  }}

void loop() {
  mpu.dmp_read_fifo();    // funcion que evalua si existen datos nuevos en el sensor y llama
}       // a funcion mostrar_valores si es el caso
