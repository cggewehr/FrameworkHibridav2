
create_library_set -name LIB_0V9 -timing "${CellLibDir}/timing/slow_vdd1v0_basicCells.lib ${CellLibDir}/timing/slow_vdd1v0_multibitsDFF.lib"
create_library_set -name LIB_1V08 -timing "${CellLibDir}/timing/slow_vdd1v2_basicCells.lib ${CellLibDir}/timing/slow_vdd1v2_multibitsDFF.lib"

create_opcond -name OPCOND_0V9 -process 1 -voltage 0.9 -temperature 125
create_opcond -name OPCOND_1V08 -process 1 -voltage 1.08 -temperature 125

create_timing_condition -name TIMINGCOND_0V9 -opcond OPCOND_0V9 -library_sets LIB_0V9
create_timing_condition -name TIMINGCOND_1V08 -opcond OPCOND_1V08 -library_sets LIB_1V08

create_rc_corner -name RC_CORNER -qrc_tech "${CellLibDir}/qrc/qx/gpdk045.tch" -temperature 125

create_delay_corner -name DELAY_CORNER_0V9 -early_timing_condition TIMINGCOND_0V9 -late_timing_condition TIMINGCOND_0V9 \
					-early_rc_corner RC_CORNER -late_rc_corner RC_CORNER
create_delay_corner -name DELAY_CORNER_1V08 -early_timing_condition TIMINGCOND_1V08 -late_timing_condition TIMINGCOND_1V08 \
					-early_rc_corner RC_CORNER -late_rc_corner RC_CORNER

if {$Standalone == 1} {

    create_constraint_mode -name DEFAULT_CONSTRAINTS -sdc_files "${ScriptDir}/standalone.sdc"
    create_constraint_mode -name DEFAULT_CONSTRAINTS_DIV_2 -sdc_files "${ScriptDir}/standaloneDiv2.sdc"

	create_analysis_view -name VIEW_0V9 -delay_corner DELAY_CORNER_0V9 -constraint_mode DEFAULT_CONSTRAINTS_DIV_2
	create_analysis_view -name VIEW_1V08 -delay_corner DELAY_CORNER_1V08 -constraint_mode DEFAULT_CONSTRAINTS

} else {

    create_constraint_mode -name DEFAULT_CONSTRAINTS -sdc_files "${ScriptDir}/constraints.sdc"

	create_analysis_view -name VIEW_0V9 -delay_corner DELAY_CORNER_0V9 -constraint_mode DEFAULT_CONSTRAINTS
	create_analysis_view -name VIEW_1V08 -delay_corner DELAY_CORNER_1V08 -constraint_mode DEFAULT_CONSTRAINTS

}

set_analysis_view -setup {VIEW_0V9 VIEW_1V08}
