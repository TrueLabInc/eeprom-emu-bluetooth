/*
 * serial.cpp
 *
 *  Created on: Sep 29, 2016
 *      Author: rafal
 */


#include "serial.h"

Serial_handler::Serial_handler(bluetooth* bt){
	bt_pt = bt;
}

char* Serial_handler::init(){
	return serial_buff;
}

bool Serial_handler::is_in_buffer(const char* string, uint8_t len, switches is_pgm){
	if(not is_pgm)
		return not strncmp(string, serial_buff,len);
	else{
		bt_pt->put_int_s(strcmp_P(string, serial_buff));
		return not strcmp_P(string, serial_buff);
	}
}

void Serial_handler::handle(){
	if (is_in_buffer("c\n"),2)
		handshake();
	if (is_in_buffer("a"))
		wait_for_ack();
	else
		bt_pt->put_s_p(msg::emulator);

}

void Serial_handler::handshake(){
	/*
	 * Initializes connection
	 * provides basic information:
	 * -SPM_PAGESIZE
	 */
	bt_pt->put_s_p(msg::handshake);
	bt_pt->put_s_p(msg::compilation_date);
	bt_pt->put_s("\n");
	bt_pt->put_s_p(msg::page_size);bt_pt->put_int_s(SPM_PAGESIZE);
}

bool Serial_handler::wait_for_ack(uint16_t timeout_ms){
	for(uint16_t i=0; i<=timeout_ms; i++){
		bt_pt->get_s(serial_buff, buff_s);
		if( is_in_buffer("ack",3) ){
			return true;
		}
		_delay_ms(1);
	}
	bt_pt->put_s_p(msg::timeout);
	return false;
}

const char Serial_handler::msg::wait_for_data_msg[] 	PROGMEM = "wait for data\n";
const char Serial_handler::msg::compilation_date[] 		PROGMEM = __DATE__;
const char Serial_handler::msg::handshake[] 			PROGMEM = "***EEPROM emulator***\ncompiled on: ";
const char Serial_handler::msg::page_size[] 			PROGMEM = "page_size:";
const char Serial_handler::msg::end[] 					PROGMEM = "end\n";
const char Serial_handler::msg::ack[] 					PROGMEM = "ack";
const char Serial_handler::msg::timeout[] 				PROGMEM = "timeout\n";
const char Serial_handler::msg::emulator[] 				PROGMEM = "emulator$>\n";
