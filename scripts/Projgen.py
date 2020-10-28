
def projgen(args):
    
    import os
    
    # Check if given project path exists. If not, mkdir
    if os.path.isdir(args.ProjectDirectory + "/" + args.ProjectName):
        
        while True:
        
            print("Warning: Project path <" + args.ProjectDirectory + "/" + args.ProjectName + "> already exists. Do you wish to proceed (Y/N)?")
            ipt = raw_input()
            
            if ipt == "Y" or ipt == "y":
                # TODO: Prompt if projgen should wipe ProjectDirectory/ProjectName clean, so that only dirs created by projgen should exist within it
                break
            elif ipt == "N" or ipt == "n":
                exit(0)
                
    else:
        
        # TODO: Check if ProjectDirectory exists, and if not so, ask the user if it should be created
        os.makedirs(args.ProjectDirectory + "/" + args.ProjectName)
        
    # Makes "log", "flow" and "platform" dirs
    try:
        os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/flow")
    except OSError:
        pass

    try:
        os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/log")
    except OSError:
        pass

    try:
        os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/platform")
    except OSError:
        pass

    try:
        os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/src_json")
    except OSError:
        pass

        if args.HardwareDirs:
	
            try:
                os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/hardware")
            except OSError:
                pass
	
            try:
                os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/hardware/Bus")
            except OSError:
                pass
	    		
            try:
                os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/hardware/Crossbar")
            except OSError:
                pass
    
            try:
                os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/hardware/Hermes")
            except OSError:
                pass
	    		
            try:
                os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/hardware/Injector")
            except OSError:
                pass
	    		
            try:
                os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/hardware/Misc")
            except OSError:
                pass
	    		
            try:
                os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/hardware/Top")
            except OSError:
                pass
	    		
    if args.Makefile is not None:
    
        try:
            MakefileName = str(args.Makefile)
        except KeyError or IndexError:
            print("Error: Makefile argument <Makefile> not given")
            exit(1)
		
        if MakefileName=="cadence":

            try:
                os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/INCA_libs")
            except OSError:
                pass
				
            try:
                os.mkdir(args.ProjectDirectory + "/" + args.ProjectName + "/INCA_libs/worklib")
            except OSError:
                pass

            # Create CDS file
            with open(args.ProjectDirectory + "/" + args.ProjectName + "/cds.lib", 'w') as cds_file:
                cds_file.write("define worklib " + args.ProjectDirectory + "/" + args.ProjectName + "/INCA_libs/worklib\n")
                cds_file.write("include $CDS_INST_DIR/tools/inca/files/cds.lib\n")
				
            # Create Makefile file
            with open(args.ProjectDirectory + "/" + args.ProjectName + "/makefile", 'w') as make_file:
                make_file.write("########################################################################\n")
                make_file.write("# Makefile geral para simulacao da Hybrid HeMPS no ambiente Nupedee\n")
                make_file.write("########################################################################\n")
                make_file.write("# Obs:\n")
                make_file.write("# Alter $(HIBRIDA_HARDWARE_PATH) for custon VHDL\n")
                make_file.write("#\n")
                make_file.write("########################################################################\n")
                make_file.write("\n")
                make_file.write("########################## Command options #############################\n")
                make_file.write("VHDL_OPTS=-work worklib -cdslib cds.lib -logfile ncvhdl.log -errormax 15 -update -v93 -linedebug -status\n")
                make_file.write("ELAB_OPTS=-work worklib -cdslib cds.lib -logfile ncelab.log -errormax 15 -update -status\n")
                make_file.write("SIMH_OPTS=-cdslib cds.lib -logfile ncsim.log -errormax 15 -gui\n")
                make_file.write("echo:\n")
                make_file.write('	@echo "VHDL FILES"\n')
                make_file.write("\n")
                make_file.write("compile:\n")
                make_file.write('	@echo "############################################################"\n')
                make_file.write('	@echo "################    COMPILE VHDL Files #  ##################"\n')
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
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Injector/Receiver.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/HyHeMPS.vhd\n")
                make_file.write("	ncvhdl $(VHDL_OPTS) $(HIBRIDA_HARDWARE_PATH)/Top/HyHeMPS_TB.vhd\n")
                make_file.write('	@echo "############### FINALIZE COMPILE VHDL Files ################"\n')
                make_file.write("\n")
                make_file.write("elab:\n")
                make_file.write('	@echo "############################################################"\n')
                make_file.write('	@echo "################# ELABORATION  HYBRID ######################"\n')
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
    
    # os.environ["MOST_RECENT_HIBRIDA_PROJECT"] = args.ProjectDirectory + "/" + args.ProjectName
    print("Created \"" + args.ProjectName + "\" at \"" + args.ProjectDirectory + "\"")
    
