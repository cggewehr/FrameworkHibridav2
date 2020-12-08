
def projgen(args):
    
    import os
    import json
    
    print(args)
    
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
        
    # Check if project name already exists
    ConfigFile = open(os.environ["HIBRIDA_CONFIG_FILE"], "r")
    ConfigDict = json.loads(ConfigFile.read())
    
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
    ProjectDict["Makefile"] = args.Makefile
    
    ConfigDict["Projects"][args.ProjectName] = ProjectDict
    ConfigDict["MostRecentProject"] = args.ProjectName
    
    ConfigFile.close()
    with open(os.environ["HIBRIDA_CONFIG_FILE"], "w") as ConfigFile:
        ConfigFile.write(json.dumps(ConfigDict, sort_keys = False, indent = 4))
        
    # Makes "log", "flow" and "platform" dirs
    os.makedirs(ProjectDir + "/flow", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
    os.makedirs(ProjectDir + "/log", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
    os.makedirs(ProjectDir + "/platform", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
    os.makedirs(ProjectDir + "/src_json", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+

    # Makes custom hardware dicts
    if args.HardwareDirs:
    
        os.makedirs(ProjectDir + "/hardware/Bus", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
        os.makedirs(ProjectDir + "/hardware/Crossbar", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
        os.makedirs(ProjectDir + "/hardware/Hermes", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
        os.makedirs(ProjectDir + "/hardware/Injector", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
        os.makedirs(ProjectDir + "/hardware/Misc", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
        os.makedirs(ProjectDir + "/hardware/Top", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
	    		
    if args.Makefile is not None:
    
        try:
            MakefileName = str(args.Makefile)
        except KeyError or IndexError:
            print("Error: Makefile argument <Makefile> not given")
            exit(1)
		
        if MakefileName=="cadence":

            os.makedirs(ProjectDir + "/INCA_libs/worklib", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
            
            # Create cds.lib file
            with open(ProjectDir + "/cds.lib", 'w') as cds_file:
                cds_file.write("define worklib " + args.ProjectDirectory + "/" + args.ProjectName + "/INCA_libs/worklib\n")
                cds_file.write("include $CDS_INST_DIR/tools/inca/files/cds.lib\n")
				
            # Create Makefile file
            with open(ProjectDir + "/makefile", 'w') as make_file:
                make_file.write("########################################################################\n")
                make_file.write("# Makefile geral para simulacao da Hybrid HeMPS no ambiente Nupedee\n")
                make_file.write("########################################################################\n")
                make_file.write("# Obs:\n")
                make_file.write("# Alter $(HIBRIDA_HARDWARE_PATH) for custon VHDL\n")
                make_file.write("#\n")
                make_file.write("########################################################################\n")
                make_file.write("\n")
                make_file.write("########################## Command options #############################\n")
                make_file.write("VHDL_OPTS=-work worklib -cdslib cds.lib -logfile cadenceLogs/ncvhdl.log -errormax 15 -update -v93 -linedebug -status\n")
                make_file.write("ELAB_OPTS=-work worklib -cdslib cds.lib -logfile cadenceLogs/ncelab.log -errormax 15 -update -status\n")
                make_file.write("SIMH_OPTS=-cdslib cds.lib -logfile cadenceLogs/ncsim.log -errormax 15 -gui\n")
                make_file.write("echo:\n")
                make_file.write('	@echo "VHDL FILES"\n')
                make_file.write("\n")
                make_file.write("compile:\n")
                make_file.write('	@echo "############################################################"\n')
                make_file.write('	@echo "################### Compile VHDL Files #####################"\n')
                make_file.write('	@echo "############################################################"\n')
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/JSON.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Misc/BufferCircular.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/HeMPS_defaults.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/Hermes_crossbar.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/Hermes_buffer.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/Hermes_switchcontrol.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/RouterCC.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/HyHeMPS_PKG.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Hermes/HermesTop.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Crossbar/CrossbarControl.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Crossbar/CrossbarRRArbiter.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Crossbar/CrossbarBridgev2.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Crossbar/CrossbarTop.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Bus/BusRRArbiter.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Bus/BusControl.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Bus/BusBridgev2.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Bus/BusTop.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Injector_PKG.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Injector.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/PE.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Trigger.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Receiver.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/HyHeMPS.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/HyHeMPS_TB.vhd\n")
                make_file.write('	@echo "############### FINALIZE COMPILE VHDL Files ################"\n')
                make_file.write("\n")
                make_file.write("elab:\n")
                make_file.write('	@echo "############################################################"\n')
                make_file.write('	@echo "################# Elaborate Top Level ######################"\n')
                make_file.write('	@echo "############################################################"\n')
                make_file.write("	ncelab $(ELAB_OPTS) worklib.hyhemps_tb\n")
                make_file.write('	@echo "########### FINALIZE ELABORATION  HYBRID Files #############"\n')
                make_file.write("\n")
                make_file.write("sim:\n")
                make_file.write('	@echo "############################################################"\n')
                make_file.write('	@echo "##################   SIMULATION HeMPS  #####################"\n')
                make_file.write('	@echo "############################################################"\n')
                make_file.write("	ncsim $(SIMH_OPTS) worklib.hyhemps_tb:rtl\n")
                make_file.write('	@echo "############### FINALIZE SIMULATION HYBRID #################"\n')
	    
        else:
            print("Error: Makefile argument <Makefile> not valid")
            exit(1)
			
    # TODO: Copy testbench HDL to project directory, in order to have project directory as reference directory in simulation tool
    
    print("Created project <" + args.ProjectName + "> at <" + os.path.abspath(ProjectDir) + ">")
