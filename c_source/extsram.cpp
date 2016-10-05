/*
 * extsram.cpp
 *
 *  Created on: Sep 24, 2016
 *      Author: rafal
 */

#include "extsram.h"
#include "string.h"
#include <avr/pgmspace.h>
//#include "leds.h"
//#include "bluetooth.h"
extsram::extsram(){
	DDRA = 0b11111111;
	DDRC |= 0b01111111;
	DDRB |= 0b11100000;
	DDRF = 0;
	PORTF = 0;
	default_mode();
}

void extsram::set_address(uint16_t addr){
	if(addr <= 0x7FFF){
		address_u a;
		a.addr = addr;
		*addr_l = a.lo;
		*addr_h = a.hi;
	}
}

void extsram::default_mode(){
	ce = hi;
	oe = hi;
	we = hi;
	data_p_mode = in;
	//PORTF = 0;

}

void extsram::set_data(uint8_t data){
	data_p_mode = out;
	*data_p = data;
}


void extsram::delay_cycles(uint8_t cycles){
	for(uint8_t i=0; i<=cycles; i++){
		asm volatile ("nop"::);
	}
}

void extsram::read_mode(uint16_t addr){
	we = hi;
	ce = hi;
	oe = hi;
	set_address(addr);
	ce = low;
	oe = low;
}

uint8_t extsram::read_single_byte(uint16_t addr){
	uint8_t data;
	read_mode(addr);
	//_delay_us(100);
	data = *data_v;
	default_mode();
	return data;
}

void extsram::write_mode(uint16_t addr){
	data_p_mode = out;
	set_address(addr);
	ce = low;
	we = low;
}

void extsram::write_single_byte(uint16_t addr, uint8_t data){
	write_mode(addr);
	//oe = low;
	//_delay_us(100);
	*data_p = data;
	default_mode();
}

 char* extsram::verify_sram_with_rand(char* str, uint8_t num_of_runs){
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
		for(a=0; a<=EXTSRAM_SIZ; a++){
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

void extsram::write_data(uint16_t start_address, uint16_t amount_of_bytes, uint8_t bytes[]){
	uint16_t a;
	uint8_t byte;
	data_p_mode = out;
	for(a=0; a<=amount_of_bytes; a++){
		set_address(start_address+a);
		byte = *(bytes+a);
		*data_p = byte;
		ce = low;
		we = low;
		ce = hi;
		we = hi;
	}
	default_mode();
}

void extsram::read_data(uint16_t start_address, uint16_t amount_of_bytes, uint8_t bytes_array[]){
/*
 * reads provided amount of bytes to bytes_arra
 */
	uint16_t a;
	uint8_t byte;
	default_mode();
	//bluetooth bt(9600);
	oe = low;
	for(a=0; a<=amount_of_bytes; a++){
		set_address(start_address+a);
		ce = low;
		byte = *data_v;
		bytes_array[a] = byte;
		ce = hi;
	}
	default_mode();
}








