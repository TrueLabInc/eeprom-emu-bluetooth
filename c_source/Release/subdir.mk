################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../uart.c 

CPP_SRCS += \
../bluetooth.cpp \
../buffers_ctrl.cpp \
../emulator.cpp \
../extsram.cpp \
../leds.cpp \
../main.cpp \
../serial.cpp 

C_DEPS += \
./uart.d 

OBJS += \
./bluetooth.o \
./buffers_ctrl.o \
./emulator.o \
./extsram.o \
./leds.o \
./main.o \
./serial.o \
./uart.o 

CPP_DEPS += \
./bluetooth.d \
./buffers_ctrl.d \
./emulator.d \
./extsram.d \
./leds.d \
./main.d \
./serial.d 


# Each subdirectory must supply rules for building sources it contributes
%.o: ../%.cpp
	@echo 'Building file: $<'
	@echo 'Invoking: AVR C++ Compiler'
	avr-g++ -Wall -Os -fpack-struct -fshort-enums -ffunction-sections -fdata-sections -funsigned-char -funsigned-bitfields -fno-exceptions -std=c++11 -mmcu=atmega128 -DF_CPU=16000000UL -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -c -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '

%.o: ../%.c
	@echo 'Building file: $<'
	@echo 'Invoking: AVR Compiler'
	avr-gcc -Wall -Os -fpack-struct -fshort-enums -ffunction-sections -fdata-sections -std=gnu99 -funsigned-char -funsigned-bitfields -mmcu=atmega128 -DF_CPU=16000000UL -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -c -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


