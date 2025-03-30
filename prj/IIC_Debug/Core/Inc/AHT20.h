/*
 * AHT20.h
 *
 *  Created on: Mar 29, 2025
 *      Author: zhangzhijie
 */

#ifndef INC_AHT20_H_
#define INC_AHT20_H_

#include "i2c.h"

/*************************************************************
 *                   Functions Declaration                   *
 * ***********************************************************/

/* Func name: AHT20_Init()
 * Description: Init the sensor AHT20 */
void AHT20_Init();

/* Func name: AHT20_CMD_Meas()
 * Description: Command AHT20 to start the measurement */
void AHT20_CMD_Meas();

/* Func name: AHT20_GetHT_VAL()
 * Description: Get the temperature values from the sensor AHT20 */
void AHT20_GetHT_VAL();

/* Func name: AHT20_PARSE_VAL()
 * Description: Parse the raw values to physical value */
void AHT20_PARSE_VAL(float *Temperature, float *Humidity);

#endif /* INC_AHT20_H_ */
