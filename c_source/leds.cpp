/*
 * leds.cpp
 *
 *  Created on: Sep 22, 2016
 *      Author: rafal
 */


#include "leds.h"

void leds_control::leds_on(){
			PORTD |= _BV(l1) | _BV(l2) | _BV(l3);
}



