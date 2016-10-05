/*
 * bluetooth.h
 *
 *  Created on: Sep 22, 2016
 *      Author: rafal
 */

#ifndef BLUETOOTH_H_
#define BLUETOOTH_H_

#include <stdlib.h>
#include <avr/io.h>

extern "C"
{
	#include "uart.h"
}


class bluetooth {
public:
	void at();
	enum usart{
		usart0,
		usart1,
	};
	void (*put_c)(uint8_t);
	void (*put_s)(const char *);
	void (*put_s_p)(const char *);
	uint16_t (*available)(void);
	uint16_t (*get_c)(void);
	void (*flush)(void);
	enum pins{
		bt_en = PF6,
	};
	enum en{
		on = true,
		off = false,
	};
	bluetooth(uint16_t, usart u=usart1);
	bool get_s(char *, uint8_t len=10);
	void put_raw_int(int);
	void put_raw_lint(uint32_t);
	void put_int_s(int, uint8_t radix=10);
	class _en {
	public:
		void operator=(en state){
			if(state){
				PORTF |= _BV(bt_en);
			}
			else{
				PORTF &= ~_BV(bt_en);
			}
		}
	};
	_en _en;
};


#endif /* BLUETOOTH_H_ */
