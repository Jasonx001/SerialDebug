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

/* Func name: AHT20_ReadTask()
 * Description: Read values from the sensor AHT20 */
void AHT20_Read(float *Temperature, float *Humidity);

#endif /* INC_AHT20_H_ */
