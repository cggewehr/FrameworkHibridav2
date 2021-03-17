
set_attribute hdl_language vhdl
set_attribute hdl_vhdl_read_version 1993

set HibridaDir $env(HIBRIDA_PATH)
set SourcesDir "${HibridaDir}/src/hardware"

read_hdl "${SourcesDir}/Top/JSON.vhd" -library JSON
read_hdl "${SourcesDir}/Misc/BufferCircular.vhd"
read_hdl "${SourcesDir}/Hermes/HeMPS_defaults.vhd" -library Hermes
read_hdl "${SourcesDir}/Hermes/Hermes_crossbar.vhd"
read_hdl "${SourcesDir}/Hermes/Hermes_buffer.vhd"
read_hdl "${SourcesDir}/Hermes/Hermes_switchcontrol.vhd"
read_hdl "${SourcesDir}/Hermes/RouterCC.vhd"
read_hdl "${SourcesDir}/Top/HyHeMPS_PKG.vhd" -library HyHeMPS
read_hdl "${SourcesDir}/Hermes/HermesTop.vhd"
read_hdl "${SourcesDir}/Crossbar/CrossbarControl.vhd"
read_hdl "${SourcesDir}/Crossbar/CrossbarRRArbiter.vhd"
read_hdl "${SourcesDir}/Crossbar/CrossbarBridgev2.vhd"
read_hdl "${SourcesDir}/Crossbar/CrossbarTop.vhd"
read_hdl "${SourcesDir}/Bus/BusRRArbiter.vhd"
read_hdl "${SourcesDir}/Bus/BusControl.vhd"
read_hdl "${SourcesDir}/Bus/BusBridgev2.vhd"
read_hdl "${SourcesDir}/Bus/BusTop.vhd"
#read_hdl "${SourcesDir}/Injector/Injector_PKG.vhd"
#read_hdl "${SourcesDir}/Injector/Injector.vhd"
#read_hdl "${SourcesDir}/Injector/Trigger.vhd"
#read_hdl "${SourcesDir}/Injector/Receiver.vhd"
#read_hdl "${SourcesDir}/Injector/InjBuffer.vhd"
#read_hdl "${SourcesDir}/Injector/PE.vhd"
#read_hdl "${SourcesDir}/Injector/PEBus.vhd"
read_hdl "${SourcesDir}/Top/HyHeMPS.vhd"
read_hdl "${SourcesDir}/Top/HyHeMPS_TB.vhd"
