/*
 * emulator.cpp
 *
 *  Created on: Sep 28, 2016
 *      Author: rafal
 */

#include "emulator.h"

void write_page_to_flash_mem(uint32_t strona, uint8_t *buf){
	uint16_t i;
	uint8_t sreg;

	sreg = SREG;	//Zapisz stan globalnej flagi zezwolenia na przerwania
	cli();

	boot_page_erase_safe(strona);
	//boot_page_erase (strona);

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


void Emulator::write_data_to_flash_mem(Bluetooth* bt){
	uint8_t page_buffer[SPM_PAGESIZE];
}

void Emulator::read_eeprom_image(Bluetooth* bt){
	uint16_t siz = EXTSRAM_SIZ;
	uint8_t byte;
	for(uint16_t i=0; i<siz; i++){
		byte = pgm_read_byte(eeprom1_image_address+i);
		bt->put_c(byte);
	}
}



uint8_t Emulator::tmp_str_siz = sizeof(tmp_str)/sizeof(*tmp_str);
uint32_t Emulator::eeprom1_image_address = 0x6000;
uint32_t Emulator::eeprom2_image_address = eeprom1_image_address + EXTSRAM_SIZ;
uint32_t Emulator::eeprom3_image_address = eeprom2_image_address + EXTSRAM_SIZ;



