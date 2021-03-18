
set_time_unit -nanoseconds

# Create main clock
create_clock -name "MainClock" -period $ClockPeriod [get_ports "Clock"]

# Create tx clocks
create_clock -name "ClockTx" -period $ClockPeriod [get_ports "PEOutputs*.ClockTx*"]

# Set unidealistic values as 5% of clock period
set_clock_uncertainty [expr $ClockPeriod * 0.05] [get_clocks]
set_clock_latency [expr $ClockPeriod * 0.05] [get_clocks]
set_input_delay -clock [get_clocks]  [expr $ClockPeriod * 0.05] [remove_from_collection [all_inputs] [get_ports "Clock"]]
set_output_delay -clock [get_clocks] [expr $ClockPeriod * 0.05] [all_outputs]

# Set output capacitances arbitrarly at 0.05 pF 
set_load -pin_load 0.05 [get_ports [all_outputs]]

# Set transition times as 1% of clock period
#set_input_transition -rise -min [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] $ClockPorts]
#set_input_transition -fall -min [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] $ClockPorts]
set_input_transition -rise -max [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] [get_ports "Clock"]]
set_input_transition -fall -max [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] [get_ports "Clock"]]
