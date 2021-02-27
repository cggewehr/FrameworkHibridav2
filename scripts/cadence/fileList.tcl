# Reads HDL source files into Genus.
read_hdl "${SourcesDir}/top/MIPS_PKG.vhd"
read_hdl "${SourcesDir}/stages/FetchStage.vhd"
read_hdl "${SourcesDir}/stages/DecodeStage.vhd"
read_hdl "${SourcesDir}/stages/ExecuteStage.vhd"
read_hdl "${SourcesDir}/stages/MemoryAccessStage.vhd"
read_hdl "${SourcesDir}/stages/WritebackStage.vhd"
read_hdl "${SourcesDir}/top/MIPS_Top.vhd"
