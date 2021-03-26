
set_time_unit -nanoseconds

# Set constraints for NoC
if {[info exists XSize]} { 

    # Create main clock(s)
    create_clock -name "MainClock" -period $ClockPeriod [get_ports "Clocks"]
    set_ideal_net [get_nets {Clocks[*]}]

    # Create tx clocks
    create_clock -name "ClockTx" -period $ClockPeriod [get_ports {PEOutputs[*][ClockTx]}]
    set_ideal_net [get_nets {PEOutputs[*][ClockTx]}]

    # Set unidealistic values as 5% of clock period
    set_clock_uncertainty [expr $ClockPeriod * 0.05] [get_clocks]
    set_clock_latency [expr $ClockPeriod * 0.05] [get_clocks]
    set_input_delay -clock [get_clocks ClockTx] [expr $ClockPeriod * 0.05] [remove_from_collection [all_inputs] [get_ports {"Clocks" {PEOutputs[*][ClockTx]}}]]
    set_output_delay -clock [get_clocks MainClock] [expr $ClockPeriod * 0.05] [remove_from_collection [all_outputs] [get_ports {PEInputs[*][ClockRx]}]]

    # Set transition times as 1% of clock period
    set_max_transition [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] [get_ports {"Clocks" {PEOutputs[*][ClockTx]}}]]

} else {

    # Create main clock(s)
    create_clock -name "MainClock" -period $ClockPeriod [get_ports "Clock"]
    set_ideal_net [get_nets "Clock"]

    # Create tx clocks
    create_clock -name "ClockTx" -period $ClockPeriod [get_ports {PEOutputs[*][ClockTx]}]
    set_ideal_net [get_nets {PEOutputs[*][ClockTx]}]

    # Set unidealistic values as 5% of clock period
    set_clock_uncertainty [expr $ClockPeriod * 0.05] [get_clocks]
    set_clock_latency [expr $ClockPeriod * 0.05] [get_clocks]
    set_input_delay -clock [get_clocks ClockTx] [expr $ClockPeriod * 0.05] [remove_from_collection [all_inputs] [get_ports {"Clock" {PEOutputs[*][ClockTx]}}]]
    set_output_delay -clock [get_clocks MainClock] [expr $ClockPeriod * 0.05] [remove_from_collection [all_outputs] [get_ports {PEInputs[*][ClockRx]}]]

    # Set transition times as 1% of clock period
    set_max_transition [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] [get_ports {"Clock" {PEOutputs[*][ClockTx]}}]]
   
}

# Create tx clocks
#create_clock -name "ClockTx" -period $ClockPeriod [get_ports {PEOutputs[*][ClockTx]}]
#set_ideal_net [get_nets {PEOutputs[*][ClockTx]}]
#create_clock -name "ClockRx" -period $ClockPeriod [get_ports {PEInputs[*][ClockRx]}]

# Set output capacitances arbitrarly at 0.05 pF 
set_load -pin_load 0.05 [remove_from_collection [all_outputs] [get_ports {PEInputs[*][ClockRx]}]]

# Set transition times as 1% of clock period
#set_input_transition -rise -min [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] $ClockPorts]
#set_input_transition -fall -min [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] $ClockPorts]
#set_input_transition -rise -max [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] [get_ports {"Clock" {PEOutputs[*][ClockTx]}}]]
#set_input_transition -fall -max [expr $ClockPeriod * 0.01] [remove_from_collection [all_inputs] [get_ports {"Clock" {PEOutputs[*][ClockTx]}}]]

