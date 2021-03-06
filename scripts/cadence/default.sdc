package require json

# Get AmountOfPEs from Platform.json
set JSONFile [open "$ProjectDir/src_json/Topology.json" r]
set JSONString [read $JSONFile]
set JSONDict [::json::json2dict $JSONString]
set AmountOfPEs [dict get $JSONDict "AmountOfPEs"]

# Get dict from ClusterClocks.json
set JSONFile [open "$ProjectDir/src_json/ClusterClocks.json" r]
set JSONString [read $JSONFile]
set JSONDict [::json::json2dict $JSONString]

# Create list containing all clock ports
set ClockPorts [lappend [get_ports "Clocks"] [get_ports "PEOutputs*.ClockTx*"]] 

# Create main clocks
set ClockPeriods [lrange [dict get $JSONDict "ClusterClockPeriods"] 0 ${AmountOfPEs}-1]
set i 0
puts "Clock ports by clock_ports command: [clock_ports]"
set_time_unit -nanoseconds
foreach ClockPeriod $ClockPeriods {
	#create_clock -name "Clock" -period $ClockPeriod [get_ports "/Clock"]
	#create_clock -name "MainClock$i" -period $ClockPeriod [clock_ports]
	create_clock -name "MainClock$i" -period $ClockPeriod [get_ports "Clocks\[$i\]"]
	#set_clock_uncertainty [expr $ClockPeriod * 0.05] [get_clocks "MainClock$i"]
	#set_clock_latency [expr $ClockPeriod * 0.05] [get_clocks "MainClock$i"]
	#set_input_delay -clock [get_clocks "MainClock$i"]  [expr $ClockPeriod * 0.05] [remove_from_collection [all_inputs] [get_ports "Clock$i"]]
	#set_output_delay -clock [get_clocks "MainClock$i"] [expr $ClockPeriod * 0.05] [all_outputs]
    set i ${i}+1
}

# Create tx clocks
#create_clock -name "MainClock" -period $ClockPeriod [get_ports "Clocks"]
#create_clock -name "ClockTx" -period $ClockPeriod [get_ports "PEOutputs*.ClockTx*"]
create_clock -name "ClockTx" -period [lindex $ClockPeriods 0] [get_ports "PEOutputs*.ClockTx*"]

# Set unidealistic values as 5% of clock period
set_clock_uncertainty [expr $ClockPeriod * 0.05] [get_clocks]
set_clock_latency [expr $ClockPeriod * 0.05] [get_clocks]
set_input_delay -clock [get_clocks]  [expr $ClockPeriod * 0.05] [remove_from_collection [all_inputs] $ClockPorts]
set_output_delay -clock [get_clocks] [expr $ClockPeriod * 0.05] [all_outputs]

# Set output capacitances arbitrarly at 0.05 pF 
set_load -pin_load 0.05 [get_ports [all_outputs]]

# Set transition times as 1% of clock period
#set_input_transition -rise -min [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] $ClockPorts]
#set_input_transition -fall -min [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] $ClockPorts]
set_input_transition -rise -max [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] $ClockPorts]
set_input_transition -fall -max [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] $ClockPorts]

