/*
 * timers.h
 *
 *  Created on: Oct 26, 2016
 *      Author: rafal
 */

#ifndef TIMERS_H_
#define TIMERS_H_
#include <avr/io.h>
#include <stdlib.h>


class Timsk{
public:
	typedef enum{
		toieo  = 0,
		ocieo  = 1,
		toie1  = 2,
		ocie1b = 3,
		oci1a  = 4,
		ticie1 = 5,
		toie2  = 6,
		ocie2  = 7,
	}bits ;
	static volatile uint8_t *register_ptr;

	typedef union{
		uint8_t register_val;
		struct {
			bool toieo  : 1;
			bool ocieo  : 1;
			bool toie1  : 1;
			bool ocie1b : 1;
			bool oci1a  : 1;
			bool ticie1 : 1;
			bool toie2  : 1;
			bool ocie2  : 1;
		}bit;
	}timsk_register;
	timsk_register _register;
	Timsk();
	void bit_set(bits);
};

class Timer16{
private:
	uint16_t _prescaler = 0;
	//timer specific registers
	volatile uint8_t* tccra;
	volatile uint8_t* tccrb;
	volatile uint8_t* tccrc;
	volatile uint16_t* ocra;
	volatile uint16_t* ocrb;
	volatile uint16_t* ocrc;
	volatile uint8_t* ocra_h;
	volatile uint8_t* ocrb_h;
	volatile uint8_t* ocrc_h;
	volatile uint8_t* ocra_l;
	volatile uint8_t* ocrb_l;
	volatile uint8_t* ocrc_l;
	volatile uint16_t* icr;
	volatile uint8_t* icr_l;
	volatile uint8_t* icr_h;
	volatile uint16_t* tcnt;
	volatile uint8_t* tcnt_h;
	volatile uint8_t* tcnt_l;

	//common registers

	volatile uint8_t* etimsk = &ETIMSK;
	volatile uint8_t* tifr = &TIFR;
	volatile uint8_t* etifr = &ETIFR;

public:
	typedef struct{
		typedef enum {timer1,
			timer3,}v;
	}timer_no;

	typedef union {
		uint8_t val;
		struct {
			uint8_t cs0_cs1_cs2 : 3;
			bool wgm2 : 1;
			bool wgm3 : 1;
			bool reserved: 1;
			bool ices : 1;
			bool icn  : 1;
		}bits;
	}tccrb_t;

	typedef union {
		uint8_t val;
		struct {
			bool wgm0 : 1;
			bool wgm1 : 1;
			bool comc0 : 1;
			bool comc1: 1;
			bool comb1 : 1;
			bool coma0  : 1;
			bool coma1  : 1;
		}bits;
	}tccra_t;

	struct tccrb_bits{
		enum{cs0  = 0,
			cs1  = 1,
			cs2  = 2,
			wgm2 = 3,
			wgm3 = 4,
			//
			ices = 6,
			icn  = 7,};
	};

	struct compare_out_mode_non_pwm{
		enum{normal_mode_OvCnt_disconnected,
			toggle_OvCnt_on_compare_match,
			clear_OvCnt_on_compare_match,
			set_OvCnt_on_compare_match,};
	};

	struct timer_mode{
		typedef enum{normal_0 = 0,
			ctc_4 = 4,
			ctc_12 = 12,}v;
	};

	struct prescaler{
		typedef enum{_0 = 0,
			_clk_div_1 = 1,
			_clk_div_8 = 2,
			_clk_div_64 = 3,
			_clk_div_256 = 4,
			_clk_div_1024 = 5,
			_external_rising = 6,
			_external_falling = 7,}v;
	};

	uint16_t _tic;
	//timer timer_typ;

	Timer16(timer_no::v timer_num=timer_no::timer1);
	void init(timer_mode::v, prescaler::v);
	void tic();
	uint32_t toc();
};

#endif /* TIMERS_H_ */
