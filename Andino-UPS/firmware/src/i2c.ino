//------------------------------------------------------------
// I2C Communication with the LTC3350
//$Rev:: 891                  $:  Revision of last commit.
//$Author:: marcus            $:  Author of last commit.
//$Date:: 2018-06-26 15:10:13#$:  Date of last commit.
//------------------------------------------------------------

#include <Wire.h>
                                // BITS  Description      
#define REG_CLR_ALARMS      0x00  // 15:0 Clear alarms register
#define REG_MSK_ALARMS      0x01  // 15:0 Enable/mask alarms register
#define REG_MSK_MON_STATUS  0x02  // 9:0 Enable/mask monitor status alerts
#define REG_CAP_ESR_PER     0x04  // 15:0 Capacitance/ESR measurement period
#define REG_VCAPFB_DAC      0x05  // 3:0 VCAPvoltage reference DAC setting
#define REG_VSHUNT          0x06  // 15:0 Capacitor shunt voltage setting
#define REG_CAP_UV_LVL      0x07  // 15:0 Capacitor undervoltage alarm level
#define REG_CAP_OV_LVL      0x08  // 15:0 Capacitor overvoltage alarm level
#define REG_GPI_UV_LVL      0x09  // 15:0 GPI undervoltage alarm level
#define REG_GPI_OV_LVL      0x0A  // 15:0 GPI overvoltage alarm level
#define REG_VIN_UV_LVL      0x0B  // 15:0 VIN undervoltage alarm level
#define REG_VIN_OV_LVL      0x0C  // 15:0 VIN overvoltage alarm level
#define REG_VCAP_UV_LVL     0x0D  // 15:0 VCAPundervoltage alarm level
#define REG_VCAP_OV_LVL     0x0E  // 15:0 VCAPovervoltage alarm level
#define REG_VOUT_UV_LVL     0x0F  // 15:0 VOUTundervoltage alarm level
#define REG_VOUT_OV_LVL     0x10  //  15:0 VOUTovervoltage alarm level
#define REG_IIN_OC_LVL      0x11  // 15:0 IIN overcurrent alarm level
#define REG_ICHG_UC_LVL     0x12  // 15:0 ICHGundercurrent alarm level
#define REG_DTEMP_COLD_LVL  0x13  // 15:0 Die temperature cold alarm level
#define REG_DTEMP_HOT_LVL   0x14  // 15:0 Die temperature hot alarm level
#define REG_ESR_HI_LVL      0x15  // 15:0 ESR high alarm level
#define REG_CAP_LO_LVL      0x16  // 15:0 Capacitance low alarm level
#define REG_CTL_REG         0x17  // 3:0 Control register
#define REG_NUM_CAPS        0x1A  //  1:0 Number of capacitors configured 
#define REG_CHRG_STATUS     0x1B  // 11:0 Charger status register
#define REG_MON_STATUS      0x1C  //  9:0 Monitor status register
#define REG_ALARM_REG       0x1D  // 15:0 Active alarms register
#define REG_MEAS_CAP        0x1E  // 15:0 Measured capacitance value
#define REG_MEAS_ESR        0x1F  // 15:0 Measured ESR value
#define REG_MEAS_VCAP1      0x20  // 15:0 Measured capacitor one voltage
#define REG_MEAS_VCAP2      0x21  // 15:0 Measured capacitor two voltage
#define REG_MEAS_VCAP3      0x22  // 15:0 Measured capacitor three voltage
#define REG_MEAS_VCAP4      0x23  // 15:0 Measured capacitor four voltage
#define REG_MEAS_GPI        0x24  // 15:0 MeasuredGPI pin voltage
#define REG_MEAS_VIN        0x25    // 15:0 Measured VINvoltage
#define REG_MEAS_VCAP       0x26  // 15:0 Measured VCAPvoltage
#define REG_MEAS_VOUT       0x27  // 15:0 Measured VOUTvoltage
#define REG_MEAS_IIN        0x28  // 15:0 Measured IIN
#define REG_MEAS_ICHG       0x29  // 15:0 Measured ICHGcurrent
#define REG_MEAS_DTEMP      0x2A  // 15:0 Measured die temperature

void i2cInit()
{
  Wire.begin(); 
  i2cSetAlarmRegister();
}


void i2cSetAlarmRegister()
{
  writeRegister(REG_MSK_ALARMS, 0xFFFF );
}

void i2cClearAlarmRegister()
{
  writeRegister(REG_CLR_ALARMS, 0xFFFF );
  i2cSetAlarmRegister();
}

unsigned int oldVCAP = 0;
void i2cCheck()
{
  unsigned int vcap = i2cReadVCAP();
  vcap = (vcap/10)*10;
  if( vcap != oldVCAP )
  {
    oldVCAP = vcap;
    StateMachineEvent( EventPowerLevelChanged, vcap );
  }
}

unsigned int i2cReadVCAP()
{
  unsigned int val = readRegister(REG_MEAS_VCAP);
  val = map(val, 0, 0x7fff, 0, 48364);  
return val;  
}

int index = 0;
void i2cDumpRegister()
{
  Serial.println( "{" );
  dumpBinary(  "chrg_sts",  REG_CHRG_STATUS, 16 );
  dumpBinary(  "moni_sts",  REG_MON_STATUS, 16 );
//  dumpBinary(  "alarm",     REG_ALARM_REG, 16 );
  dumpDecimal( "vc1",       REG_MEAS_VCAP1, 6013,0 );  
  dumpDecimal( "vc2",       REG_MEAS_VCAP2, 6013,0 );  
  dumpDecimal( "vc3",       REG_MEAS_VCAP3, 6013,0 );  
  dumpDecimal( "vc4",       REG_MEAS_VCAP4, 6013,0 );  
  dumpDecimal( "vin",       REG_MEAS_VIN, 72415,0 );  
  dumpDecimal( "vcap",      REG_MEAS_VCAP, 48364,0 );  
  dumpDecimal( "vout",      REG_MEAS_VOUT, 72415,0 );  
  dumpDecimal( "iin",       REG_MEAS_IIN, 4061,0 );  
  dumpDecimal( "ichg",      REG_MEAS_ICHG, 4061,0 );  
  dumpDecimal( "temp",      REG_MEAS_DTEMP, 917, -251 );  
  Serial.print( "\"index\":");   Serial.print( index++ );   Serial.println();
  Serial.println("}");
}

void dumpBinary( const char * name, byte addr, byte bits )
{
  Serial.print( "\"" );
  Serial.print( name );
  Serial.print( "\": 0b" );
  print_binary( readRegister( addr ), 16 );  
  Serial.print( "," );
  Serial.println();  
}

void dumpDecimal( const char * name, byte addr, long map7FFF, int offset )
{
  unsigned int val = readRegister(addr);
  Serial.print( "\"" );
  Serial.print( name );
  Serial.print( "\": " );
  Serial.print( map(val, 0, 0x7fff, 0, map7FFF)+offset );  
  Serial.print( "," );
  Serial.println();  
}


uint16_t readRegister( byte addr )
{
int low, high;
  Wire.beginTransmission(9);   // transmit to device 9
  Wire.write(byte(addr));
  Wire.endTransmission();      // stop transmitting
  Wire.requestFrom(9, 2);    // request 2 bytes from slave device #9

  if (2 <= Wire.available()) 
  {
    low  = Wire.read(); 
    high = Wire.read();
    high = high << 8;
    high |= low;
    return high;
  }
  else
  {
    return 0xFFFF;  
  }    
}

void  writeRegister( byte addr, uint16_t value )
{
int low, high;
  Wire.beginTransmission(9);   // transmit to device 9
  Wire.write(byte(addr));
  Wire.write(byte(value&0xFF));
  Wire.write(byte(value>>8));
  Wire.endTransmission();      // stop transmitting
}


void print_binary(int v, int num_places)
{
    int mask=0, n;

    for (n=1; n<=num_places; n++)
    {
        mask = (mask << 1) | 0x0001;
    }
    v = v & mask;  // truncate v to specified number of places

    while(num_places)
    {

        if (v & (0x0001 << num_places-1))
        {
             Serial.print("1");
        }
        else
        {
             Serial.print("0");
        }

        --num_places;
    }
}


