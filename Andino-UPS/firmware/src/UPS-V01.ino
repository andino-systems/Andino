//
//    ###    ##    ## ########  #### ##    ##  #######                ##     ## ########   ######  
//   ## ##   ###   ## ##     ##  ##  ###   ## ##     ##               ##     ## ##     ## ##    ## 
//  ##   ##  ####  ## ##     ##  ##  ####  ## ##     ##               ##     ## ##     ## ##       
// ##     ## ## ## ## ##     ##  ##  ## ## ## ##     ##    #######    ##     ## ########   ######  
// ######### ##  #### ##     ##  ##  ##  #### ##     ##               ##     ## ##              ## 
// ##     ## ##   ### ##     ##  ##  ##   ### ##     ##               ##     ## ##        ##    ## 
// ##     ## ##    ## ########  #### ##    ##  #######                 #######  ##         ###### 
//
//
// Default Firmware
//  
//$Rev:: 890                  $:  Revision of last commit.
//$Author:: marcus            $:  Author of last commit.
//$Date:: 2018-06-26 15:06:31#$:  Date of last commit.
//
// see: https://github.com/andino-systems/Andino-UPS/tree/master/src/firmware 
//
#define ON  1
#define OFF 0

#include "globals.h"

void setup() 
{
  ClientSignalPowerGood();
  LEDRed( OFF );
  LEDGreen( OFF );

  SerialInit();
  SetupInit();
  TimerInit();
  IOInit();
  i2cInit();
  StateMachineInit();  
}

void loop() 
{
    checkSerial();
    checkTimer();
    checkIO();
}



