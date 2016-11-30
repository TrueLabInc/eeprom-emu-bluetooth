################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../makefile.init

RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(CC_DEPS)),)
-include $(CC_DEPS)
endif
ifneq ($(strip $(C++_DEPS)),)
-include $(C++_DEPS)
endif
ifneq ($(strip $(C_UPPER_DEPS)),)
-include $(C_UPPER_DEPS)
endif
ifneq ($(strip $(CXX_DEPS)),)
-include $(CXX_DEPS)
endif
ifneq ($(strip $(ASM_DEPS)),)
-include $(ASM_DEPS)
endif
ifneq ($(strip $(S_DEPS)),)
-include $(S_DEPS)
endif
ifneq ($(strip $(S_UPPER_DEPS)),)
-include $(S_UPPER_DEPS)
endif
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
ifneq ($(strip $(CPP_DEPS)),)
-include $(CPP_DEPS)
endif
endif

-include ../makefile.defs

# Add inputs and outputs from these tool invocations to the build variables 
LSS += \
bt_eeprom_emulator.lss \

FLASH_IMAGE += \
bt_eeprom_emulator.hex \

EEPROM_IMAGE += \
bt_eeprom_emulator.eep \

SIZEDUMMY += \
sizedummy \


# All Target
all: bt_eeprom_emulator.elf secondary-outputs

# Tool invocations
bt_eeprom_emulator.elf: $(OBJS) $(USER_OBJS)
	@echo 'Building target: $@'
	@echo 'Invoking: AVR C++ Linker'
	avr-g++ -Wl,-Map,bt_eeprom_emulator.map,--cref -mrelax -Wl,--gc-sections -Wl,--section-start=.bootloader=0x1E000 -Wl,--section-start=.image_section=0x6000 -mmcu=atmega128 -o "bt_eeprom_emulator.elf" $(OBJS) $(USER_OBJS) $(LIBS)
	@echo 'Finished building target: $@'
	@echo ' '

bt_eeprom_emulator.lss: bt_eeprom_emulator.elf
	@echo 'Invoking: AVR Create Extended Listing'
	-avr-objdump -h -S bt_eeprom_emulator.elf  >"bt_eeprom_emulator.lss"
	@echo 'Finished building: $@'
	@echo ' '

bt_eeprom_emulator.hex: bt_eeprom_emulator.elf
	@echo 'Create Flash image (ihex format)'
	-avr-objcopy -R .eeprom -R .fuse -R .lock -R .signature -O ihex bt_eeprom_emulator.elf  "bt_eeprom_emulator.hex"
	@echo 'Finished building: $@'
	@echo ' '

bt_eeprom_emulator.eep: bt_eeprom_emulator.elf
	@echo 'Create eeprom image (ihex format)'
	-avr-objcopy -j .eeprom --no-change-warnings --change-section-lma .eeprom=0 -O ihex bt_eeprom_emulator.elf  "bt_eeprom_emulator.eep"
	@echo 'Finished building: $@'
	@echo ' '

sizedummy: bt_eeprom_emulator.elf
	@echo 'Invoking: Print Size'
	-avr-size --format=avr --mcu=atmega128 bt_eeprom_emulator.elf
	@echo 'Finished building: $@'
	@echo ' '

# Other Targets
clean:
	-$(RM) $(C_UPPER_DEPS)$(S_DEPS)$(LSS)$(C_DEPS)$(FLASH_IMAGE)$(CC_DEPS)$(ELFS)$(C++_DEPS)$(OBJS)$(CXX_DEPS)$(ASM_DEPS)$(EEPROM_IMAGE)$(SIZEDUMMY)$(S_UPPER_DEPS)$(CPP_DEPS) bt_eeprom_emulator.elf
	-@echo ' '

secondary-outputs: $(LSS) $(FLASH_IMAGE) $(EEPROM_IMAGE) $(SIZEDUMMY)

.PHONY: all clean dependents
.SECONDARY:

-include ../makefile.targets
