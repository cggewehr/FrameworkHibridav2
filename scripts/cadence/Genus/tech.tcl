
# Read cell library & LEF
#read_libs /home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/cds.lib

# PVT = Slow 1.1V 0C
#read_libs /home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/gsclib045/timing/slow_vdd1v0_basicCells.lib
#read_libs /home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/gsclib045/timing/slow_vdd1v0_extvdd1v0.lib
#read_libs /home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/gsclib045/timing/slow_vdd1v0_extvdd1v2.lib
#read_libs /home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/gsclib045/timing/slow_vdd1v0_multibitsDFF.lib

# PVT = Fast 1.32V 0C
# read_libs /home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/gsclib045/timing/fast_vdd1v2_basicCells.lib
# read_libs /home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/gsclib045/timing/fast_vdd1v2_extvdd1v0.lib
# read_libs /home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/gsclib045/timing/fast_vdd1v2_extvdd1v2.lib
# read_libs /home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/gsclib045/timing/fast_vdd1v2_multibitsDFF.lib

set DesignKitDir "/home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/"
set CellLibDir "${DesignKitDir}/gsclib045/"
set TechDir "${DesignKitDir}/gsclib045_tech/"

# Set cell lib characterizations
if {$ProcessCorner == "Slow" || $ProcessCorner == "s"} {

    if {$VoltageLevel == "0.9" || $VoltageLevel == "0.9V"} {
	    #read_libs /home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/gsclib045/timing/slow_vdd1v0_basicCells.lib
	    read_libs "${CellLibDir}/timing/slow_vdd1v0_basicCells.lib ${CellLibDir}/timing/slow_vdd1v0_multibitsDFF.lib"
	    #read_libs "${CellLibDir}/timing/slow_vdd1v0_multibitsDFF.lib"
    } elseif {$VoltageLevel == "1.08" || $VoltageLevel == "1.08V"} {
	    read_libs "${CellLibDir}/timing/slow_vdd1v2_basicCells.lib ${CellLibDir}/timing/slow_vdd1v2_multibitsDFF.lib"
    } else {
	    puts "VoltageLevel value <${VoltageLevel}> not recognized. Supported values are \"1.08\", \"1.08V\", \"0.9\", \"0.9V\". For further information refer to cell lib README"
        exit
    }

} elseif {$ProcessCorner == "Fast" || $ProcessCorner == "f"} {

    if {$VoltageLevel == "1.1" || $VoltageLevel == "1.1V"} {
	    read_libs "${CellLibDir}/timing/fast_vdd1v0_basicCells.lib ${CellLibDir}/timing/fast_vdd1v0_multibitsDFF.lib"
    } elseif {$VoltageLevel == "1.32" || $VoltageLevel == "1.32V"} {
	    read_libs "${CellLibDir}/timing/fast_vdd1v2_basicCells.lib ${CellLibDir}/timing/fast_vdd1v2_multibitsDFF.lib"
    } else {
	    puts "VoltageLevel value <${VoltageLevel}> not recognized. Supported values are \"1.1\", \"1.1V\", \"1.32\", \"1.32V\". For further information refer to cell lib README"
        exit
    }

} else {
    puts "Process value <${ProcessCorner}> not recognized. Supported values are \"Slow\", \"s\", \"Fast\", \"f\". For further information refer to cell lib README"
    exit
}

# STD cell layout info
#read_physical /home/tools/design_kits/cadence_pdks/gpdk045_45nm_cmos_11m-2p/reference_libs/GPDK045/gsclib045_all_v4.4/gsclib045_tech/lef/gsclib045_tech.lef
read_physical -lefs "${CellLibDir}/lef/gsclib045_tech.lef ${CellLibDir}/lef/gsclib045_macro.lef ${CellLibDir}/lef/gsclib045_multibitsDFF.lef"
#read_physical -lefs "${TechDir}/lef/gsclib045_macro.lef"
#read_physical -lefs "${TechDir}/lef/gsclib045_multibitsDFF.lef"

# Parasitic extraction rules
#set_db qrc_tech_file "${TechDir}/qrc/qx/gsclib045.tch"
set_db qrc_tech_file "${CellLibDir}/qrc/qx/gpdk045.tch"
