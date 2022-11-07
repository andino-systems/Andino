//
//    
//       ###    ##    ## ########  #### ##    ##  #######  
//      ## ##   ###   ## ##     ##  ##  ###   ## ##     ## 
//     ##   ##  ####  ## ##     ##  ##  ####  ## ##     ## 
//    ##     ## ## ## ## ##     ##  ##  ## ## ## ##     ## 
//    ######### ##  #### ##     ##  ##  ##  #### ##     ## 
//    ##     ## ##   ### ##     ##  ##  ##   ### ##     ## 
//    ##     ## ##    ## ########  #### ##    ##  #######  
//
//    ########  ####  ######   #######  
//    ##     ##  ##  ##    ## ##     ## 
//    ##     ##  ##  ##       ##     ## 
//    ########   ##  ##       ##     ## 
//    ##         ##  ##       ##     ## 
//    ##         ##  ##    ## ##     ## 
//    ##        ####  ######   #######  
//    
// Default / Sample Firmware for the Andino X1 - PICO.
// 
// This example counts impulses at the digital inputs. Count stops are cyclically sent to the Raspberry via Sertial1. 
// Optionaly all Data can be send to Serial (USB) also.
// The digital inputs are additionally de-bounced. On the other hand, the relays can be switched or pulsed.
// The settings of the firmware are changed via commands and are stored in the eeprom (Flash). 
// This Version consider the extension boards 3DI, 5DI and 1DI2DO (Command HARD).
// The Communication runs with 38400 Baud.
// Interface, Commands
// All commands or messages are sent and received via /dev/ttyS0. 
// Every command has to be terminated by CR or LF. Message ends with CR and LF.
// RESET          ( Restart controller)
// INFO           ( print settings)
// HARD           ( Hardware, 0=noShield, 1=1DI2DO, 2=3DI, 3=5DI)
// POLL 10        ( Poll cycle in ms )
// DEBO 3         ( Debounce n Scans stable to accept )
// SKIP 3         ( Skip n Scans after pulse reconized )
// EDGE 1|0       ( count on Edge HL or LH )
// SEND 5000      ( send all xxx ms )
// CHNG 0|1       ( send on Pin Change - carefull if many changes)
// CNTR 0|1       ( Send counter, Default 1 otherwise on Pin States )
// REL? 0|1       ( send relay state - 1 to on or off )
// REL1 0|1       ( set relay 1 to on or off )
// REL2 0|1       ( set relay 2 to on or off )
// REL3 0|1       ( set relay 3 to on or off )
// REL4 0|1       ( set relay 4 to on or off )
// RPU1 1000      ( pulse relay 1 for nnn ms )
// RPU2 1000      ( pulse relay 2 for nnn ms )
//
// Message from the Firmware to the Raspberry
//
// :Message-ID{counter1,counter2,..}{state1,state2}
// 
// The Message starts with a ':'. After that follows a Message-ID. This is a modulo HEX Counter from 0..FFFF.
// Then within a '{' '}' the counter follows. The number of counter depends on the Hardware shields.
// The Counter are HEX encoded and runs from 0 to FFFF (modulo).
// Then again within a '{' '}' the current state of the inputs follows. 0-off, 1-on.
// if REL? = 1 a third {,} is appended with the current state of the Relais
// The number depends on the Hardware shields. The Message ends with a CR / LF [0x0d + 0x0a]
// Example
// :0040{0002,0000,000B}{0,0,0}
// :0041{0002,0000,000B}{0,0,0}
// :0042{0004,0000,000C}{0,0,0}
// :0043{0004,0000,000C}{0,0,0}
// :0044{0008,0000,000F}{0,0,1}
// :0045{0008,0000,000F}{0,0,1}
// or if REL? = 1
// :0040{0002,0000,000B}{0,0,0}{0,0}
// :0041{0002,0000,000B}{0,0,0}{0,0}
// :0042{0004,0000,000C}{0,0,0}{0,0}
#define VERSION "20221102"
// History:
// 20221102: Command "Test" for self test
// 20220804: Based on Version 5, this is a port for Raspberry Pico
// 201106: New Option: send relay state
// 200929: void setup_in_out() correction for 5DI
// 181026: New Command CHNG, Version in Info, CNTR can switch off the Counter - Only Events will be send
// 181126: Count-up only on configured EDGE
// 181216: Fixed debouncing
//
// How to Compile:
// Add this to the Library Manager
// https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json
// Install the Library "RPi_Pico_TimerInterrupt"
// Docu are here: https://arduino-pico.readthedocs.io/en/latest/


#include <EEPROM.h>
#include <RPi_Pico_TimerInterrupt.h>

#define LED_PIN   LED_BUILTIN

#define SHIELD_NONE 0
#define SHIELD_1DI2DO 1
#define SHIELD_3DI 2
#define SHIELD_5DI 3

#define IN_1_PIN      6
#define IN_2_PIN      7
#define OUT_1_PIN     2
#define OUT_2_PIN     3

// Only available with 3DI or 1DI2DO or 5DI shield
#define IN_3_PIN   10   // INT0
// Only available with 3DI or 5DI
#define IN_4_PIN   4    // SDA
// Only available with 3DI or 5DI
#define IN_5_PIN   5    // SCL
// Only available with 5DI 
#define IN_6_PIN   16   // MISO
// Only available with 5DI 
#define IN_7_PIN   19   // MOSI
// Only available with 1DI2DO shield
#define OUT_3_PIN  5     // SCL
#define OUT_4_PIN  17    // SD_EN / CS_0

#define LF 10
#define CR 13

#define SERIAL_TTY 1
#define SERIAL_USB 2


#define BAUD_RATE 38400

// ---------------------- [ Receive Data ]------------------
#define RX_SIZE  19
typedef struct 
{
  byte Index = 0;         // Data from TTY
  char Buffer[RX_SIZE+1];
} RXData;

RXData RXBufferTTY;
RXData RXBufferUSB;

// ---------------------- [ Setup Data ]------------------
struct Setup
{
  unsigned long CRC;          // CRC of the data
  byte          StructLen;    // Length of the structure
  unsigned int  PollCycle;    // Poll cycle in ms
  byte          PollCount;    // Poll-Count till level is stable
  bool          CountOnLH;    // Count on .. edge
  byte          SkipCount;    // Skip nn Scans after recognize a pulse
  unsigned int  SendCycle;    // Send cycle in ms
  byte          Shield;       // 0 = none, 1 = 1DI2DO, 2 = 3DI
  byte          SendOnChange; // 0 = Send only in clycle, 1 = send on Demand (Pin Change)
  byte          SendCounter;  // 0 = Send only Pin States, 1 = send counter and States
  byte          SendRelayInfo;// 0 = Send no RelayChange, 1 = send relay changes
  byte          SerialToUse;  // 1 = Serial (Raspberry),  2=Serial (USB), 3 = Booth
} TheSetup;

// ---------------------- [ Input & Debounce ] ----------------
typedef struct {
  byte current_val = 0;
  byte poll_counter = 0;
  byte skip_counter = 0;
  unsigned long Counter = 0;
} CounterControl;

CounterControl Counter1;
CounterControl Counter2;
CounterControl Counter3;
CounterControl Counter4;
CounterControl Counter5;
CounterControl Counter6;
CounterControl Counter7;

int ledState = LOW;

// ---------------------- [ Releais ] ----------------
typedef struct {
  byte puls_timer  = 0;
} RelaisControl;

RelaisControl Relais1;
RelaisControl Relais2;
RelaisControl Relais3;
RelaisControl Relais4;

bool pinChanged = false;

// ---------------------- [ Timer ] ----------------
RPI_PICO_Timer Timer0(0);


void setup() 
{
  Serial.begin(BAUD_RATE);  // tty
  Serial.setTimeout(100);
  Serial1.begin(BAUD_RATE); // USB
  Serial1.setTimeout(100);

  Serial_println( "STRT" );
  EEPROM.begin( ((sizeof(TheSetup)/256)+1)*256 );
  SetupRead();
  pinMode(LED_PIN, OUTPUT);
  setup_in_out();
  setup_interrupt();
}

void setup_in_out()
{
  pinMode(IN_1_PIN,INPUT_PULLUP ); 
  pinMode(IN_2_PIN,INPUT_PULLUP ); 
  pinMode(IN_3_PIN,INPUT_PULLUP ); 
  pinMode(OUT_1_PIN,OUTPUT_2MA);
  pinMode(OUT_2_PIN,OUTPUT_2MA);
  
  if( TheSetup.Shield == SHIELD_1DI2DO )
  {  
    pinMode(OUT_3_PIN,OUTPUT_2MA);
    pinMode(OUT_4_PIN,OUTPUT_2MA);
  }
  if( TheSetup.Shield == SHIELD_3DI || TheSetup.Shield == SHIELD_5DI)
  {  
    pinMode(IN_4_PIN,INPUT_PULLUP); 
    pinMode(IN_5_PIN,INPUT_PULLUP); 
  }
  if( TheSetup.Shield == SHIELD_5DI )
  {  
    pinMode(IN_6_PIN,INPUT_PULLUP); 
    pinMode(IN_7_PIN,INPUT_PULLUP); 
  }
  
}

void setup_interrupt()
{
  unsigned long timeInMicro = TheSetup.PollCycle;
  timeInMicro *= 1000;
  Timer0.attachInterruptInterval(timeInMicro, timerInterruptHandler);
}

unsigned long lastSendMillis = 0;
unsigned long lastSecondMillis = 0;

word loopCounter = 0;

void loop() 
{
  DoCheckRxData();
  unsigned long currentMillis = millis();
  if(   (currentMillis - lastSendMillis  >= TheSetup.SendCycle) 
     || (TheSetup.SendOnChange && pinChanged ) )
  {
    pinChanged = false;
    lastSendMillis = currentMillis;
    Serial_print( ':' );
    PrintHex16(++loopCounter); 
    if( TheSetup.SendCounter )
    {
      Serial_print( '{' );
      PrintHex16(Counter1.Counter); 
      Serial_print( ',' );
      PrintHex16(Counter2.Counter);
      if( TheSetup.Shield == SHIELD_1DI2DO || TheSetup.Shield == SHIELD_3DI || TheSetup.Shield == SHIELD_5DI)
      {
        Serial_print( ',' );
        PrintHex16(Counter3.Counter);
      }
      if( TheSetup.Shield == SHIELD_3DI || TheSetup.Shield == SHIELD_5DI)
      {
        Serial_print( ',' );
        PrintHex16(Counter4.Counter);
        Serial_print( ',' );
        PrintHex16(Counter5.Counter);
      }    
      if( TheSetup.Shield == SHIELD_5DI)
      {
        Serial_print( ',' );
        PrintHex16(Counter6.Counter);
        Serial_print( ',' );
        PrintHex16(Counter7.Counter);
      }
      Serial_print( "}" );
    }    
    Serial_print( "{" );
    Serial_print(Counter1.current_val, DEC ); 
    Serial_print( ',' );
    Serial_print(Counter2.current_val, DEC ); 
    if( TheSetup.Shield == SHIELD_1DI2DO || TheSetup.Shield == SHIELD_3DI || TheSetup.Shield == SHIELD_5DI)
    {
      Serial_print( ',' );
      Serial_print(Counter3.current_val, DEC );
    }
    if( TheSetup.Shield == SHIELD_3DI || TheSetup.Shield == SHIELD_5DI )
    {
      Serial_print( ',' );
      Serial_print(Counter4.current_val, DEC );
      Serial_print( ',' );
      Serial_print(Counter5.current_val, DEC );
    }
    if( TheSetup.Shield == SHIELD_5DI )
    {
      Serial_print( ',' );
      Serial_print(Counter6.current_val, DEC );
      Serial_print( ',' );
      Serial_print(Counter7.current_val, DEC );
    }
    Serial_print( "}" );
    if( TheSetup.SendRelayInfo == 1 )
    {
      Serial_print( "{" );
      Serial_print(digitalRead(OUT_1_PIN),DEC);
      Serial_print( ',' );
      Serial_print(digitalRead(OUT_2_PIN),DEC);
      if( TheSetup.Shield == SHIELD_1DI2DO )
      {
        Serial_print( ',' );
        Serial_print(digitalRead(OUT_3_PIN),DEC);
        Serial_print( ',' );
        Serial_print(digitalRead(OUT_4_PIN),DEC);
      }
      Serial_print( "}" );
    }
    Serial_println();
  }

  if (currentMillis - lastSecondMillis  >= 100) 
  {
    lastSecondMillis = currentMillis;
    if( Relais1.puls_timer != 0 )
    {
      if( --Relais1.puls_timer == 0 )
      {
        digitalWrite(OUT_1_PIN, 0);
        Serial_println( "REL1 0" );
      }
    }
    if( Relais2.puls_timer != 0 )
    {
      if( --Relais2.puls_timer == 0 )
      {
        digitalWrite(OUT_2_PIN, 0);
        Serial_println( "REL2 0" );
      }
    }
    if( Relais3.puls_timer != 0 )
    {
      if( --Relais3.puls_timer == 0 )
      {
        digitalWrite(OUT_3_PIN, 0);
        Serial_println( "REL3 0" );
      }
    }
    if( Relais4.puls_timer != 0 )
    {
      if( --Relais4.puls_timer == 0 )
      {
        digitalWrite(OUT_4_PIN, 0);
        Serial_println( "REL4 0" );
      }
    }
  }
}

bool timerInterruptHandler(struct repeating_timer *t)
{
  byte input;
  
  if (ledState == LOW)
    ledState = HIGH;
  else
    ledState = LOW;
  digitalWrite(LED_PIN, ledState);

  doCounter( &Counter1, digitalRead( IN_1_PIN ) );
  doCounter( &Counter2, digitalRead( IN_2_PIN ) );
  if( TheSetup.Shield == SHIELD_NONE )
    return true;
  doCounter( &Counter3, digitalRead( IN_3_PIN ) );
  if( TheSetup.Shield == SHIELD_1DI2DO )
    return true;
  doCounter( &Counter4, digitalRead( IN_4_PIN ) );
  doCounter( &Counter5, digitalRead( IN_5_PIN ) );
  if( TheSetup.Shield == SHIELD_3DI )
    return true;
  doCounter( &Counter6, digitalRead( IN_6_PIN ) );
  doCounter( &Counter7, digitalRead( IN_7_PIN ) );

return true; 
}

void doCounter( CounterControl * pCounter, byte input )
{
  if( pCounter->skip_counter == 0 )
  {
    input = (input==1 )?0:1;
    if( pCounter->current_val  != input )
    {
        pCounter->poll_counter ++;
        if( pCounter->poll_counter == TheSetup.PollCount )
        {
          if( input == TheSetup.CountOnLH )
          {
             pCounter->Counter++;
          }
          pCounter->current_val   = input;
          pCounter->poll_counter  = 0;
          pCounter->skip_counter = TheSetup.SkipCount;
          pinChanged = true;
        }
    }
    else
    {
      pCounter->poll_counter = 0;
    }
  }
  else
  {
    pCounter->skip_counter--;
  }
}

// ----------------------------------------------------------------------------------
// Setup
// ----------------------------------------------------------------------------------
unsigned long SetupCalcCrc()
{
  const unsigned long crc_table[16] = {
    0x00000000, 0x1db71064, 0x3b6e20c8, 0x26d930ac,
    0x76dc4190, 0x6b6b51f4, 0x4db26158, 0x5005713c,
    0xedb88320, 0xf00f9344, 0xd6d6a3e8, 0xcb61b38c,
    0x9b64c2b0, 0x86d3d2d4, 0xa00ae278, 0xbdbdf21c
  };

  unsigned long crc = ~0L;

  byte * p = (byte*)&TheSetup.StructLen;
  int len = sizeof( TheSetup ) - sizeof( TheSetup.CRC );
  for (int i = 0 ; i<len; i++)
  {
    crc = crc_table[(crc ^ *p) & 0x0f] ^ (crc >> 4);
    crc = crc_table[(crc ^ (*p >> 4)) & 0x0f] ^ (crc >> 4);
    p++;
    crc = ~crc;
  }
  return crc;
}

void SetupDefault()
{
  TheSetup.PollCycle = 10;    // Poll cykle 
  TheSetup.PollCount = 3;     // Poll count till accepted
  TheSetup.SkipCount = 0;     // Skip nn Scans after recognize a pulse
  TheSetup.CountOnLH = 1;     // LH Edge
  TheSetup.SendCycle = 2000;  // Cycle in ms
  TheSetup.Shield = 0;        // No Shield 
  TheSetup.SendOnChange = 0;  // No Send on Pin Change 
  TheSetup.SendCounter = 1;   // Send Counter
  TheSetup.SendRelayInfo = 1; // No Relay Change
  TheSetup.SerialToUse = SERIAL_TTY; // only Serial to Raspberry
}

#define EEPROM_ADDRESS  0
void SetupRead()
{
  EEPROM.get(EEPROM_ADDRESS, TheSetup);
  if( TheSetup.CRC != SetupCalcCrc() )
  {
    Serial_println( "ERROR CONFIG SET TO DEFAULT" );
    DoCmdInfo();
    SetupDefault();
    SetupWrite();
  }
}

void SetupWrite()
{
  TheSetup.StructLen = sizeof( TheSetup );
  TheSetup.CRC = SetupCalcCrc();
  EEPROM.put(EEPROM_ADDRESS, TheSetup);
  EEPROM.commit();
}

// ----------------------------------------------------------------------------------
// R X D
// ----------------------------------------------------------------------------------
void DoCheckRxData()
{
  if( Serial.available() > 0 )
  {
    DoProcessRxData( &RXBufferUSB, Serial.read(),SERIAL_USB );
  }
  if( Serial1.available() > 0 )
  {
    DoProcessRxData( &RXBufferTTY, Serial1.read(),SERIAL_TTY );
  }
}

void DoProcessRxData(RXData * RXBuffer, byte rx, byte bit2Enable)
{
    if( RXBuffer->Index >= RX_SIZE )
    {
      RXBuffer->Index = 0;
    }

    if( RXBuffer->Index == 0 && (rx == LF || rx == CR) )
      return;
    if( rx == LF || rx == CR )
    {
      byte oldSetup = TheSetup.SerialToUse;
      TheSetup.SerialToUse |= bit2Enable;
      if( oldSetup != TheSetup.SerialToUse )
      {
        Serial.println("setup");
        SetupWrite();
      }
      RXBuffer->Buffer[RXBuffer->Index++] = 0;
      OnDataReceived(RXBuffer->Buffer); 
      RXBuffer->Index = 0;
    }
    else
    {
      RXBuffer->Buffer[RXBuffer->Index++] = rx;
    }
}


// ----------------------------------------------------------------------------------
// C O M M A N D S
// ----------------------------------------------------------------------------------
// See first page
void OnDataReceived( char* RxBuffer)
{
  bool result = false;
  bool writeSetup = false;
  bool callSetupInterrupt = false;
  String cmd = RxBuffer;
  cmd.toUpperCase();
  
  if( cmd.startsWith("RESET"))
  {
    Serial_println( "OK" );
    DoCmdReset();
  }
  
  if(  cmd.startsWith("INFO")
    || cmd.startsWith("HELP"))
  {
    DoCmdInfo();
    result = true;
  }

  if( cmd.startsWith("TEST"))
  {
    DoCmdTest();
    result = true;
  }

  int value = toInt( cmd, 5 );
  if( value != -1 )
  {
    if( cmd.startsWith("POLL "))
    {
      if( !checkRange( value, 10, 1000 ) )
        return;
      Serial_print( "POLL ");
      Serial_println( value, DEC );
      writeSetup = TheSetup.PollCycle != value;
      TheSetup.PollCycle = value;
      result = true;
      callSetupInterrupt = true;
    }
    else
    if( cmd.startsWith("SKIP "))
    {
      if( !checkRange( value, 0, 250 ) )
        return;
      Serial_print( "SKIP ");
      Serial_println( value, DEC );
      writeSetup = TheSetup.SkipCount != value;
      TheSetup.SkipCount = value;
      result = true;
      callSetupInterrupt = true;
    }
    else
    if( cmd.startsWith("DEBO "))
    {
      if( !checkRange( value, 1, 20 ) )
        return;
      Serial_print( "DEBO ");
      Serial_println( value, DEC );
      writeSetup = TheSetup.PollCount != value;
      TheSetup.PollCount = value;
      result = true;
    }
    else
    if( cmd.startsWith("EDGE "))
    {
      if( !checkRange( value, 0, 1 ) )
        return;
      TheSetup.CountOnLH = value;
      Serial_print( "EDGE ");
      Serial_println( value, DEC );
      writeSetup = TheSetup.CountOnLH != value;
      TheSetup.CountOnLH = value;
      result = true;
    }
    else
    if( cmd.startsWith("REL? "))
    {
      if( !checkRange( value, 0, 1 ) )
        return;
      writeSetup = TheSetup.SendRelayInfo != value;
      TheSetup.SendRelayInfo = value;
      Serial_print( "REL? ");
      Serial_println( value, DEC );
      result = true;
    }
    else
    if( cmd.startsWith("REL1 "))
    {
      if( !checkRange( value, 0, 1 ) )
        return;
      digitalWrite(OUT_1_PIN, value);
      Serial_print( "REL1 ");
      Serial_println( value, DEC );
      result = true;
    }
    else
    if( cmd.startsWith("REL2 "))
    {
      if( !checkRange( value, 0, 1 ) )
        return;
      digitalWrite(OUT_2_PIN, value);
      Serial_print( "REL2 ");
      Serial_println( value, DEC );
      result = true;
    }
    else
    if( TheSetup.Shield == SHIELD_1DI2DO &&  cmd.startsWith("REL3 "))
    {
      if( !checkRange( value, 0, 1 ) )
        return;
      digitalWrite(OUT_3_PIN, value);
      Serial_print( "REL3 ");
      Serial_println( value, DEC );
      result = true;
    }
    else
    if( TheSetup.Shield == SHIELD_1DI2DO && cmd.startsWith("REL4 "))
    {
      if( !checkRange( value, 0, 1 ) )
        return;
      digitalWrite(OUT_4_PIN, value);
      Serial_print( "REL4 ");
      Serial_println( value, DEC );
      result = true;
    }
    else
    if( cmd.startsWith("RPU1 "))
    {
      if( !checkRange( value, 1, 255 ) )
        return;
      digitalWrite(OUT_1_PIN, 1);
      Relais1.puls_timer = value;
      Serial_print( "RPU1 ");
      Serial_println( value, DEC );
      Serial_println( "REL1 1" );
      result = true;
    }
    else
    if( cmd.startsWith("RPU2 "))
    {
      if( !checkRange( value, 0, 255 ) )
        return;
      digitalWrite(OUT_2_PIN, 1);
      Relais2.puls_timer = value;
      Serial_print( "RPU2 ");
      Serial_println( value, DEC );
      Serial_println( "REL2 1" );
      result = true;
    }
    else
    if( TheSetup.Shield == SHIELD_1DI2DO && cmd.startsWith("RPU3 "))
    {
      if( !checkRange( value, 1, 255 ) )
        return;
      digitalWrite(OUT_3_PIN, 1);
      Relais3.puls_timer = value;
      Serial_print( "RPU3 ");
      Serial_println( value, DEC );
      Serial_println( "REL3 1" );
      result = true;
    }
    else
    if( TheSetup.Shield == SHIELD_1DI2DO && cmd.startsWith("RPU4 "))
    {
      if( !checkRange( value, 0, 255 ) )
        return;
      digitalWrite(OUT_4_PIN, 1);
      Relais4.puls_timer = value;
      Serial_print( "RPU4 ");
      Serial_println( value, DEC );
      Serial_println( "REL4 1" );
      result = true;
    }
    else
    if( cmd.startsWith("HARD"))
    {
      if( !checkRange( value, 0, 3 ) )
        return;
      Serial_print( "HARD ");
      Serial_println( value, DEC );
      setup_in_out();
      writeSetup = TheSetup.Shield != value;
      TheSetup.Shield = value;
      result = true;
    }
    else
    if( cmd.startsWith("CHNG"))
    {
      if( !checkRange( value, 0, 1 ) )
        return;
      Serial_print( "CHNG ");
      Serial_println( value, DEC );
      writeSetup = TheSetup.SendOnChange != value;
      TheSetup.SendOnChange = value;
      result = true;
    }
    else
    if( cmd.startsWith("CNTR"))
    {
      if( !checkRange( value, 0, 1 ) )
        return;
      Serial_print( "CNTR ");
      Serial_println( value, DEC );
      writeSetup = TheSetup.SendCounter != value;
      TheSetup.SendCounter = value;
      result = true;
    }
    else
    if( cmd.startsWith("SEND "))
    {
      if( !checkRange( value, 100, 50000 ) )
        return;
      Serial_print( "SEND ");
      Serial_println( value, DEC );
      writeSetup = TheSetup.SendCycle != value;
      TheSetup.SendCycle = value;
      result = true;
    }
    else
    if( cmd.startsWith("COMX"))
    {
      if( !checkRange( value, 0, 3 ) )
        return;
      Serial_print( "COMX ");
      Serial_println( value, DEC );
      writeSetup = TheSetup.SerialToUse != value;
      TheSetup.SerialToUse = value;
      result = true;
    }
  }
  if( result )
  {
    if( writeSetup )
      SetupWrite();
    if( callSetupInterrupt )
      setup_interrupt();
  }
  else
    Serial_println( "SYNTAX" );
}

void DoCmdInfo()
{
    Serial_print( "HARD "); Serial_println( TheSetup.Shield, DEC );
    Serial_print( "COMX "); Serial_println( TheSetup.SerialToUse, DEC );
    Serial_print( "POLL "); Serial_println( TheSetup.PollCycle, DEC );
    Serial_print( "DEBO "); Serial_println( TheSetup.PollCount, DEC );
    Serial_print( "SKIP "); Serial_println( TheSetup.SkipCount, DEC );
    Serial_print( "EDGE "); Serial_println(TheSetup.CountOnLH, DEC );
    Serial_print( "SEND "); Serial_println( TheSetup.SendCycle, DEC);
    Serial_print( "CHNG "); Serial_println( TheSetup.SendOnChange, DEC);
    Serial_print( "CNTR "); Serial_println( TheSetup.SendCounter, DEC);
    Serial_print( "REL? "); Serial_println( TheSetup.SendRelayInfo, DEC);
    Serial_print( "REL1 "); Serial_println( digitalRead(OUT_1_PIN), DEC);
    Serial_print( "REL2 "); Serial_println( digitalRead(OUT_2_PIN), DEC);
    if( TheSetup.Shield == SHIELD_1DI2DO)
    {
      Serial_print( "REL3 "); Serial_println( digitalRead(OUT_3_PIN), DEC);
      Serial_print( "REL4 "); Serial_println( digitalRead(OUT_4_PIN), DEC);
    }
    Serial_println( "HARD 0 (no extension)" );
    Serial_println( "HARD 1 (1DI2DO)" );
    Serial_println( "HARD 2 (3DI)" );
    Serial_println( "HARD 3 (5DO)" );
    Serial_print( "VERS " ); Serial_println(VERSION);
}

void DoCmdReset()
{
//  wdt_enable( WDTO_60MS );
   while(1) {}
}

void DoCmdTest()
{
bool fail = false;

    Serial_println( "TEST - START" );
    digitalWrite(OUT_1_PIN, 0 );
    digitalWrite(OUT_2_PIN, 0 );
    delay(200);

    while(1==1)
    {
        // Check Rel 1  + Input 1
        if( Counter1.current_val != 0 )
        {
          Serial_println( "Pin 1 - 0 fail" );
          fail = true;
          break;
        }
        digitalWrite(OUT_1_PIN, 1 );
        delay(400);
        if( Counter1.current_val != 1 )
        {
          Serial_println( "Pin 1 - 1 fail" );
          fail = true;
          break;
        }
        digitalWrite(OUT_1_PIN, 0);
        delay(400);
        if( Counter1.current_val != 0 )
        {
          Serial_println( "Pin 1 - 0 fail" );
          fail = true;
          break;
        }
        
        // Check Rel 1  + Input 1
        if( Counter2.current_val != 0 )
        {
          Serial_println( "Pin 2 - 0 fail" );
          fail = true;
          break;
        }
        digitalWrite(OUT_2_PIN, 1 );
        delay(400);
        if( Counter2.current_val != 1 )
        {
          Serial_println( "Pin 2 - 1 fail" );
          fail = true;
          break;
        }
        digitalWrite(OUT_2_PIN, 0);
        delay(400);
        if( Counter2.current_val != 0 )
        {
          Serial_println( "Pin 2 - 0 fail" );
          fail = true;
          break;
        }
        fail = false;
        break;
    }  
    if( fail )
      Serial_println( "TEST - FAIL" );
    else
      Serial_println( "TEST - OKAY" );
}


bool checkRange( unsigned int val, unsigned int mini, unsigned int maxi )
{
  if( val < mini || val > maxi )
  {
    Serial_print( "INVALID. MIN=" );
    Serial_print( mini, DEC );
    Serial_print( " MAX=" );
    Serial_println( maxi, DEC );
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

//-------------------------------[ Print from here ]--------------------------------

void PrintHex16(word data)
{
 char tmp[5];
 byte first;
 int j=0;

   first = (data >> 12) | 48;
   if (first > 57) tmp[0] = first + (byte)7;
   else tmp[0] = first ;
  
   first = ((data>>8) & 0x0F) | 48;
   if (first > 57) tmp[1] = first + (byte)7; 
   else tmp[1] = first;

   first = ((data>>4) & 0x0F) | 48;
   if (first > 57) tmp[2] = first + (byte)7; 
   else tmp[2] = first;

   first = (data & 0x0F) | 48;
   if (first > 57) tmp[3] = first + (byte)7; 
   else tmp[3] = first;
   
   tmp[4] = 0;
   Serial_print(tmp);
}


void Serial_print(const String &s) 
{
  if( (TheSetup.SerialToUse & SERIAL_TTY ) != 0 )
    Serial1.print( s ); 
  if( (TheSetup.SerialToUse & SERIAL_USB ) != 0 )
    Serial.print( s ); 
}

void Serial_print(const char s[]) 
{
  if( (TheSetup.SerialToUse & SERIAL_TTY ) != 0 )
    Serial1.print( s ); 
  if( (TheSetup.SerialToUse & SERIAL_USB ) != 0 )
    Serial.print( s ); 
}

void Serial_print(char s) 
{
  if( (TheSetup.SerialToUse & SERIAL_TTY ) != 0 )
    Serial1.print( s ); 
  if( (TheSetup.SerialToUse & SERIAL_USB ) != 0 )
    Serial.print( s ); 
}

void Serial_print(unsigned char s, int base)
{
  if( (TheSetup.SerialToUse & SERIAL_TTY ) != 0 )
    Serial1.print( s,base );
  if( (TheSetup.SerialToUse & SERIAL_USB ) != 0 )
    Serial.print( s,base );
}

void Serial_print(int s, int base)
{
  if( (TheSetup.SerialToUse & SERIAL_TTY ) != 0 )
    Serial1.print( s,base );
  if( (TheSetup.SerialToUse & SERIAL_USB ) != 0 )
    Serial.print( s,base );
}

void Serial_print(unsigned int s, int base)
{
  if( (TheSetup.SerialToUse & SERIAL_TTY ) != 0 )
    Serial1.print( s,base );
  if( (TheSetup.SerialToUse & SERIAL_USB ) != 0 )
    Serial.print( s,base );
}

void Serial_print(long s, int base)
{
  if( (TheSetup.SerialToUse & SERIAL_TTY ) != 0 )
    Serial1.print( s,base );
  if( (TheSetup.SerialToUse & SERIAL_USB ) != 0 )
    Serial.print( s,base );
}

void Serial_print(unsigned long s, int base)
{
  if( (TheSetup.SerialToUse & SERIAL_TTY ) != 0 )
    Serial1.print( s,base );
  if( (TheSetup.SerialToUse & SERIAL_USB ) != 0 )
    Serial.print( s,base );
}

//void Serial_print(double n, int digits)
//{
//  Serial.print( n,digits );
//}

// println
void Serial_println() 
{
  Serial_print("\r\n"); 
}

void Serial_println(const String &s) 
{
  Serial_print( s ); 
  Serial_println();
}

void Serial_println(const char str[]) 
{
  Serial_print( str ); 
  Serial_println();
}

void Serial_println(char c) 
{
  Serial_print( c );
  Serial_println();
}

void Serial_println(unsigned char b, int base)
{
  Serial_print( b,base );
  Serial_println();
}

void Serial_println(int n, int base)
{
  Serial_print( n,base );
  Serial_println();
}

void Serial_println(unsigned int n, int base)
{
  Serial_print( n,base );
  Serial_println();
}

void Serial_println(long n, int base)
{
  Serial_print( n,base );
  Serial_println();
}

void Serial_println(unsigned long n, int base)
{
  Serial_print( n,base );
  Serial_println();
}

//void Serial_println(double n, int digits)
//{
//  Serial_print( n,digits );
//  Serial_println();
//}
