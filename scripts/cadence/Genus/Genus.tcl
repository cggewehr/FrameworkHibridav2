
# Set up vars
set ProjectDir $env(SynthProjectDir)
source "${ProjectDir}/synthesis/scripts/setup.tcl"

# Read cell lib info
source "${ScriptDir}/tech.tcl"

# Read HDL sources
source "${ScriptDir}/sources.tcl"

# Elaborates top level entity
elaborate
check_design -all

# Read constraints
read_sdc "${ScriptDir}/constraints.sdc"
check_timing_intent -verbose

# Synthesize design
syn_generic
syn_map
syn_opt

# Generate reports
report_area > "${ReportDir}/area.rpt"
report_design_rules > "${ReportDir}/design_rules.rpt"
report_power > "${ReportDir}/power_beforeVCD.rpt"
report_timing > "${ReportDir}/timing.rpt"
write_hdl > "${ReportDir}/HyHeMPS.v"
#report_summary
report_messages -all
report_messages -all > "${ReportDir}/messages.rpt"

# TODO: Call NCSim.tcl to generate VCD file and re-evaluate power for post-synthesis simulation
quit

