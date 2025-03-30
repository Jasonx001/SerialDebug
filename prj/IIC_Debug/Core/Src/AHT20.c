/*
 * AHT20.c
 *
 *  Created on: Mar 29, 2025
 *      Author: zhangzhijie
 */

#include "AHT20.h"

/*************************************************************
 *                   Global Macros                           *
 * ***********************************************************/
#define ATH20_ADDRESS         0x70
#define I2C_MAXDELAY_MS       1000

/*************************************************************
 *                      Global Variables                     *
 * ***********************************************************/
#define AHT20_RxBurrferSize 6U
uint8_t rdBuffer[AHT20_RxBurrferSize] = {0};

/*************************************************************
 *                   Local Functions                         *
 * ***********************************************************/

/* Func name: AHT20_Init()
 * Description: Init the sendor AHT20 */
void AHT20_Init()
{
	uint8_t rdVal;

	HAL_Delay(40);
	HAL_I2C_Master_Receive(&hi2c1, ATH20_ADDRESS, &rdVal, 1, I2C_MAXDELAY_MS);
	if ((rdVal & 0x08) == 0)
	{
		uint8_t txCmd[3] = { 0xBE, 0x08, 0x00 };
		HAL_I2C_Master_Transmit(&hi2c1, ATH20_ADDRESS, txCmd, 3, I2C_MAXDELAY_MS);
	}
}

/* Func name: AHT20_CMD_Meas()
 * Description: Command AHT20 to start the measurement */
void AHT20_CMD_Meas()
{
	uint8_t txCmd[3] = { 0xAC, 0x033, 0x00 };
	HAL_I2C_Master_Transmit_IT(&hi2c1, ATH20_ADDRESS, txCmd, 3);
}

/* Func name: AHT20_GetHT_VAL()
 * Description: Get the temperature values from the sensor AHT20 */
void AHT20_GetHT_VAL()
{
	HAL_I2C_Master_Receive_IT(&hi2c1, ATH20_ADDRESS, rdBuffer, AHT20_RxBurrferSize);
}

/* Func name: AHT20_PARSE_VAL()
 * Description: Parse the raw values to physical value */
void AHT20_PARSE_VAL(float *Temperature, float *Humidity)
{
	if ((rdBuffer[0] & 0x80) == 0x00)
	{
		uint32_t rawHumidity      =  0;
		uint32_t rawTemperature   =  0;
		// split and concatenate form buffer
		rawHumidity = ((uint32_t)rdBuffer[1] << 12) + ((uint32_t)rdBuffer[2] << 4) + ((uint32_t)rdBuffer[3] >> 4U);
		*Humidity = rawHumidity * 100.0f / (1 << 20);

		rawTemperature = (((uint32_t)rdBuffer[3] & 0x0F) << 16) + ((uint32_t)rdBuffer[4] << 8) + ((uint32_t)rdBuffer[5]);
		*Temperature = rawTemperature * 200.0f / (1 << 20) - 50;
	}
}



