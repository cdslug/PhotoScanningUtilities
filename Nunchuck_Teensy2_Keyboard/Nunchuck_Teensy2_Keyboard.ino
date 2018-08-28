#include <Wire.h>
#include <EEPROM.h>
#include "wiinunchuk.h" // Wii Nunchuk Library
#define CONST_NONE -1
#define CONST_UP 0
#define CONST_RIGHT 1
#define CONST_DOWN 2
#define CONST_LEFT 3

int led = 11; // Use LED on Pro Trinket for Status and Button Press Indicator
int loop_cnt=0;
int mode = 0; // Defines mode of the iTapStick: left mouse click is C or Z button

// parameters for reading the joystick:
// output range of X or Y movement // resting threshold
// resting position value
int range = 201;
int threshold = range/10;
int center = range/2;

void setup() {
    pinMode(led, OUTPUT);
    
//    nunchuk_setpowerpins();
    nunchuk_init(); // initilization for the Wii Nunchuk
    delay(250);
    
    while(!nunchuk_get_data()){ // loop until Wii Nunchuk is connected to Nunchucky
        nunchuk_init();
        delay(250);
        nunchuk_get_data();
        digitalWrite(led, HIGH);
        delay(250);
        digitalWrite(led, LOW);
        delay(500);
    }
    digitalWrite(led, HIGH); // let user know they can select mode within (5 seconds)
    delay(5000);
    
    // check if user is holding any of buttons to change mode
    
    nunchuk_init();
    delay(250); // Once connected lets get additional data to determine if C or Z
    nunchuk_get_data(); // button is being held down for programming mode
    delay(10);
    nunchuk_get_data();
    delay(10);
    nunchuk_get_data();
    
    int leftState = nunchuk_zbutton();
    int rightState = nunchuk_cbutton();
    
    if(leftState){ // save mode for future time if Z is defined as left mouse click
        mode = 0;
        EEPROM.write(0, 0);
        digitalWrite(led, LOW);
        delay(250);
        digitalWrite(led, HIGH);
        delay(250);
        
        digitalWrite(led, LOW);
        delay(250);
        digitalWrite(led, HIGH);
        delay(250);
        digitalWrite(led, LOW);
        delay(250);
        digitalWrite(led, HIGH);
        delay(3000);
        
    }else if(rightState){ // save mode for future time if C is defined as left mouse click
        mode = 1;
        EEPROM.write(0, 1);
        digitalWrite(led, LOW);
        delay(100);
        digitalWrite(led, HIGH);
        delay(100);
        digitalWrite(led, LOW);
        delay(100);
        digitalWrite(led, HIGH);
        delay(100);
        digitalWrite(led, LOW);
        delay(100);
        digitalWrite(led, HIGH);
        delay(100);
        digitalWrite(led, LOW);
        delay(100);
        digitalWrite(led, HIGH);
        delay(100);
        digitalWrite(led, LOW);
        delay(100);
        digitalWrite(led, HIGH);
        delay(100);
        digitalWrite(led, LOW);
        delay(100);
        digitalWrite(led, HIGH);
        delay(3000);
    }else
    {
        mode = EEPROM.read(0);   // no mode selection load in saved mode
    }
    
    digitalWrite(led, LOW); // get LED indicator ready to show when buttons are being pressed
    
    // Start Pro Trinket into Mouse mode
    Keyboard.begin(); // Initialize mouse library
}

int leftStateOld = 0;
int rightStateOld = 0;
int arrowKeyStateOld = CONST_NONE;

void flashLED()
{
 digitalWrite(led,HIGH);
 delay(10);
 digitalWrite(led,LOW); 
}

void loop()
{
    if( loop_cnt > 10 )
    { // every 10 msecs get new data
        loop_cnt = 0;
        
        
        if(nunchuk_get_data()) // only check for data if data is available from Wii Nunchuk
        {
            
            // right and left click control
            int leftState = nunchuk_zbutton();
            int rightState = nunchuk_cbutton();
            
            if (leftState != leftStateOld) // if button is pressed update
            {
              if (leftState){
                  if(mode==0)
                  {
                        Keyboard.print("z\n");
                        flashLED();
                  }
                  else
                  {
                      Keyboard.print("D\n");
                      flashLED();
                  }
              }
//                digitalWrite(led, HIGH); // show button is pressed by LED  
            }
            if (rightState != rightStateOld) // if button is pressed update
            {
              if (rightState)
              {
                  if(mode==0)
                  {
                        Keyboard.print("D\n"); //delete
                        flashLED();
                  }
                  else
                  {
                        Keyboard.print("z\n");
                        flashLED();
                  }
              }
             }
//                digitalWrite(led, HIGH);// show button is pressed by LED
                  leftStateOld = leftState;
                  rightStateOld = rightState;

            
            int xReading = nunchuk_joy_x(); // read the x axis
            xReading = map(xReading, 38, 232, 0, range); // map accordingly
            int xDistance = xReading - center;
            if (abs(xDistance) < threshold)
            {
                xDistance = 0;
            }
            
            int yReading = nunchuk_joy_y(); // read the y axis
            yReading = map(yReading, 38, 232, 0, range); // map accordingly
            int yDistance = yReading - center;
            if (abs(yDistance) < threshold)
            {
                yDistance = 0;                
            }
            
            int arrowKeyState = arrowKeyStateOld;
             if(yDistance > 1.5*threshold && abs(yDistance) > abs(xDistance) + 1.5*threshold)
             {
                arrowKeyState = CONST_UP;
             } 
             else if(xDistance > 1.5*threshold && abs(xDistance) > abs(yDistance) + threshold)
             {
                arrowKeyState = CONST_RIGHT;
             } 
             else if (yDistance < -1.5*threshold && abs(yDistance) > abs(xDistance) + threshold)
             {
                arrowKeyState = CONST_DOWN; 
             }
             else if (xDistance < -1.5*threshold && abs(xDistance) > abs(yDistance) + threshold)
             {
                arrowKeyState = CONST_LEFT; 
             }
             else if (xDistance == 0 && yDistance == 0)
             {
                arrowKeyState = CONST_NONE; 
             }
            
            
            
            if (arrowKeyState != arrowKeyStateOld && arrowKeyStateOld == CONST_NONE)
            {
               if (arrowKeyState == CONST_UP)
               {
                   Keyboard.print("0\n");
//                 Keyboard.press(KEY_UP_ARROW);
//                 Keyboard.release(KEY_UP_ARROW);
//                 Keyboard.println("");
                    flashLED();
               }
               else if (arrowKeyState == CONST_DOWN)
               {
                   Keyboard.print("2\n");
//                 Keyboard.press(KEY_DOWN_ARROW);
//                 Keyboard.release(KEY_DOWN_ARROW);
//                 Keyboard.println("");
                    flashLED();
               }
               else if (arrowKeyState == CONST_RIGHT)
               {
                   Keyboard.print("1\n");
//                 Keyboard.press(KEY_RIGHT_ARROW);
//                 Keyboard.release(KEY_RIGHT_ARROW);
//                 Keyboard.println("");
                    flashLED();
               }
               else if (arrowKeyState == CONST_LEFT)
               {
                   Keyboard.print("3\n");
//                 Keyboard.press(KEY_LEFT_ARROW);
//                 Keyboard.release(KEY_LEFT_ARROW);
//                 Keyboard.println("");
                    flashLED();
               }
            }
            arrowKeyStateOld = arrowKeyState;
        
        }
    }
    loop_cnt++;
    delay(1);
}
