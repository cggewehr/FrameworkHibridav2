import json
import os

def sim(args):

    ConfigFile = open(os.environ["HIBRIDA_CONFIG_FILE"], "r+")
    ConfigDict = json.loads(ConfigFile.read())

    if args.ProjectName is None:
        print("Warning: No project passed as target, using <" + ConfigDict["MostRecentProject"] + "> as default")
        args.ProjectName = ConfigDict["MostRecentProject"]
        
    ProjectDir = ConfigDict["Projects"][args.ProjectName]["ProjectDir"]
        
    # Check if given project path exists
    if not os.path.isdir(ProjectDir):
        
        print("Error: ProjectDir <" + ProjectDir + "> does not exist")
        exit(1)
    
    if args.Tool == "cadence":
        
        # Check if makefile exists
        if not os.path.isfile(os.path.join(ProjectDir, "makefile")):
        
            print("Error: Makefile does not exist for project <" + args.ProjectName + ">")
            print("Did you run projgen for another tool? To compile/elab/sim with with Cadence tools you must run projgen with Tool set as \"cadence\".")
        
        # Runs makefile with sim rule
        os.system("make -f " + os.path.join(ProjectDir, "makefile") + " -C " + ProjectDir + " sim " + "NCSIM_CMD_OPTS=" + args.opt)
        
    elif args.Tool == "vivado":
        
        # Runs vivado with sim script
        TCLScript = os.path.join(ConfigDict["HibridaPath"], "scripts", "vivado", "sim.tcl")
        TCLArgs = args.ProjectName + " " + ProjectDir
        os.system("vivado -mode batch -source " + TCLScript + " -tclargs " + TCLArgs)
        
    else:
    
        print("Error: Tool <" + args.Tool + "> is not recognized")
        exit(1)
    
    ConfigDict["MostRecentProject"] = args.ProjectName
    ConfigFile.seek(0)
    ConfigFile.truncate(0)
    ConfigFile.write(json.dumps(ConfigDict, sort_keys = False, indent = 4))
    ConfigFile.close()
    
    print("sim executed successfully!")
    
