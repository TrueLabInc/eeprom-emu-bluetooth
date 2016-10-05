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

class buffers_ctrl{
public:
	enum pins{
		addr_buff_oe_pin = PB3,
		ce_conn_ctrl_pin = PB2,
	};
	buffers_ctrl();
	class addr_buff_oe_ {
	public:
		void operator=(pin_state state){
			if(state){
				PORTB |= _BV(addr_buff_oe_pin);
			}
			else{
				PORTB &= ~_BV(addr_buff_oe_pin);
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
	addr_buff_oe_ hex_buffer_impedance; ce_conn_ctrl_ ce_conn_ctrl;

};




#endif /* BUFFERS_CTRL_H_ */
