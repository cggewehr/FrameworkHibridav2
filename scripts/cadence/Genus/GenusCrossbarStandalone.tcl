
# Define auxiliary vars defined by shell script
#set HDLSourcesFile env(SynthHDLSourcesFile)
#set SDCFile $env(SynthSDCFile)
set ProjectDir $env(SynthProjectDir)
set VoltageLevel $env(SynthVoltageLevel)
set ProcessCorner $env(SynthProcessCorner)
set AmountOfPEs $env(SynthAmountOfPEs)
set ClockPeriod $env(SynthClockPeriod)
set BridgeBufferSize $env(SynthBridgeBufferSize)

# Read cell lib info
source "${ProjectDir}/synthesis/scripts/tech.tcl"

# Read HDL sources
#source "${ProjectDir}/synthesis/scripts/sources.tcl"
set_db hdl_language vhdl
set_db hdl_vhdl_read_version 1993
set HibridaDir $env(HIBRIDA_PATH)
set SourcesDir "${HibridaDir}/src/hardware"
read_hdl "${SourcesDir}/Top/JSON.vhd" -library JSON
read_hdl "${SourcesDir}/Hermes/HeMPS_defaults.vhd" -library Hermes
read_hdl "${SourcesDir}/Misc/BufferCircular.vhd"
read_hdl "${SourcesDir}/Top/HyHeMPS_PKG.vhd" -library HyHeMPS
read_hdl "${SourcesDir}/Crossbar/CrossbarControl.vhd"
read_hdl "${SourcesDir}/Crossbar/CrossbarRRArbiter.vhd"
read_hdl "${SourcesDir}/Crossbar/CrossbarBridgev2.vhd"
read_hdl "${SourcesDir}/Crossbar/CrossbarTop.vhd"
read_hdl "${SourcesDir}/Crossbar/CrossbarStandaloneWrapper.vhd"

# Elaborates top level entity
elaborate CrossbarStandaloneWrapper -parameters "{AmountOfPEs $AmountOfPEs} {BridgeBufferSize $BridgeBufferSize}"
check_design -all

# Read constraints
read_sdc "${ProjectDir}/synthesis/scripts/standalone.sdc"
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
report_area > "${ReportDir}/area_${VoltageLevel}V.rpt"
report_design_rules > "${ReportDir}/design_rules_${VoltageLevel}V.rpt"
report_power > "${ReportDir}/power_${VoltageLevel}V.rpt"
report_timing > "${ReportDir}/timing_${VoltageLevel}V.rpt"
write_hdl > "${ReportDir}/Crossbar_${VoltageLevel}V.v"
#report_summary
report_messages

# TODO: Call NCSim.tcl to generate VCD file and re-evaluate power
quit

