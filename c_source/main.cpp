/*
 * main.cpp
 *
 *  Created on: Sep 21, 2016
 *      Author: rafal
 */

/*
 * random comment2
 */
#include "main.h"
#include <avr/boot.h>

//extern const uint32_t eeprom_image1[];

void check_sram(){
	leds_control led;
	extsram sram;
	led.L1 = led.off;
	bluetooth bt(9600);
	char sram_verification[50];
	sram.verify_sram_with_rand(&sram_verification[0], 2);
	bt.put_s(sram_verification);
	led.L1 = led.on;
}


uint8_t data_bytes[256];
uint32_t u = eeprom_image1[0];

int main(){
	for (int var = 0; var < 256; ++var) {
		data_bytes[var] = var;
	}

	leds_control led;
	bluetooth bt(57600);
	bluetooth xm(9600, bluetooth::usart0);
	bluetooth* bt_p;
	bt_p = &bt;
	extsram sram;
	buffers_ctrl hex_buffers;
	uint32_t loop_cnt = 0;
	emulator emu;
	Serial_handler serial(bt_p);
	Serial_handler xm_serial(&xm);
	char* xm_serial_buff = xm_serial.serial_buff;
	char* serial_buff = serial.serial_buff;
	uint8_t serial_buff_len = serial.buff_s;
	sei();
	led.L3 = led.sw;
	xm.put_s("I am bluetooth");
	while(1){
		_delay_ms(500);

		led.L1 = led.sw;
		//led.L2 = led.sw;
		loop_cnt++;
		if(bt.get_s(serial_buff, serial_buff_len)){
			led.L2 = led.sw;
			serial.handle();
			_delay_ms(10);
			bt.flush();
		}
		if(bt.get_s(xm_serial_buff, xm_serial.buff_s)){
			led.L3 = led.sw;
			_delay_ms(10);
			xm.put_s("I am bluetooth");
			xm.flush();
		}

	}
}

