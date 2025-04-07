#define color_s0 33
#define color_s1 32
#define color_s2 34 
#define color_s3 35
#define color_out 37

#define colorSensorDelay 200 // Milliseconds
#define colorAverageDelay 20 // Milliseconds
#define redthreshold 200

// Frequency read by photodiodes of color sensor
uint32_t redFreq;
uint32_t greenFreq;
uint32_t blueFreq;
//takes in red,green and blue and processes the color
uint32_t processcolor(){
  if(redFreq < 100 || greenFreq <100 || blueFreq<100 )
    return 2;
  if(redFreq > 500 || greenFreq > 500 || blueFreq>500) 
    return 2;
  if(greenFreq < redFreq){
    return 1;
  }
  return 0;
}

 // Find the color of the paper
void findColor() { 
  // Setting RED (R) filtered photodiodes to be read
  digitalWrite(color_s2, LOW);
  digitalWrite(color_s3, LOW);
  //delay(200);
  delay(colorSensorDelay);

  // Reading the output frequency for RED
  redFreq = pulseIn(color_out, LOW);
  //delay(colorSensorDelay);

  // Setting GREEN (G) filtered photodiodes to be read
  digitalWrite(color_s2, HIGH);
  digitalWrite(color_s3, HIGH);
  delay(colorSensorDelay);

  // Reading the output frequency for GREEN
  greenFreq = pulseIn(color_out, LOW);
  //delay(colorSensorDelay);

  // Setting BLUE (B) filtered photodiodes to be read
  digitalWrite(color_s2, LOW);
  digitalWrite(color_s3, HIGH);
  delay(colorSensorDelay);

  // Reading the output frequency for BLUE
  blueFreq = pulseIn(color_out, LOW);
  //delay(colorSensorDelay);
  //delay(colorSensorDelay);
  
 /* Serial.print(" G = ");
  Serial.print(greenFreq);
  Serial.print(" B = ");
  Serial.print(blueFreq);
  Serial.print(" R = ");*/
}
void setupColor() {
  pinMode(color_s0, OUTPUT);
  pinMode(color_s1, OUTPUT);
  pinMode(color_s2, OUTPUT);
  pinMode(color_s0, OUTPUT);
  pinMode(color_out, INPUT);
  
  // Setting frequency scaling to 20%
  digitalWrite(color_s0, HIGH);      
  digitalWrite(color_s1, HIGH);
}