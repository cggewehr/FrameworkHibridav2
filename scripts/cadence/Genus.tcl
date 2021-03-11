
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
check_timing_intent -verbose

# Synthesize design
set_db "syn_generic_effort" "high"
syn_generic

set_db "syn_map_effort" "high"
syn_map

set_db "syn_opt_effort" "high"
syn_opt

# Generate reports
#write_snapshot -outdir "." -tag "after_opt"
set ReportDir "${ProjectDir}/synthesis/deliverables"
report_area > "${ReportDir}/area.rpt"
report_design_rules > "${ReportDir}/design_rules.rpt"
report_power > "${ReportDir}/power_beforeVCD.rpt"
report_timing > "${ReportDir}/timing.rpt"
write_hdl > "${ReportDir}/HyHeMPS.v"
report_summary
report_messages

# TODO: Call NCSim.tcl to generate VCD file and re-evaluate power

