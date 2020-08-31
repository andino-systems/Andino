//------------------------------------------------------------
// I/O Stuff (Relay, LED .. )
//$Rev:: 891                  $:  Revision of last commit.
//$Author:: marcus            $:  Author of last commit.
//$Date:: 2018-06-26 15:10:13#$:  Date of last commit.
//------------------------------------------------------------

#define JUMPER_1  6
#define JUMPER_2  7
#define LED_GREEN 10
#define LED_RED   13
#define REL_POWER 14 
#define REL_FAIL  15
#define PFO       3
#define CAPGD     4
#define ALERT     2   

void IOInit()
{
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED,OUTPUT);
  pinMode(REL_POWER,OUTPUT);
  pinMode(REL_FAIL,OUTPUT);
  pinMode(JUMPER_1,INPUT);
  pinMode(JUMPER_2,INPUT);
  pinMode(PFO,INPUT_PULLUP);
  pinMode(CAPGD,INPUT_PULLUP);
  pinMode(ALERT,INPUT);
}

int pfoOld = 0xFF; // first Timer change
int pfoCurr = 0;
int pfoCount = 0;
#define PFO_READ_COUNT  10
void checkIO()
{
  pfoCurr += digitalRead(PFO);
  pfoCount++;
  if( pfoCount == PFO_READ_COUNT )
  {
    if( pfoCurr == PFO_READ_COUNT && pfoOld != 1)
    {
      StateMachineEvent( EventPowerUp, pfoCurr );
      pfoOld = 1;
    }
    if( pfoCurr == 0 && pfoOld != 0)
    {
      StateMachineEvent( EventPowerDown, pfoCurr );
      pfoOld = 0;
    }
    pfoCurr = 0;
    pfoCount = 0;
  }
}


bool isPowerUp()
{
  return digitalRead(PFO) == 1;
}

bool isPowerDown()
{
  return digitalRead(PFO) == 0;
}

void LEDRedBlink( int interval )
{
  redInterval = interval;
  redMillis = millis();
  if( interval == 0 )
      LEDRed(OFF);
}

void LEDGreenBlink( int interval )
{
  greenInterval = interval;
  greenMillis = millis();
  if( interval == 0 )
      LEDGreen(OFF);
}


void LEDGreen( byte state )
{
  digitalWrite(LED_GREEN,state);
}

void LEDRed( byte state )
{
  digitalWrite(LED_RED,state);
}

void ClientSignalPowerDown()
{
  digitalWrite(REL_FAIL, OFF );
}

void ClientSignalPowerGood()
{
  digitalWrite(REL_FAIL, ON );
}

void ClientSwitchPowerOn()
{
  digitalWrite(REL_POWER, OFF );
}

void ClientSwitchPowerOff()
{
  digitalWrite(REL_POWER, ON );
}


