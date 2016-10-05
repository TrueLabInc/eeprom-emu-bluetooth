/*
 * bluetooth.cpp
 *
 *  Created on: Sep 24, 2016
 *      Author: rafal
 */

#include "bluetooth.h"
#include <util/delay.h>
#include <avr/interrupt.h>


bluetooth::bluetooth(uint16_t baud, usart u){
	//DDRF &= ~_BV(bt_state);
	//DDRF |= _BV(bt_en);
	//DDRE |= _BV(rx);
	//DDRE &= ~_BV(tx);
	if(u==usart0){
		uart0_init(baud);
		put_c = uart0_putc;
		put_s = uart0_puts;
		put_s_p = uart0_puts_p;
		get_c = uart0_getc;
		available = uart0_available;
		flush = uart0_flush;
		flush();
	}else if(u==usart1){
		uart1_init(baud);
		put_c = uart1_putc;
		put_s = uart1_puts;
		put_s_p = uart1_puts_p;
		get_c = uart1_getc;
		available = uart1_available;
		flush = uart1_flush;
		flush();
	}
	PORTF &= ~_BV(bt_en);
	sei();
}

void bluetooth::at(){
	_en = on;
	_delay_ms(1500);
	_en = off;
}

bool bluetooth::get_s(char *str_val, uint8_t len){
	char c = '0';
	uint8_t index=0;
	if(available()==0){
		return false;
	}
	else{
		while(c != '\n' and c != '\r' and index <= (len-1)){
			if(available()){
				c= get_c();
				str_val[index] = c;
				index++;
		}
		}
	}
	str_val[index] = NULL;
	flush();
	return true;
}

void bluetooth::put_raw_int(int val){
	/*
	 * puts integer to serial in hex format
	 */
	put_c(val>>8);
	put_c(val&0xff);
}

void bluetooth::put_raw_lint(uint32_t val){
	/*
	 * puts long integer to serial in hex format
	 */
	put_c(val>>24);
	put_c(val>>16);
	put_c(val>>8);
	put_c(val&0xff);
}

void bluetooth::put_int_s(int val, uint8_t radix){
	/*
	 * puts integer to serial in string format
	 * max string length: 10
	 */
	char tmp[10];
	itoa(val, tmp, radix);
	put_s(tmp);
}



