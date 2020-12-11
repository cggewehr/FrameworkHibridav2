# $0 = ProjectName, $1 = ProjectDir, $2 = FPGA code (irrelevant for behavioural simulation) $3 = HardwarePath
set ProjectName [lindex $argv 0]
set ProjectDir [lindex $argv 1]
set FPGA [lindex $argv 2]
set HardwarePath [lindex $argv 3]

# Creates Vivado project
create_project $ProjectName $ProjectDir -part $FPGA
puts "Created Vivado project <${ProjectName}> at directory <${ProjectDir}>"

# Includes design files to project
open_project ${ProjectDir}/${ProjectName}.xpr

add_files "${HardwarePath}/Bus"
add_files "${HardwarePath}/Crossbar"
add_files "${HardwarePath}/Hermes"
add_files "${HardwarePath}/Injector"
add_files "${HardwarePath}/Misc"
add_files "${HardwarePath}/Top"

update_compile_order -fileset sources_1
#set_property top HyHeMPS_TB [current_fileset]
set_property top HyHeMPS_TB -fileset sources_1
set_property generic ProjectDir=\"${ProjectDir}\" [get_filesets sources_1]

puts "Added files to project <${ProjectName}>"

close_project
