//------------------------------------------------------------
// All abount Timer. LED, I2C and FSM Timer
//$Rev:: 891                  $:  Revision of last commit.
//$Author:: marcus            $:  Author of last commit.
//$Date:: 2018-06-26 15:10:13#$:  Date of last commit.
//------------------------------------------------------------

void TimerInit()
{
}

void TimerStartStateMachine( unsigned long interval )
{
  stateMachineInterval = interval;
  stateMachineMillis = millis();
}

void TimerStopStateMachine()
{
  stateMachineInterval = 0;
  stateMachineMillis = millis();
}

void TimerStartCheckI2C( unsigned long interval )
{
  i2cCheckInterval = interval ;
  i2cCheckMillis = millis();
}

void TimerStopCheckI2C()
{
  i2cCheckInterval = 0;
  i2cCheckMillis = millis();
}

void TimerStartRedBlink( unsigned long interval )
{
  redInterval = interval ;
  redMillis = millis();
}

void TimerStopRedBlink()
{
  redInterval = 0;
  redMillis = millis();
  LEDRed( OFF );
}

void TimerStartGreenBlink( unsigned long interval )
{
  greenInterval = interval ;
  greenMillis = millis();
}

void TimerStopGreenBlink()
{
  greenInterval = 0;
  greenMillis = millis();
  LEDGreen( OFF );
}



void checkTimer()
{
    unsigned long currentMillis = millis();

    if (greenInterval != 0 && (currentMillis - greenMillis) >= greenInterval) 
    {
      greenMillis = currentMillis;
      digitalWrite(LED_GREEN, !digitalRead(LED_GREEN));
    }
    if (redInterval != 0 && (currentMillis - redMillis) >= redInterval) 
    {
      redMillis = currentMillis;
      digitalWrite(LED_RED, !digitalRead(LED_RED));
    }

    if ((stateMachineInterval != 0) && (currentMillis - stateMachineMillis) >= stateMachineInterval ) 
    {
      TimerStopStateMachine();
      StateMachineEvent( EventTimerTick, 0 );
      return; // only one Event to the SM per TimerTick.
    }

    if (i2cCheckInterval !=  0 && (currentMillis - i2cCheckMillis) >= i2cCheckInterval ) 
    {
      i2cCheckMillis = currentMillis;
      i2cCheck();
      return; // only one Event to the SM per TimerTick.
    }
}

