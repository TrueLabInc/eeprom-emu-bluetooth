/*
 * buffers_ctrl.h
 *
 *  Created on: Sep 25, 2016
 *      Author: rafal
 */

#ifndef BUFFERS_CTRL_H_
#define BUFFERS_CTRL_H_

#include <stdlib.h>
#include <avr/io.h>
#include "pins.h"

class BuffersCtrl{
public:
	typedef enum pins{
		addr_buff_oe_pin = PB3,
		ce_conn_ctrl_pin = PB2,
	}pins;
	BuffersCtrl();
	class addr_buff_oe_ {
	public:
		void operator=(pin_state state){
			if(state == pin_state::hi)
				PORTB |= _BV(pins::addr_buff_oe_pin);
			else if(state == pin_state::toggle)
				PORTB ^= _BV(pins::addr_buff_oe_pin);
			else{
				PORTB &= ~_BV(pins::addr_buff_oe_pin);
			}
		}
	};
	class ce_conn_ctrl_ {
	public:
		void operator=(pin_state state){
			if(state){
				PORTB |= _BV(ce_conn_ctrl_pin);
			}
			else{
				PORTB &= ~_BV(ce_conn_ctrl_pin);
			}
		}
	};
	addr_buff_oe_ address_port_conn; ce_conn_ctrl_ ce_conn_ctrl;

};

//class PinModify{
//public:
//	BuffersCtrl::pins _pin;
//	PinModify(BuffersCtrl::pins pin);
//	void operator=(pin_state state){
//		if(state == pin_state::hi)
//			PORTB |= _BV(_pin);
//		else if(state == pin_state::toggle)
//			PORTB ^= _BV(_pin);
//		else{
//			PORTB &= ~_BV(_pin);
//		}
//	}
//};
//
//PinModify::PinModify(BuffersCtrl::pins  pin){
//	_pin = pin;
//}

#endif /* BUFFERS_CTRL_H_ */
