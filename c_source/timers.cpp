/*
 * timers.cpp
 *
 *  Created on: Oct 26, 2016
 *      Author: rafal
 */



#include "timers.h"

Timer16::Timer16(timer_no::v timer_num){
	if(timer_num==timer_no::timer1){
		tccra = &TCCR1A;
		tccrb = &TCCR1B;
		tccrc = &TCCR1C;
		ocra = &OCR1A;
		ocrb = &OCR1B;
		ocrc = &OCR1C;
		ocra_h = &OCR1AH;
		ocrb_h = &OCR1BH;
		ocrc_h = &OCR1CH;
		ocra_l = &OCR1AL;
		ocrb_l = &OCR1BL;
		ocrc_l = &OCR1CL;
		icr = &ICR1;
		icr_l = &ICR1L;
		icr_h = &ICR1H;
		tcnt = &TCNT1;
		tcnt_h = &TCNT1H;
		tcnt_l = &TCNT1L;
	}
}

volatile uint8_t* Timsk::register_ptr = &TIMSK;
Timsk::Timsk(){
	_register.register_val = *register_ptr;
}

void Timsk::bit_set(bits bit){
	*register_ptr |= _BV(bit);
}

void Timer16::init(timer_mode::v mode, prescaler::v pre){
	switch (pre) {
		case prescaler::_0:
			_prescaler = 0;
			break;
		case prescaler::_clk_div_1:
			_prescaler = 1;
			break;
		case prescaler::_clk_div_8:
			_prescaler = 8;
			break;
		case prescaler::_clk_div_64:
			_prescaler = 64;
			break;
		case prescaler::_clk_div_256:
			_prescaler = 256;
			break;
		case prescaler::_clk_div_1024:
			_prescaler = 1024;
			break;
		default:
			break;
	}
	tccrb_t tccrb_;
	tccra_t tccra_;
	union {
		uint8_t val;
		struct{
			bool _0 : 1;
			bool _1 : 1;
			bool _2 : 1;
			bool _3 : 1;
		}b;
	}wgm;
	wgm.val = mode;
	tccra_.bits.wgm0 = wgm.b._0;
	tccra_.bits.wgm1 = wgm.b._1;
	tccrb_.bits.wgm2 = wgm.b._2;
	tccrb_.bits.wgm3 = wgm.b._3;
	tccrb_.bits.cs0_cs1_cs2 = pre;
	*tccra = tccra_.val;
	*tccrb = tccrb_.val;
	*tcnt = 0;
}

void Timer16::tic(){
	_tic = *tcnt;
}
uint32_t Timer16::toc(){
	/*
	 * function returns time difference between tic - toc in microseconds
	 * tic();
	 * ...;
	 * time_diff = toc();
	 */
	float us = 1000000000/F_CPU;
	uint32_t tdif = *tcnt - _tic;
	float result = tdif*_prescaler*us/1000;
	return (uint32_t)result;
}

