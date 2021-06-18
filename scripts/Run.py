import json
import os

def run(args):

    # Gets framework configs
    with open(os.getenv("HIBRIDA_CONFIG_FILE"), "r") as ConfigFile:
        ConfigDict = json.loads(ConfigFile.read())
        
    # Gets framework project index
    with open(ConfigDict["HibridaPath"] + "/data/projectIndex.json", "r") as ProjectIndexFile:
        ProjectIndexDict = json.loads(ProjectIndexFile.read())
    
    # Sets default project as MRU project
    if args.ProjectName is None:
        print("Warning: No project passed as target, using <" + ConfigDict["MostRecentProject"] + "> as default")
        args.ProjectName = ConfigDict["MostRecentProject"]
        
    # Checks if project exists
    if args.ProjectName not in ProjectIndexDict.keys():
        print("Error: Project <" + args.ProjectName + "> doesnt exist")
        exit(1)
        
    # Gets project dir
    ProjectDir = ProjectIndexDict[args.ProjectName]
    
    # Check if given project path exists
    if not os.path.isdir(ProjectDir):
        
        print("Error: ProjectDir <" + ProjectDir + "> does not exist")
        exit(1)
    
    # Tool-specific behaviour
    if args.Tool == "cadence":
        
        # Check if makefile exists
        if not os.path.isfile(os.path.join(ProjectDir, "makefile")):
        
            print("Error: Makefile does not exist for project <" + args.ProjectName + ">")
            print("Did you run projgen for another tool? To compile/elab/sim with with Cadence tools you must run projgen with Tool set as \"cadence\".")
        
        # Runs makefile with "run" rule
        os.system("make -f " + os.path.join(ProjectDir, "makefile") + " run " + "NCVHDL_CMD_OPTS=" + args.compopt + " NCELAB_CMD_OPTS=" + args.elabopt + " NCSIM_CMD_OPTS=" + args.simopt)
        
    elif args.Tool == "vivado":
        
        # Runs vivado with "run" script
        TCLScript = os.path.join(ConfigDict["HibridaPath"], "scripts", "vivado", "run.tcl")
        TCLArgs = args.ProjectName + " " + ProjectDir
        os.system("vivado -mode batch -source " + TCLScript + " -tclargs " + TCLArgs)
        
    else:
    
        print("Error: Tool <" + args.Tool + "> is not recognized")
        exit(1)
    
    with open(os.getenv("HIBRIDA_CONFIG_FILE"), "w") as ConfigFile:
        ConfigDict["MostRecentProject"] = args.ProjectName
        ConfigFile.write(json.dumps(ConfigDict, sort_keys = False, indent = 4))
    
    print("run executed successfully!")
    
