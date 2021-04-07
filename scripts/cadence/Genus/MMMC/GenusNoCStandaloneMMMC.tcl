
# Set up vars
set ProjectDir $env(SynthProjectDir)
set XSize $env(SynthXSize)
set YSize $env(SynthYSize)
set ClockPeriod $env(SynthClockPeriod)
set ClockPeriodMult2 [expr $ClockPeriod * 2]
source "${ProjectDir}/synthesis/scripts/setup.tcl"

# Read MMMC info
read_mmmc "$ScriptDir/MMMC.tcl"

# Read physical info
read_physical -lefs "${CellLibDir}/lef/gsclib045_tech.lef ${CellLibDir}/lef/gsclib045_macro.lef ${CellLibDir}/lef/gsclib045_multibitsDFF.lef"

# Read HDL sources
#source "${ScriptDir}/sources.tcl"
read_hdl "${SourcesDir}/Top/JSON.vhd" -library JSON
read_hdl "${SourcesDir}/Hermes/HeMPS_defaults.vhd" -library Hermes
read_hdl "${SourcesDir}/Top/HyHeMPS_PKG.vhd" -library HyHeMPS
read_hdl "${SourcesDir}/Hermes/Hermes_buffer.vhd"
read_hdl "${SourcesDir}/Hermes/Hermes_crossbar.vhd"
read_hdl "${SourcesDir}/Hermes/Hermes_switchcontrol.vhd"
read_hdl "${SourcesDir}/Hermes/RouterCC.vhd"
read_hdl "${SourcesDir}/Hermes/HermesTop.vhd"

# Elaborates top level entity
elaborate Hermes -parameters "{NoCXSize $XSize} {NoCYSize $YSize}"
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
