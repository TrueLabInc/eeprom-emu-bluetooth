/*
 * emulator.h
 *
 *  Created on: Sep 28, 2016
 *      Author: rafal
 */

#ifndef EMULATOR_H_
#define EMULATOR_H_

#include <avr/pgmspace.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include <avr/boot.h>
#include "bluetooth.h"

#define EEPROM_IMAGE_SECTION __attribute__((section(".image_section")))
#define EXTSRAM_SIZ 0x8000L

//const uint8_t eeprom_image1[EXTSRAM_SIZ/2] EEPROM_IMAGE_SECTION = {1};
//const uint8_t eeprom_image2[EXTSRAM_SIZ/2] EEPROM_IMAGE_SECTION = {2};
//const uint8_t eeprom_image3[EXTSRAM_SIZ/2] EEPROM_IMAGE_SECTION = {3};
//const uint8_t eeprom_image4[EXTSRAM_SIZ/2] EEPROM_IMAGE_SECTION = {4};

class Emulator{
private:
	char tmp_str[10];
	static uint8_t tmp_str_siz;
public:
	static uint32_t eeprom1_image_address;
	static uint32_t eeprom2_image_address;
	static uint32_t eeprom3_image_address;
	//below section is just for memory reservation
//	uint32_t image_p1addr = (uint32_t)&eeprom_image1;
//	uint32_t image_p2addr = (uint32_t)&eeprom_image2;
//	uint32_t image_p3addr = (uint32_t)&eeprom_image3;
//	uint32_t image_p4addr = (uint32_t)&eeprom_image4;

	void write_page_to_flash_mem(uint32_t strona, uint8_t *buf) BOOTLOADER_SECTION;
	//void write_page_to_flash_mem(uint32_t strona, uint8_t *buf);
	void write_data_to_flash_mem(Bluetooth* bt);
	void read_eeprom_image(Bluetooth* bt);
	Emulator(){};
};


void write_page_to_flash_mem(uint32_t strona, uint8_t *buf) BOOTLOADER_SECTION;
//void write_page_to_flash_mem(uint32_t strona, uint8_t *buf);
#endif /* EMULATOR_H_ */
