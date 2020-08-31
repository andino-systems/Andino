//------------------------------------------------------------
// Global variables and definition
//$Rev:: 891                  $:  Revision of last commit.
//$Author:: marcus            $:  Author of last commit.
//$Date:: 2018-06-26 15:10:13#$:  Date of last commit.
//------------------------------------------------------------

typedef enum 
{
/*  0 */  StateInit,
/*  1 */  StatePowerUpCharging,
/*  2 */  StatePowerUpCharged,
/*  3 */  StatePowerDown,
/*  4 */  StatePowerDownAlarm,
/*  5 */  StatePowerReturned,
/*  6 */  StatePowerReturnedCharged,
/*  7 */  StatePowerReturnedClientDown,
} States;

States CurrentState = StateInit;

typedef enum 
{
/*  0 */  EventLeave,
/*  1 */  EventEnter,
/*  2 */  EventTimerTick,
/*  3 */  EventPowerDown,
/*  4 */  EventPowerUp,
/*  5 */  EventPowerLevelChanged
} Events;


// ---------------------- [ Timer Data ]------------------
unsigned long greenMillis = 0;
unsigned long redMillis = 0;
unsigned long stateMachineMillis = 0;
unsigned long i2cCheckMillis = 0;

unsigned long greenInterval = 0;
unsigned long redInterval = 0;
unsigned long stateMachineInterval = 0;
unsigned long i2cCheckInterval = 0;

// ---------------------- [ Setup Data ]------------------
struct Setup
{
  unsigned long CRC;          // CRC of the data
  byte          StructLen;    // Length of the structure
  byte          PowerGood;    // Power level good in % [Allowed 20..90 / Default 80%]
  byte          TimerHyst;    // Power Return: wait after rise over PowerGood level to PowerOff Client [0=Disabled / Default: 5 sec]
  byte          TimerDown;    // Power Return: PowerOff Client duration in sec. [Default: 5 sec]
  bool          Trace;        // Enable traceing [ default: false ]
} TheSetup;

unsigned int PowerGoodLevel = -1; // in milli Volt Calculated from PowerGood in Init

#define LF 10
#define CR 13

#define SLOW 1000
#define FAST 250


