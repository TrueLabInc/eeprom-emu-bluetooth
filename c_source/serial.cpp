/*
 * serial.cpp
 *
 *  Created on: Sep 29, 2016
 *      Author: rafal
 */


#include "serial.h"
#include <avr/wdt.h>
#include <util/crc16.h>
#include "timers.h"

extern Bluetooth dbg;


//	typedef Timer16 T16;
//	T16 t1(T16::timer_no::timer1);
//	t1.init(T16::timer_mode::normal_0, T16::prescaler::_clk_div_64);
//t1.tic();
//dbg.put_lint_s(t1.toc());

#define _crc(crc, data) _crc_xmodem_update(crc, data)
#define CRC_LEN 2
#define	BUFF_SIZ_MULTIPLIER 4
#define RCV_BUFF_SIZ SPM_PAGESIZE*BUFF_SIZ_MULTIPLIER


void reset_avr(){
	//_delay_ms(1000);
	wdt_enable(WDTO_15MS);
}

void Serial_handler::reset_buff(){
	serial_buff[0] = NULL;
}

Serial_handler::Serial_handler(Bluetooth* bt, Leds* led){
	bluetooth = bt;
	_led = led;
}

char* Serial_handler::init(){
	return serial_buff;
}

//char* Serial_handler::is_in_buffer(const char* string, switches is_pgm){
bool Serial_handler::is_in_buffer(const char* string, switches is_pgm){
	//return strstr(serial_buff, string);
	//char* s = &serial_buff[0];
	char* endl = strstr(serial_buff, "\r");
	if (!endl)
		endl = strstr(serial_buff, "\n");
	//if(endl != s)
	*endl = '\0';
	return !strcmp(serial_buff, string);
}

void Serial_handler::emulate(){
	emulator_iface.address_port_conn = pin_state::hi;
	PORTB &= ~_BV(PB3);
	sram.high_impedance();
	bluetooth->put_s_n("emulating");
}

void Serial_handler::pinb_change(){
	PORTB ^= _BV(PB3);
}

void Serial_handler::handle(){
	//buffers_ctrl emulator_iface;
	if (is_in_buffer("c"))
		handshake();
	else if (is_in_buffer("write")){
		emulator_iface.address_port_conn = pin_state::hi;
		emulator_iface.ce_conn_ctrl = pin_state::hi;
		receive_data();
		sram.write_data(0, 0x8000, Emulator::eeprom1_image_address);
		emulator_iface.address_port_conn = pin_state::low;
		emulator_iface.ce_conn_ctrl = pin_state::low;
	}
	else if (is_in_buffer("flashRd")){
		bluetooth->put_s_p(msg::sending);
		_delay_ms(10);
		read_flash();
	}
	else if (is_in_buffer("CeOn")){
		emulator_iface.ce_conn_ctrl = pin_state::hi;
		bluetooth->put_s_n("CeOn");
	}
	else if (is_in_buffer("emulate")){
		emulate();
	}
	else if (is_in_buffer("reset"))
		reset_avr();
	else if (is_in_buffer("load_im1")){
		sram.write_data(0, 0x8000, Emulator::eeprom1_image_address);
		bluetooth->put_s_p_n(msg::image_loaded);
	}
	else if (is_in_buffer("load_im2")){
		sram.write_data(0, 0x8000, Emulator::eeprom2_image_address);
		bluetooth->put_s_p_n(msg::image_loaded);
	}
	else if (is_in_buffer("load_im3")){
		sram.write_data(0, 0x8000, Emulator::eeprom3_image_address);
		bluetooth->put_s_p_n(msg::image_loaded);
	}
	else if (is_in_buffer("sramRd")){
		bluetooth->put_s_p(msg::sending);
		_delay_ms(10);
		sram.read_data_and_transmit(0, 0x8000, bluetooth);
	}
	else if (is_in_buffer("pinb")){
		bluetooth->put_s_n("pin changing");
		pinb_change();
		bluetooth->put_s_n("pin changed");
		bluetooth->put_int_s(PINB, 2);
	}
	else{
		bluetooth->put_s_p_n(msg::emulator_s);
		return;
	}
	bluetooth->put_s_p_n(msg::end);
}

void Serial_handler::receive_data(){

	uint16_t num_of_bytes = 0x8000;
	uint8_t num_of_pages = num_of_bytes/(RCV_BUFF_SIZ);
	uint8_t single_crc_siz = sizeof(uint8_t)*8;
	uint8_t crc_summary_siz = num_of_pages/single_crc_siz;
	uint8_t crc_summary[crc_summary_siz] = {(uint8_t)0};
	bluetooth->put_s("test");
	bool crc_result;
	bool global_crc_flag = false;
	bluetooth->put_s("start");
	wdt_enable(WDTO_500MS);
	uint16_t i=0;
	for(i=0 ; i<num_of_pages; ++i){
		crc_result = receive_and_write_page_with_crc_check(emu.eeprom1_image_address + i*RCV_BUFF_SIZ);
		bluetooth->put_c('.');
		if(crc_result){
			global_crc_flag = true;
			//dbg.put_int_s(i);
		}
		crc_summary[i/single_crc_siz] |= (crc_result<<(i%single_crc_siz));
		wdt_reset();
	}
	if(global_crc_flag){
		bluetooth->put_s_p(msg::nok);
		retransmition_req(crc_summary, num_of_pages, single_crc_siz);
	}
	bluetooth->put_s_p(msg::ack);
	wdt_disable();
}

void Serial_handler::retransmition_req(uint8_t crc_summary[], uint8_t num_of_pages, uint8_t single_crc_siz){
	/*
	 * Function will send ids of failed pages and wait for retransmission
	 */

	bool crc_result = 1;
	char feedback_array[3] = {0,0,0};
	for(int page_num=0 ; page_num<num_of_pages; ++page_num){
		if(crc_summary[page_num/single_crc_siz]&(1<<page_num%single_crc_siz)){
			wdt_reset();
			while(crc_result){
				feedback_array[0]=page_num;
				bluetooth->put_c_array(feedback_array,3);	//send len3 frame
				crc_result = receive_and_write_page_with_crc_check(emu.eeprom1_image_address + page_num*RCV_BUFF_SIZ);
			}
			crc_result = 1;
		}
	}
}

bool Serial_handler::receive_and_write_page_with_crc_check(uint32_t page_addr){
	/*
	 * Function receives page of len of RCV_BUFF_SIZ and additional CRC_LEN bytes
	 * Last num bytes CRC_LEN is crc calculated by transmitter
	 * Function returns ack or nack according to crc result
	 */

	uint16_t rcv_crc;
	uint8_t buffer[RCV_BUFF_SIZ+CRC_LEN];
	//uint8_t *buffer_l = &buffer[0];
	//uint8_t *buffer_h = &buffer[RCV_BUFF_SIZ/2];
	receive_page(buffer, RCV_BUFF_SIZ+CRC_LEN);
	rcv_crc = buffer[RCV_BUFF_SIZ] + (buffer[RCV_BUFF_SIZ+1]<<8);
	if(rcv_crc == calc_crc(buffer, RCV_BUFF_SIZ)){
		//write_page_to_flash_mem(page_addr, buffer);
		//write_page_to_flash_mem(page_addr, buffer_l);
		for(uint8_t b=0; b<=BUFF_SIZ_MULTIPLIER; b++){
			_led->L3 = Leds::on;
			write_page_to_flash_mem(page_addr+b*SPM_PAGESIZE, &buffer[b*SPM_PAGESIZE]);
			_led->L3 = Leds::off;
			//dbg.put_lint_s(page_addr+(b-1)*SPM_PAGESIZE, 16);
		}
		return ack;
	}
	else{
		return nack;
	}
}

void Serial_handler::read_flash(){
	//bluetooth->put_s("reading flash\n");
	emu.read_eeprom_image(bluetooth);
}

void Serial_handler::handshake(){
	/*
	 * Initializes connection
	 * provides basic information:
	 * -SPM_PAGESIZE
	 */
	bluetooth->put_s_p(msg::handshake);
	bluetooth->put_s_p(msg::compilation_date);
	bluetooth->put_s("\n");
	bluetooth->put_s_p(msg::compilation_time);
	bluetooth->put_s("\n");
	bluetooth->put_s_p(msg::page_size);bluetooth->put_int_s(SPM_PAGESIZE);
}

void Serial_handler::strcpy_to_point(char* dst, char* src, char* p){
	/*
	 * Function will copy fist bytes of src array to dst until p pointer
	 * in terms of address value is reached
	 * String ending NULL will be added to the end
	 */
	int i=0;
	for (i = 0; i < (int)(p-serial_buff); ++i) {
		dst[i] = serial_buff[i];
	}
	dst[i] = NULL;
}

//void Serial_handler::wait_for_ack_and_put_data_to_buff(char* data){
//	strcpy_to_point(data, serial_buff, wait_for_ack());
//	reset_buff();
//}

//uint16_t Serial_handler::ask_for(const char* ask){
//	//bt_pt->put_s_p(msg::addr);
//	//bt_pt->put_s_p(ask);
//	char tmp[10];
//	wait_for_ack_and_put_data_to_buff(tmp);
//	uint16_t a = atol(tmp);
//	return a;
//}

void Serial_handler::receive_page(uint8_t *buffer, uint16_t buff_len){
	uint16_t cnt=0;
	while(cnt!=(buff_len)){
		while(bluetooth->available()){
			buffer[cnt] = bluetooth->get_c();
			cnt++;
		}
	}
}

uint16_t Serial_handler::calc_crc(uint8_t *buffer, uint16_t siz){
	/*
	 * Function calculates crc for provided array only for first "siz" bytes
	 */
	uint16_t crc = 0;
	for (uint16_t i = 0; i < siz; ++i) {
		crc = _crc(crc, buffer[i]);
	}
	return crc;
}

//char* Serial_handler::wait_for_ack(uint16_t timeout_ms){
//	char* pointer;
//	for(uint16_t i=0; i<=timeout_ms; i++){
//		bt_pt->get_s(serial_buff, buff_s);
//		if((pointer = is_in_buffer("."))){
//			return pointer;
//		}
//		_delay_ms(1);
//	}
//	bt_pt->put_s_p(msg::timeout);
//	reset_avr();
//	return pointer;
//}

const char Serial_handler::msg::wait_for_data_msg[] 	PROGMEM = "wait for data";
const char Serial_handler::msg::compilation_date[] 		PROGMEM = __DATE__;
const char Serial_handler::msg::compilation_time[] 		PROGMEM = __TIME__;
const char Serial_handler::msg::handshake[] 			PROGMEM = "***EEPROM emulator***\ncompiled on: ";
const char Serial_handler::msg::page_size[] 			PROGMEM = "page_size:";
const char Serial_handler::msg::end[] 					PROGMEM = "end";
const char Serial_handler::msg::ack[] 					PROGMEM = "ack";
const char Serial_handler::msg::nok[] 					PROGMEM = "nok";
const char Serial_handler::msg::timeout[] 				PROGMEM = "timeout";
const char Serial_handler::msg::emulator_s[] 				PROGMEM = "emulator$>";
const char Serial_handler::msg::addr[] 					PROGMEM = "addr";
const char Serial_handler::msg::amount[] 					PROGMEM = "amount";
const char Serial_handler::msg::image_loaded[] 					PROGMEM = "image loaded";
const char Serial_handler::msg::sending[] 					PROGMEM = "sending";
