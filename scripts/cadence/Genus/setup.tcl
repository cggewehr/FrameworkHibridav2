
# Set vars from environment variables
#set ProjectDir $env(SynthProjectDir)
#set VoltageLevel $env(SynthVoltageLevel)
#set ProcessCorner $env(SynthProcessCorner)
catch {set VoltageLevel $env(SynthVoltageLevel)}
catch {set ProcessCorner $env(SynthProcessCorner)}
catch {set Standalone $env(SynthStandalone)}

set HibridaDir $env(HIBRIDA_PATH)

# Set up auxiliary dir paths
set SourcesDir "${HibridaDir}/src/hardware"
set ScriptDir "${ProjectDir}/synthesis/scripts"
set ReportDir "${ProjectDir}/synthesis/deliverables"
set WorkDir "${ProjectDir}/synthesis/work"
set CellLibDir "/home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/gsclib045"

# Set VHDL info
set_db hdl_language vhdl
set_db hdl_vhdl_read_version 1993

# Set synthesis effort
set_db "syn_generic_effort" "high"
set_db "syn_map_effort" "high"
set_db "syn_opt_effort" "high"
