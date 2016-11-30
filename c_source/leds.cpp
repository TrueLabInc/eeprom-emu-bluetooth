/*
 * leds.cpp
 *
 *  Created on: Sep 22, 2016
 *      Author: rafal
 */


#include "leds.h"

Leds::Leds(){	//constructor without args
	DDRD |= _BV(l1) | _BV(l2) | _BV(l3);
}

void Leds::leds_on(){
			PORTD |= _BV(l1) | _BV(l2) | _BV(l3);
}



