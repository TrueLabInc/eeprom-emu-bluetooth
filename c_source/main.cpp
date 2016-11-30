/*
 * main.cpp
 *
 *  Created on: Sep 21, 2016
 *      Author: rafal
 */


#include "main.h"
#include <avr/boot.h>
#include <avr/io.h>
#include <stdlib.h>
#include <util/delay.h>
#include <util/atomic.h>
#include <string.h>
#include <stdio.h>
#include "extsram.h"

//extern const uint32_t eeprom_image1[];

Bluetooth dbg(115200, Bluetooth::usart0);
//Timsk timsk;

void check_sram(){
	Leds led;
	Extsram sram;
	led.L1 = led.off;
	Bluetooth bt(9600);
	char sram_verification[50];
	sram.verify_sram_with_rand(&sram_verification[0], 2);
	bt.put_s(sram_verification);
	led.L1 = led.on;
}


int main(){
	Bluetooth bt(115200);
	Extsram sram(&bt);
	sram.write_data(0, 0x8000, Emulator::eeprom1_image_address);
	BuffersCtrl hex_buffers;
	uint32_t loop_cnt = 0;
	Leds led;
	Serial_handler serial(&bt, &led);
	serial.handshake();
	char* serial_buff = serial.serial_buff;
	uint8_t serial_buff_len = serial.buff_s;
	led.L2 = led.on;
	dbg.put_s("reset");
	//serial.emulate();
	sei();
	while(1){
		loop_cnt++;
		if(not (loop_cnt%10000)){
			led.L1 = led.sw;
			led.L2 = led.sw;
		}
		if(bt.get_s(serial_buff, serial_buff_len)){
			dbg.put_s(serial_buff);
			serial.handle();
			bt.flush();
		}
		_delay_us(5);
	}
}

