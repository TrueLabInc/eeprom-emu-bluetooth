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
#include "main.h"
#define EEPROM_IMAGE_SECTION __attribute__((section(".image_section")))
#define EXTSRAM_SIZ 0x8000L

const uint32_t eeprom_image1[EXTSRAM_SIZ/4/2] EEPROM_IMAGE_SECTION = {};
const uint32_t eeprom_image2[EXTSRAM_SIZ/4/2] EEPROM_IMAGE_SECTION = {};


class emulator{
private:
	char tmp_str[10];
	static uint8_t tmp_str_siz;
public:
	void write_page_to_flash_mem(uint32_t strona, uint8_t *buf) BOOTLOADER_SECTION;
	void write_data_to_flash_mem(bluetooth* bt);
	emulator(){};
};
#endif /* EMULATOR_H_ */
