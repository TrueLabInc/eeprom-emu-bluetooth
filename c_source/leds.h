/*
 * leds.cpp
 *
 *  Created on: Sep 22, 2016
 *      Author: rafal
 */


#include <avr/io.h>

namespace leds{
	enum led
	{
		_l1 = PD7,
		_l2 = PD6,
		_l3 = PD5,
	};
}

class Leds {
public:
	Leds();
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




