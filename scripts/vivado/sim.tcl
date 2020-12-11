# $0 = ProjectName, $1 = ProjectDir
set ProjectName [lindex $argv 0]
set ProjectDir [lindex $argv 1]

open_project ${ProjectDir}/${ProjectName}.xpr

start_gui

puts "Beginning simulation of project <${ProjectName}>"
launch_simulation -step simulate
