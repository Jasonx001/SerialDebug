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

/* Func name: AHT20_ReadTask()
 * Description: Read values from the sensor AHT20 */
void AHT20_Read(float *Temperature, float *Humidity)
{
	uint8_t txCmd[3] = { 0xAC, 0x033, 0x00 };
	uint8_t rdBuffer[6];
	HAL_I2C_Master_Transmit(&hi2c1, ATH20_ADDRESS, txCmd, 3, I2C_MAXDELAY_MS);
	HAL_Delay(75);
	HAL_I2C_Master_Receive(&hi2c1, ATH20_ADDRESS, rdBuffer, 6, I2C_MAXDELAY_MS);
	if ((rdBuffer[0] & 0x80) == 0x00)
	{
		uint32_t rawHumidity      =            0;
		uint32_t rawTemperature   =            0;
		rawHumidity = ((uint32_t)rdBuffer[1] << 12) + ((uint32_t)rdBuffer[2] << 4) + ((uint32_t)rdBuffer[3] >> 4U);
		*Humidity = rawHumidity * 100.0f / (1 << 20);

		rawTemperature = (((uint32_t)rdBuffer[3] & 0x0F) << 16) + ((uint32_t)rdBuffer[4] << 8) + ((uint32_t)rdBuffer[5]);
		*Temperature = rawTemperature * 200.0f / (1 << 20) - 50;
	}
}

