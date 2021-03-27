
# Set up vars
source "${ProjectDir}/synthesis/scripts/setup.tcl"
set AmountOfPEs $env(SynthAmountOfPEs)
set ClockPeriod $env(SynthClockPeriod)
set BridgeBufferSize $env(SynthBridgeBufferSize)

# Read MMMC info
read_mmmc "$ScriptDir/MMMC.tcl"

# Read physical info
read_physical -lefs "${CellLibDir}/lef/gsclib045_tech.lef ${CellLibDir}/lef/gsclib045_macro.lef ${CellLibDir}/lef/gsclib045_multibitsDFF.lef"

# Read HDL sources
#source "${ScriptDir}/sources.tcl"
read_hdl "${SourcesDir}/Top/JSON.vhd" -library JSON
read_hdl "${SourcesDir}/Hermes/HeMPS_defaults.vhd" -library Hermes
read_hdl "${SourcesDir}/Misc/BufferCircular.vhd"
read_hdl "${SourcesDir}/Top/HyHeMPS_PKG.vhd" -library HyHeMPS
read_hdl "${SourcesDir}/Bus/BusRRArbiter.vhd"
read_hdl "${SourcesDir}/Bus/BusControl.vhd"
read_hdl "${SourcesDir}/Bus/BusBridgev2.vhd"
read_hdl "${SourcesDir}/Bus/BusTop.vhd"
read_hdl "${SourcesDir}/Bus/BusStandaloneWrapper.vhd"

# Elaborates top level entity
elaborate
check_design -all

# Apply constraits to design
init_design

# Synthesize design
syn_generic
syn_map
syn_opt

# Generate reports
report_power -view VIEW_0V9 > "${ReportDir}/power_0V9.rpt"
report_power -view VIEW_1V08 > "${ReportDir}/power_1V08.rpt"
report_timing -view VIEW_0V9 > "${ReportDir}/timing_0V9.rpt"
report_timing -view VIEW_1V08 > "${ReportDir}/timing_1V08.rpt"
write_hdl > "${ReportDir}/HyHeMPS.v"
#report_summary
report_area -physical > "${ReportDir}/area.rpt"
report_design_rules > "${ReportDir}/design_rules.rpt"
report_messages -all
report_messages -all > "${ReportDir}/messages.rpt"

# TODO: Call NCSim.tcl to generate VCD file and re-evaluate power for post-synthesis simulation
quit
