
import os
import json

def projgen(args):
    
    if args.AppendName is not None:
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
        
    # Open framework config file
    with open(os.environ["HIBRIDA_CONFIG_FILE"], "r") as ConfigFile:
        ConfigDict = json.loads(ConfigFile.read())
        
    # Open framework project index
    with open(ConfigDict["HibridaPath"] + "/data/projectIndex.json", "r") as ProjectIndexFile:
        ProjectIndexDict = json.loads(ProjectIndexFile.read())
    
    # Check if project name already exists
    if args.ProjectName in ProjectIndexDict.keys():
    
        while True:
    
            print("Warning: Project <" + args.ProjectName + "> already exists. Do you wish to proceed (Y/N)?")
            ipt = input()
            
            if ipt == "Y" or ipt == "y":
                # TODO: Prompt if projgen should wipe ProjectDirectory/ProjectName clean, so that only dirs created by projgen should exist within it
                break
            elif ipt == "N" or ipt == "n":
                exit(0)
            
    # Updates framework project index with newly created project
    with open(ConfigDict["HibridaPath"] + "/data/projectIndex.json", "w") as ProjectIndexFile:
        ProjectIndexDict[args.ProjectName] = ProjectDir
        ProjectIndexFile.write(json.dumps(ProjectIndexDict, sort_keys = False, indent = 4))
        
    # Updates framework config file with newly created project as MRU project
    with open(os.environ["HIBRIDA_CONFIG_FILE"], "w") as ConfigFile:
    
        ConfigDict["MostRecentProject"] = args.ProjectName
        
        ConfigFile.write(json.dumps(ConfigDict, sort_keys = False, indent = 4))
        
    # Makes project dirs
    os.makedirs(ProjectDir, exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
    os.makedirs(ProjectDir + "/flow", exist_ok = True)
    os.makedirs(ProjectDir + "/log", exist_ok = True)
    os.makedirs(ProjectDir + "/platform", exist_ok = True)
    os.makedirs(ProjectDir + "/src_json", exist_ok = True)

    # Creates info JSON for newly created project
    with open(ProjectDir + "/projectInfo.json", "w") as ProjectInfoFile:
        
        ProjectDict = dict()
        
        ProjectDict["ProjectName"] = args.ProjectName
        ProjectDict["ProjectDir"] = ProjectDir
        ProjectDict["AllocationMapFile"] = None
        ProjectDict["ClusterClocksFile"] = None
        ProjectDict["TopologyFile"] = None
        ProjectDict["WorkloadFile"] = None

        ProjectInfoFile.write(json.dumps(ProjectDict, sort_keys = False, indent = 4))

    # Tool-specific behaviour
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
            
            # Create hdl.var file for NCSIM
            with open(ProjectDir + "/hdl.var", 'w') as hdl_var:
                hdl_var.write("DEFINE WORK worklib\n")
            
            # Create cds.lib file for NCSIM
            with open(ProjectDir + "/cds.lib", 'w') as cds_file:
                cds_file.write("define worklib " + ProjectDir + "/INCA_libs/worklib\n")
                cds_file.write("define json " + ProjectDir + "/INCA_libs/JSON\n")
                cds_file.write("define hyhemps " + ProjectDir + "/INCA_libs/HyHeMPS\n")
                cds_file.write("define hermes " + ProjectDir + "/INCA_libs/Hermes\n")
                cds_file.write("include $CDS_INST_DIR/tools/inca/files/cds.lib\n")
				
            # Create Makefile
            with open(ProjectDir + "/makefile", 'w') as makefile:
                makefile.write("########################################################################\n")
                makefile.write("# HyHeMPS Cadence tools makefile\n")
                makefile.write("########################################################################\n")
                makefile.write("# Obs:\n")
                makefile.write("# Alter $(HIBRIDA_HARDWARE_PATH) for custom sources\n")
                makefile.write("#\n")
                makefile.write("########################################################################\n")
                makefile.write("\n")
                makefile.write("########################## Command options #############################\n")
                makefile.write("PROJECT_DIR=" + ProjectDir + "\n")
                makefile.write("HIBRIDA_HARDWARE_PATH=" + ConfigDict["HibridaPath"] + "/src/hardware\n")
                makefile.write("# $NCVHDL_CMD_OPTS, $NCELAB_CMD_OPTS and $NCSIM_CMD_OPTS should be defined from command line or calling script\n")
                makefile.write("NCVHDL_BASE_OPTS=-smartlib -cdslib cds.lib -logfile log/cadence/ncvhdl.log -errormax 15 -update -v93 -linedebug -status\n")
                makefile.write("NCVHDL_OPTS=$(NCVHDL_BASE_OPTS) $(NCVHDL_CMD_OPTS)\n")
                makefile.write("NCELAB_BASE_OPTS=-work worklib -cdslib cds.lib -logfile log/cadence/ncelab.log -errormax 15 -update -status\n")
                makefile.write("NCELAB_OPTS=$(NCELAB_BASE_OPTS) $(NCELAB_CMD_OPTS)\n")
                makefile.write("NCSIM_BASE_OPTS=-cdslib cds.lib -logfile log/cadence/ncsim.log -errormax 15\n")
                makefile.write("NCSIM_OPTS=$(NCSIM_BASE_OPTS) $(NCSIM_CMD_OPTS)\n")
                makefile.write("\n")
                makefile.write("echo:\n")
                makefile.write('	@echo "ECHO MAKEFILE @ $(PROJECT_DIR)"\n')
                makefile.write("\n")
                makefile.write("compile:\n")
                makefile.write('	@echo "############################################################"\n')
                makefile.write('	@echo "################# Compiling VHDL files #####################"\n')
                makefile.write('	@echo "############################################################"\n')
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/JSON.vhd -work JSON\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Misc/BufferCircular.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/HeMPS_defaults.vhd -work Hermes\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/Hermes_crossbar.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/Hermes_buffer.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/Hermes_switchcontrol.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/RouterCC.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/HyHeMPS_PKG.vhd -work HyHeMPS\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Arbiter/RoundRobinArbiter.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Arbiter/ArbiterFactory.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/HermesTop.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Crossbar/CrossbarBridgev2.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Crossbar/CrossbarTop.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Bus/BusControl.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Bus/BusBridgev2.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Bus/BusTop.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Injector_PKG.vhd -work HyHeMPS\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Injector.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Trigger.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Logger.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/InjBuffer.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/PEBus.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/PE.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/DVFS/ClockDivider.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/DVFS/DVFSController.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/HyHeMPS.vhd\n")
                makefile.write("	ncvhdl $(NCVHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/HyHeMPS_TB.vhd\n")
                makefile.write('	@echo "############################################################"\n')
                makefile.write('	@echo "################ Done compiling VHDL files #################"\n')
                makefile.write('	@echo "############################################################"\n')
                makefile.write("\n")
                makefile.write("elab:\n")
                makefile.write('	@echo "############################################################"\n')
                makefile.write('	@echo "############### Elaborating top-level entity ###############"\n')
                makefile.write('	@echo "############################################################"\n')
                makefile.write("	ncelab $(NCELAB_OPTS) worklib.hyhemps_tb -generic \":ProjectDir => \\\"$(PROJECT_DIR)\\\"\" \n")
                makefile.write('	@echo "############################################################"\n')
                makefile.write('	@echo "############# Done elaborating top-level entity ############"\n')
                makefile.write('	@echo "############################################################"\n')
                makefile.write("\n")
                makefile.write("sim:\n")
                makefile.write('	@echo "############################################################"\n')
                makefile.write('	@echo "############### Beginning simulation with GUI ##############"\n')
                makefile.write('	@echo "############################################################"\n')
                makefile.write("	ncsim $(NCSIM_OPTS) -gui worklib.hyhemps_tb:rtl\n")
                makefile.write('	@echo "############################################################"\n')
                makefile.write('	@echo "################## GUI simulation ended ####################"\n')
                makefile.write('	@echo "############################################################"\n')
                makefile.write("\n")
                makefile.write("simnogui:\n")
                makefile.write('	@echo "############################################################"\n')
                makefile.write('	@echo "############## Beginning simulation w/o GUI ################"\n')
                makefile.write('	@echo "############################################################"\n')
                makefile.write("	ncsim $(NCSIM_OPTS) worklib.hyhemps_tb:rtl\n")
                makefile.write('	@echo "############################################################"\n')
                makefile.write('	@echo "################# No-GUI simulation ended ##################"\n')
                makefile.write('	@echo "############################################################"\n')
                makefile.write("\n")
                makefile.write("run:\n")
                makefile.write("	make -C $(PROJECT_DIR) all\n")
                makefile.write("\n")
                makefile.write("runnogui:\n")
                makefile.write("	make -C $(PROJECT_DIR) compile\n")
                makefile.write("	make -C $(PROJECT_DIR) elab\n")
                makefile.write("	make -C $(PROJECT_DIR) simnogui\n")
                makefile.write("\n")
                makefile.write("all:\n")
                makefile.write("	make -C $(PROJECT_DIR) compile\n")
                makefile.write("	make -C $(PROJECT_DIR) elab\n")
                makefile.write("	make -C $(PROJECT_DIR) sim\n")
                makefile.write("\n")
                
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
            FPGA = "xcku040-ffva1156-2-e"  # Default value, to be changed later with Vivado GUI
            HardwarePath = os.path.join(ConfigDict["HibridaPath"], "src", "hardware")
            TCLArgs = args.ProjectName + " " + ProjectDir + " " + FPGA + " " + HardwarePath
            os.system("vivado -mode batch -source " + TCLScript + " -tclargs " + TCLArgs)
        
        else:
        
            print("Error: Tool <" + args.Tool + "> is not recognized")
            exit(1)
			
    print("Created project <" + args.ProjectName + "> at <" + os.path.abspath(ProjectDir) + ">")
