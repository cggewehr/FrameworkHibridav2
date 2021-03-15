
# Define auxiliary vars defined by shell script
#set HDLSourcesFile env(SynthHDLSourcesFile)
#set SDCFile $env(SynthSDCFile)
set ProjectDir $env(SynthProjectDir)
set VoltageLevel $env(SynthVoltageLevel)
set ProcessCorner $env(SynthProcessCorner)
#set ClockPeriod $env(SynthClockPeriod)

# Read cell lib info
source "${ProjectDir}/synthesis/scripts/tech.tcl"
# Read HDL sources
source "${ProjectDir}/synthesis/scripts/sources.tcl"

# Elaborates top level entity
elaborate
check_design -all

# Read constraints
read_sdc "${ProjectDir}/synthesis/scripts/constraints.sdc"
report timing -lint
#check_timing_intent -verbose

# Synthesize design
synthesize -to_gen -effort "high"
synthesize -to_map -effort "high"

# Generate reports
set ReportDir "${ProjectDir}/synthesis/deliverables"
report design_rules > ${ReportDir}/drc.rpt
report area  > ${ReportDir}/area.rpt
report timing > ${ReportDir}/timing.rpt
report gates  > ${ReportDir}/gates.rpt
set_attribute lp_power_analysis_effort high
report power > ${ReportDir}/power_BEFORE_VCD.rpt
write_sdf -edge check_edge -nonegchecks -setuphold split -version 2.1 -design "HyHeMPS" > ${ReportDir}/SDF_FILE.sdf
write_hdl > ${ReportDir}/HyHeMPS.v

# TODO: Call NCSim.tcl to generate VCD file and re-evaluate power
quit

