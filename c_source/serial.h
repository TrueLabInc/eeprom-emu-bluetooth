/*
 * serial.h
 *
 *  Created on: Sep 29, 2016
 *      Author: rafal
 */

#ifndef SERIAL_H_
#define SERIAL_H_
#include <stdint.h>
#include "bluetooth.h"
#include "string.h"
#include <avr/delay.h>
#include <avr/pgmspace.h>

class Serial_handler{
	bluetooth *bt_pt;
	typedef enum{
		pgm = true,
		not_pgm = false,
	}switches;
	struct msg{
		static const char wait_for_data_msg[];
		static const char compilation_date[];
		static const char handshake[];
		static const char page_size[];
		static const char end[];
		static const char ack[];
		static const char timeout[];
		static const char emulator[];
	};
	struct command{
		char handshake = 'c';
	};
	bool is_in_buffer(const char*, uint8_t len=1, switches pgm_space=not_pgm);
public:
	Serial_handler(bluetooth*);
	char serial_buff[10];
	char* init();
	void handle();
	uint16_t buff_s = sizeof(serial_buff)/sizeof(*serial_buff);
	void handshake();
	bool wait_for_ack(uint16_t timeout_ms=5000);
};

#endif /* SERIAL_H_ */
