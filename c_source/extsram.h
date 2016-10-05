/*
 * extsram.h
 *
 *  Created on: Sep 24, 2016
 *      Author: rafal
 */

#ifndef EXTSRAM_H_
#define EXTSRAM_H_

#include <avr/io.h>
#include <avr/delay.h>
#include <stdlib.h>
#include "pins.h"

#define EXTSRAM_SIZ 0x8000L

static volatile uint8_t* data_dir_p = &DDRF;
static volatile uint8_t* ctrl_port = &PORTB;

class extsram{
private:
	void delay_cycles(uint8_t);
public:
	enum result_status{
		ok = true,
		nok = false,
	};
	typedef union{
		uint16_t addr;
		struct{
			uint8_t lo;
			uint8_t hi;
		};
	}address_u;
	typedef struct {
		bool result;
		uint16_t addr;
	}address_result;
	volatile uint8_t* addr_l = &PORTA;
	volatile uint8_t* addr_h = &PORTC;
	volatile uint8_t* data_p = &PORTF;
	volatile uint8_t* data_v = &PINF;
	enum ctrl_pins{
		ce_pin = PB7,
		oe_pin = PB6,
		we_pin = PB5,
	};
	void set_address(uint16_t);
	void set_data(uint8_t);
	uint8_t read_single_byte(uint16_t);
	void write_single_byte(uint16_t addr, uint8_t data);
	void write_data(uint16_t start_address, uint16_t amount_of_bytes, uint8_t bytes[]);
	void read_data(uint16_t start_address, uint16_t amount_of_bytes, uint8_t bytes_array[]);
	void default_mode();
	void read_mode(uint16_t);
	void write_mode(uint16_t);
	char*  verify_sram_with_rand(char*, uint8_t);
	extsram();

	class ce_ {
	public:
		void operator=(pin_state st){
			if(st){
				*ctrl_port |= _BV(ce_pin);
			}
			else{
				*ctrl_port &= ~_BV(ce_pin);
			}
		}
	};
	class oe_ {
	public:
		void operator=(pin_state st){
			if(st){
				*ctrl_port |= _BV(oe_pin);
			}
			else{
				*ctrl_port &= ~_BV(oe_pin);
			}
		}
	};
	class we_ {
	public:
		void operator=(pin_state st){
			if(st){
				*ctrl_port |= _BV(we_pin);
			}
			else{
				*ctrl_port &= ~_BV(we_pin);
			}
		}
	};
	class data_p_mode {
	public:
		void operator=(port_state mode){
			if(mode == in){
				*data_dir_p = 0;
			}
			else{
				*data_dir_p = 0xff;
			}
		}
	};
	ce_ ce;
	oe_ oe;
	we_ we;
	data_p_mode data_p_mode;
};



#endif /* EXTSRAM_H_ */
