/*
 * emulator.cpp
 *
 *  Created on: Sep 28, 2016
 *      Author: rafal
 */

#include "emulator.h"

void emulator::write_page_to_flash_mem(uint32_t strona, uint8_t *buf){
	uint16_t i;
	uint8_t sreg;

	sreg = SREG;	//Zapisz stan globalnej flagi zezwolenia na przerwania
	cli();

	boot_page_erase_safe(strona);

	for (i=0; i<SPM_PAGESIZE; i+=2)
	{
		uint16_t slowo=*buf++;
		slowo+=(*buf++)<<8;
		boot_page_fill_safe(strona+i, slowo);	//Zapisz dane do bufora
	}

	boot_page_write_safe(strona);     //Zapisz bufor do pamiêci FLASH
	boot_rww_enable_safe();			  //Odblokuj dostêp do pamiêci RWW
	SREG = sreg;					  //Odtwórz stan przerwañ
}

void emulator::write_data_to_flash_mem(bluetooth* bt){
	uint8_t page_buffer[SPM_PAGESIZE];
}



uint8_t emulator::tmp_str_siz = sizeof(tmp_str)/sizeof(*tmp_str);




