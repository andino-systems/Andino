//------------------------------------------------------------
// Main Part - The Finite State Machine
//$Rev:: 891                  $:  Revision of last commit.
//$Author:: marcus            $:  Author of last commit.
//$Date:: 2018-06-26 15:10:13#$:  Date of last commit.
//------------------------------------------------------------

/*
 *  https://dreampuf.github.io/GraphvizOnline/
digraph finite_state_machine {
  rankdir=TD;
  forcelabels=true;
  node [fontname = "helvetica bold" fontsize  = 20];
  node [shape = doublecircle]; Init;
  node [shape = circle];
  edge [fontname = "helvetica" fontsize  = 20];
  "Init" [label=Initialize];
  "Init" -> "Charging" [ label = "is charging" ];
  "Init" -> "Charged" [ label = "is charged" ];
  "Charging" -> "Down" [ label = "is down" ];
  "Charging" -> "Charged" [ label = "is charged" ];
  "Charged" -> "Down" [ label = "is down" ];
  "Alarm" -> "Power returned" [ label = "is up again" ];
  "Down" -> "Alarm" [ label = "below good" ];
  "Down" -> "Charging" [ label = "is up again" ];
  "Init" -> "Alarm" [ label = "is down" ];
  "Power returned" -> "Return charged" [ label = "is up & above good" ];
  "Return charged" -> "Client Down" [ label = "HYST Timer" ];
  "Client Down" -> "Charging" [ label = "DOWN Timer" ];
  "Alarm" [label=<Alarm<BR /><FONT POINT-SIZE="15">Signal client power down</FONT>>];
  "Client Down" [label=<Client Down<BR /><FONT POINT-SIZE="15">Switch off client</FONT>>];
}
 */



void StateMachineInit()
{
  PowerGoodLevel = TheSetup.PowerGood * 100;
  CurrentState = StateInit;  
  StateMachineEvent( EventEnter,0 );

  TimerStartCheckI2C(2000);
}


void  DoStateInit( Events event, unsigned int value )
{
  switch( event )
  {
      case   EventEnter:
        ClientSignalPowerGood();
        if( !isPowerFail() )
        {
          if( isChargedAboveGoodLevel() )
          {
            TransitTo( StatePowerUpCharged );
          }
          else
          {
            TransitTo( StatePowerUpCharging );
          }
        }
        else
        {
            TransitTo( StatePowerDownAlarm );
        }
        break;
        
      case   EventLeave:
      break;
      case   EventTimerTick:
      break;
      case   EventPowerDown:
      break;
      case   EventPowerUp:
      break;
      case   EventPowerLevelChanged:
      break;
      default:
      break;
  }
}

void  DoStatePowerUpCharging( Events event, unsigned int value )
{
  switch( event )
  {
      case   EventEnter:
        TimerStopRedBlink();
        TimerStartGreenBlink(SLOW);
        TimerStartStateMachine(5000);
        break;
      case   EventLeave:  
      break;
      case   EventPowerDown:
          TransitTo( StatePowerDown );
      break;
      case   EventPowerUp:
      break;
      case   EventTimerTick:
      case   EventPowerLevelChanged:
        if( isChargedAboveGoodLevel() )
        {
          TransitTo( StatePowerUpCharged );
          return;
        }
        TimerStartStateMachine(5000);
      break;
      default:
      break;
  }
}

void  DoStatePowerUpCharged( Events event, unsigned int value )
{
  switch( event )
  {
      case   EventEnter:
        TimerStopRedBlink();
        LEDGreen(ON);
      break;
      case   EventLeave:
      break;
      case   EventTimerTick:
      break;
      case   EventPowerDown:
        TransitTo( StatePowerDown );
      break;
      case   EventPowerUp:
      break;
      case   EventPowerLevelChanged:
      if( !isChargedFull() )
      {
        TimerStartGreenBlink(FAST);
      }
      else
      {
        TimerStopGreenBlink();
        LEDGreen( ON );
      }
      break;
      default:
      break;
  }
}


void  DoStatePowerDown( Events event, unsigned int value )
{
  switch( event )
  {
      case   EventEnter:
        TimerStopGreenBlink();
        TimerStartRedBlink(SLOW);
        break;
      case   EventLeave:
      break;
      case   EventTimerTick:
        TransitTo( StatePowerDownAlarm );
      break;
      case   EventPowerDown:
      break;
      case   EventPowerUp:
        TransitTo( StatePowerUpCharging );
      break;
      case   EventPowerLevelChanged:
      if( !isChargedAboveGoodLevel() )
      {
        TransitTo( StatePowerDownAlarm );
      }
      break;
      default:
      break;
  }
}

void  DoStatePowerDownAlarm( Events event, unsigned int value )
{
  switch( event )
  {
      case   EventEnter:
        TimerStopGreenBlink();
        TimerStartRedBlink(FAST);
        ClientSignalPowerDown();
        break;
      case   EventLeave:
      break;
      case   EventTimerTick:
      break;
      case   EventPowerDown:
      break;
      case   EventPowerUp:
          TransitTo( StatePowerReturned );
      break;
      case   EventPowerLevelChanged:
      break;
      default:
      break;
  }
}

void  DoStatePowerReturned( Events event, unsigned int value )
{
  switch( event )
  {
      case   EventEnter:
          TimerStartStateMachine(15000);
      break;
      case   EventLeave:
      break;
      case   EventTimerTick:
          TransitTo( StatePowerReturnedCharged );
      break;
      case   EventPowerDown:
      break;
      case   EventPowerUp:
      break;
      case   EventPowerLevelChanged:
        if( isPowerUp() && isChargedAboveGoodLevel() )
        {
          TransitTo( StatePowerReturnedCharged );
        }
      break;
      default:
      break;
  }
}

void  DoStatePowerReturnedCharged( Events event, unsigned int value )
{
  switch( event )
  {
      case   EventEnter:
          TimerStartStateMachine(((unsigned long)TheSetup.TimerHyst)*1000);
      break;
      case   EventLeave:
      break;
      case   EventTimerTick:
        TransitTo(StatePowerReturnedClientDown);
      break;
      case   EventPowerDown:
      break;
      case   EventPowerUp:
      break;
      case   EventPowerLevelChanged:
      break;
      default:
      break;
  }
}



void  DoStatePowerReturnedClientDown( Events event, unsigned int value )
{
  switch( event )
  {
      case   EventEnter:
        ClientSwitchPowerOff();
        ClientSignalPowerGood();
        TimerStartStateMachine(((unsigned long)TheSetup.TimerDown)*1000);
      break;
      case   EventLeave:
      break;
      case   EventTimerTick:
        if( isPowerUp() )
        {
          ClientSwitchPowerOn();
          TransitTo( StatePowerUpCharging );
          return;
        }
        TimerStartStateMachine(2000);
      break;
      case   EventPowerDown:
      break;
      case   EventPowerUp:
      break;
      case   EventPowerLevelChanged:
      break;
      default:
      break;
  }  
}


bool isPowerFail()
{
  return digitalRead(PFO) == 0;
}

bool isChargedAboveGoodLevel()
{
  unsigned int val = i2cReadVCAP();
  return val > PowerGoodLevel; 
}

bool isChargedFull()
{
  unsigned int val = i2cReadVCAP();
  return val > 9000; 
}

void StateMachineEvent( Events event, unsigned int value )
{
  if( TheSetup.Trace )
    StateMachineTrace( event, value );
    
  switch( CurrentState )
  {
    case StateInit:
      DoStateInit(event, value );
      break;
    case StatePowerUpCharging:
      DoStatePowerUpCharging(event, value );
      break;
    case StatePowerUpCharged:
      DoStatePowerUpCharged(event, value );
      break;
    case StatePowerDown:
      DoStatePowerDown(event, value );
      break;
    case StatePowerDownAlarm:
      DoStatePowerDownAlarm(event, value );
      break;
    case StatePowerReturned:
      DoStatePowerReturned(event, value );
      break;
    case StatePowerReturnedCharged:
      DoStatePowerReturnedCharged(event, value );
      break;
    case StatePowerReturnedClientDown:
      DoStatePowerReturnedClientDown(event, value );
      break;
    default:
      Serial.print( "Unknown State: "); Serial.println( CurrentState );
      DoCmdReset();
    }  
}

void StateMachineTrace( Events event, unsigned int value )
{
  StateMachinePrintState( CurrentState );
  Serial.print( " / " );

  switch( event )
  {
      case   EventEnter:
        Serial.print( F("Enter") );
      break;
      case   EventLeave:
        Serial.print( F("Leave") );
      break;
      case   EventTimerTick:
        Serial.print( F("Tick") );
      break;
      case   EventPowerDown:
        Serial.print( F("Down") );
      break;
      case   EventPowerUp:
        Serial.print( F("Up") );
      break;
      case   EventPowerLevelChanged:
        Serial.print( F("Level") );
      break;
      default:
      break;
  }  
  Serial.print( "  Val: " ); Serial.println( value );
}

void StateMachinePrintState( States state )
{
  switch( state )
  {
    case StateInit:
      Serial.print( F("Init") );
      break;
    case StatePowerUpCharging:
      Serial.print( F("Charging") );
      break;
    case StatePowerUpCharged:
      Serial.print( F("Charged") );
      break;
    case StatePowerDown:
      Serial.print( F("Down") );
      break;
    case StatePowerDownAlarm:
      Serial.print( F("Alarm") );
      break;
    case StatePowerReturned:
      Serial.print( F("Returned") );
      break;
    case StatePowerReturnedCharged:
      Serial.print( F("ReturnedCharged") );
      break;
    case StatePowerReturnedClientDown:
      Serial.print( F("ClientDown") );
      break;
    default:
      Serial.print( F("ERR-State: ")); Serial.println( CurrentState );
  }  
}



void TransitTo( States state )
{
  if( TheSetup.Trace )
  {
    StateMachinePrintState( CurrentState  ); 
    Serial.print(" -> ");
    StateMachinePrintState( state  ); 
    Serial.println();
  }
  TimerStopStateMachine();
  StateMachineEvent( EventLeave, 0 );
  CurrentState = state;
  StateMachineEvent( EventEnter, 0 );
}

