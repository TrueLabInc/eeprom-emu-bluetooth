/*
 * serial.h
 *
 *  Created on: Sep 29, 2016
 *      Author: rafal
 */

#ifndef SERIAL_H_
#define SERIAL_H_
#include <stdint.h>
#include "emulator.h"
#include "extsram.h"
#include "bluetooth.h"
#include "string.h"
#include <avr/delay.h>
#include <avr/pgmspace.h>
#include "leds.h"
#include "buffers_ctrl.h"

void reset_avr();

class Serial_handler{
private:
	BuffersCtrl emulator_iface;
	Bluetooth *bluetooth;
	Extsram sram;
	Leds* _led;
	Emulator emu;
	typedef enum{
		pgm = true,
		not_pgm = false,
	}switches;
	enum{
		ack = 0,
		nack = 1,
	};
	struct msg{
		static const char wait_for_data_msg[];
		static const char compilation_date[];
		static const char handshake[];
		static const char page_size[];
		static const char end[];
		static const char ack[];
		static const char nok[];
		static const char timeout[];
		static const char emulator_s[];
		static const char compilation_time[];
		static const char addr[];
		static const char amount[];
		static const char image_loaded[];
		static const char sending[];
	};
	struct command{
		char handshake = 'c';
	};
	//char* is_in_buffer(const char*, switches pgm_space=not_pgm);
	bool is_in_buffer(const char*, switches pgm_space=not_pgm);
	void reset_buff();
public:
	Serial_handler(Bluetooth*, Leds*);
	char serial_buff[10];
	char* init();
	void handle();
	uint16_t buff_s = sizeof(serial_buff)/sizeof(*serial_buff);
	void handshake();
	void receive_data();
	void strcpy_to_point(char* dst, char* src, char* p);
	//void wait_for_ack_and_put_data_to_buff(char* data);
	void read_flash();
	void receive_page(uint8_t *buffer, uint16_t buff_len);
	void retransmition_req(uint8_t crc_summary[], uint8_t num_of_pages, uint8_t single_crc_siz);
	bool receive_and_write_page_with_crc_check(uint32_t page_addr);
	void emulate();
	void pinb_change();
	//uint16_t ask_for(const char* ask);
	//char*  wait_for_ack(uint16_t timeout_ms=5000);
	uint16_t calc_crc(uint8_t [], uint16_t);
};

#endif /* SERIAL_H_ */
