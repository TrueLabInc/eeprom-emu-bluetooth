/*
 * main.h
 *
 *  Created on: Sep 21, 2016
 *      Author: rafal
 */

#ifndef MAIN_H_
#define MAIN_H_
#include "bluetooth.h"
#include "uart.h"
#include "buffers_ctrl.h"
#include "serial.h"
#include "timers.h"

#define __STR2__(x) #x
#define __STR__(x) __STR2__(x)
#pragma message("Compilation date:")
#pragma message(__STR__(__DATE__))
#pragma message(__STR__(F_CPU))
#define CONCATENATE(str1, str2) str1 ## str2
//extern const uint8_t PROGMEM eeprom_image[];


#endif /* MAIN_H_ */
