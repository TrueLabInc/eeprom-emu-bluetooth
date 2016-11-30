/*
 * extsram.cpp
 *
 *  Created on: Sep 24, 2016
 *      Author: rafal
 */

#include "extsram.h"
#include "string.h"
#include <avr/pgmspace.h>
#include "leds.h"
//#include "bluetooth.h"
Extsram::Extsram(Bluetooth* b){
	DDRA = 0b11111111;
	DDRC |= 0b01111111;
	DDRB |= 0b11100000;
	DDRF = 0;
	PORTF = 0;
	default_mode();
	//bt = b;
}

void Extsram::high_impedance(){
	DDRA = 0b00000000;
	PORTA = 0;
	DDRC |= 0b00000000;
	PORTC |= 0b00000000;
	DDRF = 0;
	PORTF = 0;
	PORTB &= ~_BV(ce_pin) & ~_BV(oe_pin);
	PINB &= ~_BV(ce_pin) & ~_BV(oe_pin);
	DDRB &= ~_BV(ce_pin) & ~_BV(oe_pin);
}

Extsram::Extsram(){
	DDRA = 0b11111111;
	DDRC |= 0b01111111;
	DDRB |= 0b11101110;
	DDRF = 0;
	PORTF = 0;
	default_mode();
}

void Extsram::set_address(uint16_t addr){
	if(addr <= 0x7FFF){
		address_u a;
		a.addr = addr;
		*addr_l = a.lo;
		*addr_h = a.hi;
	}
}

void Extsram::default_mode(){
	ce = hi;
	oe = hi;
	we = hi;
	data_p_mode = in;
	addr_p_mode = in;
	set_address(0);
	//PORTF = 0;
}

void Extsram::read_sram_mode(){
	ce = hi;
	oe = hi;
	we = hi;
	data_p_mode = in;
	addr_p_mode = out;
	set_address(0);
	//PORTF = 0;
}

void Extsram::set_data(uint8_t data){
	data_p_mode = out;
	*data_p = data;
}


void Extsram::delay_cycles(uint8_t cycles){
	for(uint8_t i=0; i<=cycles; i++){
		asm volatile ("nop"::);
	}
}

void Extsram::read_mode(){
	addr_p_mode = out;
	data_p_mode = in;
	we = hi;
	ce = hi;
	oe = hi;

}

uint8_t Extsram::read_single_byte(uint16_t addr){
	uint8_t data;
	read_mode();

	set_address(addr);
	ce = low;
	oe = low;
	data = *data_v;

	default_mode();
	return data;
}

void Extsram::write_mode(){
	data_p_mode = out;
	addr_p_mode = out;
	ce = low;
	we = low;
}

void Extsram::write_single_byte(uint16_t addr, uint8_t data){
	write_mode();

	set_address(addr);
	*data_p = data;

	default_mode();
}

 char* Extsram::verify_sram_with_rand(char* str, uint8_t num_of_runs){
	//leds_control l;
	char status_ok[] PROGMEM = "sram verification succesfull";
	char status_nok[] PROGMEM = "rand sram verification failed at address:";
	char tmp_string[6];
	address_result result;
	uint16_t a;
	result.result = ok;
	result.addr = 0;
	uint8_t rand_d;
	for(uint16_t r=0; r <= num_of_runs; r++){
		//l.L1 = l.sw;
		for(a=0; a<EXTSRAM_SIZ; a++){
			rand_d = rand();
			write_single_byte(a, rand_d);
			if(read_single_byte(a) != rand_d){
				result.addr = a;
				result.result = nok;
				break;
			}
		}
	}
	if(not result.result){
		strcpy(str, status_nok);
		utoa(result.addr, tmp_string, 10);
		strcat(str, tmp_string);
	}
	else{
		strcpy(str, status_ok);
	}
	return str;
}

void Extsram::write_data(uint16_t start_address, uint16_t amount_of_bytes, uint32_t flash_address){
	uint16_t a;
	uint8_t byte;
	data_p_mode = out;
	addr_p_mode = out;
	for(a=0; a<amount_of_bytes; a++){
		set_address(start_address+a);
		byte = pgm_read_byte(Emulator::eeprom1_image_address+a);
		*data_p = byte;
		//_delay_us(20);
		ce = low;
		we = low;
		//_delay_us(20);
		ce = hi;
		we = hi;
		//_delay_us(20);
	}
	default_mode();
	//l.L2 = Leds::off;
}

void Extsram::read_data_and_transmit(uint16_t start_address, uint16_t amount_of_bytes, Bluetooth* bt){
/*
 * reads provided amount of bytes to bt
 */
	uint16_t a;
	uint8_t byte;
	read_sram_mode();
	oe = low;
	for(a=0; a<amount_of_bytes; a++){
		set_address(start_address+a);
		//_delay_us(20);
		ce = low;
		//_delay_us(20);
		byte = *data_v;
		//byte = 'u';
		bt->put_c(byte);
		ce = hi;
	}
	default_mode();
}








