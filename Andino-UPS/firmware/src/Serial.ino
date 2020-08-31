//------------------------------------------------------------
// Serial communication and command parsing
//$Rev:: 891                  $:  Revision of last commit.
//$Author:: marcus            $:  Author of last commit.
//$Date:: 2018-06-26 15:10:13#$:  Date of last commit.
//------------------------------------------------------------

#include <avr/wdt.h>

void SerialInit()
{
  Serial.begin(38400);
}

#define RX_SIZE  10
byte RxIndex = 0;
char RxBuffer[RX_SIZE+1];

void checkSerial()
{
  if( Serial.available() > 0 )
  {
    if( RxIndex >= RX_SIZE )
    {
      RxIndex = 0;
    }
    byte rx = Serial.read();

    if( RxIndex == 0 && (rx == LF || rx == CR) )
      return;
    if( rx == LF || rx == CR )
    {
      RxBuffer[RxIndex++] = 0;
      OnDataReceived(); 
      RxIndex = 0;
    }
    else
    {
      RxBuffer[RxIndex++] = rx;
    }
  }
}

void OnDataReceived()
{
  bool result = false;
  bool writeSetup = false;
  String cmd = RxBuffer;
  cmd.toUpperCase();
  
  if( cmd.startsWith("RESET"))
  {
    Serial.println( "OK" );
    DoCmdReset();
  }
  
  if(    cmd.startsWith("INFO")
      || cmd.startsWith("HELP"))
  {
    DoCmdInfo();
    result = true;
  }

  if( cmd.startsWith("REGS"))
  {
    i2cDumpRegister();
    result = true;
  }

  int value = toInt( cmd, 5 );
  if( value != -1 )
  {
    if( cmd.startsWith("GOOD "))
    {
      if( !checkRange( value, 20, 98 ) )
        return;
      TheSetup.PowerGood = value;
      PowerGoodLevel = TheSetup.PowerGood * 100;
      Serial.print( F("GOOD "));
      Serial.println( value, DEC );
      writeSetup = true;
      result = true;
    }
    else
    if( cmd.startsWith("HYST "))
    {
      if( !checkRange( value, 1, 100 ) )
        return;
      TheSetup.TimerHyst = value;
      Serial.print( F("HYST "));
      Serial.println( value, DEC );
      writeSetup = true;
      result = true;
    }
    else
    if( cmd.startsWith("DOWN "))
    {
      if( !checkRange( value, 1, 100 ) )
        return;
      TheSetup.TimerDown = value;
      Serial.print( "DOWN ");
      Serial.println( value, DEC );
      result = true;
      writeSetup = true;
    }
    else
    if( cmd.startsWith("TRCE "))
    {
      if( !checkRange( value, 0, 1 ) )
        return;
      TheSetup.Trace = (value==1);
      Serial.print( "TRCE ");
      Serial.println( value, DEC );
      result = true;
      writeSetup = true;
    }
  }
  if( result )
  {
    if( writeSetup )
      SetupWrite();
  }
  else
    Serial.println( "SYNTAX" );
}

void DoCmdInfo()
{
    Serial.print( F("GOOD val....Power good level in % [20..98] =")); Serial.println( TheSetup.PowerGood, DEC );
    Serial.print( F("HYST val....Wait after Power return to switch off client[1..100 sec] =")); Serial.println( TheSetup.TimerHyst, DEC );
    Serial.print( F("DOWN val....Wait after Power return. Duration client switch off [1..100 sec] =")); Serial.println( TheSetup.TimerDown, DEC );
    Serial.print( F("TRCE val....Enable Trace [0..1] =")); Serial.println( TheSetup.TimerDown, DEC );
}

void DoCmdReset()
{
  wdt_enable( WDTO_60MS );
   while(1) {}
}


bool checkRange( unsigned int val, unsigned int mini, unsigned int maxi )
{
  if( val < mini || val > maxi )
  {
    Serial.print( F("INVALID. MIN=") );
    Serial.print( mini, DEC );
    Serial.print( F(" MAX=") );
    Serial.println( maxi, DEC );
    return false;
  }
  return true;
}

int toInt( String s, int pos  )
{
  String valString = s.substring(pos);
  valString.trim();
  if( valString.length() == 0 )
    return -1;
  if( !isNumeric(valString) )
    return -1;
  return valString.toInt();
}

boolean isNumeric(String str) 
{
    for(char i = 0; i < str.length(); i++) 
    {
        if ( !(isDigit(str.charAt(i)) || str.charAt(i) == '.' )) 
        {
            return false;
        }
    }
    return true;
}



