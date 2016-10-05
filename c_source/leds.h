/*
 * leds.cpp
 *
 *  Created on: Sep 22, 2016
 *      Author: rafal
 */


#include <avr/io.h>

class leds_control {
public:
	leds_control(){	//constructor withou args
		DDRD |= _BV(l1) | _BV(l2) | _BV(l3);
	}
	enum led_state{
		on = 1,
		off = 0,
		sw = 2,
	};
	enum led
	{
		l1 = PD7,
		l2 = PD6,
		l3 = PD5,
	};
public:
	void leds_on();
	struct led1 {
		void operator = (led_state v){
			if(v==on){
				PORTD |= _BV(l1);
			}
			else if (v==sw) {
				PORTD ^= _BV(l1);
			}
			else {
				PORTD &= ~_BV(l1);
			}
		}
	};
	struct led2 {
			void operator = (led_state v){
				if(v==on){
					PORTD |= _BV(l2);
				}
				else if (v==sw) {
					PORTD ^= _BV(l2);
				}
				else {
					PORTD &= ~_BV(l2);
				}
			}
		};
	struct led3 {
			void operator = (led_state v){
				if(v==on){
					PORTD |= _BV(l3);
				}
				else if (v==sw) {
					PORTD ^= _BV(l3);
				}
				else {
					PORTD &= ~_BV(l3);
				}
			}
		};
	led1 L1; led2 L2; led3 L3;
};




