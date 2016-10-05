/*
 * buffers_ctrl.cpp
 *
 *  Created on: Sep 25, 2016
 *      Author: rafal
 */

#include "buffers_ctrl.h"

buffers_ctrl::buffers_ctrl(){
	/*
	 * configures control pins for hex buffers
	 * inital state is high impedance
	 */
	DDRB |= _BV(addr_buff_oe_pin) | _BV(ce_conn_ctrl_pin);
	hex_buffer_impedance = hi;
}



