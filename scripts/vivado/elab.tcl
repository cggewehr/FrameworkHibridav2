# $0 = ProjectName, $1 = ProjectDir
set ProjectName [lindex $argv 0]
set ProjectDir [lindex $argv 1]

open_project ${ProjectDir}/${ProjectName}.xpr

launch_simulation -step elab

close_project

puts "Elaborated project <${ProjectName}>"
