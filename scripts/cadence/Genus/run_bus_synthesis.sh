#!/bin/bash

#  Required arguments are:
# PROJECT_DIR (Dir where project source files are stored),
# CLOCK_PERIOD (Clock period, in nanoseconds, for synthesis),
# PROCESS_CORNER (Synthesis supply voltage and temperature corner) ["Fast" or "f", for Fast, "Slow" or "s" for Slow] (Temperature corner is always @ 0C)
# SUPPLY_VOLTAGE (Supply voltage for standard cells) ["1.1" or "1.1V" for 1.1 Volts, "1.32" or "1.32V" for 1.32 Volts]
# TODO: VCD_SIM_FLAG (automatically simulate synthesized design, generate VCD and new power report, considering generated VCD) [1 for yes]

if [ ! $# -eq "4" ]; 
then 
	#echo "Usage: sh run_synthesis.sh <PROJECT_DIR> <CLOCK_PERIOD (in nanoseconds, number only)> <PROCESS_CORNER> <SUPPLY_VOLTAGE> <VCD_SIM_FLAG>"
    echo "Usage: sh run_synthesis.sh <PROJECT_DIR> <SUPPLY_VOLTAGE> <PROCESS_CORNER> <CLOCK_PERIOD (in nanoseconds, number only)> <AMOUNT_OF_PES>"
	exit 1
fi

# Export environment variables, to be read in Genus.tcl
export SynthProjectDir=$1
export SynthVoltageLevel=$2
export SynthProcessCorner=$3
export SynthClockPeriod=$4
export SynthAmountOfPEs=$5

# Prints out given arguments for debug
#echo "RUNNING GENUS WITH ARGS:"
#echo "PROJECT_DIR: ${SynthProjectDir}"
#echo "SUPPLY_VOLTAGE: ${SynthVoltageLevel}"
#echo "PROCESS_CORNER: ${SynthProcessCorner}"
#echo "CLOCK_PERIOD: ${SynthClockPeriod}"

module add cdn/genus/genus181
#module add cdn/incisiv/incisive152

cd ${SynthProjectDir}/synthesis/work
genus -log genus.log -f ${SynthProjectDir}/synthesis/scripts/GenusBusStandalone.tcl
