
def projgen(args):
    
    import os
    import json
    
    #print(args)
    
    if args.AppendName is not None:
    #if args.appendname is not None:
        ProjectDir = args.ProjectDirectory + "/" + args.ProjectName
    else:
        ProjectDir = args.ProjectDirectory
        
    # Check if given project path exists. If not, mkdir
    if os.path.isdir(ProjectDir):
        
        while True:
        
            print("Warning: Project path <" + ProjectDir + "> already exists. Do you wish to proceed (Y/N)?")
            #ipt = raw_input()
            ipt = input()
            
            # TODO: Prompt if projgen should wipe ProjectDirectory/ProjectName clean, so that only dirs created by projgen should exist within it
            if ipt == "Y" or ipt == "y":
                break
                
            elif ipt == "N" or ipt == "n":
                exit(0)
        
    ConfigFile = open(os.environ["HIBRIDA_CONFIG_FILE"], "r")
    ConfigDict = json.loads(ConfigFile.read())
    
    # Check if project name already exists
    if args.ProjectName in ConfigDict["Projects"].keys():
    
        while True:
    
            print("Warning: Project <" + args.ProjectName + "> already exists. Do you wish to proceed (Y/N)?")
            #ipt = raw_input()
            ipt = input()
            
            if ipt == "Y" or ipt == "y":
                # TODO: Prompt if projgen should wipe ProjectDirectory/ProjectName clean, so that only dirs created by projgen should exist within it
                break
            elif ipt == "N" or ipt == "n":
                exit(0)
            
    # Makes main project dir
    os.makedirs(ProjectDir, exist_ok = True)
        
    # Updates framework config file
    ProjectDict = dict()
    ProjectDict["ProjectDir"] = ProjectDir
    
    ProjectDict["AllocationMapFile"] = None
    ProjectDict["ClusterClocksFile"] = None
    ProjectDict["TopologyFile"] = None
    ProjectDict["WorkloadFile"] = None
    
    #ProjectDict["CustomHardware"] = args.CustomHardware
    #ProjectDict["Makefile"] = args.Makefile
    
    ConfigDict["Projects"][args.ProjectName] = ProjectDict
    ConfigDict["MostRecentProject"] = args.ProjectName
    
    ConfigFile.close()
    with open(os.environ["HIBRIDA_CONFIG_FILE"], "w") as ConfigFile:
        ConfigFile.write(json.dumps(ConfigDict, sort_keys = False, indent = 4))
        
    # Makes "log", "flow" and "platform" dirs
    os.makedirs(ProjectDir + "/flow", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
    os.makedirs(ProjectDir + "/log", exist_ok = True) 
    os.makedirs(ProjectDir + "/platform", exist_ok = True) 
    os.makedirs(ProjectDir + "/src_json", exist_ok = True)

    # Makes custom hardware dicts
    if args.HardwareDirs:
    
        os.makedirs(ProjectDir + "/hardware/Bus", exist_ok = True)
        os.makedirs(ProjectDir + "/hardware/Crossbar", exist_ok = True)
        os.makedirs(ProjectDir + "/hardware/Hermes", exist_ok = True)
        os.makedirs(ProjectDir + "/hardware/Injector", exist_ok = True)
        os.makedirs(ProjectDir + "/hardware/Misc", exist_ok = True)
        os.makedirs(ProjectDir + "/hardware/Top", exist_ok = True)
	    		
    if args.Tool is not None:
		
        if args.Tool == "cadence" or args.Tool == "Genus" or args.Tool == "RTLCompiler":

            # Make subdirs
            os.makedirs(ProjectDir + "/INCA_libs/worklib", exist_ok = True)
            os.makedirs(ProjectDir + "/INCA_libs/JSON", exist_ok = True)
            os.makedirs(ProjectDir + "/INCA_libs/HyHeMPS", exist_ok = True)
            os.makedirs(ProjectDir + "/INCA_libs/Hermes", exist_ok = True)
            os.makedirs(ProjectDir + "/log/cadence", exist_ok = True)
            os.makedirs(ProjectDir + "/synthesis/scripts", exist_ok = True)
            os.makedirs(ProjectDir + "/synthesis/deliverables", exist_ok = True)
            os.makedirs(ProjectDir + "/synthesis/work", exist_ok = True)

            # TODO: Copy UPF file
            
            # Create hdl.var file
            with open(ProjectDir + "/hdl.var", 'w') as hdl_var:
                hdl_var.write("DEFINE WORK worklib\n")
            
            # Create cds.lib file
            with open(ProjectDir + "/cds.lib", 'w') as cds_file:
                cds_file.write("define worklib " + ProjectDir + "/INCA_libs/worklib\n")
                cds_file.write("define json " + ProjectDir + "/INCA_libs/JSON\n")
                cds_file.write("define hyhemps " + ProjectDir + "/INCA_libs/HyHeMPS\n")
                cds_file.write("define hermes " + ProjectDir + "/INCA_libs/Hermes\n")
                cds_file.write("include $CDS_INST_DIR/tools/inca/files/cds.lib\n")
				
            # Create Makefile
            with open(ProjectDir + "/makefile", 'w') as make_file:
                make_file.write("########################################################################\n")
                make_file.write("# HyHeMPS Cadence tools makefile\n")
                make_file.write("########################################################################\n")
                make_file.write("# Obs:\n")
                make_file.write("# Alter $(HIBRIDA_HARDWARE_PATH) for custom sources\n")
                make_file.write("#\n")
                make_file.write("########################################################################\n")
                make_file.write("\n")
                make_file.write("########################## Command options #############################\n")
                make_file.write("PROJECT_DIR=" + ProjectDir + "\n")
                make_file.write("HIBRIDA_HARDWARE_PATH=" + ConfigDict["HibridaPath"] + "/src/hardware\n")
                make_file.write("VHDL_OPTS=-smartlib -cdslib cds.lib -logfile log/cadence/ncvhdl.log -errormax 15 -update -v93 -linedebug -status\n")
                make_file.write("ELAB_OPTS=-work worklib -cdslib cds.lib -logfile log/cadence/ncelab.log -errormax 15 -update -status\n")
                make_file.write("SIMH_OPTS=-cdslib cds.lib -logfile log/cadence/ncsim.log -errormax 15\n")
                make_file.write("\n")
                make_file.write("echo:\n")
                make_file.write('	@echo "VHDL FILES"\n')
                make_file.write("\n")
                make_file.write("compile:\n")
                make_file.write('	@echo "############################################################"\n')
                make_file.write('	@echo "################### Compile VHDL Files #####################"\n')
                make_file.write('	@echo "############################################################"\n')
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/JSON.vhd -work JSON\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Misc/BufferCircular.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/HeMPS_defaults.vhd -work Hermes\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/Hermes_crossbar.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/Hermes_buffer.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/Hermes_switchcontrol.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/RouterCC.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/HyHeMPS_PKG.vhd -work HyHeMPS\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/HermesTop.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Crossbar/CrossbarControl.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Crossbar/CrossbarRRArbiter.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Crossbar/CrossbarBridgev2.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Crossbar/CrossbarTop.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Bus/BusRRArbiter.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Bus/BusControl.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Bus/BusBridgev2.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Bus/BusTop.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Injector_PKG.vhd -work HyHeMPS\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Injector.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Trigger.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Receiver.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/InjBuffer.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/PEBus.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/PE.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/DVFS/ClockDivider.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/DVFS/DVFSController.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/HyHeMPS.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/HyHeMPS_TB.vhd\n")
                make_file.write('	@echo "############### FINALIZE COMPILE VHDL Files ################"\n')
                make_file.write("\n")
                make_file.write("elab:\n")
                make_file.write('	@echo "############################################################"\n')
                make_file.write('	@echo "################## Elaborate Top Level #####################"\n')
                make_file.write('	@echo "############################################################"\n')
                make_file.write("	ncelab $(ELAB_OPTS) worklib.hyhemps_tb -generic \":ProjectDir => \\\"$(PROJECT_DIR)\\\"\" \n")
                make_file.write('	@echo "########### FINALIZE ELABORATION  HYBRID Files #############"\n')
                make_file.write("\n")
                make_file.write("sim:\n")
                make_file.write('	@echo "############################################################"\n')
                make_file.write('	@echo "##################  SIMULATION HeMPS   #####################"\n')
                make_file.write('	@echo "############################################################"\n')
                make_file.write("	ncsim $(SIMH_OPTS) -gui worklib.hyhemps_tb:rtl\n")
                make_file.write('	@echo "############### FINALIZE SIMULATION HYBRID #################"\n')
                make_file.write("\n")
                make_file.write("simnogui:\n")
                make_file.write('	@echo "############################################################"\n')
                make_file.write('	@echo "##################   SIMULATION HeMPS  #####################"\n')
                make_file.write('	@echo "############################################################"\n')
                make_file.write("	ncsim $(SIMH_OPTS) worklib.hyhemps_tb:rtl\n")
                make_file.write('	@echo "############### FINALIZE SIMULATION HYBRID #################"\n')
                make_file.write("\n")
                make_file.write("all:\n")
                make_file.write("	make compile\n")
                make_file.write("	make elab\n")
                make_file.write("	make sim\n")
                
                # TODO: make clean
                # waves.shm
                # *.err
                # *.diag
                # *.log
                # *.key
                # logs/cadence/*
                # INCA_libs/JSON/*
                # INCA_libs/HyHeMPS/*
                # INCA_libs/Hermes/*
                
            # Copy synthesis scripts and default constraints
            if args.Tool == "Genus" or args.Tool == "RTLCompiler":
            
                if args.Tool == "Genus":
                    scriptsSourcePath = os.path.join(ConfigDict["HibridaPath"], "scripts", "cadence", "Genus")
                elif args.Tool == "RTLCompiler":
                    scriptsSourcePath = os.path.join(ConfigDict["HibridaPath"], "scripts", "cadence", "RTLCompiler")
                scriptsTargetPath = os.path.join(ProjectDir, "synthesis", "scripts")
                
                from shutil import copy
                copy(os.path.join(scriptsSourcePath, "Genus.tcl"), os.path.join(scriptsTargetPath, "Genus.tcl"))
                copy(os.path.join(scriptsSourcePath, "GenusBusStandalone.tcl"), os.path.join(scriptsTargetPath, "GenusBusStandalone.tcl"))
                copy(os.path.join(scriptsSourcePath, "GenusCrossbarStandalone.tcl"), os.path.join(scriptsTargetPath, "GenusCrossbarStandalone.tcl"))
                copy(os.path.join(scriptsSourcePath, "GenusNoCStandalone.tcl"), os.path.join(scriptsTargetPath, "GenusNoCStandalone.tcl"))
                copy(os.path.join(scriptsSourcePath, "run_bus_synthesis.sh"), os.path.join(scriptsTargetPath, "run_bus_synthesis.sh"))
                copy(os.path.join(scriptsSourcePath, "run_crossbar_synthesis.sh"), os.path.join(scriptsTargetPath, "run_crossbar_synthesis.sh"))
                copy(os.path.join(scriptsSourcePath, "run_noc_synthesis.sh"), os.path.join(scriptsTargetPath, "run_noc_synthesis.sh"))
                copy(os.path.join(scriptsSourcePath, "sources.tcl"), os.path.join(scriptsTargetPath, "sources.tcl"))
                copy(os.path.join(scriptsSourcePath, "setup.tcl"), os.path.join(scriptsTargetPath, "setup.tcl"))
                copy(os.path.join(ConfigDict["HibridaPath"], "scripts", "cadence", "default.sdc"), os.path.join(scriptsTargetPath, "constraints.sdc"))
                copy(os.path.join(ConfigDict["HibridaPath"], "scripts", "cadence", "standalone.sdc"), os.path.join(scriptsTargetPath, "standalone.sdc"))
                copy(os.path.join(ConfigDict["HibridaPath"], "scripts", "cadence", "standaloneDiv2.sdc"), os.path.join(scriptsTargetPath, "standaloneDiv2.sdc"))
                
                try:
                    copy(os.path.join(scriptsSourcePath, "tech.tcl"), os.path.join(scriptsTargetPath, "tech.tcl"))
                except IOError:
                    print("Warning: tech.tcl file was not found")
                    pass
                    
                # Copy MMMC scripts
                if args.Tool == "Genus":
                
                    scriptsSourcePath = os.path.join(scriptsSourcePath, "MMMC")
                    
                    copy(os.path.join(scriptsSourcePath, "GenusMMMC.tcl"), os.path.join(scriptsTargetPath, "GenusMMMC.tcl"))
                    copy(os.path.join(scriptsSourcePath, "MMMC.tcl"), os.path.join(scriptsTargetPath, "MMMC.tcl"))
                    copy(os.path.join(scriptsSourcePath, "GenusBusStandaloneMMMC.tcl"), os.path.join(scriptsTargetPath, "GenusBusStandaloneMMMC.tcl"))
                    copy(os.path.join(scriptsSourcePath, "GenusCrossbarStandaloneMMMC.tcl"), os.path.join(scriptsTargetPath, "GenusCrossbarStandaloneMMMC.tcl"))
                    copy(os.path.join(scriptsSourcePath, "GenusNoCStandaloneMMMC.tcl"), os.path.join(scriptsTargetPath, "GenusNoCStandaloneMMMC.tcl"))
                    copy(os.path.join(scriptsSourcePath, "run_bus_synthesis_MMMC.sh"), os.path.join(scriptsTargetPath, "run_bus_synthesis_MMMC.sh"))
                    copy(os.path.join(scriptsSourcePath, "run_crossbar_synthesis_MMMC.sh"), os.path.join(scriptsTargetPath, "run_crossbar_synthesis_MMMC.sh"))
                    copy(os.path.join(scriptsSourcePath, "run_noc_synthesis_MMMC.sh"), os.path.join(scriptsTargetPath, "run_noc_synthesis_MMMC.sh"))
                                
        elif args.Tool == "vivado" or args.Tool == "Vivado":
        
            # Runs vivado with create project script
            TCLScript = os.path.join(ConfigDict["HibridaPath"], "scripts", "vivado", "projgen.tcl")
            FPGA = "xcku040-ffva1156-2-e"
            HardwarePath = os.path.join(ConfigDict["HibridaPath"], "src", "hardware")
            TCLArgs = args.ProjectName + " " + ProjectDir + " " + FPGA + " " + HardwarePath
            os.system("vivado -mode batch -source " + TCLScript + " -tclargs " + TCLArgs)
        
        else:
        
            print("Error: Tool <" + args.Tool + "> is not recognized")
            exit(1)
			
    # TODO: Copy testbench HDL to project directory, in order to have project directory as reference directory in simulation tool
    
    print("Created project <" + args.ProjectName + "> at <" + os.path.abspath(ProjectDir) + ">")
